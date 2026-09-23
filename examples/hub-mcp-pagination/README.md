# HF Hub MCP pagination reproduction

Companion to [the technical case study](../../notes/mcp-tool-discovery.md) and [upstream Issue #4956](https://github.com/huggingface/huggingface_hub/issues/4956).

Status checked on 23 September 2026: [PR #4960](https://github.com/huggingface/huggingface_hub/pull/4960), authored by Kayvan-Zahiri, was merged on 22 September and resolves Issue #4956 using the issue reproduction. My contribution is the report and reproduction; the merged code is the other author's work. This directory preserves the original affected version and local proposal for comparison, not an official Hub release. The upstream fix requires MCP >=1.9.4; the historical local proposal below used 1.9.1.

## Run the affected version

Use a fresh working directory, Python 3.11, Git, and [uv](https://docs.astral.sh/uv/). From this example directory:

```bash
git clone https://github.com/huggingface/huggingface_hub.git hub-source
git -C hub-source checkout 8efc0a954dfd20cd8f4fd7987f1e51531f313dae
uv venv --python 3.11
uv pip install --python .venv/bin/python -e 'hub-source[mcp]' 'mcp==1.30.0'
.venv/bin/python reproduce.py
```

The final command is expected to print `tools=['search_docs']` and raise `AssertionError`. Dependency installation needs the network; the reproduction itself uses only a local stdio child process and sends no model request. On Windows, use `.venv/Scripts/python.exe` in place of `.venv/bin/python`; the recorded runs were on macOS.

The server exposes `search_docs` on its first page and `fetch_doc` on its second. Both tools should be discoverable before any model is called.

## Apply the local proposal

```bash
git -C hub-source apply ../proposal.patch
.venv/bin/python reproduce.py
```

Now the expected output is `tools=['search_docs', 'fetch_doc']`, with exit code 0. The proposal also includes regression tests and raises the optional MCP minimum to 1.9.1; its testing-extra change is not needed to run this single stdio script. Detailed regression and minimum-version results are recorded in the case study.

The exact baseline, script and patch were tested locally. Package versions beyond the explicitly pinned MCP version can change when installing in a new environment.

## Scope and attribution

The patch modifies Hugging Face Hub, copyright the Hugging Face team, under the Apache License 2.0; that license is included here. The reproduction and additional test code are provided under the same license. AI assisted investigation, implementation, review and writing. This is a locally reproduced protocol behavior, with no production incident claimed. The report is resolved upstream by another contributor's merged fix; no package release or ownership of that implementation is claimed.
