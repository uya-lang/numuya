# Failed Todo

当前暂无未修复失败项。

## Phase 24: NumPy 兼容面扩展

- [f] `.npz` zip 容器。
  - [~] 在 `io_npy.uya` 新增 `save_npy_f64_to_buffer` / `load_npy_f64_from_buffer`，供 `.npz` 内部调用并通过测试。
  - [ ] 实现 `io_npz.uya`：ZIP STORED writer/reader，支持多个 f64 数组。
  - [ ] 编写 `test_io_npz.uya` 并验证 save/load roundtrip。

失败原因：本轮为归档清理轮，不启动/继续任务执行。该任务块此前处于 `[f]` 状态，含未完成的 `[~]` 子任务与未启动的 `[ ]` 子任务，整体移入失败归档待后续重开。
后续重开条件：重新从 Phase 24 的 `.npz` zip 容器任务开始，先完成 `io_npy.uya` 的 buffer 接口及测试，再实现 `io_npz.uya` 与 roundtrip 测试。
