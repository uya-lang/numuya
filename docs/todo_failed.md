# Failed Todo

## Phase 0: 脚手架与测试基础

- [x] 验证外部项目通过 `upm add` 使用 NumUya。
  - 在临时目录执行 `../uya/bin/uya upm init --src-layout consumer_smoke` 或等价初始化。
  - 执行 `../uya/bin/uya upm add numuya --path <numuya_repo> --manifest-path <tmp>/consumer_smoke/uya.toml`。
  - consumer 源码只写 `use numuya.*`，不设置 `UYA_ROOT`，不传 `--project-root`。
  - `../uya/bin/uya upm install --manifest-path <tmp>/consumer_smoke/uya.toml` 和 `../uya/bin/uya test <tmp>/consumer_smoke/src/main.uya --manifest-path <tmp>/consumer_smoke/uya.toml` 成功。
  - 修复：上游 Uya 已支持 `use <module>.*;`，parser 接受通配符导入，checker 将其展开为模块导出项导入。
  - 验证：
    - `./bin/uya test tests/test_use_wildcard_module_path.uya` 通过。
    - `./bin/uya test tests/test_use_directory_module_path.uya && ./bin/uya test tests/test_use_file_module_path.uya && ./bin/uya test tests/test_std_mem_directory_module_alias.uya` 通过。
    - `make test` 通过。
    - `make verify-upm-consumer` 通过。
    - 临时 UPM consumer 使用 `use numuya.*;` 通过；额外验证 `return zeros_f64();` 也通过。
## Phase 3: 创建数组与基础 get/set

- [x] TDD: `empty<T>`。
  - shape 正确。
  - size 正确。
  - contiguous flags 正确。
  - 不读取元素值。
  - 修复状态：当前 `creation.empty<T>`、`full<T>`、`from_slice<T>` 已能实例化 `Array<f64>`/`Storage<f64>`，旧的 C99 codegen blocker 未复现。
  - 验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya` 通过。

## Phase 10: Statistics

- [x] 写 `src/numuya/_tests/test_stats.uya`。
  - 覆盖：`var_all_f64`、`std_all_f64`、`percentile_f64` 的正常路径、空数组/非法参数，以及 non-contiguous transpose view。
  - 验证：`make test-one TEST=src/numuya/_tests/test_stats.uya` 通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] 创建 PTX source-of-truth。
  - `src/numuya/cuda/ptx/core_sm86.ptx`。
  - `src/numuya/cuda/kernels_ptx.uya` 由 `src/numuya/_tools/embed_ptx.uya` 生成。
  - 不创建必需 `.cu` 源，不把 `nvcc` 放进 TDD 主路径。
  - 修复：`embed_ptx.uya` 生成稳定的 PTX byte array，并追加 PTX 字符串加载所需的 trailing null byte。
  - 验证：
    - `make cuda-ptx-embed` 通过。
    - `make cuda-ptx-validate` 通过。
    - `make test-one TEST=src/numuya/_tests/test_ptx_embed.uya` 通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: 加载 embedded PTX/cubin。
  - `sm_86` 优先。
  - PTX JIT fallback 可用。
  - 修复：`cuda_kernels_load` 优先尝试 embedded sm_86 cubin cache，失败或缺失时回退到 embedded PTX；`cuda.module` 新增 `cuda_module_load_data`，底层 Driver shim 统一走 `cuModuleLoadData`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_cuda_module.uya` 通过。
