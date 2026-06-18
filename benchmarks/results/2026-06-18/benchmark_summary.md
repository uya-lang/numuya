# Benchmark Summary

- run_date: 2026-06-18
- numuya_commit: 8ff0e4593895aae0ac174e79f9d482576f3d2f84
- commands: benchmarks/python/bench_numpy_cpu.py --json, benchmarks/python/bench_gpu_reference.py --json, make bench > benchmarks/results/2026-06-18/numuya_raw.txt

## Sources

- numpy_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numpy_cpu.json`
- gpu_reference_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/gpu_reference.json`
- numuya_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cpu.json`
- numuya_cuda_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cuda.json`
- numuya_raw_text: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_raw.txt`

## CPU

| operation | dtype | shape | status | baseline | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | ok | 6517.0 | 6292 | 15069.0 | 17.149 GiB/s | 1.42 |
| add | float32 | 1000000 | ok | ok | 635760.5 | 584423 | 701641.0 | 17.579 GiB/s | 0.98 |
| add | float32 | 10000000 | ok | ok | 25895772.0 | 25205936 | 26640497.0 | 4.316 GiB/s | 0.67 |
| add | float64 | 10000 | ok | ok | 7876.5 | 7813 | 23165.0 | 28.378 GiB/s | 1.09 |
| add | float64 | 1000000 | ok | ok | 919842.0 | 871557 | 964226.0 | 24.300 GiB/s | 1.39 |
| add | float64 | 10000000 | ok | ok | 50122524.0 | 49388016 | 51042510.0 | 4.459 GiB/s | 0.69 |
| mul | float32 | 10000 | ok | ok | 6314.0 | 6289 | 16093.0 | 17.700 GiB/s | 0.58 |
| mul | float32 | 1000000 | ok | ok | 585941.0 | 552802 | 638347.0 | 19.073 GiB/s | 0.75 |
| mul | float32 | 10000000 | ok | ok | 26171574.0 | 25449693 | 26668619.0 | 4.270 GiB/s | 0.68 |
| mul | float64 | 10000 | ok | ok | 8131.5 | 8077 | 8184.0 | 27.488 GiB/s | 1.07 |
| mul | float64 | 1000000 | ok | ok | 947011.5 | 894386 | 1018759.0 | 23.602 GiB/s | 1.01 |
| mul | float64 | 10000000 | ok | ok | 50256726.5 | 49022920 | 51147946.0 | 4.448 GiB/s | 0.69 |
| sum | float32 | 10000 | ok | ok | 1873.0 | 1855 | 1901.0 | 19.889 GiB/s | 4.01 |
| sum | float32 | 1000000 | ok | ok | 138850.0 | 135455 | 147601.0 | 26.830 GiB/s | 2.99 |
| sum | float32 | 10000000 | ok | ok | 2221840.5 | 1933095 | 2996988.0 | 16.767 GiB/s | 2.09 |
| sum | float64 | 10000 | ok | ok | 3160.5 | 3147 | 3177.0 | 23.574 GiB/s | 2.58 |
| sum | float64 | 1000000 | ok | ok | 298243.0 | 266181 | 343707.0 | 24.982 GiB/s | 1.31 |
| sum | float64 | 10000000 | ok | ok | 6607088.0 | 6167406 | 7247076.0 | 11.277 GiB/s | 1.18 |
| matmul | float32 | 256x256 | ok | ok | 8422628.0 | 8043954 | 8802854.0 | 0.004 TFLOP/s | 0.36 |
| matmul | float32 | 1024x1024 | ok | ok | 520099715.0 | 516192320 | 527000767.0 | 0.004 TFLOP/s | 0.01 |
| matmul | float32 | 2048x2048 | ok | ok | 3992919945.5 | 3966400696 | 4095566546.0 | 0.004 TFLOP/s | 0.01 |
| random | float32 | 1000000 | ok | ok | 3419566.5 | 3136244 | 3590579.0 | 1.089 GiB/s | 1.64 |
| random | float32 | 10000000 | ok | ok | 49126482.0 | 48197282 | 51706556.0 | 0.758 GiB/s | 0.81 |

## CUDA end-to-end
非同类设备对比，仅作端到端参考。

| operation | dtype | shape | status | baseline | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | ok | 32742.814 | 32742.814 | 32742.814 | 3.413 GiB/s | 0.28 |
| add | float32 | 1000000 | ok | ok | 1310705.16 | 1310705.16 | 1310705.16 | 8.527 GiB/s | 0.48 |
| add | float32 | 10000000 | ok | ok | 16721879.8 | 16721879.8 | 16721879.8 | 6.683 GiB/s | 1.04 |
| add | float64 | 10000 | ok | ok | 68479.599 | 68479.599 | 68479.599 | 3.264 GiB/s | 0.13 |
| add | float64 | 1000000 | ok | ok | 2445467.01 | 2445467.01 | 2445467.01 | 9.140 GiB/s | 0.52 |
| add | float64 | 10000000 | ok | ok | 32858880.8 | 32858880.8 | 32858880.8 | 6.802 GiB/s | 1.06 |
| mul | float32 | 10000 | ok | ok | 33336.197 | 33336.197 | 33336.197 | 3.352 GiB/s | 0.11 |
| mul | float32 | 1000000 | ok | ok | 1286893.75 | 1286893.75 | 1286893.75 | 8.684 GiB/s | 0.34 |
| mul | float32 | 10000000 | ok | ok | 14092948.6 | 14092948.6 | 14092948.6 | 7.930 GiB/s | 1.27 |
| mul | float64 | 10000 | ok | ok | 67412.596 | 67412.596 | 67412.596 | 3.316 GiB/s | 0.13 |
| mul | float64 | 1000000 | ok | ok | 2393177.94 | 2393177.94 | 2393177.94 | 9.340 GiB/s | 0.4 |
| mul | float64 | 10000000 | ok | ok | 28116992.7 | 28116992.7 | 28116992.7 | 7.950 GiB/s | 1.24 |
| sum | float32 | 10000 | ok | ok | 29989.549 | 29989.549 | 29989.549 | 1.242 GiB/s | 0.25 |
| sum | float32 | 1000000 | ok | ok | 483765.38 | 483765.38 | 483765.38 | 7.701 GiB/s | 0.86 |
| sum | float32 | 10000000 | ok | ok | 4431153.7 | 4431153.7 | 4431153.7 | 8.407 GiB/s | 1.05 |
| sum | float64 | 10000 | ok | ok | 52473.276 | 52473.276 | 52473.276 | 1.420 GiB/s | 0.16 |
| sum | float64 | 1000000 | ok | ok | 858546.67 | 858546.67 | 858546.67 | 8.678 GiB/s | 0.46 |
| sum | float64 | 10000000 | ok | ok | 10865483.1 | 10865483.1 | 10865483.1 | 6.857 GiB/s | 0.72 |
| matmul | float32 | 256x256 | ok | ok | 201915.2 | 201915.2 | 201915.2 | 0.166 TFLOP/s | 14.89 |
| matmul | float32 | 1024x1024 | ok | ok | 3159395.1 | 3159395.1 | 3159395.1 | 0.680 TFLOP/s | 1.41 |
| matmul | float32 | 2048x2048 | ok | ok | 20516184.4 | 20516184.4 | 20516184.4 | 0.837 TFLOP/s | 2.14 |
| random | float32 | 1000000 | ok | ok | 450055.82 | 450055.82 | 450055.82 | 8.277 GiB/s | 12.44 |
| random | float32 | 10000000 | ok | ok | 5890630.0 | 5890630.0 | 5890630.0 | 6.324 GiB/s | 6.72 |
| transfer_d2h | float64 | 1000000 | ok | missing | 817503.04 | 817503.04 | 817503.04 | missing | ok |
| transfer_h2d | float64 | 1000000 | ok | missing | 784982.24 | 784982.24 | 784982.24 | missing | ok |

## CUDA kernel-only

| operation | dtype | shape | status | baseline | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | ok | 2040.605 | 2040.605 | 2040.605 | 54.767 GiB/s | 4.53 |
| add | float32 | 1000000 | ok | ok | 43947.61 | 43947.61 | 43947.61 | 254.300 GiB/s | 14.22 |
| add | float32 | 10000000 | ok | ok | 359606.8 | 359606.8 | 359606.8 | 310.780 GiB/s | 48.57 |
| add | float64 | 10000 | ok | ok | 2245.853 | 2245.853 | 2245.853 | 99.525 GiB/s | 3.83 |
| add | float64 | 1000000 | ok | ok | 73824.83 | 73824.83 | 73824.83 | 302.767 GiB/s | 17.36 |
| add | float64 | 10000000 | ok | ok | 773206.7 | 773206.7 | 773206.7 | 289.078 GiB/s | 45.04 |
| mul | float32 | 10000 | ok | ok | 2051.321 | 2051.321 | 2051.321 | 54.481 GiB/s | 1.78 |
| mul | float32 | 1000000 | ok | ok | 38793.48 | 38793.48 | 38793.48 | 288.086 GiB/s | 11.3 |
| mul | float32 | 10000000 | ok | ok | 366860.3 | 366860.3 | 366860.3 | 304.636 GiB/s | 48.82 |
| mul | float64 | 10000 | ok | ok | 2001.699 | 2001.699 | 2001.699 | 111.664 GiB/s | 4.36 |
| mul | float64 | 1000000 | ok | ok | 84189.35 | 84189.35 | 84189.35 | 265.494 GiB/s | 11.39 |
| mul | float64 | 10000000 | ok | ok | 782042.7 | 782042.7 | 782042.7 | 285.812 GiB/s | 44.5 |
| sum | float32 | 10000 | ok | ok | 23055.168 | 23055.168 | 23055.168 | 1.616 GiB/s | 0.33 |
| sum | float32 | 1000000 | ok | ok | 30529.39 | 30529.39 | 30529.39 | 122.023 GiB/s | 13.58 |
| sum | float32 | 10000000 | ok | ok | 151315.2 | 151315.2 | 151315.2 | 246.194 GiB/s | 30.7 |
| sum | float64 | 10000 | ok | ok | 22774.558 | 22774.558 | 22774.558 | 3.271 GiB/s | 0.36 |
| sum | float64 | 1000000 | ok | ok | 47128.29 | 47128.29 | 47128.29 | 158.091 GiB/s | 8.29 |
| sum | float64 | 10000000 | ok | ok | 308933.4 | 308933.4 | 308933.4 | 241.171 GiB/s | 25.2 |
| matmul | float32 | 256x256 | ok | ok | 97460.4 | 97460.4 | 97460.4 | 0.344 TFLOP/s | 30.85 |
| matmul | float32 | 1024x1024 | ok | ok | 1816420.7 | 1816420.7 | 1816420.7 | 1.182 TFLOP/s | 2.45 |
| matmul | float32 | 2048x2048 | ok | ok | 15333579.3 | 15333579.3 | 15333579.3 | 1.120 TFLOP/s | 2.87 |
| random | float32 | 1000000 | ok | ok | 18481.58 | 18481.58 | 18481.58 | 201.568 GiB/s | 302.91 |
| random | float32 | 10000000 | ok | ok | 123799.3 | 123799.3 | 123799.3 | 300.914 GiB/s | 319.83 |
| matmul_vendor_tf32 | float32 | 2048x2048 | ok | missing | 1612128.2 | 1612128.2 | 1612128.2 | missing | ok |

## CuPy reference

| operation | dtype | shape | status | baseline | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | ok | 21288.0 | 20837 | 36634.0 | 5.250 GiB/s | 0.43 |
| add | float32 | 1000000 | ok | ok | 58844.5 | 57709 | 69162.0 | 189.922 GiB/s | 10.62 |
| add | float32 | 10000000 | ok | ok | 382540.0 | 379807 | 649975.0 | 292.149 GiB/s | 45.66 |
| add | float64 | 10000 | ok | ok | 22405.0 | 21403 | 25717.0 | 9.976 GiB/s | 0.38 |
| add | float64 | 1000000 | ok | ok | 93867.0 | 93249 | 105386.0 | 238.121 GiB/s | 13.65 |
| add | float64 | 10000000 | ok | ok | 873665.0 | 735194 | 1051695.0 | 255.839 GiB/s | 39.86 |
| mul | float32 | 10000 | ok | ok | 21753.0 | 20729 | 43165.0 | 5.138 GiB/s | 0.17 |
| mul | float32 | 1000000 | ok | ok | 58616.5 | 57481 | 272395.0 | 190.661 GiB/s | 7.48 |
| mul | float32 | 10000000 | ok | ok | 384191.5 | 380346 | 516546.0 | 290.893 GiB/s | 46.62 |
| mul | float64 | 10000 | ok | ok | 23921.0 | 22452 | 240660.0 | 9.344 GiB/s | 0.36 |
| mul | float64 | 1000000 | ok | ok | 93600.0 | 92824 | 95624.0 | 238.801 GiB/s | 10.24 |
| mul | float64 | 10000000 | ok | ok | 752326.5 | 736662 | 1042428.0 | 297.102 GiB/s | 46.26 |
| sum | float32 | 10000 | ok | ok | 31878.0 | 29386 | 56901.0 | 1.169 GiB/s | 0.24 |
| sum | float32 | 1000000 | ok | ok | 41281.5 | 39864 | 73908.0 | 90.241 GiB/s | 10.04 |
| sum | float32 | 10000000 | ok | ok | 150799.0 | 146502 | 414192.0 | 247.037 GiB/s | 30.81 |
| sum | float64 | 10000 | ok | ok | 30559.0 | 30029 | 45470.0 | 2.438 GiB/s | 0.27 |
| sum | float64 | 1000000 | ok | ok | 57212.5 | 54624 | 72245.0 | 130.226 GiB/s | 6.83 |
| sum | float64 | 10000000 | ok | ok | 274569.5 | 268896 | 539704.0 | 271.355 GiB/s | 28.35 |
| matmul | float32 | 256x256 | ok | ok | 50348.0 | 49526 | 54533.0 | 0.666 TFLOP/s | 59.71 |
| matmul | float32 | 1024x1024 | ok | ok | 348871.0 | 342388 | 490868.0 | 6.156 TFLOP/s | 12.73 |
| matmul | float32 | 2048x2048 | ok | ok | 2571098.5 | 2248112 | 2776895.0 | 6.682 TFLOP/s | 17.1 |
| random | float32 | 1000000 | ok | ok | 46765.5 | 45801 | 261990.0 | 79.659 GiB/s | 119.71 |
| random | float32 | 10000000 | ok | ok | 157763.0 | 156232 | 311475.0 | 236.132 GiB/s | 250.97 |
