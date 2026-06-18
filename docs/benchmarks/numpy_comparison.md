# NumUya vs NumPy Benchmark 规则

本文档固定 Phase 24 的 NumUya vs NumPy 对比口径，后续所有原始结果、汇总脚本和报告都必须遵守这里的规则，避免混用 CPU、CUDA end-to-end、CUDA kernel-only 与可选 GPU reference。

## Benchmark 固定规则

### 1. 对比分组

- CPU 主表只允许比较 `NumUya CPU/SIMD` vs `NumPy CPU`。
- GPU 主表拆成两层：
  - `NumUya CUDA end-to-end` vs `NumPy CPU baseline`，其中 end-to-end 固定包含 H2D + kernel + D2H。
  - `NumUya CUDA kernel-only` 单列报告，只用于说明设备端纯计算能力，不伪造 `NumPy GPU`。
- 如果同机环境安装了 `cupy`，可额外追加 `CuPy reference` 表；它必须与 NumPy 主表分开，不能替代 `NumPy CPU baseline`。

### 2. 第一版固定测试矩阵

首轮 Python 对照和 NumUya 对照必须覆盖相同 workload，且第一版主表矩阵固定如下；后续若要扩项，只能新增附表，不能覆盖这套主矩阵。

- elementwise / reduction
  - operation：elementwise 固定 `add`、`mul`；reduction 固定 `sum`
  - dtype：`f32`、`f64`
  - 长度档位：`1e4`、`1e6`、`1e7`
  - 数据布局：contiguous 1-D array
- matmul
  - operation：`matmul`
  - shape：`256x256`、`1024x1024`、`2048x2048`
  - CPU / GPU 使用相同 dtype 和 shape
  - 第一版 dtype 固定 `f32`；若后续补 `f64`，必须单列为扩展项
- random fill
  - operation：`random`
  - dtype：`f32`，元素数 `1e6`、`1e7`
- GPU 额外分类
  - 小数据传输敏感：优先使用 `1e4` elementwise / reduction 与 `256x256` matmul，突出 launch + H2D/D2H 开销
  - 大数据算力敏感：优先使用 `1e7` elementwise / reduction、`2048x2048` matmul 与 `1e7` random fill，突出 kernel / memory throughput

如果某个实现暂时缺少上述 workload，结果中必须明确标注 `missing`，并在报告里解释缺口，而不是私自缩减矩阵口径。

### 3. 固定 warmup、repeat 与统计

- `add` / `mul` / `sum` / `random`
  - warmup：5 次
  - repeat：20 次
- `matmul`
  - warmup：3 次
  - repeat：10 次
- 统计输出固定包含：
  - `median`
  - `best`
  - `p95`
- 原始 JSON 必须保留全部单次样本，便于复算统计值。

### 3.5 正确性护栏

- 跑任何 CPU benchmark 前，先执行 `make bench-guardrails-cpu`；它固定包含 `make test` 和 benchmark workload 的 Python spot-check。
- 跑任何 GPU benchmark 前，先执行 `make bench-guardrails-gpu`；它固定包含 `make test-cuda` 和 GPU spot-check。
- 若本轮要走 vendor 路径，先执行 `make bench-guardrails-gpu-vendor`，确保 `make test-cuda-vendor` 先通过。
- `benchmarks/python/spotcheck_benchmarks.py` 会先跑 `src/numuya/_tools/bench_spotcheck.uya`，再对 `add`、`mul`、`sum`、`matmul`、`random` 做小尺寸 spot-check；GPU 侧额外校验 `add`、`sum`，并在可用时附带 `CuPy` 一致性检查。
- spot-check 是 benchmark 前置护栏，不替代常规 correctness test，也不能替代最终原始 benchmark 结果。

### 4. 线程与 CPU backend 规则

运行 CPU benchmark 前固定导出以下环境变量，并把最终值写入结果元数据：

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `NUMEXPR_NUM_THREADS=1`

CPU benchmark 默认允许 `NumPy` 调用其已安装的 BLAS backend，因为这更符合真实用户环境；但结果中必须明确记录：

- `numpy.__version__`
- BLAS backend 名称与实现来源，例如 OpenBLAS / MKL
- `np.show_config()` 或等价探针提取出的 backend 关键信息

如果需要额外跑“禁用多线程 BLAS”的对照，只能作为附表，不能替代默认主表。

### 5. GPU 计时边界

所有 GPU benchmark 都必须在计时前后显式 synchronize。

