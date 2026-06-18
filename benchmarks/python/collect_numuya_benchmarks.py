from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


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
    return {
        "operation": payload["operation"],
        "mode": payload["mode"],
        "metric": payload["metric"],
        "dtype": payload["dtype"],
        "shape": parse_shape(payload["shape"]),
        "iterations": int(payload["iterations"]),
        "total_ns": int(payload["total_ns"]),
        "ns_per_iter": int(payload["total_ns"]) / int(payload["iterations"]),
    }


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
