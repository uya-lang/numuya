from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import platform
import math
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

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
    dtype: str
    warmup: int
    repeat: int


ELEMENT_LENGTHS = (10_000, 1_000_000, 10_000_000)
MATMUL_SIZES = (256, 1024, 2048)
RANDOM_LENGTHS = (1_000_000, 10_000_000)

FIXED_SPECS = [
    *[
        BenchSpec(operation, (length,), dtype, 5, 20)
        for operation in ("add", "mul", "sum")
        for dtype in ("float32", "float64")
        for length in ELEMENT_LENGTHS
    ],
    *[BenchSpec("matmul", (size, size), "float32", 3, 10) for size in MATMUL_SIZES],
    *[BenchSpec("random", (length,), "float32", 5, 20) for length in RANDOM_LENGTHS],
]

QUICK_SPECS = [
    *[
        BenchSpec(operation, (length,), dtype, 0, 1)
        for operation in ("add", "mul", "sum")
        for dtype in ("float32", "float64")
        for length in (8, 16, 32)
    ],
    *[BenchSpec("matmul", (size, size), "float32", 0, 1) for size in (4, 8, 16)],
    *[BenchSpec("random", (length,), "float32", 0, 1) for length in (16, 32)],
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    parser.add_argument("--quick", action="store_true", help="use tiny shapes for script tests")
    return parser.parse_args()


def selected_specs(quick: bool) -> list[BenchSpec]:
    return QUICK_SPECS if quick else FIXED_SPECS


def detect_blas_backend() -> str:
    buffer = io.StringIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with contextlib.redirect_stdout(buffer):
            np.__config__.show()
    text = buffer.getvalue().strip()
    return text or "unknown"


def collect_metadata() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    return {
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "blas": detect_blas_backend(),
        "thread_env": {key: os.environ.get(key, "") for key in THREAD_ENV_KEYS},
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
        "command": " ".join(os.sys.argv),
        "run_date": os.environ.get("BENCH_RUN_DATE", ""),
        "numuya_commit": os.environ.get("BENCH_NUMUYA_COMMIT", ""),
        "repo_root": str(root),
    }


def percentile(samples: list[int], q: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    index = max(0, math.ceil((q / 100.0) * len(ordered)) - 1)
    return float(ordered[index])


def median(samples: list[int]) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return float(ordered[mid])
    return (float(ordered[mid - 1]) + float(ordered[mid])) / 2.0


def dtype_size(dtype: str) -> int:
    if dtype in ("float32", "f32"):
        return 4
    if dtype in ("float64", "f64"):
        return 8
    return 0


def element_count(shape: tuple[int, ...] | list[int]) -> int:
    total = 1
    for dim in shape:
        total *= int(dim)
    return total


def throughput_for(spec: BenchSpec, ns_per_iter: float) -> tuple[str, str, float | None]:
    if ns_per_iter <= 0:
        return "latency", "ns/iter", None
    seconds = ns_per_iter / 1_000_000_000.0
    if spec.operation in ("add", "mul"):
        bytes_per_iter = element_count(spec.shape) * dtype_size(spec.dtype) * 3
        return "bandwidth", "GiB/s", (bytes_per_iter / (1024.0 ** 3)) / seconds
    if spec.operation == "sum":
        bytes_per_iter = element_count(spec.shape) * dtype_size(spec.dtype)
        return "bandwidth", "GiB/s", (bytes_per_iter / (1024.0 ** 3)) / seconds
    if spec.operation == "random":
        bytes_per_iter = element_count(spec.shape) * dtype_size(spec.dtype)
        return "bandwidth", "GiB/s", (bytes_per_iter / (1024.0 ** 3)) / seconds
    if spec.operation == "matmul" and len(spec.shape) == 2:
        n = int(spec.shape[0])
        flops = 2.0 * n * n * n
        return "tflops", "TFLOP/s", (flops / 1e12) / seconds
    return "latency", "ns/iter", None


def benchmark_case(
    spec: BenchSpec,
    setup: Callable[..., tuple[Any, ...]],
    runner: Callable[..., Any],
    sync: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    inputs = setup()
    for _ in range(spec.warmup):
        runner(*inputs)
        if sync is not None:
            sync()
    samples: list[int] = []
    for _ in range(spec.repeat):
        started = time.perf_counter_ns()
        runner(*inputs)
        if sync is not None:
            sync()
        samples.append(time.perf_counter_ns() - started)
    ns_per_iter = median(samples)
    metric, unit, throughput = throughput_for(spec, ns_per_iter)
    return {
        "operation": spec.operation,
        "dtype": spec.dtype,
        "shape": list(spec.shape),
        "warmup": spec.warmup,
        "repeat": spec.repeat,
        "iterations": spec.repeat,
        "samples_ns": samples,
        "total_ns": sum(samples),
        "ns_per_iter": ns_per_iter,
        "median": ns_per_iter,
        "best": min(samples) if samples else 0,
        "p95": percentile(samples, 95.0),
        "metric": metric,
        "unit": unit,
        "throughput": throughput,
    }


def numpy_inputs_for(spec: BenchSpec, rng: np.random.Generator) -> tuple[Any, ...]:
    dtype = np.dtype(spec.dtype)
    if spec.operation in ("add", "mul"):
        return (
            np.full(spec.shape, 1.5, dtype=dtype),
            np.full(spec.shape, 2.5, dtype=dtype),
        )
    if spec.operation == "sum":
        return (np.linspace(0.0, 1.0, spec.shape[0], dtype=dtype),)
    if spec.operation == "matmul":
        return (
            rng.random(spec.shape, dtype=dtype),
            rng.random(spec.shape, dtype=dtype),
        )
    return tuple()


def benchmark_numpy_spec(spec: BenchSpec, rng: np.random.Generator) -> dict[str, Any]:
    if spec.operation == "add":
        return benchmark_case(spec, lambda: numpy_inputs_for(spec, rng), lambda left, right: np.add(left, right))
    if spec.operation == "mul":
        return benchmark_case(spec, lambda: numpy_inputs_for(spec, rng), lambda left, right: np.multiply(left, right))
    if spec.operation == "sum":
        return benchmark_case(spec, lambda: numpy_inputs_for(spec, rng), lambda values: np.sum(values))
    if spec.operation == "matmul":
        return benchmark_case(spec, lambda: numpy_inputs_for(spec, rng), lambda left, right: np.matmul(left, right))
    if spec.operation == "random":
        dtype = np.dtype(spec.dtype)
        return benchmark_case(spec, lambda: tuple(), lambda: rng.random(spec.shape, dtype=dtype))
    raise ValueError(f"unsupported benchmark operation: {spec.operation}")


def format_table(title: str, rows: list[dict[str, Any]]) -> str:
    headers = ["operation", "dtype", "shape", "repeat", "median_ns", "best_ns", "p95_ns", "throughput"]
    lines = [title, " | ".join(headers)]
    lines.append(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        throughput = row.get("throughput")
        lines.append(
            " | ".join(
                [
                    str(row.get("operation", "")),
                    str(row.get("dtype", "")),
                    str(row.get("shape", "")),
                    str(row.get("repeat", row.get("iterations", ""))),
                    f"{row.get('ns_per_iter', 0.0):.1f}",
                    f"{row.get('best', 0.0):.1f}",
                    f"{row.get('p95', 0.0):.1f}",
                    "missing" if throughput is None else f"{float(throughput):.3f} {row.get('unit', '')}",
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
