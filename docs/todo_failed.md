# Failed Todo

当前暂无未修复失败项。

## Phase 24: NumPy 兼容面扩展

- [x] `einsum` MVP。
  - 修复：`bij,bjk->bik` batch matrix multiplication 用例的 `b_data` 改为匹配 `shape3(2, 3, 2)` 的 row-major 布局，测试数据现在与注释和期望值一致。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_einsum.uya --manifest-path uya.toml` — 8/8 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_einsum_debug.uya --manifest-path uya.toml` — 1/1 通过；`make test` — 全部非 CUDA 测试通过。
  - 相关文件：`src/numuya/einsum.uya`、`src/numuya/_tests/test_einsum.uya`、`src/numuya/_tests/test_einsum_debug.uya`
