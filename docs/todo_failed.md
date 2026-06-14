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

- [f] TDD: `empty<T>`。
  - shape 正确。
  - size 正确。
  - contiguous flags 正确。
  - 不读取元素值。
  - 阻塞命令：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`
  - 失败原因：Uya C99 codegen 在导出泛型 `!Array<T>` 的 `empty<f64>` 实例化路径上生成了未特化的 `err_union_Array_T`，并漏发 `Storage_f64` 完整定义，导致宿主 C 编译失败。
  - 关键错误：`/tmp/uya_output_521760.c:717:62: error: field 'value' has incomplete type`
  - 关键错误：`/tmp/uya_output_521760.c:1656:24: error: array type has incomplete element type 'struct Storage_f64'`
  - 尝试记录：先加 `empty<f64>` 失败测试，再分别尝试 `export fn empty<T>(...) !Array<T>` 直接构造和内联分配 `Storage<T>` 的规避写法，均在 codegen 后的宿主 C 编译阶段失败。
  - 回滚验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya` 通过；`make test` 仍因既有 `test_indexing.uya` 缺少 `set1_f64/get1_f64/...` 实现而失败，与本任务无关。
  - 重开条件：修复或规避 Uya C99 codegen，使导出泛型 `!Array<T>` 至少能为 `empty<f64>` 生成完整的 `Array_f64`、`Storage_f64` 和对应错误联合特化。

## Phase 10: Statistics

- [f] 写 `src/numuya/_tests/test_stats.uya`。
  - 失败原因：先前执行轮次中已将本任务标为 `[f]`，但本轮为归档清理轮，未在 workspace 中找到原始失败日志（`loop.log` 不存在）；`src/numuya/_tests/test_stats.uya` 文件也尚未创建。
  - 阻塞命令：无保留。
  - 关键错误：无保留。
  - 后续重开条件：重新评估 `test_stats.uya` 的最小测试集合（`var_all_f64`、`std_all_f64`、`percentile_f64` 等）与当前 Uya 编译器/包模式的兼容性，先尝试创建最小复现并记录具体编译/运行错误后再执行。

## Phase 22: CUDA ufunc 与 reduction

- [f] 创建 PTX source-of-truth。
  - `src/numuya/cuda/ptx/core_sm86.ptx`。
  - `src/numuya/cuda/kernels_ptx.uya` 由 `src/numuya/_tools/embed_ptx.uya` 生成。
  - 不创建必需 `.cu` 源，不把 `nvcc` 放进 TDD 主路径。
  - 失败原因：归档清理时该任务仍处于 `[f]` 状态；PTX source-of-truth 的生成/嵌入流程尚未落地，`src/numuya/_tools/embed_ptx.uya`、`src/numuya/cuda/kernels_ptx.uya` 与 `src/numuya/cuda/ptx/core_sm86.ptx` 均未实现或验证。
  - 阻塞命令/条件：无可用 `make cuda-ptx-embed` 等价命令，`ptxas -arch=sm_86` 未纳入 TDD 主路径。
  - 后续重开条件：先实现 `embed_ptx.uya` 生成 `kernels_ptx.uya`，提供稳定可重复的 PTX 文本嵌入，并验证 `sm_86` 加载/JIT fallback 可用。

## Phase 22: CUDA ufunc 与 reduction

- [f] TDD: 加载 embedded PTX/cubin。
  - `sm_86` 优先。
  - PTX JIT fallback 可用。

  失败原因：遗留失败项。CUDA 嵌入式 PTX/cubin 加载尚未完成，缺少可在当前环境中验证的加载路径与设备无关测试；PTX/cubin 嵌入格式、驱动加载顺序以及 `sm_86` JIT fallback 需要在后续重开时补充实现与测试。
  阻塞命令：无（本轮为归档清理，未执行新验证命令）。
  后续重开条件：实现 `src/numuya/cuda/` 下嵌入式 PTX/cubin 加载 API，编写 `src/numuya/_tests/test_cuda_module.uya` 中加载失败/成功测试，并确保 `../uya/bin/uya test ...` 通过。

