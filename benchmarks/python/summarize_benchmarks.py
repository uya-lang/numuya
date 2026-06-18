from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _bench_common import FIXED_SPECS


SECTION_ORDER = [
    ("CPU", "cpu"),
    ("CUDA end-to-end", "end-to-end"),
    ("CUDA kernel-only", "kernel-only"),
    ("CuPy reference", "cupy"),
]

FIXED_KEYS = [(spec.operation, spec.dtype, tuple(spec.shape)) for spec in FIXED_SPECS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--doc-path")
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


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


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
    for key in ("median", "ns_per_iter"):
        value = row.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
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
    key: tuple[str, str, tuple[int, ...]],
) -> dict[str, Any]:
    target = row or {}
    operation, dtype, shape = key
    return {
        "category": category,
        "operation": target.get("operation") or (baseline.get("operation") if baseline else operation),
        "dtype": target.get("dtype") or (baseline.get("dtype") if baseline else dtype),
        "shape": target.get("shape") or (baseline.get("shape") if baseline else list(shape)),
        "status": row_status(row),
        "baseline_status": baseline_status(baseline),
        "total_ns": target.get("total_ns") if row else None,
        "ns_per_iter": target.get("ns_per_iter") if row else None,
        "warmup": target.get("warmup") if row else None,
        "repeat": target.get("repeat") or target.get("iterations") if row else None,
        "median": target.get("median") or target.get("ns_per_iter") if row else None,
        "best": target.get("best") if row else None,
        "p95": target.get("p95") if row else None,
        "samples_ns": target.get("samples_ns") if row else None,
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


def fixed_then_extra_keys(current_index: dict[tuple[str, str, tuple[int, ...]], dict[str, Any]]) -> list[tuple[str, str, tuple[int, ...]]]:
    fixed = list(FIXED_KEYS)
    fixed_set = set(fixed)
    extras = sorted(key for key in current_index if key not in fixed_set)
    return fixed + extras


def render_markdown(metadata: dict[str, Any], sections: list[dict[str, Any]]) -> str:
    sources = metadata.get("sources", {})
    lines = [
        "# Benchmark Summary",
        "",
        f"- run_date: {metadata.get('run_date', 'unknown')}",
        f"- numuya_commit: {metadata.get('numuya_commit', 'unknown')}",
        f"- commands: {', '.join(metadata.get('commands', [])) or 'unknown'}",
        "",
    ]
    if sources:
        lines.append("## Sources")
        lines.append("")
        for key, value in sources.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    for section in sections:
        lines.append(f"## {section['category']}")
        if section["category"] == "CUDA end-to-end":
            lines.append("非同类设备对比，仅作端到端参考。")
        lines.append("")
        lines.append("| operation | dtype | shape | status | baseline | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in section["rows"]:
            shape = "x".join(str(v) for v in row["shape"]) if row["shape"] else "-"
            lines.append(
                "| {operation} | {dtype} | {shape} | {status} | {baseline_status} | {median} | {best} | {p95} | {throughput} | {speedup} |".format(
                    operation=row["operation"] or "-",
                    dtype=row["dtype"] or "-",
                    shape=shape,
                    status=row["status"],
                    baseline_status=row["baseline_status"],
                    median=row["median"] if row["median"] is not None else row["status"],
                    best=row["best"] if row["best"] is not None else row["status"],
                    p95=row["p95"] if row["p95"] is not None else row["status"],
                    throughput=format_throughput(row),
                    speedup=row["speedup_vs_numpy_cpu"] if row["speedup_vs_numpy_cpu"] is not None else row["status"],
                )
            )
        lines.append("")
    return "\n".join(lines)


def render_report_section(input_dir: Path, metadata: dict[str, Any], sections: list[dict[str, Any]], gpu_reference: dict[str, Any]) -> str:
    sources = metadata.get("sources", {})
    commands = metadata.get("commands", [])
    lines = [
        "## 第一版 CPU / GPU 对比报告",
        "",
        f"- 原始结果目录：`{input_dir}`",
        f"- benchmark 运行日期：`{metadata.get('run_date', 'unknown')}`",
        f"- NumUya commit：`{metadata.get('numuya_commit', 'unknown')}`",
        "- 计时口径：CPU 与 `NumPy CPU baseline` 结论来自 wall-clock median；`NumUya CUDA end-to-end` 逐 workload 计入传输与计算；`NumUya CUDA kernel-only` 只代表设备端 kernel 时间。",
        "- 说明：NumPy 无 GPU backend，因此 GPU 主表只比较 `NumUya CUDA end-to-end` 与 `NumPy CPU baseline`；`NumUya CUDA kernel-only` 单列报告，不伪造 `NumPy GPU` 数据。",
        "",
    ]
    if commands:
        lines.append(f"- 具体命令行：`{commands[0]}`")
        lines.append("")
    if sources:
        lines.append("### 原始 JSON / 文本来源")
        lines.append("")
        for key, value in sources.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    for section in sections:
        lines.append(f"### {section['category']}")
        if section["category"] == "CUDA end-to-end":
            lines.append("")
            lines.append("非同类设备对比，仅作端到端参考。")
        lines.append("")
        lines.append("| operation | dtype | shape | status | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in section["rows"]:
            shape = "x".join(str(v) for v in row["shape"]) if row["shape"] else "-"
            lines.append(
                f"| {row['operation'] or '-'} | {row['dtype'] or '-'} | {shape} | {row['status']} | "
                f"{row['median'] if row['median'] is not None else 'missing'} | "
                f"{row['best'] if row['best'] is not None else 'missing'} | "
                f"{row['p95'] if row['p95'] is not None else 'missing'} | "
                f"{format_throughput(row)} | "
                f"{row['speedup_vs_numpy_cpu'] if row['speedup_vs_numpy_cpu'] is not None else 'missing'} |"
            )
        lines.append("")
    if not gpu_reference.get("available", False):
        hint = gpu_reference.get("install_hint")
        suffix = f"；安装提示：`{hint}`" if hint else ""
        lines.append(f"- CuPy reference：不可用（{gpu_reference.get('reason', 'unknown')}{suffix}）。")
    else:
        lines.append(f"- CuPy reference：可用（{gpu_reference.get('device_name', 'unknown device')}）。")
    lines.append("")
    lines.extend(render_lagging_notes(sections))
    lines.append("")
    return "\n".join(lines)


def lagging_rows(section: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in section.get("rows", [])
        if isinstance(row.get("speedup_vs_numpy_cpu"), (int, float))
        and row.get("speedup_vs_numpy_cpu") < 1.0
    ]


def find_section(sections: list[dict[str, Any]], category: str) -> dict[str, Any]:
    for section in sections:
        if section.get("category") == category:
            return section
    return {"category": category, "rows": []}


def render_lagging_notes(sections: list[dict[str, Any]]) -> list[str]:
    cpu_lag = lagging_rows(find_section(sections, "CPU"))
    e2e_lag = lagging_rows(find_section(sections, "CUDA end-to-end"))
    kernel_lag = lagging_rows(find_section(sections, "CUDA kernel-only"))
    cupy_lag = lagging_rows(find_section(sections, "CuPy reference"))

    return [
        "### 未追平项说明",
        "",
        f"- 固定矩阵完整性：四个对比类别均按固定矩阵渲染，缺项会显示为 `missing`；本次 CPU 未追平 {len(cpu_lag)} 行，CUDA end-to-end 未追平 {len(e2e_lag)} 行，CUDA kernel-only 未追平 {len(kernel_lag)} 行，CuPy reference 未追平 {len(cupy_lag)} 行。",
        "- CPU：`matmul float32` 仍是最大差距，当前实现是不依赖 BLAS/LAPACK 的纯 Uya contiguous fast path，不能与 NumPy/OpenBLAS 的成熟 GEMM 微内核直接追平；大数组 `add/mul` 仍是内存带宽与分配路径限制，`random float32 1e7` 已改为直接 f32 生成但仍低于 NumPy。",
        "- CUDA end-to-end：小数据 `1e4` 和部分 `1e6` 行主要受 H2D、kernel launch、D2H 固定开销限制；同机 CuPy reference 的 `1e4` 行也低于 NumPy CPU，说明这类行不能用 kernel-only 吞吐冒充端到端追平。",
        "- CUDA kernel-only：大多数固定矩阵行已超过 NumPy CPU；仍落后的 `sum float32/float64 1e4` 是小规模 reduction launch/同步开销，不代表大规模设备端吞吐。",
    ]


def format_throughput(row: dict[str, Any]) -> str:
    value = row.get("throughput")
    if value is None:
        return "missing"
    unit = row.get("unit", "")
    if isinstance(value, (int, float)):
        return f"{float(value):.3f} {unit}".strip()
    return str(value)


def write_report_doc(doc_path: Path, input_dir: Path, metadata: dict[str, Any], sections: list[dict[str, Any]], gpu_reference: dict[str, Any]) -> None:
    original = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    marker = "## 第一版 CPU / GPU 对比报告"
    if marker in original:
        original = original.split(marker, 1)[0].rstrip() + "\n\n"
    elif original and not original.endswith("\n"):
        original += "\n"
    report = render_report_section(input_dir, metadata, sections, gpu_reference)
    doc_path.write_text(f"{original}{report}", encoding="utf-8")


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
        rows = [make_row(category, current_index.get(key), numpy_index.get(key), key) for key in fixed_then_extra_keys(current_index)]
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
        "commands": dedupe_preserve_order(
            [
                value
                for value in [
                    numpy_cpu.get("metadata", {}).get("command"),
                    gpu_reference.get("metadata", {}).get("command"),
                    numuya_cpu.get("metadata", {}).get("command"),
                    numuya_cuda.get("metadata", {}).get("command"),
                ]
                if value
            ]
        ),
        "sources": {
            "numpy_cpu_json": str((input_dir / "numpy_cpu.json").resolve()),
            "gpu_reference_json": str((input_dir / "gpu_reference.json").resolve()),
            "numuya_cpu_json": str((input_dir / "numuya_cpu.json").resolve()),
            "numuya_cuda_json": str((input_dir / "numuya_cuda.json").resolve()),
            "numuya_raw_text": numuya_cpu.get("metadata", {}).get("raw_output_path")
            or numuya_cuda.get("metadata", {}).get("raw_output_path")
            or "unknown",
        },
    }
    summary = {"metadata": metadata, "sections": sections}

    (output_dir / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "benchmark_summary.md").write_text(render_markdown(metadata, sections), encoding="utf-8")
    if args.doc_path:
        write_report_doc(Path(args.doc_path), input_dir, metadata, sections, gpu_reference.get("gpu_reference", {}))


if __name__ == "__main__":
    main()
