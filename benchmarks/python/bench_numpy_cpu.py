from __future__ import annotations

import numpy as np

from _bench_common import BenchSpec, benchmark_case, collect_metadata, emit, format_table, parse_args


SPECS = [
    BenchSpec("add", (1_000_000,), 200),
    BenchSpec("mul", (1_000_000,), 200),
    BenchSpec("sum", (1_000_000,), 400),
    BenchSpec("matmul", (512, 512), 20),
    BenchSpec("random", (1_000_000,), 100),
]


def run_cases() -> list[dict[str, object]]:
    rng = np.random.default_rng(42)
    rows: list[dict[str, object]] = []

    for spec in SPECS:
        if spec.operation == "add":
            rows.append(
                benchmark_case(
                    "add",
                    lambda: (
                        np.full(spec.shape, 1.5, dtype=np.float64),
                        np.full(spec.shape, 2.5, dtype=np.float64),
                    ),
                    lambda left, right: np.add(left, right),
                    spec.iterations,
                )
            )
        elif spec.operation == "mul":
            rows.append(
                benchmark_case(
                    "mul",
                    lambda: (
                        np.full(spec.shape, 1.5, dtype=np.float64),
                        np.full(spec.shape, 2.5, dtype=np.float64),
                    ),
                    lambda left, right: np.multiply(left, right),
                    spec.iterations,
                )
            )
        elif spec.operation == "sum":
            rows.append(
                benchmark_case(
                    "sum",
                    lambda: (np.linspace(0.0, 1.0, spec.shape[0], dtype=np.float64),),
                    lambda values: np.sum(values),
                    spec.iterations,
                )
            )
        elif spec.operation == "matmul":
            rows.append(
                benchmark_case(
                    "matmul",
                    lambda: (
                        rng.random(spec.shape, dtype=np.float64),
                        rng.random(spec.shape, dtype=np.float64),
                    ),
                    lambda left, right: np.matmul(left, right),
                    spec.iterations,
                )
            )
        elif spec.operation == "random":
            rows.append(
                benchmark_case(
                    "random",
                    lambda: tuple(),
                    lambda: rng.random(spec.shape, dtype=np.float64),
                    spec.iterations,
                )
            )
        rows[-1]["shape"] = list(spec.shape)
        rows[-1]["dtype"] = "float64"
    return rows


def main() -> None:
    args = parse_args()
    results = run_cases()
    payload = {
        "benchmark": "numpy_cpu",
        "metadata": collect_metadata(),
        "results": results,
    }
    emit(payload, format_table("NumPy CPU benchmark", results), args.json)


if __name__ == "__main__":
    main()
