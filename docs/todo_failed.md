# Failed Todo

当前暂无未修复失败项。

## Phase 24: NumPy 兼容面扩展

- [x] `.npz` zip 容器。
  - [x] 在 `io_npy.uya` 新增 `save_npy_f64_to_buffer` / `load_npy_f64_from_buffer`，供 `.npz` 内部调用并通过测试。
  - [x] 实现 `io_npz.uya`：ZIP STORED writer/reader，支持多个 f64 数组。
  - [x] 编写 `test_io_npz.uya` 并验证 save/load roundtrip。

修复结果：已完成 `io_npy.uya` 的 f64 buffer API、`io_npz.uya` 的 ZIP STORED writer/reader，以及 `test_io_npz.uya` 的多数组 save/load roundtrip 覆盖。
验证命令：
- `../uya/bin/uya check src/numuya/_tests/test_io_npz.uya --manifest-path uya.toml`
- `../uya/bin/uya test src/numuya/_tests/test_io_npz.uya --manifest-path uya.toml`
- `../uya/bin/uya test src/numuya/_tests/test_io_npy.uya --manifest-path uya.toml`
- `make test`
