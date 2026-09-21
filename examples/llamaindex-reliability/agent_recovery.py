"""Offline end-to-end evidence for parallel tool-result message pairing.

Run with the installed llama-index-core version, or use PYTHONPATH for a
specific source checkout. No library source or upstream tests are modified. Both standalone and AgentWorkflow execution paths
are exercised, with streaming enabled and disabled. The script exits nonzero
when a completed tool result is lost or an error is fabricated as an assistant
message. All data, tools, and model responses are synthetic.
"""

import asyncio
import hashlib
import inspect
from importlib.metadata import version
import platform
import json
import socket
from collections import Counter
from unittest.mock import patch

from llama_index.core import Settings
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    ToolCallResult,
)
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.llms.llm import ToolSelection
from llama_index.core.llms.mock import MockFunctionCallingLLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool


ERROR_TEXT = "Synthetic location unavailable; use verified fallback"
VERIFY_TEXT = "Synthetic map evidence verified"
FINAL_TEXT = "Synthetic fallback selected after reading both tool results"
EXPECTED_IDS = ["call_locate", "call_verify"]


def summarise(message):
    return {
        "role": message.role.value,
        "tool_call_id": message.additional_kwargs.get("tool_call_id"),
        "requested_tool_ids": [
            call.tool_id for call in message.additional_kwargs.get("tool_calls", [])
        ],
        "content": message.content,
    }


async def run_case(wrapper, streaming):
    model_inputs = []
    tool_events = []
    executed_tools = []
    release_verifier = asyncio.Event()

    async def locate():
        """Synthetic direct-return location tool that fails."""
        executed_tools.append("locate")
        raise RuntimeError(ERROR_TEXT)

    async def verify():
        """Synthetic ordinary verifier, released after locate's result event."""
        await release_verifier.wait()
        executed_tools.append("verify")
        return VERIFY_TEXT

    def respond(messages, **kwargs):
        model_inputs.append([summarise(message) for message in messages])
        if len(model_inputs) == 1:
            return ChatMessage(
                role="assistant",
                content="Checking location and map evidence in parallel",
                additional_kwargs={
                    "tool_calls": [
                        ToolSelection(
                            tool_id="call_locate", tool_name="locate", tool_kwargs={}
                        ),
                        ToolSelection(
                            tool_id="call_verify", tool_name="verify", tool_kwargs={}
                        ),
                    ]
                },
            )
        if len(model_inputs) != 2:
            raise AssertionError("Unexpected third model call")
        return ChatMessage(role="assistant", content=FINAL_TEXT)

    agent = FunctionAgent(
        name="offline_location_agent",
        description="Synthetic offline regression probe",
        tools=[
            FunctionTool.from_defaults(async_fn=locate, return_direct=True),
            FunctionTool.from_defaults(async_fn=verify),
        ],
        llm=MockFunctionCallingLLM(response_generator=respond),
        streaming=streaming,
        allow_parallel_tool_calls=True,
        timeout=10,
    )
    runner = (
        AgentWorkflow(agents=[agent], root_agent=agent.name, timeout=10)
        if wrapper == "AgentWorkflow"
        else agent
    )
    memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
    handler = runner.run(user_msg="Choose a synthetic fallback location", memory=memory)
    async for event in handler.stream_events():
        if isinstance(event, ToolCallResult):
            tool_events.append(
                {
                    "tool_call_id": event.tool_id,
                    "is_error": event.tool_output.is_error,
                    "return_direct": event.return_direct,
                }
            )
            if event.tool_id == "call_locate":
                release_verifier.set()
    result = await handler
    second_input = model_inputs[1] if len(model_inputs) > 1 else []
    tool_messages = [m for m in second_input if m["role"] == "tool"]
    tool_ids = [m["tool_call_id"] for m in tool_messages]
    fake_assistant_errors = [
        m
        for m in second_input
        if m["role"] == "assistant" and ERROR_TEXT in (m["content"] or "")
    ]
    checks = {
        "both_tools_actually_executed": executed_tools == ["locate", "verify"],
        "failed_direct_result_arrived_first": tool_events
        == [
            {"tool_call_id": "call_locate", "is_error": True, "return_direct": True},
            {"tool_call_id": "call_verify", "is_error": False, "return_direct": False},
        ],
        "model_called_again_after_error": len(model_inputs) == 2,
        "all_tool_call_ids_matched_once": Counter(tool_ids) == Counter(EXPECTED_IDS),
        "normal_tool_output_visible": any(
            m["tool_call_id"] == "call_verify" and m["content"] == VERIFY_TEXT
            for m in tool_messages
        ),
        "error_retained_as_tool_output": any(
            m["tool_call_id"] == "call_locate" and ERROR_TEXT in (m["content"] or "")
            for m in tool_messages
        ),
        "no_fabricated_assistant_error": not fake_assistant_errors,
        "workflow_reaches_final_response": result.response.content == FINAL_TEXT,
    }
    return {
        "runner": wrapper,
        "streaming": streaming,
        "tool_result_events": tool_events,
        "second_model_input": second_input,
        "checks": checks,
        "passed": all(checks.values()),
    }


async def run_checks():
    # A deterministic local tokenizer avoids external model/tokenizer assets.
    Settings.tokenizer = lambda text: list(text.encode("utf-8"))
    cases = []
    for wrapper in ("FunctionAgent", "AgentWorkflow"):
        for streaming in (False, True):
            try:
                cases.append(await run_case(wrapper, streaming))
            except Exception as exc:
                cases.append(
                    {
                        "runner": wrapper,
                        "streaming": streaming,
                        "error": f"{type(exc).__name__}: {exc}",
                        "passed": False,
                    }
                )
    print(
        json.dumps(
            {
                "network": "socket connections blocked",
                "implementation_module": FunctionAgent.__module__,
                "versions": {
                    "python": platform.python_version(),
                    **{
                        name: version(name)
                        for name in (
                            "llama-index-core",
                            "llama-index-workflows",
                            "pydantic",
                        )
                    },
                },
                "handler_source_sha256": hashlib.sha256(
                    inspect.getsource(FunctionAgent.handle_tool_call_results).encode()
                ).hexdigest(),
                "cases": cases,
                "passed": all(case["passed"] for case in cases),
            },
            indent=2,
        ),
        flush=True,
    )
    return all(case["passed"] for case in cases)


async def main():
    # asyncio.run creates the event loop before entering this connection guard.
    with (
        patch.object(
            socket.socket, "connect", side_effect=RuntimeError("Network forbidden")
        ),
        patch.object(
            socket.socket, "connect_ex", side_effect=RuntimeError("Network forbidden")
        ),
        patch.object(
            socket, "create_connection", side_effect=RuntimeError("Network forbidden")
        ),
    ):
        return await asyncio.wait_for(run_checks(), timeout=45)


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