- `NumUya CUDA end-to-end`
  - 计入：host 端准备完成后的 H2D、kernel 执行、D2H
  - 不计入：首次 driver 初始化、模块加载、allocator 首次扩容
- `NumUya CUDA kernel-only`
  - 只计 kernel 执行时间
  - 输入输出 buffer 必须预分配；不得把 H2D / D2H / 每轮分配混入 kernel-only
- `CuPy reference`（如有）
  - 必须与 `NumUya CUDA kernel-only` 使用相同 workload、dtype、shape
  - 必须注明计时边界是 CuPy event / synchronize 后的 kernel-only 还是包含传输的 end-to-end

任何 GPU 结果都必须标注属于 `CUDA end-to-end`、`CUDA kernel-only` 或 `CuPy reference`，禁止只写一个模糊的 “GPU time”。

### 6. 固定产物位置

- 原始 benchmark 结果固定落到 `benchmarks/results/<YYYY-MM-DD>/`；每次运行使用独立日期目录，目录内按 benchmark 类别继续分文件保存 JSON 原始结果，避免覆盖历史样本。
- Phase 24 的 Markdown 汇总文档固定为 `docs/benchmarks/numpy_comparison.md`。
- 后续自动汇总生成的机器可读 summary 必须与原始结果目录同级落在对应日期目录内，作为该次运行的单一汇总产物，禁止散落到临时目录或未版本化路径。

### 7. 结果展示与元数据

每次 benchmark 结果都必须包含以下元数据：

- `python --version`
- `numpy.__version__`
- `cupy.__version__`（如有）
- 线程环境变量
- CPU 型号、逻辑核数、内存容量
- GPU 型号、driver/runtime 版本、显存容量（如有）
- NumUya commit
- benchmark 运行日期
- 具体命令行

最终 Markdown 汇总表至少包含：

- 绝对耗时
- 吞吐 / 带宽 / TFLOP/s
- 相对 `NumPy CPU baseline` 的 speedup
- 具体命令行
- NumUya commit
- benchmark 运行日期
- 硬件/驱动/版本信息
- 对比类别：`CPU`、`CUDA end-to-end`、`CUDA kernel-only`、`CuPy reference`

如果表中出现 `NumUya CUDA end-to-end` vs `NumPy CPU baseline`，必须紧邻注明“非同类设备对比，仅作端到端参考”。

## 第一版 CPU / GPU 对比报告

- 原始结果目录：`benchmarks/results/2026-06-18`
- benchmark 运行日期：`2026-06-18`
- NumUya commit：`8ff0e4593895aae0ac174e79f9d482576f3d2f84`
- 计时口径：CPU 与 `NumPy CPU baseline` 结论来自 wall-clock median；`NumUya CUDA end-to-end` 逐 workload 计入传输与计算；`NumUya CUDA kernel-only` 只代表设备端 kernel 时间。
- 说明：NumPy 无 GPU backend，因此 GPU 主表只比较 `NumUya CUDA end-to-end` 与 `NumPy CPU baseline`；`NumUya CUDA kernel-only` 单列报告，不伪造 `NumPy GPU` 数据。

- 具体命令行：`benchmarks/python/bench_numpy_cpu.py --json`

### 原始 JSON / 文本来源

