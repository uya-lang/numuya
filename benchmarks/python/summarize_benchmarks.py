from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SECTION_ORDER = [
    ("CPU", "cpu"),
    ("CUDA end-to-end", "end-to-end"),
    ("CUDA kernel-only", "kernel-only"),
    ("CuPy reference", "cupy"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def key_for_row(row: dict[str, Any]) -> tuple[str, str, tuple[int, ...]]:
    shape = tuple(int(v) for v in row.get("shape", []))
    return str(row.get("operation", "")), str(row.get("dtype", "")), shape


def index_rows(rows: list[dict[str, Any]]) -> dict[tuple[str, str, tuple[int, ...]], dict[str, Any]]:
    return {key_for_row(row): row for row in rows}


def round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 2)


def baseline_status(row: dict[str, Any] | None) -> str:
    if row is None:
        return "missing"
    if row.get("status") == "failed":
        return "failed"
    return "ok"


def row_status(row: dict[str, Any] | None) -> str:
    if row is None:
        return "missing"
    return str(row.get("status", "ok"))


def extract_latency_ns(row: dict[str, Any] | None) -> float | None:
    if row is None or row.get("status") == "failed":
        return None
    value = row.get("ns_per_iter")
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    total_ns = row.get("total_ns")
    iterations = row.get("iterations")
    if isinstance(total_ns, (int, float)) and isinstance(iterations, int) and iterations > 0 and total_ns > 0:
        return float(total_ns) / float(iterations)
    return None


def speedup_vs_numpy(row: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    current_ns = extract_latency_ns(row)
    baseline_ns = extract_latency_ns(baseline)
    if current_ns is None or baseline_ns is None or current_ns == 0:
        return None
    return baseline_ns / current_ns


def make_row(
    category: str,
    row: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    target = row or {}
    return {
        "category": category,
        "operation": target.get("operation") or baseline.get("operation") if baseline else "",
        "dtype": target.get("dtype") or baseline.get("dtype") if baseline else "",
        "shape": target.get("shape") or baseline.get("shape") if baseline else [],
        "status": row_status(row),
        "baseline_status": baseline_status(baseline),
        "total_ns": target.get("total_ns") if row else None,
        "ns_per_iter": target.get("ns_per_iter") if row else None,
        "metric": target.get("metric", "latency"),
        "unit": target.get("unit", "ns/iter"),
        "throughput": target.get("throughput"),
        "speedup_vs_numpy_cpu": round_or_none(speedup_vs_numpy(row, baseline)),
    }


def union_keys(*indexes: dict[tuple[str, str, tuple[int, ...]], dict[str, Any]]) -> list[tuple[str, str, tuple[int, ...]]]:
    keys: set[tuple[str, str, tuple[int, ...]]] = set()
    for idx in indexes:
        keys.update(idx.keys())
    return sorted(keys)


def render_markdown(metadata: dict[str, Any], sections: list[dict[str, Any]]) -> str:
    lines = [
        "# Benchmark Summary",
        "",
        f"- run_date: {metadata.get('run_date', 'unknown')}",
        f"- numuya_commit: {metadata.get('numuya_commit', 'unknown')}",
        f"- commands: {', '.join(metadata.get('commands', [])) or 'unknown'}",
        "",
    ]
    for section in sections:
        lines.append(f"## {section['category']}")
        if section["category"] == "CUDA end-to-end":
            lines.append("非同类设备对比，仅作端到端参考。")
        lines.append("")
        lines.append("| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in section["rows"]:
            shape = "x".join(str(v) for v in row["shape"]) if row["shape"] else "-"
            lines.append(
                "| {operation} | {dtype} | {shape} | {status} | {baseline_status} | {total_ns} | {ns_per_iter} | {throughput} | {speedup} |".format(
                    operation=row["operation"] or "-",
                    dtype=row["dtype"] or "-",
                    shape=shape,
                    status=row["status"],
                    baseline_status=row["baseline_status"],
                    total_ns=row["total_ns"] if row["total_ns"] is not None else row["status"],
                    ns_per_iter=row["ns_per_iter"] if row["ns_per_iter"] is not None else row["status"],
                    throughput=row["throughput"] if row["throughput"] is not None else "missing",
                    speedup=row["speedup_vs_numpy_cpu"] if row["speedup_vs_numpy_cpu"] is not None else row["status"],
                )
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    numpy_cpu = load_json(input_dir / "numpy_cpu.json")
    gpu_reference = load_json(input_dir / "gpu_reference.json")
    numuya_cpu = load_json(input_dir / "numuya_cpu.json")
    numuya_cuda = load_json(input_dir / "numuya_cuda.json")

    numpy_index = index_rows(numpy_cpu.get("results", []))
    cpu_index = index_rows(numuya_cpu.get("results", []))
    cuda_e2e_index = index_rows([row for row in numuya_cuda.get("results", []) if row.get("mode") == "end-to-end"])
    cuda_kernel_index = index_rows([row for row in numuya_cuda.get("results", []) if row.get("mode") == "kernel-only"])
    cupy_index = index_rows(gpu_reference.get("gpu_reference", {}).get("results", []))

    sections: list[dict[str, Any]] = []
    for category, mode in SECTION_ORDER:
        if mode == "cpu":
            current_index = cpu_index
        elif mode == "end-to-end":
            current_index = cuda_e2e_index
        elif mode == "kernel-only":
            current_index = cuda_kernel_index
        else:
            current_index = cupy_index
        rows = [
            make_row(category, current_index.get(key), numpy_index.get(key))
            for key in union_keys(current_index, numpy_index)
        ]
        sections.append({"category": category, "rows": rows})

    metadata = {
        "run_date": numpy_cpu.get("metadata", {}).get("run_date")
        or gpu_reference.get("metadata", {}).get("run_date")
        or numuya_cpu.get("metadata", {}).get("run_date")
        or numuya_cuda.get("metadata", {}).get("run_date")
        or "unknown",
        "numuya_commit": numuya_cpu.get("metadata", {}).get("numuya_commit")
        or numuya_cuda.get("metadata", {}).get("numuya_commit")
        or numpy_cpu.get("metadata", {}).get("numuya_commit")
        or "unknown",
        "commands": [
            value
            for value in [
                numpy_cpu.get("metadata", {}).get("command"),
                gpu_reference.get("metadata", {}).get("command"),
                numuya_cpu.get("metadata", {}).get("command"),
                numuya_cuda.get("metadata", {}).get("command"),
            ]
            if value
        ],
    }
    summary = {"metadata": metadata, "sections": sections}

    (output_dir / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "benchmark_summary.md").write_text(render_markdown(metadata, sections), encoding="utf-8")


if __name__ == "__main__":
    main()
