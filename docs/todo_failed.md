# Failed Todo

当前没有失败项。

## Phase 22: CUDA ufunc 与 reduction

- [f] TDD: auto backend。
  - 显式 `cuda` 走 GPU。
  - `auto` 在 GPU 可用时走 GPU。
  - 显存不足或 GPU unavailable 时按设计返回错误或回退 CPU。
  - 失败记录：接手前已标记为 [f]，本轮为归档清理，未重新运行验证。失败根因与阻塞命令需参考先前轮次日志；当前可见障碍为 CUDA auto backend 依赖的 GPU 运行时/实现尚未就绪。后续重开条件：明确 auto backend 设计并具备可运行 CUDA 测试环境后，从本归档移回主 todo 重新执行 TDD。

## Phase 23: CUDA linalg、random、benchmark

- [f] Benchmark: `sum_f32/sum_f64` throughput。
  - 失败原因：前序轮次已标记为 `[f]`，本轮为归档清理；未在当前轮次保留可复现的失败日志与阻塞命令。
  - 关键错误：无新捕获日志。
  - 后续重开条件：重新实现 `sum_f32/sum_f64` throughput benchmark 并满足 Phase 23 strict 阈值（`sum_f32` 有效读带宽 >= 60 GiB/s）后，从失败归档移回主 todo 验证。

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
