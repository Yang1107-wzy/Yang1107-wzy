# Invalid point clouds must not look like perfect predictions

A runnable, offline companion to my [TorchMetrics issue #3542](https://github.com/Lightning-AI/torchmetrics/issues/3542) and [draft repair PR #3543](https://github.com/Lightning-AI/torchmetrics/pull/3543). As of 2 October 2026, the PR is submitted and **not merged**.

Procrustes disparity compares point clouds after centering, scaling and alignment. A cloud containing only one distinct point cannot be normalized. In the affected implementation, the resulting SVD error is caught and replaced by a scalar zero score plus scale/rotation tensors. That looks like a perfect match, affects the whole batch, and returns a tuple even when callers requested only disparity. The stateful metric then crashes when it tries to sum that tuple.

The proposed repair validates inputs before normalization and lets unexpected backend failures propagate. It detects identical points before centering: a repeated decimal such as `0.1` can otherwise acquire a tiny nonzero centered norm through mean rounding. It preserves valid collinear clouds; collinearity alone is not a reason to reject a cloud. This example reflects my interest in geometry and measurement reliability through MetroHeight, without claiming that project uses TorchMetrics.

## Reproduce

Use Python 3.12 in a disposable environment. Installation needs network access; the script itself only uses synthetic CPU tensors and calls no model service.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install 'torch==2.10.0' 'numpy==2.3.5' 'lightning-utilities==0.15.3' 'packaging==26.3'
.venv/bin/python -m pip install --no-deps 'torchmetrics @ git+https://github.com/Lightning-AI/torchmetrics.git@6c551c6469dc04fe92291c000ce2607860df92d2'
.venv/bin/python check_point_clouds.py
```

The last command should print JSON and exit **1**: zero-spread integer-valued clouds return a zero-score tuple, while repeated `0.1` coordinates can slip through the mean-based check and incorrectly update the metric. Valid collinear inputs should pass. To compare the proposed repair in the same environment:

```bash
.venv/bin/python -m pip install --no-deps --force-reinstall 'torchmetrics @ git+https://github.com/Yang1107-wzy/torchmetrics.git@5ecdc77ff71a4246b4d1620f8e2cfe36410783ae'
.venv/bin/python check_point_clouds.py
```

The repaired implementation should exit **0** with all eight checks passing. Runtime verdicts work with `python -O` as well. On Windows use `.venv/Scripts/python.exe`.

Local verification: macOS ARM64, Python 3.12.13, PyTorch 2.10.0. The baseline and proposed commit were each installed from their pinned remote commits into a fresh environment using the dependencies above; normal and optimized Python produced the expected exit codes. This is a focused behavioral probe, not the complete upstream CI. The separate PR shape suite passed 35 CPU tests with two distributed tests excluded. No GPU result is claimed.

These original diagnostic files use the included MIT license. Codex assisted with investigation, implementation, testing and writing. TorchMetrics is the external library being tested; this example does not represent maintainer acceptance or a released fix.
