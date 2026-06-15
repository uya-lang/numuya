# Failed Todo

当前正在重新处理失败项。

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

- [f] Benchmark strict 阈值。
  - H2D/D2H pageable copy 各自 >= 6 GiB/s。
  - contiguous `add_f32` 有效内存带宽 >= 150 GiB/s。
  - contiguous `add_f64` 有效内存带宽 >= 100 GiB/s。
  - `sum_f32` 有效读带宽 >= 60 GiB/s。
  - pure kernel `matmul_f32` 1024x1024 >= 1.0 TFLOP/s。
  - vendor cuBLASLt + TF32 2048x2048 启用时 >= 6.0 TFLOP/s。
  - random fill f32 >= 40 GiB/s。
  - 失败原因：strict benchmark 已补齐并能执行阈值检查，但当前 RTX 3060 实测 pure `matmul_f32` 1024x1024 约 0.40 TFLOP/s，低于 1.0 TFLOP/s；vendor cuBLASLt + TF32 2048x2048 约 2.88 TFLOP/s，低于 6.0 TFLOP/s。继续完成需要新的 matmul kernel/供应商路径优化或调整硬件/阈值。
  - 阻塞命令：`../uya/bin/uya run src/numuya/_benchmarks/bench_cuda.uya --manifest-path uya.toml` 返回 1。
  - 已验证：`make cuda-cubin-embed` 成功；`../uya/bin/uya test src/numuya/_tests/test_cuda_reductions.uya --manifest-path uya.toml` 15 tests passed；benchmark 中 H2D 9.23 GB/s、D2H 9.01 GB/s、add_f32 287.57 GB/s、add_f64 301.12 GB/s 均通过 strict 阈值。
  - 后续重开条件：实现 tiled/shared-memory pure matmul 或修正 cuBLASLt TF32 路径达到阈值后，重新运行 benchmark 并归档完成。
