from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from _bench_common import collect_metadata, emit, format_table, parse_args


ROOT = Path(__file__).resolve().parents[2]
UYA = ROOT.parent / "uya" / "bin" / "uya"
MANIFEST = ROOT / "uya.toml"
SPOTCHECK_TOOL = ROOT / "src/numuya/_tools/bench_spotcheck.uya"


def run_numuya_spotcheck() -> tuple[dict[str, dict[str, np.ndarray | float]], bool]:
    completed = subprocess.run(
        [str(UYA), "run", str(SPOTCHECK_TOOL), "--manifest-path", str(MANIFEST)],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    suites: dict[str, dict[str, np.ndarray | float]] = {"cpu": {}, "gpu": {}}
    gpu_available = False
    for raw_line in completed.stdout.splitlines():
        if not raw_line.startswith("SPOTCHECK|"):
            continue
        parts = dict(item.split("=", 1) for item in raw_line.split("|")[1:])
        suite = parts["suite"]
        if suite == "gpu" and "available" in parts:
            gpu_available = parts["available"] == "true"
            continue
        values = parts["values"]
        if ";" in values:
            parsed = np.array([[float(cell) for cell in row.split(",")] for row in values.split(";")], dtype=np.float64)
        elif "," in values:
            parsed = np.array([float(cell) for cell in values.split(",")], dtype=np.float64)
        else:
            parsed = float(values)
        suites[suite][parts["operation"]] = parsed
    return suites, gpu_available


def pcg64_values(init_state: int, init_seq: int, count: int) -> np.ndarray:
    state = (init_state + ((init_seq << 1) | 1)) & ((1 << 64) - 1)
    inc = ((init_seq << 1) | 1) & ((1 << 64) - 1)
    out = []
    for _ in range(count):
        state = (state * 6364136223846793005 + inc) & ((1 << 64) - 1)
        value = state ^ (state >> 17)
        out.append(value / 18446744073709551616.0)
    return np.array(out, dtype=np.float64)


def expected_cpu() -> dict[str, np.ndarray | float]:
    left = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64)
    right = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]], dtype=np.float64)
    mat_left = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)
    mat_right = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float64)
    return {
        "add": np.add(left, right),
        "mul": np.multiply(left, right),
        "sum": float(np.sum(left)),
        "matmul": np.matmul(mat_left, mat_right),
        "random": pcg64_values(42, 54, 5),
    }


def compare_case(operation: str, actual: np.ndarray | float, expected: np.ndarray | float) -> dict[str, Any]:
    if isinstance(actual, np.ndarray):
        match = bool(np.allclose(actual, expected, rtol=1e-12, atol=1e-12))
        actual_repr = actual.tolist()
        expected_repr = expected.tolist()
    else:
        match = abs(actual - float(expected)) <= 1e-12
        actual_repr = actual
        expected_repr = float(expected)
    return {
        "operation": operation,
        "match": match,
        "actual": actual_repr,
        "expected": expected_repr,
    }


def gpu_reference_rows(numuya_gpu: dict[str, np.ndarray | float], gpu_available: bool) -> list[dict[str, Any]]:
    left = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64)
    right = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]], dtype=np.float64)
    numpy_expected = {
        "add": np.add(left, right),
        "sum": float(np.sum(left)),
    }
    rows = []
    for operation in ("add", "sum"):
        row = compare_case(operation, numuya_gpu[operation], numpy_expected[operation]) if gpu_available else {
            "operation": operation,
            "match": False,
            "actual": None,
            "expected": numpy_expected[operation].tolist() if isinstance(numpy_expected[operation], np.ndarray) else numpy_expected[operation],
        }
        row["available"] = gpu_available
        row["cupy_match"] = None
        if gpu_available:
            try:
                import cupy as cp
            except ImportError:
                pass
            else:
                cupy_actual = cp.add(cp.asarray(left), cp.asarray(right)) if operation == "add" else cp.sum(cp.asarray(left))
                if operation == "add":
                    row["cupy_match"] = bool(np.allclose(cp.asnumpy(cupy_actual), numpy_expected[operation], rtol=1e-12, atol=1e-12))
                else:
                    row["cupy_match"] = abs(float(cp.asnumpy(cupy_actual)) - float(numpy_expected[operation])) <= 1e-12
        rows.append(row)
    return rows


def main() -> None:
    args = parse_args()
    suites, gpu_available = run_numuya_spotcheck()
    cpu_rows = [compare_case(operation, suites["cpu"][operation], expected_cpu()[operation]) for operation in ("add", "mul", "sum", "matmul", "random")]
    gpu_rows = gpu_reference_rows(suites["gpu"], gpu_available)
    payload = {
        "benchmark": "spotcheck",
        "metadata": collect_metadata(),
        "cpu_workloads": cpu_rows,
        "gpu_workloads": gpu_rows,
    }
    emit(payload, format_table("Benchmark spot-check", cpu_rows + gpu_rows), args.json)


if __name__ == "__main__":
    main()
