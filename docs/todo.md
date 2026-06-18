# NumUya TDD Todo

本文档列出未完成项和待优化项。已完成项见 `docs/todo_completed.md`。

状态标记约定：
- `[ ]` 未开始
- `[~]` 进行中
- `[x]` 已完成（移至 `docs/todo_completed.md`）
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

## 每次提交前检查

- `make test` 已通过。
- 涉及 CUDA benchmark 时，`make test-cuda` 已通过；涉及 vendor 路径时，`make test-cuda-vendor` 已通过。
- 原始 benchmark 结果已落盘，并记录命令、commit、运行日期和版本信息。
- 汇总脚本已运行，生成结果可回放，不依赖手工编辑表格。
- 汇总文档明确区分 `CPU`、`CUDA end-to-end`、`CUDA kernel-only`、`CuPy reference`（如有）。
- 文档中已明确说明 NumPy 本身不运行在 GPU 上。
