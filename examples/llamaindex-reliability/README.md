# Offline LlamaIndex reliability probes

Runnable companions to the [image-stream case](../../notes/llamaindex-image-streams.md) and [agent-recovery review](../../notes/agent-tool-results.md). The scripts generate synthetic inputs and make no model request. They do not load private projects, credentials, or research data.

## Run the affected release

Use Python 3.12 and [uv](https://docs.astral.sh/uv/). From this directory:

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python image_stream.py
.venv/bin/python agent_recovery.py
```

Dependency installation needs network access unless packages are cached. Both scripts print JSON and exit **1 on the pinned affected release**; run the two commands separately so the first failure does not prevent the second. Exit 0 means all checks passed. Failure exit codes remain effective with `python -O`.

All 62 package versions are pinned to the environment validated on **macOS / CPython 3.12.13 on 21 September 2026**, including `llama-index-core==0.14.24` and `llama-index-workflows==2.24.1`. Other operating systems were not tested; on Windows the environment interpreter is `.venv/Scripts/python.exe`.

| Probe | Expected result on the pinned release |
| --- | --- |
| `image_stream.py` | `bytes` passes; `BytesIO` fails Base64 and data-URL checks, reporting `UnicodeDecodeError` |
| `agent_recovery.py` | Four combinations reproduce a missing completed tool response and an extra assistant answer containing the tool error |

The agent combinations are `FunctionAgent` and a **single-agent** `AgentWorkflow`, each with streaming on/off. They do not exercise actual cross-agent handoff or a live model provider. Runtime checks block socket connections after event-loop creation; the agent probe has per-workflow and overall timeouts. JSON reports dependency versions without embedding a local source path; the agent probe also records its handler source hash. The agent probe reports per-case exceptions separately from failed behavioral checks; its overall timeout exits with an exception before a complete JSON report. The image probe records data-URL exception types, while other unexpected errors propagate normally.

## Compare another implementation

The scripts test the code Python imports; they do not download or apply a PR. With an existing checkout, select its core source explicitly:

```bash
PYTHONPATH=/path/to/llama_index/llama-index-core .venv/bin/python image_stream.py
PYTHONPATH=/path/to/llama_index/llama-index-core .venv/bin/python agent_recovery.py
```

The installed package version reported in JSON remains the installed distribution version when `PYTHONPATH` overrides the source. Record the checkout commit separately.

Locally verified comparisons:

- Image probe: [proposed image fix `6e7527c`](https://github.com/Yang1107-wzy/llama_index/commit/6e7527ca48d861cfaa73eea724ce12aed8e0412e) passes with exit 0. [PR #23159](https://github.com/run-llama/llama_index/pull/23159) is submitted, not merged as of the validation date.
- Agent probe: replaying the `FunctionAgent` file from [PR #22562 head `4624630`](https://github.com/run-llama/llama_index/pull/22562/commits/462463054382088055d47d6b3737db0e9d58fac9) against core base `f475afd8a9bbda84f252567e045d89d07b5701b3` (replacing only that source file) preserves both tool responses but still adds the assistant error; all four combinations exit with a failing verdict. This is distinct from the pinned release's original missing-response defect.
- A local alternative matching the aggregator's selection passes all four combinations. It was used to validate the [review feedback](https://github.com/run-llama/llama_index/pull/22562#pullrequestreview-5266960619), not submitted as a competing PR or packaged here as an accepted fix.

These are behavioral probes, not a full test suite or an upstream acceptance claim. Normal and optimized Python runs were checked for each comparison.

## Attribution

LlamaIndex is the external library under investigation. The image fix is my submitted contribution; PR #22562 belongs to **Sehlani042**, and my contribution there is regression evidence and review. These original diagnostic scripts are provided under the included MIT license. Codex assisted with development, independent review, testing, and writing.
