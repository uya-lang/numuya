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

- [ ] 固定第一版测试矩阵，避免反复改口径。
  - elementwise / reduction：`f32`、`f64`，长度至少覆盖 `1e4`、`1e6`、`1e7` 三档。
  - matmul：至少覆盖 `256x256`、`1024x1024`、`2048x2048`；CPU/GPU 使用相同 dtype 和 shape。
  - random fill：至少覆盖 `f32`、`1e6` 和 `1e7` 元素两档。
  - GPU 额外区分“小数据传输敏感”与“大数据算力敏感”两类 case。

- [ ] 增加正确性护栏，确保 benchmark 不是“跑得快但算错了”。
  - benchmark 前先跑 `make test`。
  - GPU benchmark 前先跑 `make test-cuda`；若要走 vendor 路径，再跑 `make test-cuda-vendor`。
  - Python 对照脚本对每个 workload 先做小尺寸 spot-check，比对 NumUya / NumPy / CuPy（如有）结果一致性。

- [ ] 固定原始结果与汇总产物位置。
  - 原始结果建议落到 `benchmarks/results/2026-06-18/` 这类按日期命名的目录。
  - 汇总文档建议新增 `docs/benchmarks/numpy_comparison.md`。
  - 汇总表至少包含：绝对耗时、吞吐/带宽、相对 NumPy CPU speedup、命令行、commit、运行日期、硬件/驱动/版本信息。
  - 若某项只有 NumUya CUDA 与 NumPy CPU，必须明确标注“非同类设备对比，仅作端到端参考”。

- [ ] 添加汇总报告生成任务。
  - 建议新增 `benchmarks/python/summarize_benchmarks.py`，读取 NumUya 与 Python 对照脚本输出的 JSON 结果。
  - 建议新增 `make bench-report` 目标，负责把原始结果汇总成 `Markdown + JSON summary`。
  - 汇总逻辑必须统一计算 speedup、带宽/吞吐单位、缺失项标记和环境信息，避免手工抄表。
  - 报告生成时必须显式区分 `CPU`、`CUDA end-to-end`、`CUDA kernel-only`、`CuPy reference`（如有）。
  - 若某个 workload 缺少对照组或运行失败，报告中必须保留该项并标注 `missing` / `failed`，不能静默跳过。

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
