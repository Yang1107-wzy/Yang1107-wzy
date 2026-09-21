# Keeping tool failures out of an agent's answer

**Contribution:** regression evidence and code review on [LlamaIndex PR #22562](https://github.com/run-llama/llama_index/pull/22562), authored by **Sehlani042**. I did not author that PR. **Status: [review submitted](https://github.com/run-llama/llama_index/pull/22562#pullrequestreview-5266960619)** on 21 September 2026; not accepted or merged.

This investigation relates to the validation and fallback work in my MapAgent project. All tools, positions, and model responses in the reproduction are synthetic; it does not use private research data or imply that MapAgent runs on LlamaIndex.

[Run the offline reproduction](../examples/llamaindex-reliability/README.md): pinned dependencies, synthetic inputs, explicit failure exit codes, and comparison instructions.

## The failure boundary

A function-calling agent keeps tool responses in its message history before deciding what to do next. A tool configured with `return_direct=True` can provide the final answer, but a tool failure must remain an error the agent can recover from.

The existing PR fixes missing responses from parallel calls. I checked its exact head, `462463054382088055d47d6b3737db0e9d58fac9`, and found a remaining mismatch: its message handler can select a failed direct-return result, while the workflow's aggregator selects only successful results.

| Completed results | Expected message handling | Observed at the reviewed head |
| --- | --- | --- |
| Failed direct-return tool + ordinary successful tool | Keep both tool responses and let the model recover | Both responses retained, plus an assistant answer containing the error |
| Failed direct-return tool + successful direct-return tool | Use the successful result as the direct answer | The handler stores the earlier failure as the assistant answer |

Matching the aggregator's first-successful-result rule also keeps handoff selection consistent: select the eligible result first, then omit a direct assistant answer when that result is a handoff.

## Validation and review scope

I replayed the proposed `FunctionAgent` file against core base `f475afd8a9bbda84f252567e045d89d07b5701b3` (replacing only that file), using a mock LLM and real execution of synthetic tools. `FunctionAgent` and a single-agent `AgentWorkflow`, each with streaming on and off, all retained both tool-call IDs but added the extra assistant error. Network connections were blocked for these checks. This was not a test of a real model provider or cross-agent handoff.

A local alternative matching the aggregator passed all four recovery checks. I shared the failure case and regression suggestions with the existing PR rather than opening a competing implementation. Submission does not establish that the review has been accepted or the proposed change merged.

AI assistance: Codex assisted with investigation, tests, independent review, and writing; the reported checks were executed locally.
