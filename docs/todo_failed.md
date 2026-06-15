# Failed Todo

失败项已全部重新处理完成。

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: auto backend。
  - 显式 `cuda` 走 GPU。
  - `auto` 在 GPU 可用时走 GPU。
  - 显存不足或 GPU unavailable 时按设计返回错误或回退 CPU。
  - 修复结果：现有实现已覆盖 `BackendKind.Auto`、显式 `Cuda`、无 CUDA 回退 CPU、CUDA 可用时选择 GPU，以及 auto API 的 host-return 行为和 OOM 错误路径。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 23 tests passed。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_auto.uya --manifest-path uya.toml` — 6 tests passed。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_location_preserving.uya --manifest-path uya.toml` — 4 tests passed。

## Phase 23: CUDA linalg、random、benchmark

- [x] Benchmark: `sum_f32/sum_f64` throughput。
  - 修复结果：`gpu_sum_all_f32`/`gpu_sum_all_f64` 复用 `BackendState` reduction scratch，避免每次调用反复 `cudaMalloc/cudaFree`；`sum_all_f64` PTX 从单线程循环改为两阶段 shared-memory 归约。
  - 验证命令：
    - `make cuda-ptx-embed cuda-cubin-embed` — ptxas 与内嵌资源生成成功。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 23 tests passed。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_reductions.uya --manifest-path uya.toml` — 15 tests passed。
    - `../uya/bin/uya run src/numuya/_benchmarks/bench_cuda.uya --manifest-path uya.toml` — `sum_all_f32` 89.68 GiB/s，`sum_all_f64` 150.02 GiB/s。

## Phase 23: CUDA linalg、random、benchmark

- [x] Benchmark strict 阈值。
  - H2D/D2H pageable copy 各自 >= 6 GiB/s。
  - contiguous `add_f32` 有效内存带宽 >= 150 GiB/s。
  - contiguous `add_f64` 有效内存带宽 >= 100 GiB/s。
  - `sum_f32` 有效读带宽 >= 60 GiB/s。
  - pure kernel `matmul_f32` 1024x1024 >= 1.0 TFLOP/s。
  - vendor cuBLASLt + TF32 2048x2048 启用时 >= 6.0 TFLOP/s。
  - random fill f32 >= 40 GiB/s。
  - 修复结果：strict benchmark 现在汇总阈值结果并在失败时返回 1；benchmark 中 `matmul_f32`/`random_f32` 改为预分配输出后重复写入，避免把循环内分配计入 kernel/fill 吞吐。
  - 修复结果：pure `matmul_f32` 增加 16x64 aligned shared-memory tile 快路径，每个线程计算 4 个相邻列输出；非对齐尺寸仍回退 generic tile kernel。
  - 修复结果：cuBLASLt 路径将 NumUya row-major 矩阵表达为等价 column-major 转置乘法，使 TF32 vendor 路径使用 cuBLASLt 原生快路径。
  - 验证命令：
    - `make cuda-ptx-embed cuda-cubin-embed` — ptxas 与内嵌资源生成成功。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_linalg.uya --manifest-path uya.toml` — 10 tests passed。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_random.uya --manifest-path uya.toml` — 8 tests passed。
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_reductions.uya --manifest-path uya.toml` — 15 tests passed。
    - `../uya/bin/uya run src/numuya/_benchmarks/bench_cuda.uya --manifest-path uya.toml` — 返回 0；H2D 9.27 GB/s、D2H 9.12 GB/s、`add_f32` 256.77 GB/s、`add_f64` 300.75 GB/s、pure `matmul_f32` 1024x1024 1.22 TFLOP/s、cuBLASLt TF32 2048x2048 11.01 TFLOP/s、`sum_all_f32` 75.57 GB/s、`random_f32` 191.54 GB/s。
