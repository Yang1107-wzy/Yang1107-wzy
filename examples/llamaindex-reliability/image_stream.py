"""Check synthetic image bytes and streams without making a model request."""

import base64
from importlib.metadata import version
from io import BytesIO
import json
import platform
import socket
from unittest.mock import patch

from PIL import Image
from llama_index.core.base.llms.types import ImageBlock


def main():
    stream = BytesIO()
    Image.new("RGB", (2, 2), (23, 45, 67)).save(stream, format="PNG")
    raw = stream.getvalue()
    expected_base64 = base64.b64encode(raw)
    expected_url = "data:image/png;base64," + expected_base64.decode()
    cases = []
    for name, source in [("bytes", raw), ("BytesIO", BytesIO(raw))]:
        block = ImageBlock(image=source, image_mimetype="image/png")
        checks = {
            "raw_matches": block.resolve_image().read() == raw,
            "base64_matches": block.resolve_image(as_base64=True).read()
            == expected_base64,
        }
        error = None
        try:
            checks["inline_url_matches"] = block.inline_url() == expected_url
        except Exception as exc:
            checks["inline_url_matches"] = False
            error = type(exc).__name__
        cases.append(
            {
                "input": name,
                "checks": checks,
                "inline_url_error": error,
                "passed": all(checks.values()),
            }
        )
    passed = all(case["passed"] for case in cases)
    print(
        json.dumps(
            {
                "versions": {
                    "python": platform.python_version(),
                    "llama-index-core": version("llama-index-core"),
                },
                "network": "socket connections blocked during checks",
                "cases": cases,
                "passed": passed,
            },
            indent=2,
        )
    )
    return passed


if __name__ == "__main__":
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
        raise SystemExit(0 if main() else 1)
