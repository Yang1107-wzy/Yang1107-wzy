# Fixing cross-process cache locks in Hugging Face Datasets

**Zhengyang Wang · AI-assisted open-source contribution · 21 September 2026**

[Hugging Face Datasets PR #8654](https://github.com/huggingface/datasets/pull/8654) proposes a fix for a cross-process locking bug. At the time of writing, the PR is **open, awaiting upstream review, and not merged**. The change and regression tests are in [commit `9020531`](https://github.com/Yang1107-wzy/datasets/commit/9020531e2b504de6fcf2894d4277a217a0af4efd).

## The problem and its scope

A file lock coordinates processes only when they lock the same file. Datasets shortens oversized lock filenames to fit the filesystem's filename limit. Its existing implementation used `str(hash(filename))` for the shortened suffix. Independently started Python processes could therefore turn the same requested path into different physical lock files, allowing both processes into the supposedly protected section.

This affects filenames that enter the shortening branch. An actual internal caller is [`DatasetBuilder.__init__`](https://github.com/huggingface/datasets/blob/3e2c1a6c33b883fd9710f55f7b6fa4ab64d0ee07/src/datasets/builder.py#L404), which flattens a cache-directory path into a lock basename. A deeply nested path can make that basename long even when the original directory components are individually valid.

Synthetic long paths reproduce the loss of mutual exclusion. Short lock names bypass the shortening branch.

## Minimal reproduction

The following identity check is adapted from [Issue #8653](https://github.com/huggingface/datasets/issues/8653). Run it in an environment with the affected Datasets checkout installed: baseline commit `3e2c1a6c33b883fd9710f55f7b6fa4ab64d0ee07`, reported as `5.0.2.dev0`.

```python
import os
import subprocess
import sys
import tempfile

child = """
import sys
from datasets.utils._filelock import FileLock
print(FileLock(sys.argv[1]).lock_file)
"""
with tempfile.TemporaryDirectory() as directory:
    path = os.path.join(directory, "a" * 1000 + ".lock")
    names = [
        subprocess.check_output(
            [sys.executable, "-c", child, path],
            env=dict(os.environ, PYTHONHASHSEED=seed),
            text=True,
        ).strip()
        for seed in ("0", "1")
    ]
    assert names[0] == names[1], names
```

The assertion fails on the affected implementation: the two processes produce different names. This isolates the naming defect without a dataset download or external service.

## Root cause and the design decision

Python deliberately randomizes string hashes across interpreter invocations. A value stable within one process is consequently unsuitable as a shared filesystem identifier. [`PYTHONHASHSEED`](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED) makes this reproducible; the two seeds expose the mismatch without relying on chance between ordinary launches.

The proposed suffix is `hashlib.sha256(os.fsencode(filename)).hexdigest()[:16]`. Filesystem encoding supplies the bytes, SHA-256 supplies a deterministic digest, and 16 hexadecimal characters retain 64 bits. The existing readable prefix and `.lock` ending remain.

Digest length matters here. An initial full-length SHA-256 suffix consumed 64 characters; adding `...` and `.lock` required 72 before any prefix. Review found that a 64-character filename limit then produced a negative prefix-slice boundary and an oversized result. The compact suffix leaves room under the tested 32- and 64-character limits. Its width is comparable to the previous hash on the tested 64-bit runtime. The suffix remains finite-width; the retained prefix is also part of the lock identity.

## Testing the behavior that matters

Matching names explains the cause, but the regression checks actual exclusion. The parent acquires the lock, then starts a fresh interpreter with seed 0 or 1. While the parent holds the lock, the child's immediate acquisition must raise `filelock.Timeout`. After release, another child must acquire successfully. Both children receive the original path, forcing independent shortening.

Short filenames provide a control. Separate tests constrain filename length to 32 and 64 characters and acquire the resulting locks. The [submitted tests](https://github.com/Yang1107-wzy/datasets/blob/9020531e2b504de6fcf2894d4277a217a0af4efd/tests/test_filelock.py) therefore cover naming limits, exclusion, and release.

Local macOS ARM64 validation used Python 3.12.13. The initial regression produced **2 failed, 3 passed** on the baseline: both long-name children acquired locks while the parent held its lock. The final patch produced **7 passed** with filelock 4.0.1; the earlier five-test suite also passed with filelock 3.25.2. Repository linting and formatting checks passed. A subsequent [focused GitHub Actions run](https://github.com/Yang1107-wzy/datasets/actions/runs/35593091250) checked the exact PR commit on Linux and Windows with two environments on each OS: Python 3.10 / filelock 3.25.2 and Python 3.14 / filelock 4.0.1. Each of the four jobs passed all seven tests. This workflow is kept on a separate fork branch; upstream full CI still awaits maintainer approval.

Long lock names change with this fix, so old and patched processes should not be assumed to coordinate during mixed-version execution. The lesson is that synchronization depends on stable resource identity as well as the locking primitive.

AI assisted investigation, implementation, tests, review, and writing. The reported results come from executed checks; upstream acceptance remains pending. The underlying Datasets implementation is copyright Hugging Face and licensed under [Apache License 2.0](https://github.com/huggingface/datasets/blob/3e2c1a6c33b883fd9710f55f7b6fa4ab64d0ee07/LICENSE).

## 中文摘要

Datasets 用 Python 的进程随机哈希缩短长锁名，导致同一路径在不同进程中对应不同文件，互斥失效。PR #8654 提议采用确定性摘要，并用父进程持锁、子进程尝试获取、释放后重试的回归验证实际行为。本地 macOS 与 Linux、Windows 四组云端环境的七项相关测试均通过；PR 尚待审查、未合并，过程使用 AI 辅助。
