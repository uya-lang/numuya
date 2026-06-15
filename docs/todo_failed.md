# Failed Todo

暂无失败项。

## Phase 24: NumPy 兼容面扩展

- [f] `einsum` MVP。
  - 失败原因：batch matrix multiplication `bij,bjk->bik` 测试失败（ERROR），其余 7 个测试通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_einsum.uya --manifest-path uya.toml`
  - 关键错误：`TEST: einsum batch matrix multiplication bij,bjk->bik ... ERROR`
  - 相关文件：`src/numuya/einsum.uya`、`src/numuya/_tests/test_einsum.uya`、`src/numuya/_tests/test_einsum_debug.uya`
  - 后续重开条件：修复 batch 维度求和/索引逻辑或测试期望，重新运行全部 einsum 测试通过。
