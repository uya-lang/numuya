import argparse
import contextlib
import io
import json
import os
import platform
import time
from dataclasses import dataclass
from typing import Any

import numpy as np


THREAD_ENV_KEYS = [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]


@dataclass
class BenchSpec:
    operation: str
    shape: tuple[int, ...]
    iterations: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    return parser.parse_args()


def detect_blas_backend() -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        np.__config__.show()
    text = buffer.getvalue().strip()
    return text or "unknown"


def collect_metadata() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "blas": detect_blas_backend(),
        "thread_env": {key: os.environ.get(key, "") for key in THREAD_ENV_KEYS},
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
    }


def benchmark_case(operation: str, setup: callable, runner: callable, iterations: int) -> dict[str, Any]:
    inputs = setup()
    started = time.perf_counter_ns()
    for _ in range(iterations):
        runner(*inputs)
    elapsed_ns = time.perf_counter_ns() - started
    return {
        "operation": operation,
        "iterations": iterations,
        "total_ns": elapsed_ns,
        "ns_per_iter": elapsed_ns / iterations if iterations else 0.0,
    }


def format_table(title: str, rows: list[dict[str, Any]]) -> str:
    headers = ["operation", "shape", "iterations", "ns_per_iter"]
    lines = [title, " | ".join(headers)]
    lines.append(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        lines.append(
            " | ".join(
                [
                    str(row.get("operation", "")),
                    str(row.get("shape", "")),
                    str(row.get("iterations", "")),
                    f"{row.get('ns_per_iter', 0.0):.1f}",
                ]
            )
        )
    return "\n".join(lines)


def emit(payload: dict[str, Any], table: str, json_only: bool) -> None:
    if json_only:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))
    print()
    print(table)