- numpy_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numpy_cpu.json`
- gpu_reference_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/gpu_reference.json`
- numuya_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cpu.json`
- numuya_cuda_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cuda.json`
- numuya_raw_text: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_raw.txt`

### CPU

| operation | dtype | shape | status | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | 6517.0 | 6292 | 15069.0 | 17.149 GiB/s | 1.42 |
| add | float32 | 1000000 | ok | 635760.5 | 584423 | 701641.0 | 17.579 GiB/s | 0.98 |
| add | float32 | 10000000 | ok | 25895772.0 | 25205936 | 26640497.0 | 4.316 GiB/s | 0.67 |
| add | float64 | 10000 | ok | 7876.5 | 7813 | 23165.0 | 28.378 GiB/s | 1.09 |
| add | float64 | 1000000 | ok | 919842.0 | 871557 | 964226.0 | 24.300 GiB/s | 1.39 |
| add | float64 | 10000000 | ok | 50122524.0 | 49388016 | 51042510.0 | 4.459 GiB/s | 0.69 |
| mul | float32 | 10000 | ok | 6314.0 | 6289 | 16093.0 | 17.700 GiB/s | 0.58 |
| mul | float32 | 1000000 | ok | 585941.0 | 552802 | 638347.0 | 19.073 GiB/s | 0.75 |
| mul | float32 | 10000000 | ok | 26171574.0 | 25449693 | 26668619.0 | 4.270 GiB/s | 0.68 |
| mul | float64 | 10000 | ok | 8131.5 | 8077 | 8184.0 | 27.488 GiB/s | 1.07 |
| mul | float64 | 1000000 | ok | 947011.5 | 894386 | 1018759.0 | 23.602 GiB/s | 1.01 |
| mul | float64 | 10000000 | ok | 50256726.5 | 49022920 | 51147946.0 | 4.448 GiB/s | 0.69 |
| sum | float32 | 10000 | ok | 1873.0 | 1855 | 1901.0 | 19.889 GiB/s | 4.01 |
| sum | float32 | 1000000 | ok | 138850.0 | 135455 | 147601.0 | 26.830 GiB/s | 2.99 |
| sum | float32 | 10000000 | ok | 2221840.5 | 1933095 | 2996988.0 | 16.767 GiB/s | 2.09 |
| sum | float64 | 10000 | ok | 3160.5 | 3147 | 3177.0 | 23.574 GiB/s | 2.58 |
| sum | float64 | 1000000 | ok | 298243.0 | 266181 | 343707.0 | 24.982 GiB/s | 1.31 |
| sum | float64 | 10000000 | ok | 6607088.0 | 6167406 | 7247076.0 | 11.277 GiB/s | 1.18 |
| matmul | float32 | 256x256 | ok | 8422628.0 | 8043954 | 8802854.0 | 0.004 TFLOP/s | 0.36 |
| matmul | float32 | 1024x1024 | ok | 520099715.0 | 516192320 | 527000767.0 | 0.004 TFLOP/s | 0.01 |
| matmul | float32 | 2048x2048 | ok | 3992919945.5 | 3966400696 | 4095566546.0 | 0.004 TFLOP/s | 0.01 |
| random | float32 | 1000000 | ok | 3419566.5 | 3136244 | 3590579.0 | 1.089 GiB/s | 1.64 |
| random | float32 | 10000000 | ok | 49126482.0 | 48197282 | 51706556.0 | 0.758 GiB/s | 0.81 |

### CUDA end-to-end

非同类设备对比，仅作端到端参考。

| operation | dtype | shape | status | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | 32742.814 | 32742.814 | 32742.814 | 3.413 GiB/s | 0.28 |
| add | float32 | 1000000 | ok | 1310705.16 | 1310705.16 | 1310705.16 | 8.527 GiB/s | 0.48 |
| add | float32 | 10000000 | ok | 16721879.8 | 16721879.8 | 16721879.8 | 6.683 GiB/s | 1.04 |
| add | float64 | 10000 | ok | 68479.599 | 68479.599 | 68479.599 | 3.264 GiB/s | 0.13 |
| add | float64 | 1000000 | ok | 2445467.01 | 2445467.01 | 2445467.01 | 9.140 GiB/s | 0.52 |
| add | float64 | 10000000 | ok | 32858880.8 | 32858880.8 | 32858880.8 | 6.802 GiB/s | 1.06 |
| mul | float32 | 10000 | ok | 33336.197 | 33336.197 | 33336.197 | 3.352 GiB/s | 0.11 |
| mul | float32 | 1000000 | ok | 1286893.75 | 1286893.75 | 1286893.75 | 8.684 GiB/s | 0.34 |
| mul | float32 | 10000000 | ok | 14092948.6 | 14092948.6 | 14092948.6 | 7.930 GiB/s | 1.27 |
| mul | float64 | 10000 | ok | 67412.596 | 67412.596 | 67412.596 | 3.316 GiB/s | 0.13 |
| mul | float64 | 1000000 | ok | 2393177.94 | 2393177.94 | 2393177.94 | 9.340 GiB/s | 0.4 |
| mul | float64 | 10000000 | ok | 28116992.7 | 28116992.7 | 28116992.7 | 7.950 GiB/s | 1.24 |
| sum | float32 | 10000 | ok | 29989.549 | 29989.549 | 29989.549 | 1.242 GiB/s | 0.25 |
| sum | float32 | 1000000 | ok | 483765.38 | 483765.38 | 483765.38 | 7.701 GiB/s | 0.86 |
| sum | float32 | 10000000 | ok | 4431153.7 | 4431153.7 | 4431153.7 | 8.407 GiB/s | 1.05 |
| sum | float64 | 10000 | ok | 52473.276 | 52473.276 | 52473.276 | 1.420 GiB/s | 0.16 |
| sum | float64 | 1000000 | ok | 858546.67 | 858546.67 | 858546.67 | 8.678 GiB/s | 0.46 |
| sum | float64 | 10000000 | ok | 10865483.1 | 10865483.1 | 10865483.1 | 6.857 GiB/s | 0.72 |
| matmul | float32 | 256x256 | ok | 201915.2 | 201915.2 | 201915.2 | 0.166 TFLOP/s | 14.89 |
| matmul | float32 | 1024x1024 | ok | 3159395.1 | 3159395.1 | 3159395.1 | 0.680 TFLOP/s | 1.41 |
| matmul | float32 | 2048x2048 | ok | 20516184.4 | 20516184.4 | 20516184.4 | 0.837 TFLOP/s | 2.14 |
| random | float32 | 1000000 | ok | 450055.82 | 450055.82 | 450055.82 | 8.277 GiB/s | 12.44 |
| random | float32 | 10000000 | ok | 5890630.0 | 5890630.0 | 5890630.0 | 6.324 GiB/s | 6.72 |
| transfer_d2h | float64 | 1000000 | ok | 817503.04 | 817503.04 | 817503.04 | missing | missing |
| transfer_h2d | float64 | 1000000 | ok | 784982.24 | 784982.24 | 784982.24 | missing | missing |

### CUDA kernel-only

| operation | dtype | shape | status | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | 2040.605 | 2040.605 | 2040.605 | 54.767 GiB/s | 4.53 |
| add | float32 | 1000000 | ok | 43947.61 | 43947.61 | 43947.61 | 254.300 GiB/s | 14.22 |
| add | float32 | 10000000 | ok | 359606.8 | 359606.8 | 359606.8 | 310.780 GiB/s | 48.57 |
| add | float64 | 10000 | ok | 2245.853 | 2245.853 | 2245.853 | 99.525 GiB/s | 3.83 |
| add | float64 | 1000000 | ok | 73824.83 | 73824.83 | 73824.83 | 302.767 GiB/s | 17.36 |
| add | float64 | 10000000 | ok | 773206.7 | 773206.7 | 773206.7 | 289.078 GiB/s | 45.04 |
| mul | float32 | 10000 | ok | 2051.321 | 2051.321 | 2051.321 | 54.481 GiB/s | 1.78 |
| mul | float32 | 1000000 | ok | 38793.48 | 38793.48 | 38793.48 | 288.086 GiB/s | 11.3 |
| mul | float32 | 10000000 | ok | 366860.3 | 366860.3 | 366860.3 | 304.636 GiB/s | 48.82 |
| mul | float64 | 10000 | ok | 2001.699 | 2001.699 | 2001.699 | 111.664 GiB/s | 4.36 |
| mul | float64 | 1000000 | ok | 84189.35 | 84189.35 | 84189.35 | 265.494 GiB/s | 11.39 |
| mul | float64 | 10000000 | ok | 782042.7 | 782042.7 | 782042.7 | 285.812 GiB/s | 44.5 |
| sum | float32 | 10000 | ok | 23055.168 | 23055.168 | 23055.168 | 1.616 GiB/s | 0.33 |
| sum | float32 | 1000000 | ok | 30529.39 | 30529.39 | 30529.39 | 122.023 GiB/s | 13.58 |
| sum | float32 | 10000000 | ok | 151315.2 | 151315.2 | 151315.2 | 246.194 GiB/s | 30.7 |
| sum | float64 | 10000 | ok | 22774.558 | 22774.558 | 22774.558 | 3.271 GiB/s | 0.36 |
| sum | float64 | 1000000 | ok | 47128.29 | 47128.29 | 47128.29 | 158.091 GiB/s | 8.29 |
| sum | float64 | 10000000 | ok | 308933.4 | 308933.4 | 308933.4 | 241.171 GiB/s | 25.2 |
| matmul | float32 | 256x256 | ok | 97460.4 | 97460.4 | 97460.4 | 0.344 TFLOP/s | 30.85 |
| matmul | float32 | 1024x1024 | ok | 1816420.7 | 1816420.7 | 1816420.7 | 1.182 TFLOP/s | 2.45 |
| matmul | float32 | 2048x2048 | ok | 15333579.3 | 15333579.3 | 15333579.3 | 1.120 TFLOP/s | 2.87 |
| random | float32 | 1000000 | ok | 18481.58 | 18481.58 | 18481.58 | 201.568 GiB/s | 302.91 |
| random | float32 | 10000000 | ok | 123799.3 | 123799.3 | 123799.3 | 300.914 GiB/s | 319.83 |
| matmul_vendor_tf32 | float32 | 2048x2048 | ok | 1612128.2 | 1612128.2 | 1612128.2 | missing | missing |

### CuPy reference

| operation | dtype | shape | status | median_ns | best_ns | p95_ns | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 10000 | ok | 21288.0 | 20837 | 36634.0 | 5.250 GiB/s | 0.43 |
| add | float32 | 1000000 | ok | 58844.5 | 57709 | 69162.0 | 189.922 GiB/s | 10.62 |
| add | float32 | 10000000 | ok | 382540.0 | 379807 | 649975.0 | 292.149 GiB/s | 45.66 |
| add | float64 | 10000 | ok | 22405.0 | 21403 | 25717.0 | 9.976 GiB/s | 0.38 |
| add | float64 | 1000000 | ok | 93867.0 | 93249 | 105386.0 | 238.121 GiB/s | 13.65 |
| add | float64 | 10000000 | ok | 873665.0 | 735194 | 1051695.0 | 255.839 GiB/s | 39.86 |
| mul | float32 | 10000 | ok | 21753.0 | 20729 | 43165.0 | 5.138 GiB/s | 0.17 |
| mul | float32 | 1000000 | ok | 58616.5 | 57481 | 272395.0 | 190.661 GiB/s | 7.48 |
| mul | float32 | 10000000 | ok | 384191.5 | 380346 | 516546.0 | 290.893 GiB/s | 46.62 |
| mul | float64 | 10000 | ok | 23921.0 | 22452 | 240660.0 | 9.344 GiB/s | 0.36 |
| mul | float64 | 1000000 | ok | 93600.0 | 92824 | 95624.0 | 238.801 GiB/s | 10.24 |
| mul | float64 | 10000000 | ok | 752326.5 | 736662 | 1042428.0 | 297.102 GiB/s | 46.26 |
| sum | float32 | 10000 | ok | 31878.0 | 29386 | 56901.0 | 1.169 GiB/s | 0.24 |
| sum | float32 | 1000000 | ok | 41281.5 | 39864 | 73908.0 | 90.241 GiB/s | 10.04 |
| sum | float32 | 10000000 | ok | 150799.0 | 146502 | 414192.0 | 247.037 GiB/s | 30.81 |
| sum | float64 | 10000 | ok | 30559.0 | 30029 | 45470.0 | 2.438 GiB/s | 0.27 |
| sum | float64 | 1000000 | ok | 57212.5 | 54624 | 72245.0 | 130.226 GiB/s | 6.83 |
| sum | float64 | 10000000 | ok | 274569.5 | 268896 | 539704.0 | 271.355 GiB/s | 28.35 |
| matmul | float32 | 256x256 | ok | 50348.0 | 49526 | 54533.0 | 0.666 TFLOP/s | 59.71 |
| matmul | float32 | 1024x1024 | ok | 348871.0 | 342388 | 490868.0 | 6.156 TFLOP/s | 12.73 |
| matmul | float32 | 2048x2048 | ok | 2571098.5 | 2248112 | 2776895.0 | 6.682 TFLOP/s | 17.1 |
| random | float32 | 1000000 | ok | 46765.5 | 45801 | 261990.0 | 79.659 GiB/s | 119.71 |
| random | float32 | 10000000 | ok | 157763.0 | 156232 | 311475.0 | 236.132 GiB/s | 250.97 |

- CuPy reference：可用（NVIDIA GeForce RTX 3060）。

### 未追平项说明

- 固定矩阵完整性：四个对比类别均按固定矩阵渲染，缺项会显示为 `missing`；本次 CPU 未追平 11 行，CUDA end-to-end 未追平 13 行，CUDA kernel-only 未追平 2 行，CuPy reference 未追平 6 行。
- CPU：`matmul float32` 仍是最大差距，当前实现是不依赖 BLAS/LAPACK 的纯 Uya contiguous fast path，不能与 NumPy/OpenBLAS 的成熟 GEMM 微内核直接追平；大数组 `add/mul` 仍是内存带宽与分配路径限制，`random float32 1e7` 已改为直接 f32 生成但仍低于 NumPy。
- CUDA end-to-end：小数据 `1e4` 和部分 `1e6` 行主要受 H2D、kernel launch、D2H 固定开销限制；同机 CuPy reference 的 `1e4` 行也低于 NumPy CPU，说明这类行不能用 kernel-only 吞吐冒充端到端追平。
- CUDA kernel-only：大多数固定矩阵行已超过 NumPy CPU；仍落后的 `sum float32/float64 1e4` 是小规模 reduction launch/同步开销，不代表大规模设备端吞吐。
