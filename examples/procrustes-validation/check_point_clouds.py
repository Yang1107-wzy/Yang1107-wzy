"""Offline behavioral probe for TorchMetrics issue #3542; synthetic CPU inputs only."""

import hashlib
import inspect
import json
import sys
import warnings

import torch
from torchmetrics.functional.shape import procrustes_disparity
from torchmetrics.shape import ProcrustesDisparity


def main():
    cloud = torch.arange(24, dtype=torch.float64).reshape(2, 4, 3)
    checks = []
    observed = []
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        disparity = procrustes_disparity(cloud, 3 * cloud + 4)
        valid = isinstance(disparity, torch.Tensor) and disparity.shape == (2,)
        valid = valid and torch.allclose(disparity, torch.zeros(2, dtype=cloud.dtype), atol=1e-12)
        checks.append({"case": "valid_collinear_transform", "passed": bool(valid)})
        for label, invalid in [("constant", torch.ones_like(cloud)), ("nan", cloud.clone())]:
            if label == "nan":
                invalid[1, 0, 0] = float("nan")
            for return_all in (False, True):
                try:
                    result = procrustes_disparity(invalid, cloud, return_all=return_all)
                except ValueError:
                    outcome, passed = "ValueError", True
                except Exception as exc:
                    outcome, passed = type(exc).__name__, False
                else:
                    value = result[0] if isinstance(result, tuple) else result
                    outcome = {"type": type(result).__name__, "disparity": value.tolist()}
                    passed = False
                checks.append({"case": f"{label}_return_all_{return_all}", "passed": passed, "observed": outcome})
        metric = ProcrustesDisparity()
        metric.update(cloud, cloud)
        before = (metric.disparity.clone(), metric.total.clone())
        try:
            metric.update(torch.ones_like(cloud), cloud)
        except ValueError:
            outcome, rejected = "ValueError", True
        except Exception as exc:
            outcome, rejected = type(exc).__name__, False
        else:
            outcome, rejected = "accepted", False
        unchanged = torch.equal(before[0], metric.disparity) and torch.equal(before[1], metric.total)
        checks.append({"case": "metric_rejects_without_accumulating", "passed": rejected and unchanged, "observed": outcome})
        observed = [str(item.message) for item in captured]
    report = {
        "torch_version": torch.__version__,
        "functional_source_sha256": hashlib.sha256(inspect.getsource(procrustes_disparity).encode()).hexdigest(),
        "checks": checks,
        "warnings": observed,
    }
    print(json.dumps(report, indent=2))
    return 0 if all(item["passed"] for item in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
