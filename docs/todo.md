# NumUya TDD Todo

本文档列出未完成项和待优化项。已完成项见 `docs/completed.md`。

状态标记约定：
- `[ ]` 未开始
- `[~]` 进行中
- `[x]` 已完成（移至 completed.md）
- `[f]` 暂时失败，需要记录 blocker 和最小复现

通用命令：

```bash
test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm
../uya/bin/uya upm install --manifest-path uya.toml
../uya/bin/uya check src/numuya/_tests/test_shape.uya --manifest-path uya.toml
../uya/bin/uya test src/numuya/_tests/test_shape.uya --manifest-path uya.toml
```

完成一个阶段后，至少运行该阶段及之前所有测试。添加 Makefile 后改用 `make test`，但 Makefile 内部必须先确认 `../uya/bin/cmd/upm` 存在，再调用 `../uya/bin/uya ... --manifest-path uya.toml` 或等价 UPM/package-mode 命令。`--project-root src` 只允许用于编译器最小复现，不作为项目常规测试入口。

测试布局约定：

- NumUya 的默认 TDD 单测放在 `src/numuya/_tests/`，因为新版 package-mode 只会把 root source root 物化到临时 build root。
- 包内测试按 source-root 相对路径导入，例如 `use shape.Shape;`、`use creation.zeros_f64;`，不要依赖根包自别名 `numuya.*`。
- 外部 consumer fixture 才使用 `use numuya.*`，用于验证其他项目通过 UPM 使用 NumUya。
- `_tests`、`_tools`、`_benchmarks` 是内部模块，外部 consumer fixture 不得导入 `numuya._tests.*`、`numuya._tools.*` 或 `numuya._benchmarks.*`。

## 待优化项

- [x] SIMD `numuya_simd_*` 当前为标量循环占位，替换为 `@vector` 内建（依赖 Uya 编译器支持）
- [x] GPU axis reduction (`sum_axis/mean_axis/argmax`) 当前为 D2H→CPU→H2D fallback，需实现纯 GPU kernel
- [x] GPU sub/neg/div 无 strided/broadcast 路径（当前仅 contiguous），需扩展类似 add_f64_strided
- [x] sub/neg/div GPU ufunc 测试（当前仅编译通过，需添加 GPU 端测试）
- [x] Complex dtype（FFT 已切换为 `Array<Complex>` wrapper 存储）
- [x] `arange_f64` 支持 negative step（已补负步长与空区间测试）

## 每次提交前检查

- [x] CUDA kernel source-of-truth 是 PTX/Uya 生成资产；没有把必需实现藏在 `.cu`/`nvcc` 路径。
- [x] CUDA backend host 侧用纯 Uya 实现（`driver.uya`、`cublaslt.uya`、`cufft.uya`、`curand.uya`），通过 `dl_stub.c`（唯一 C helper）动态加载。所有 vendor stub C 文件已删除。
- [x] 没有硬编码只服务当前测试输入的分支。
- [x] 文档中的 public API 与实际实现一致。
