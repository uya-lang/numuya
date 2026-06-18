from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from _bench_common import BenchSpec, median, percentile, throughput_for


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to raw `make bench` stdout")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--command", required=True)
    return parser.parse_args()


def git_commit(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=root,
    )
    return completed.stdout.strip()


def parse_shape(value: str) -> list[int]:
    return [int(part) for part in value.split("x") if part]


def parse_bench_json_line(line: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for chunk in line.strip().split("|")[1:]:
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        payload[key] = value
    samples_ns = [int(part) for part in payload.get("samples_ns", "").split(",") if part]
    has_explicit_samples = bool(samples_ns)
    repeat = int(payload.get("repeat", payload.get("iterations", len(samples_ns) or "0")))
    total_ns = int(payload["total_ns"]) if "total_ns" in payload else sum(samples_ns)
    if not samples_ns and repeat > 0:
        samples_ns = [total_ns // repeat]
    ns_per_iter = float(payload.get("ns_per_iter", "0") or 0)
    if has_explicit_samples:
        ns_per_iter = median(samples_ns)
    elif ns_per_iter <= 0 and repeat > 0:
        ns_per_iter = total_ns / repeat
    row: dict[str, Any] = {
        "operation": payload["operation"],
        "mode": payload["mode"],
        "metric": payload["metric"],
        "dtype": payload["dtype"],
        "shape": parse_shape(payload["shape"]),
        "warmup": int(payload.get("warmup", "0")),
        "repeat": repeat,
        "iterations": repeat,
        "samples_ns": samples_ns,
        "total_ns": total_ns,
        "ns_per_iter": ns_per_iter,
    }
    if "throughput" not in payload and ns_per_iter > 0:
        spec = BenchSpec(
            operation=row["operation"],
            dtype=row["dtype"],
            shape=tuple(row["shape"]),
            warmup=row["warmup"],
            repeat=row["repeat"],
        )
        metric, unit, throughput = throughput_for(spec, ns_per_iter)
        row["metric"] = metric if metric != "latency" else row["metric"]
        row["unit"] = unit
        row["throughput"] = throughput
    for key in ("median", "best", "p95", "throughput"):
        if key in payload and payload[key] != "":
            row[key] = float(payload[key])
    if "median" not in row:
        row["median"] = median(samples_ns) if has_explicit_samples else ns_per_iter
    if "best" not in row:
        row["best"] = min(samples_ns) if has_explicit_samples and samples_ns else ns_per_iter
    if "p95" not in row:
        row["p95"] = percentile(samples_ns, 95.0) if has_explicit_samples else ns_per_iter
    if "unit" in payload:
        row["unit"] = payload["unit"]
    return row


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        parse_bench_json_line(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("BENCH_JSON|")
    ]

    cpu_rows = [row for row in rows if row["mode"] == "cpu"]
    cuda_rows = [row for row in rows if row["mode"] != "cpu"]
    commit = git_commit(root)

    common_metadata = {
        "numuya_commit": commit,
        "run_date": args.run_date,
        "command": args.command,
        "raw_output_path": str(input_path.resolve()),
    }
    (output_dir / "numuya_cpu.json").write_text(
        json.dumps({"benchmark": "numuya_cpu", "metadata": common_metadata, "results": cpu_rows}, indent=2),
        encoding="utf-8",
    )
    (output_dir / "numuya_cuda.json").write_text(
        json.dumps({"benchmark": "numuya_cuda", "metadata": common_metadata, "results": cuda_rows}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
