from __future__ import annotations

import numpy as np

from _bench_common import BenchSpec, benchmark_numpy_spec, collect_metadata, emit, format_table, parse_args, selected_specs


def run_cases(specs: list[BenchSpec]) -> list[dict[str, object]]:
    rng = np.random.default_rng(42)
    return [benchmark_numpy_spec(spec, rng) for spec in specs]


def main() -> None:
    args = parse_args()
    results = run_cases(selected_specs(args.quick))
    payload = {
        "benchmark": "numpy_cpu",
        "metadata": collect_metadata(),
        "results": results,
    }
    emit(payload, format_table("NumPy CPU benchmark", results), args.json)


if __name__ == "__main__":
    main()
