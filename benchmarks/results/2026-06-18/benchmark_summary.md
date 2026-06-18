# Benchmark Summary

- run_date: 2026-06-18
- numuya_commit: 47580f8d5dd4ee3fc3fcd52b9083d96c3808fc74
- commands: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 make bench, OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 make bench

## Sources

- numpy_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numpy_cpu.json`
- gpu_reference_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/gpu_reference.json`
- numuya_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cpu.json`
- numuya_cuda_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cuda.json`
- numuya_raw_text: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_raw.txt`

## CPU

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | ok | ok | 7555689787 | 75556897.87 | missing | 0.02 |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | ok | ok | 7619641384 | 76196413.84 | missing | 0.02 |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float64 | 1000000 | ok | ok | 3234991256 | 32349912.56 | missing | 0.01 |

## CUDA end-to-end
非同类设备对比，仅作端到端参考。

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | missing | 162927272 | 1629272.72 | missing | ok |
| add | float64 | 1000000 | ok | ok | 166710135 | 1667101.35 | missing | 0.77 |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | missing | 162035673 | 1620356.73 | missing | ok |
| sum | float64 | 1000000 | ok | ok | 163893351 | 1638933.51 | missing | 0.24 |
| transfer_d2h | float64 | 1000000 | ok | missing | 80094687 | 800946.87 | missing | ok |
| transfer_h2d | float64 | 1000000 | ok | missing | 78947194 | 789471.94 | missing | ok |

## CUDA kernel-only

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | missing | 3885391 | 38853.91 | missing | ok |
| add | float64 | 1000000 | ok | ok | 7668254 | 76682.54 | missing | 16.71 |
| matmul | float32 | 1024x1024 | ok | missing | 16592064 | 1659206.4 | missing | ok |
| matmul | float32 | 2048x2048 | ok | missing | 134827168 | 13482716.8 | missing | ok |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| matmul_vendor_tf32 | float32 | 2048x2048 | ok | missing | 14700434 | 1470043.4 | missing | ok |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float32 | 1000000 | ok | missing | 2311687 | 23116.87 | missing | ok |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | missing | 2993792 | 29937.92 | missing | ok |
| sum | float64 | 1000000 | ok | ok | 4851470 | 48514.7 | missing | 8.26 |

## CuPy reference

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
