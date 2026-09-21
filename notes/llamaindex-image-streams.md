# In-memory images and model input encoding

**Status, 21 September 2026:** [LlamaIndex PR #23159](https://github.com/run-llama/llama_index/pull/23159) submitted; not merged. The change concerns multimodal image preparation, an area related to my image-data and validation work.

## The failure

LlamaIndex accepts both `bytes` and file-like image streams. On `llama-index-core==0.14.24` and upstream commit `f475afd8`, the same PNG works as bytes but fails as `BytesIO` when converted into a data URL:

```python
from io import BytesIO
from PIL import Image
from llama_index.core.base.llms.types import ImageBlock

stream = BytesIO()
Image.new("RGB", (2, 2), (23, 45, 67)).save(stream, format="PNG")
block = ImageBlock(image=stream, image_mimetype="image/png")
block.inline_url()  # Before the fix: UnicodeDecodeError at PNG byte 0x89
```

`inline_url()` requests Base64, but the stream branch of `resolve_image()` returns the original binary data. Decoding that PNG as UTF-8 fails before any model request. This reproduction needs no model credentials or private images.

## The fix and its boundaries

The proposed change uses the existing binary-normalization helper only when Base64 is requested for a stream. Reusing that helper matters: some streams already contain Base64, and unconditional encoding would add an incorrect second layer.

Default resolution still returns the original stream. Its contents and ownership remain unchanged, and the cursor is reset to zero. This preserves the buffer-reuse behavior from [PR #21339](https://github.com/run-llama/llama_index/pull/21339). Automatic MIME inference and audio/video behavior are outside this patch.

## Verification

- The two initial regressions fail on the unchanged implementation; the release-wheel reproduction also fails.
- Final tests cover raw and encoded image streams, repeated calls, a nonzero starting cursor, unchanged source contents and identity, data URLs, and empty-stream errors.
- All **115 tests in `tests/base/llms/test_types.py` pass locally** on Python 3.12. This is the affected module, not the entire repository suite.
- Repository pre-commit hooks pass on both changed files. Upstream review and CI are tracked on the PR.

[Patch and regression tests](https://github.com/Yang1107-wzy/llama_index/commit/6e7527ca48d861cfaa73eea724ce12aed8e0412e).

Codex assisted with investigation, implementation, tests, and writing. An independent Codex review checked compatibility and caught the double-encoding case during development. No human maintainer acceptance is claimed before review.

中文说明：这项修复针对多模态模型输入之前的图像编码环节。内存 PNG 流此前没有按要求转成 Base64，导致生成图像链接时异常；补丁同时保留流复用行为，并兼容已经编码的图片。当前为已提交、待审状态。
