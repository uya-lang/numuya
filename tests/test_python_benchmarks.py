import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PythonBenchmarkScriptsTest(unittest.TestCase):
    def run_script(self, relative_path: str) -> dict:
        script_path = ROOT / relative_path
        completed = subprocess.run(
            [sys.executable, str(script_path), "--json"],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout)

    def assert_common_metadata(self, payload: dict) -> None:
        metadata = payload["metadata"]
        self.assertIn("python_version", metadata)
        self.assertIn("machine", metadata)
        self.assertIn("platform", metadata)
        self.assertIn("blas", metadata)
        self.assertIn("thread_env", metadata)
        self.assertIn("numpy_version", metadata)

    def test_numpy_cpu_benchmark_outputs_expected_operations(self) -> None:
        payload = self.run_script("benchmarks/python/bench_numpy_cpu.py")
        self.assertEqual(payload["benchmark"], "numpy_cpu")
        self.assert_common_metadata(payload)
        self.assertEqual(
            sorted(case["operation"] for case in payload["results"]),
            ["add", "matmul", "mul", "random", "sum"],
        )

    def test_gpu_reference_benchmark_outputs_numpy_baseline(self) -> None:
        payload = self.run_script("benchmarks/python/bench_gpu_reference.py")
        self.assertEqual(payload["benchmark"], "gpu_reference")
        self.assert_common_metadata(payload)
        self.assertIn("numpy_cpu_baseline", payload)
        self.assertIsInstance(payload["gpu_reference"], dict)

    def test_bench_simd_declares_cpu_scope_aligned_with_numpy(self) -> None:
        source = (ROOT / "src/numuya/_benchmarks/bench_simd.uya").read_text(encoding="utf-8")
        self.assertIn("Scope: add/mul/sum only; matmul/random remain Python-only in this round.", source)
        self.assertRegex(source, r'print_result\("add_f64"')
        self.assertRegex(source, r'print_result\("mul_f64"')
        self.assertRegex(source, r'print_result\("sum_all_f64"')

    def test_bench_cuda_emits_machine_readable_modes(self) -> None:
        source = (ROOT / "src/numuya/_benchmarks/bench_cuda.uya").read_text(encoding="utf-8")
        self.assertIn("BENCH_JSON|", source)
        self.assertIn("mode=kernel-only", source)
        self.assertIn("mode=end-to-end", source)
        self.assertIn("fn print_json_result(", source)

    def test_makefile_exposes_numpy_comparison_targets(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertRegex(makefile, r"(?m)^bench-numpy-cpu:")
        self.assertRegex(makefile, r"(?m)^bench-numpy-gpu-ref:")
        self.assertRegex(makefile, r"(?m)^bench-compare:")

    def test_makefile_exposes_benchmark_guardrail_targets(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertRegex(makefile, r"(?m)^bench-spotcheck:")
        self.assertRegex(makefile, r"(?m)^bench-spotcheck-gpu:")
        self.assertRegex(makefile, r"(?m)^bench-guardrails-cpu:")
        self.assertRegex(makefile, r"(?m)^bench-guardrails-gpu:")
        self.assertRegex(makefile, r"(?m)^bench-guardrails-gpu-vendor:")

    def test_makefile_exposes_benchmark_report_target(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertRegex(makefile, r"(?m)^bench-report:")

    def test_spotcheck_script_reports_cpu_and_gpu_consistency(self) -> None:
        payload = self.run_script("benchmarks/python/spotcheck_benchmarks.py")
        self.assertEqual(payload["benchmark"], "spotcheck")
        self.assertIn("cpu_workloads", payload)
        self.assertIn("gpu_workloads", payload)
        self.assertTrue(all(row["match"] for row in payload["cpu_workloads"]))
        self.assertTrue(all("operation" in row for row in payload["gpu_workloads"]))

    def test_numpy_comparison_doc_freezes_v1_matrix(self) -> None:
        doc = (ROOT / "docs/benchmarks/numpy_comparison.md").read_text(encoding="utf-8")
        self.assertIn("第一版固定测试矩阵", doc)
        self.assertIn("elementwise / reduction", doc)
        self.assertIn("长度档位：`1e4`、`1e6`、`1e7`", doc)
        self.assertIn("matmul", doc)
        self.assertIn("`256x256`、`1024x1024`、`2048x2048`", doc)
        self.assertIn("CPU / GPU 使用相同 dtype 和 shape", doc)
        self.assertIn("random fill", doc)
        self.assertIn("`f32`，元素数 `1e6`、`1e7`", doc)
        self.assertIn("小数据传输敏感", doc)
        self.assertIn("大数据算力敏感", doc)

    def test_numpy_comparison_doc_mentions_correctness_guardrails(self) -> None:
        doc = (ROOT / "docs/benchmarks/numpy_comparison.md").read_text(encoding="utf-8")
        self.assertIn("bench-guardrails-cpu", doc)
        self.assertIn("bench-guardrails-gpu", doc)
        self.assertIn("spot-check", doc)

    def test_numpy_comparison_doc_freezes_artifact_locations(self) -> None:
        results_root = ROOT / "benchmarks/results"
        self.assertTrue(results_root.is_dir())

        doc = (ROOT / "docs/benchmarks/numpy_comparison.md").read_text(encoding="utf-8")
        self.assertIn("固定产物位置", doc)
        self.assertIn("`benchmarks/results/<YYYY-MM-DD>/`", doc)
        self.assertIn("`docs/benchmarks/numpy_comparison.md`", doc)
        self.assertIn("绝对耗时", doc)
        self.assertIn("吞吐 / 带宽 / TFLOP/s", doc)
        self.assertIn("相对 `NumPy CPU baseline` 的 speedup", doc)
        self.assertIn("具体命令行", doc)
        self.assertIn("NumUya commit", doc)
        self.assertIn("benchmark 运行日期", doc)
        self.assertIn("硬件/驱动/版本信息", doc)
        self.assertIn("非同类设备对比，仅作端到端参考", doc)

    def test_summarize_benchmarks_generates_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            input_dir = tmpdir / "inputs"
            output_dir = tmpdir / "outputs"
            doc_path = tmpdir / "numpy_comparison.md"
            input_dir.mkdir()
            output_dir.mkdir()
            doc_path.write_text("# NumUya vs NumPy Benchmark 规则\n", encoding="utf-8")

            (input_dir / "numpy_cpu.json").write_text(
                json.dumps(
                    {
                        "benchmark": "numpy_cpu",
                        "metadata": {
                            "python_version": "3.12.0",
                            "numpy_version": "2.0.0",
                            "blas": "OpenBLAS",
                            "thread_env": {"OMP_NUM_THREADS": "1"},
                            "machine": "x86_64",
                            "platform": "Linux",
                            "numuya_commit": "abc123",
                            "run_date": "2026-06-18",
                            "command": "python benchmarks/python/bench_numpy_cpu.py --json",
                        },
                        "results": [
                            {
                                "operation": "add",
                                "shape": [1000000],
                                "dtype": "float64",
                                "iterations": 200,
                                "total_ns": 2000000,
                                "ns_per_iter": 10000.0,
                            },
                            {
                                "operation": "sum",
                                "shape": [1000000],
                                "dtype": "float64",
                                "iterations": 400,
                                "total_ns": 3200000,
                                "ns_per_iter": 8000.0,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (input_dir / "gpu_reference.json").write_text(
                json.dumps(
                    {
                        "benchmark": "gpu_reference",
                        "metadata": {
                            "python_version": "3.12.0",
                            "numpy_version": "2.0.0",
                            "cupy_version": "13.0.0",
                            "thread_env": {"OMP_NUM_THREADS": "1"},
                            "machine": "x86_64",
                            "platform": "Linux",
                            "numuya_commit": "abc123",
                            "run_date": "2026-06-18",
                            "command": "python benchmarks/python/bench_gpu_reference.py --json",
                        },
                        "numpy_cpu_baseline": [
                            {
                                "operation": "add",
                                "shape": [1000000],
                                "dtype": "float64",
                                "iterations": 200,
                                "total_ns": 2000000,
                                "ns_per_iter": 10000.0,
                            }
                        ],
                        "gpu_reference": {
                            "available": True,
                            "device_name": "Mock GPU",
                            "results": [
                                {
                                    "operation": "add",
                                    "shape": [1000000],
                                    "dtype": "float64",
                                    "iterations": 200,
                                    "total_ns": 1000000,
                                    "ns_per_iter": 5000.0,
                                }
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )
            (input_dir / "numuya_cpu.json").write_text(
                json.dumps(
                    {
                        "benchmark": "numuya_cpu",
                        "metadata": {
                            "numuya_commit": "abc123",
                            "run_date": "2026-06-18",
                            "command": "../uya/bin/uya run src/numuya/_benchmarks/bench_simd.uya --manifest-path uya.toml",
                        },
                        "results": [
                            {
                                "operation": "add",
                                "mode": "cpu",
                                "dtype": "float64",
                                "shape": [1000000],
                                "iterations": 100,
                                "metric": "throughput",
                                "unit": "ns/iter",
                                "total_ns": 700000,
                                "ns_per_iter": 7000.0,
                            },
                            {
                                "operation": "sum",
                                "mode": "cpu",
                                "dtype": "float64",
                                "shape": [1000000],
                                "iterations": 100,
                                "metric": "throughput",
                                "unit": "ns/iter",
                                "total_ns": 0,
                                "ns_per_iter": 0.0,
                                "status": "failed",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (input_dir / "numuya_cuda.json").write_text(
                json.dumps(
                    {
                        "benchmark": "numuya_cuda",
                        "metadata": {
                            "gpu_name": "Mock GPU",
                            "cuda_driver_version": "555.1",
                            "numuya_commit": "abc123",
                            "run_date": "2026-06-18",
                            "command": "../uya/bin/uya run src/numuya/_benchmarks/bench_cuda.uya --manifest-path uya.toml",
                        },
                        "results": [
                            {
                                "operation": "transfer_h2d",
                                "mode": "end-to-end",
                                "dtype": "float64",
                                "shape": [1000000],
                                "iterations": 100,
                                "metric": "bandwidth",
                                "unit": "GB/s",
                                "total_ns": 400000,
                                "throughput": 12.0,
                            },
                            {
                                "operation": "add",
                                "mode": "end-to-end",
                                "dtype": "float64",
                                "shape": [1000000],
                                "iterations": 100,
                                "metric": "throughput",
                                "unit": "GB/s",
                                "total_ns": 900000,
                                "throughput": 32.0,
                            },
                            {
                                "operation": "add",
                                "mode": "kernel-only",
                                "dtype": "float64",
                                "shape": [1000000],
                                "iterations": 100,
                                "metric": "throughput",
                                "unit": "GB/s",
                                "total_ns": 600000,
                                "throughput": 48.0,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "benchmarks/python/summarize_benchmarks.py"),
                    "--input-dir",
                    str(input_dir),
                    "--output-dir",
                    str(output_dir),
                    "--doc-path",
                    str(doc_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.stderr, "")

            summary_json = json.loads((output_dir / "benchmark_summary.json").read_text(encoding="utf-8"))
            summary_md = (output_dir / "benchmark_summary.md").read_text(encoding="utf-8")
            report_doc = doc_path.read_text(encoding="utf-8")

            self.assertEqual(summary_json["metadata"]["run_date"], "2026-06-18")
            self.assertEqual(
                [section["category"] for section in summary_json["sections"]],
                ["CPU", "CUDA end-to-end", "CUDA kernel-only", "CuPy reference"],
            )
            cpu_rows = summary_json["sections"][0]["rows"]
            self.assertEqual(cpu_rows[0]["speedup_vs_numpy_cpu"], 1.43)
            self.assertEqual(cpu_rows[1]["status"], "failed")
            self.assertEqual(cpu_rows[1]["baseline_status"], "ok")
            self.assertEqual(summary_json["sections"][1]["rows"][0]["speedup_vs_numpy_cpu"], 1.11)
            self.assertEqual(summary_json["sections"][3]["rows"][0]["speedup_vs_numpy_cpu"], 2.0)
            self.assertIn(
                "transfer_h2d",
                [row["operation"] for row in summary_json["sections"][1]["rows"]],
            )
            self.assertIn("missing", summary_md)
            self.assertIn("failed", summary_md)
            self.assertIn("CUDA end-to-end", summary_md)
            self.assertIn("CUDA kernel-only", summary_md)
            self.assertIn("CuPy reference", summary_md)
            self.assertIn("## 第一版 CPU / GPU 对比报告", report_doc)
            self.assertIn("NumPy 无 GPU backend", report_doc)
            self.assertIn(str(input_dir), report_doc)


if __name__ == "__main__":
    unittest.main()
