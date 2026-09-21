# Discovering every MCP tool before applying an allowlist

**Zhengyang Wang · AI-assisted open-source investigation · 21 September 2026**

[Hugging Face Hub Issue #4956](https://github.com/huggingface/huggingface_hub/issues/4956) reports incomplete tool discovery in `MCPClient`. The issue is open and awaiting scope feedback. A local patch and regression tests are complete; **no upstream PR has been opened and no fix has been merged**.

## A tool can exist but remain invisible

The affected client asks an MCP server for its tools once. If the server returns a second-page cursor, the client stops anyway. A local server advertising `search_docs` first and `fetch_doc` next therefore exposes only `search_docs` to the Hub client. Filtering for `allowed_tools=["fetch_doc"]` then produces no tools at all.

The failure happens during discovery, before model inference. A model cannot choose a tool that the application never added to its available-tool list or session lookup.

MCP's [tool-listing operation](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#listing-tools) supports pagination. Its [pagination specification](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/pagination) treats cursors as opaque tokens; the absence of a continuation cursor ends the sequence. The client should pass tokens back unchanged and support both single-page and paginated responses.

## Reproduction through a real local server

The [runnable example and proposed patch](../examples/hub-mcp-pagination/) pin the affected Hub source to commit `8efc0a954dfd20cd8f4fd7987f1e51531f313dae`, reported as `1.33.0.dev0`. The [script](../examples/hub-mcp-pagination/reproduce.py) launches a child process using the official MCP server and stdio transport. The parent uses Hub's public `MCPClient.add_mcp_server` API.

| Execution | Discovered tools | Result |
| --- | --- | --- |
| Affected source | `['search_docs']` | Assertion fails |
| Local proposal | `['search_docs', 'fetch_doc']` | Assertion passes |

The reproduction needs no dataset, GPU, API key or model request. Its purpose is to establish the missing page at the protocol boundary.

## Collect pages, then filter

The proposed flow collects the first response, follows each `nextCursor`, and appends the tools from every page. Only after discovery finishes does it apply the existing allowlist and register tools against their sessions. Existing duplicate-name handling stays in place.

An empty page is not by itself an end marker: a server may still provide a continuation cursor. One regression case deliberately places an empty page between the two tools. Another allows only the last-page tool. Together they check both complete discovery and filtering order.

The three cases use actual MCP `Server` and `ClientSession` messages over in-memory streams. They replace the transport, not the method whose pagination behavior is being fixed. Assertions cover available-tool names, session keys and requested cursors. The separate stdio example additionally verifies a real subprocess boundary.

## Compatibility is part of the fix

Hub's original MCP extra allowed SDK 1.8.0. That version's convenience `list_tools()` method has no cursor parameter. The proposal chooses a minimum of 1.9.1, which forwards the cursor correctly, and keeps one implementation path using the public convenience method.

This is a maintenance choice, not a claim that supporting older SDKs is impossible. Older SDKs would require an additional protocol compatibility layer: their request types also differ, so adding a version check and passing a cursor is insufficient. That alternative adds code paths and a separate serialization test matrix. Calling the low-level API on every SDK version is undesirable: newer [`ClientSession.list_tools`](https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/src/mcp/client/session.py) also records tool output schemas for later validation. The proposal preserves that bookkeeping and explicitly raises the optional dependency floor for maintainer discussion.

## Executed checks and limits

On macOS ARM64 with Python 3.11.15, the three new regressions produced **2 failures and 1 pass** before the fix. After the fix, **all 3 passed on MCP 1.9.1 and again on 1.30.0**. The stdio reproduction passed on both versions. `make style` and `make quality` passed in the local Hub checkout.

These are local results, not upstream CI or multi-platform results. The tests cover discovery and registration; they do not claim to exercise model inference, every server implementation or malformed pagination that repeats forever.

The issue-first workflow follows the repository's [contribution guidance](https://github.com/huggingface/huggingface_hub/blob/8efc0a954dfd20cd8f4fd7987f1e51531f313dae/CONTRIBUTING.md). Scope and the dependency decision remain open to maintainer feedback. AI assisted the investigation, code, testing, review and writing; all stated test results come from executed checks.

## 中文摘要

HF Hub 的 MCPClient 原先只获取工具列表第一页，后续页面的工具不会进入可用列表和 session 映射，允许列表若只选后页工具还会得到空结果。已用真实本地 stdio 服务复现，并准备“完整分页后再过滤”的修复与三类回归，在 MCP 1.9.1、1.30.0 验证通过。依赖下限调整是待维护者讨论的取舍；当前是已报告、补丁完成，尚未提交 PR 或合并。
