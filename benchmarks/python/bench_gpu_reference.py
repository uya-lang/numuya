from __future__ import annotations

import platform
from typing import Any

import numpy as np

from _bench_common import benchmark_case, collect_metadata, emit, format_table, parse_args


def run_numpy_baseline() -> list[dict[str, Any]]:
    left = np.full((1_000_000,), 1.5, dtype=np.float64)
    right = np.full((1_000_000,), 2.5, dtype=np.float64)
    values = np.linspace(0.0, 1.0, 1_000_000, dtype=np.float64)
    rows = [
        benchmark_case("add", lambda: (left, right), lambda a, b: np.add(a, b), 200),
        benchmark_case("sum", lambda: (values,), lambda a: np.sum(a), 400),
    ]
    for row in rows:
        row["shape"] = [1_000_000]
        row["dtype"] = "float64"
    return rows


def run_cupy_reference() -> dict[str, Any]:
    try:
        import cupy as cp
    except ImportError:
        return {"available": False, "reason": "cupy not installed"}

    left = cp.full((1_000_000,), 1.5, dtype=cp.float64)
    right = cp.full((1_000_000,), 2.5, dtype=cp.float64)
    stream = cp.cuda.Stream.null

    def sync_add(a: Any, b: Any) -> Any:
        result = cp.add(a, b)
        stream.synchronize()
        return result

    result = benchmark_case("add", lambda: (left, right), sync_add, 200)
    result["shape"] = [1_000_000]
    result["dtype"] = "float64"
    device = cp.cuda.runtime.getDeviceProperties(0)
    return {
        "available": True,
        "cupy_version": cp.__version__,
        "device_name": device["name"].decode() if isinstance(device["name"], bytes) else device["name"],
        "results": [result],
    }


def main() -> None:
    args = parse_args()
    metadata = collect_metadata()
    gpu_reference = run_cupy_reference()
    metadata["cupy_version"] = gpu_reference.get("cupy_version", "")
    metadata["host_python"] = platform.python_implementation()
    numpy_rows = run_numpy_baseline()
    payload = {
        "benchmark": "gpu_reference",
        "metadata": metadata,
        "numpy_cpu_baseline": numpy_rows,
        "gpu_reference": gpu_reference,
    }
    emit(payload, format_table("NumPy CPU baseline for GPU comparison", numpy_rows), args.json)


if __name__ == "__main__":
    main()
