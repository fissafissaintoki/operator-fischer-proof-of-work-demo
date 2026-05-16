#!/usr/bin/env python3
"""
Safe Prompterator Security Check

Purpose:
- Defensive validation of Prompterator protection layers.
- Designed for systems owned or explicitly authorized by the operator.
- No mass scanning, no exploit payloads, no bypass logic, no secret handling.

Default target:
- https://www.prompterator.de

Usage:
    python3 tests/security/safe_prompterator_security_check.py

Optional:
    PROMPTERATOR_TARGET=https://www.prompterator.de python3 tests/security/safe_prompterator_security_check.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


TARGET = os.environ.get("PROMPTERATOR_TARGET", "https://www.prompterator.de").rstrip("/")
ORIGIN = os.environ.get("PROMPTERATOR_ORIGIN", "https://www.prompterator.de")


@dataclass
class Result:
    label: str
    method: str
    path: str
    status: int | str
    body: str
    expected: str


def send(method: str, path: str, *, headers: dict[str, str] | None = None, body: object | str | None = None) -> tuple[int | str, str]:
    headers = headers or {}
    data = None

    if body is not None:
        if isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(TARGET + path, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - defensive diagnostic output only
        return "ERROR", f"{type(exc).__name__}: {exc}"


def run_test(label: str, method: str, path: str, expected: str, *, headers: dict[str, str] | None = None, body: object | str | None = None) -> Result:
    status, response_body = send(method, path, headers=headers, body=body)
    return Result(label=label, method=method, path=path, status=status, body=response_body, expected=expected)


def print_result(result: Result) -> None:
    print("\n" + "=" * 78)
    print(f"TEST:     {result.label}")
    print(f"REQUEST:  {result.method} {result.path}")
    print(f"STATUS:   {result.status}")
    print(f"EXPECTED: {result.expected}")
    preview = result.body.replace("\n", " ")[:500]
    print(f"BODY:     {preview}")


def main() -> int:
    print("Prompterator Ring 8 Safe Shield Check")
    print(f"Target: {TARGET}")
    print("Mode: defensive / low-volume / own-system only")

    tests: list[Result] = []

    tests.append(run_test(
        "Public healthcheck must stay minimal",
        "GET",
        "/health",
        '200 with {"status":"ok"} and no internal ring details',
    ))

    tests.append(run_test(
        "Admin usage endpoint without token must stay hidden",
        "GET",
        "/api/usage",
        "404",
    ))

    tests.append(run_test(
        "Generate without Origin must be rejected before model call",
        "POST",
        "/api/generate",
        "403 if origin requirement is active",
        headers={"Content-Type": "application/json"},
        body={"raw_input": "Test"},
    ))

    tests.append(run_test(
        "Wrong content type must be rejected",
        "POST",
        "/api/generate",
        "415",
        headers={"Origin": ORIGIN, "Content-Type": "text/plain"},
        body="raw_input=Test",
    ))

    tests.append(run_test(
        "Unexpected JSON fields must be rejected",
        "POST",
        "/api/generate",
        "400",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        body={"raw_input": "", "extra": True},
    ))

    tests.append(run_test(
        "Large input must be rejected before model call",
        "POST",
        "/api/generate",
        "413",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        body={"raw_input": "A" * 10000},
    ))

    print("\nControlled low-volume rate-limit probe")
    print("Uses empty input to avoid successful model calls and cost.")
    rate_statuses: list[int | str] = []
    for _ in range(5):
        status, _ = send(
            "POST",
            "/api/generate",
            headers={"Origin": ORIGIN, "Content-Type": "application/json"},
            body={"raw_input": ""},
        )
        rate_statuses.append(status)
        time.sleep(0.25)

    for result in tests:
        print_result(result)

    print("\n" + "=" * 78)
    print("TEST:     Controlled rate-limit probe")
    print(f"STATUSES: {rate_statuses}")
    print("EXPECTED: strict deployments may return 429 after repeated invalid requests")

    print("\nDone. Interpret manually. This script is intentionally low-volume and defensive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
