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
