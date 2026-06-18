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
- NumUya commit：`47580f8d5dd4ee3fc3fcd52b9083d96c3808fc74`
- 计时口径：CPU 与 `NumPy CPU baseline` 结论来自 wall-clock；`NumUya CUDA kernel-only` 只代表设备端 kernel 时间；当前 `CuPy` 未安装则不生成同机 GPU reference。
- 说明：NumPy 无 GPU backend，因此 GPU 主表只比较 `NumUya CUDA end-to-end` 与 `NumPy CPU baseline`；`NumUya CUDA kernel-only` 单列报告，不伪造 `NumPy GPU` 数据。

### 原始 JSON / 文本来源

- numpy_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numpy_cpu.json`
- gpu_reference_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/gpu_reference.json`
- numuya_cpu_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cpu.json`
- numuya_cuda_json: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_cuda.json`
- numuya_raw_text: `/media/winger/_dde_data/winger/uya/numuya/benchmarks/results/2026-06-18/numuya_raw.txt`

### CPU

| operation | dtype | shape | status | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | ok | 75556897.87 | missing | 0.02 |
| matmul | float64 | 512x512 | missing | missing | missing | missing |
| mul | float64 | 1000000 | ok | 76196413.84 | missing | 0.02 |
| random | float64 | 1000000 | missing | missing | missing | missing |
| sum | float64 | 1000000 | ok | 32349912.56 | missing | 0.01 |

### CUDA end-to-end

非同类设备对比，仅作端到端参考。

| operation | dtype | shape | status | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | 1629272.72 | missing | missing |
| add | float64 | 1000000 | ok | 1667101.35 | missing | 0.77 |
| matmul | float64 | 512x512 | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | 1620356.73 | missing | missing |
| sum | float64 | 1000000 | ok | 1638933.51 | missing | 0.24 |
| transfer_d2h | float64 | 1000000 | ok | 800946.87 | missing | missing |
| transfer_h2d | float64 | 1000000 | ok | 789471.94 | missing | missing |

### CUDA kernel-only

| operation | dtype | shape | status | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- |
| add | float32 | 1000000 | ok | 38853.91 | missing | missing |
| add | float64 | 1000000 | ok | 76682.54 | missing | 16.71 |
| matmul | float32 | 1024x1024 | ok | 1659206.4 | missing | missing |
| matmul | float32 | 2048x2048 | ok | 13482716.8 | missing | missing |
| matmul | float64 | 512x512 | missing | missing | missing | missing |
| matmul_vendor_tf32 | float32 | 2048x2048 | ok | 1470043.4 | missing | missing |
| mul | float64 | 1000000 | missing | missing | missing | missing |
| random | float32 | 1000000 | ok | 23116.87 | missing | missing |
| random | float64 | 1000000 | missing | missing | missing | missing |
| sum | float32 | 1000000 | ok | 29937.92 | missing | missing |
| sum | float64 | 1000000 | ok | 48514.7 | missing | 8.26 |

### CuPy reference

| operation | dtype | shape | status | ns_per_iter | throughput | speedup_vs_numpy_cpu |
| --- | --- | --- | --- | --- | --- | --- |
| add | float64 | 1000000 | missing | missing | missing | missing |
| matmul | float64 | 512x512 | missing | missing | missing | missing |
| mul | float64 | 1000000 | missing | missing | missing | missing |
| random | float64 | 1000000 | missing | missing | missing | missing |
| sum | float64 | 1000000 | missing | missing | missing | missing |

- CuPy reference：不可用（cupy not installed）。
