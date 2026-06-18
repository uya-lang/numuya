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

- 当前无未完成项；已完成项已移至 `docs/completed.md`。

## 每次提交前检查

- 当前无待确认项；已完成检查已移至 `docs/completed.md`。
