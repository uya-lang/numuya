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
