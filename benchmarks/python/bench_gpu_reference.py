from __future__ import annotations

import platform
from typing import Any

import numpy as np

from _bench_common import BenchSpec, benchmark_case, benchmark_numpy_spec, collect_metadata, emit, format_table, parse_args, selected_specs


def run_numpy_baseline(specs: list[BenchSpec]) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    return [benchmark_numpy_spec(spec, rng) for spec in specs]


def cupy_case(cp: Any, spec: BenchSpec) -> dict[str, Any]:
    dtype = cp.dtype(spec.dtype)
    rng = cp.random.default_rng(42)
    stream = cp.cuda.Stream.null
    if spec.operation in ("add", "mul"):
        left = cp.full(spec.shape, 1.5, dtype=dtype)
        right = cp.full(spec.shape, 2.5, dtype=dtype)
        runner = cp.add if spec.operation == "add" else cp.multiply
        return benchmark_case(spec, lambda: (left, right), runner, stream.synchronize)
    if spec.operation == "sum":
        values = cp.linspace(0.0, 1.0, spec.shape[0], dtype=dtype)
        return benchmark_case(spec, lambda: (values,), cp.sum, stream.synchronize)
    if spec.operation == "matmul":
        left = rng.random(spec.shape, dtype=dtype)
        right = rng.random(spec.shape, dtype=dtype)
        return benchmark_case(spec, lambda: (left, right), cp.matmul, stream.synchronize)
    if spec.operation == "random":
        return benchmark_case(spec, lambda: tuple(), lambda: rng.random(spec.shape, dtype=dtype), stream.synchronize)
    raise ValueError(f"unsupported CuPy benchmark operation: {spec.operation}")


def run_cupy_reference(specs: list[BenchSpec]) -> dict[str, Any]:
    try:
        import cupy as cp
    except ImportError:
        return {
            "available": False,
            "reason": "cupy not installed",
            "install_hint": "python -m pip install cupy-cuda13x",
            "results": [],
        }

    device = cp.cuda.runtime.getDeviceProperties(0)
    return {
        "available": True,
        "cupy_version": cp.__version__,
        "device_name": device["name"].decode() if isinstance(device["name"], bytes) else device["name"],
        "results": [cupy_case(cp, spec) for spec in specs],
    }


def main() -> None:
    args = parse_args()
    specs = selected_specs(args.quick)
    metadata = collect_metadata()
    gpu_reference = run_cupy_reference(specs)
    metadata["cupy_version"] = gpu_reference.get("cupy_version", "")
    metadata["host_python"] = platform.python_implementation()
    numpy_rows = run_numpy_baseline(specs)
    payload = {
        "benchmark": "gpu_reference",
        "metadata": metadata,
        "numpy_cpu_baseline": numpy_rows,
        "gpu_reference": gpu_reference,
    }
    emit(payload, format_table("NumPy CPU baseline for GPU comparison", numpy_rows), args.json)


if __name__ == "__main__":
    main()
