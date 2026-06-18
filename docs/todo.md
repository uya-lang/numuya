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

### Phase 24: NumPy 性能对比（CPU / GPU）

目标：给出一份可复现、口径统一的 NumUya vs NumPy 性能对比，并把 CPU 与 GPU 路径分开汇报。

说明：

- CPU 对比口径是 `NumUya CPU/SIMD` vs `NumPy CPU`。
- NumPy 本身没有 GPU backend，因此“GPU 对比”必须拆成两层：
  - `NumUya CUDA end-to-end`（H2D + kernel + D2H）vs `NumPy CPU baseline`。
  - `NumUya CUDA kernel-only` 单独报告，不伪造“NumPy GPU”数据。
- 如环境允许，可额外记录 `CuPy` 作为同机 GPU reference，但必须单列展示，不能替代 NumPy baseline。

- [ ] 生成第一版 CPU / GPU 对比报告。
  - CPU 段落：先给 `NumUya CPU/SIMD` vs `NumPy CPU`。
  - GPU 段落：先给 `NumUya CUDA end-to-end` vs `NumPy CPU`，再单列 `NumUya CUDA kernel-only`。
  - 若 `CuPy` 可用，再附一张 `NumUya CUDA` vs `CuPy` 的同机 GPU 横向表，但和 NumPy 主表分开。
  - 明确写出哪些结论来自 wall-clock，哪些来自 kernel/event 计时。

- [ ] 验收：本机能稳定复现一版对比结果。
  - `make bench`、Python 对照脚本、汇总脚本都能独立运行。
  - `docs/benchmarks/numpy_comparison.md` 同时包含 CPU 与 GPU 两部分。
  - 每个数字都能追溯到原始 JSON/文本输出。
  - 文档中明确写出 NumPy 无 GPU backend，避免读者误解。

## 每次提交前检查

- `make test` 已通过。
- 涉及 CUDA benchmark 时，`make test-cuda` 已通过；涉及 vendor 路径时，`make test-cuda-vendor` 已通过。
- 原始 benchmark 结果已落盘，并记录命令、commit、运行日期和版本信息。
- 汇总脚本已运行，生成结果可回放，不依赖手工编辑表格。
- 汇总文档明确区分 `CPU`、`CUDA end-to-end`、`CUDA kernel-only`、`CuPy reference`（如有）。
- 文档中已明确说明 NumPy 本身不运行在 GPU 上。
