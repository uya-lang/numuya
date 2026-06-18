# Benchmark Summary

- run_date: 2026-06-18
- numuya_commit: bba2b7af2be1e8c9b097c3146e330dec134f8958
- commands: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 make bench, OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 make bench

## CPU

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | ok | ok | 9280931973 | 92809319.73 | missing | 0.02 |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | ok | ok | 8031348110 | 80313481.1 | missing | 0.02 |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float64 | 1000000 | ok | ok | 3322115076 | 33221150.76 | missing | 0.01 |

## CUDA end-to-end
非同类设备对比，仅作端到端参考。

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | missing | 192805777 | 1928057.77 | missing | ok |
| add | float64 | 1000000 | ok | ok | 196820599 | 1968205.99 | missing | 0.8 |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | missing | 192344163 | 1923441.63 | missing | ok |
| sum | float64 | 1000000 | ok | ok | 194755462 | 1947554.62 | missing | 0.21 |
| transfer_d2h | float64 | 1000000 | ok | missing | 91692008 | 916920.08 | missing | ok |
| transfer_h2d | float64 | 1000000 | ok | missing | 97225076 | 972250.76 | missing | ok |

## CUDA kernel-only

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | missing | 3888693 | 38886.93 | missing | ok |
| add | float64 | 1000000 | ok | ok | 7903515 | 79035.15 | missing | 19.85 |
| matmul | float32 | 1024x1024 | ok | missing | 17086604 | 1708660.4 | missing | ok |
| matmul | float32 | 2048x2048 | ok | missing | 139139445 | 13913944.5 | missing | ok |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| matmul_vendor_tf32 | float32 | 2048x2048 | ok | missing | 15135346 | 1513534.6 | missing | ok |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float32 | 1000000 | ok | missing | 2663465 | 26634.65 | missing | ok |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | missing | 3427079 | 34270.79 | missing | ok |
| sum | float64 | 1000000 | ok | ok | 5838378 | 58383.78 | missing | 7.09 |

## CuPy reference

| operation | dtype | shape | status | baseline | total_ns | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| matmul | float64 | 512x512 | missing | ok | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
| sum | float64 | 1000000 | missing | ok | missing | missing | missing | missing |
