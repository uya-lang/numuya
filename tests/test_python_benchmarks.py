import json
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
