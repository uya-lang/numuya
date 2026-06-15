# NumUya TDD Todo

本文档是实现顺序。每个条目都必须先写测试，确认失败，再实现。状态标记约定：

- `[ ]` 未开始
- `[~]` 进行中
- `[x]` 已完成
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

## Phase 3: 创建数组与基础 get/set

- 注：当前 Uya codegen 对导出泛型 `!Array<T>` 路径仍有实例化限制；后续 `empty<T>/full<T>/from_slice<T>` 先用失败测试锁定可行写法，必要时抽最小复现。

## Phase 10: Statistics

## Phase 19: SIMD 与性能

## Phase 22: CUDA ufunc 与 reduction


## Phase 23: CUDA linalg、random、benchmark

## Phase 24: NumPy 兼容面扩展



## 每次提交前检查

- [ ] CPU core 没有 runtime 依赖 Python/NumPy/BLAS/LAPACK/libm/C helper。
- [ ] CUDA backend 没有 Python/NumPy/PyTorch/C helper 依赖；CUDA Driver API 绑定和可选 cuBLAS/cuFFT/cuRAND backend 必须在文档与配置中显式开启。
- [ ] CUDA kernel source-of-truth 是 PTX/Uya 生成资产；没有把必需实现藏在 `.cu`/`nvcc` 路径。
- [ ] DeviceArray view/drop 路径经过 DeviceStorage refcount 测试。
- [ ] host-return `_auto` API 与 location-preserving `_on` API 都有测试。
- [ ] 没有硬编码只服务当前测试输入的分支。
- [ ] 文档中的 public API 与实际实现一致。
