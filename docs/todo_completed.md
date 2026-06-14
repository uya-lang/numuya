# Completed Todo

## Phase 0: 脚手架与测试基础

- [x] 可选创建 `Makefile`。
  - `make bootstrap-upm`
  - `make upm-install`
  - `make test-one TEST=src/numuya/_tests/test_shape.uya`
  - `make test`
  - `make check-one TEST=src/numuya/_tests/test_shape.uya`
  - `make verify-upm-consumer`
  - 验证：
    - `make bootstrap-upm && make upm-install && make test-one TEST=src/numuya/_tests/test_testing_helpers.uya && make test && make check-one TEST=src/numuya/_tests/test_testing_helpers.uya && make verify-upm-consumer`
    - 结果：通过；包内测试 1 个测试文件通过，外部 UPM consumer fixture check/run 通过。

## Phase 0: 脚手架与测试基础

- [x] 验证本地 Uya UPM 子命令可用。
  - 执行 `test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm`。
  - 执行 `../uya/bin/uya upm --help`。
  - 若主入口处于自举过渡状态，仅允许临时用 `../uya/bin/uya-upm-stage2` 跑 package-mode check/test；文档和 Makefile 仍以 `../uya/bin/uya` 为默认入口。
  - 验证：
    - `test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm`：通过，退出码 0。
    - `../uya/bin/uya upm --help`：通过，退出码 0，输出 Uya Package Manager help。

## NumUya TDD Todo / Phase 0: 脚手架与测试基础

- [x] 创建 UPM manifest `uya.toml`。
  - `[package].name = "numuya"`。
  - `[package].version = "0.1.0"`。
  - `[package].source-dir = "src/numuya"`。
  - 可选 `package.uya_min_version = "0.10.0"`。
  - 初始 `[dependencies]` 为空。
  - 验证：`python3 - <<'PY' ... PY` 解析 `uya.toml` 并断言 package/dependencies 字段，结果 `uya.toml OK`。

- [x] 创建目录结构：`src/numuya/`、`src/numuya/_tests/`、`tests/fixtures/`。
  - 添加 `src/numuya/errors.uya`、`src/numuya/testing.uya` 作为源码根占位。
  - 添加 `.gitkeep` 保留测试与 fixture 目录。
  - 验证：`../uya/bin/uya upm install --manifest-path uya.toml` 通过，退出码 0，并生成 `uya.lock`。

## Phase 0: 脚手架与测试基础

- [x] 创建目录结构：`src/numuya/`、`src/numuya/_tests/`、`tests/fixtures/`。
  - 验证命令：`ls -ld src/numuya src/numuya/_tests tests/fixtures`
  - 验证结果：通过，三个目录均存在。

## Phase 0: 脚手架与测试基础

- [x] 创建 `src/numuya/errors.uya`，只放 error 声明，不写业务逻辑。
  - 验证命令：`../uya/bin/uya check src/numuya/errors.uya --manifest-path uya.toml`
  - 验证结果：通过，checker 通过（未执行代码生成）。
  - 验证命令：`../uya/bin/uya upm install --manifest-path uya.toml`
  - 验证结果：通过，退出码 0。
## Phase 0: 脚手架与测试基础

- [x] 创建 `src/numuya/testing.uya`，写 `expect_close_f64`、`expect_eq_usize`、`expect_shape_eq` 的测试占位。
  - 验证：`../uya/bin/uya check src/numuya/testing.uya --manifest-path uya.toml` 通过。
  - 备注：`../uya/bin/uya check src/numuya --manifest-path uya.toml` 不能用于当前库目录验证；编译器要求目录中存在 `main`，返回“未找到包含 main 函数的文件”。

## Phase 0: 脚手架与测试基础

- [x] 新增 `src/numuya/_tests/test_testing_helpers.uya`。
  - 测试文件使用 `use testing.expect_close_f64;` 等 source-root 相对导入。
  - 先测试 `expect_close_f64(1.0, 1.0 + 1e-13, 1e-12)` 通过。
  - 测试明显不相等时返回错误。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_testing_helpers.uya --manifest-path uya.toml`，通过，2 个测试 OK。
  - 验证：`../uya/bin/uya check src/numuya/testing/testing.uya --manifest-path uya.toml`，通过，checker 通过。

## Phase 0: 脚手架与测试基础

- [x] 创建外部 UPM consumer fixture。
  - 目录：`tests/fixtures/upm_consumer/`。
  - fixture 自己有 `uya.toml`，`[package].source-dir = "src"`。
  - 该 fixture 的 `uya.toml` 声明 `numuya = { path = "../../.." }` 或等价相对路径。
  - fixture 代码使用 `use numuya.shape.Shape;` 和 `use numuya.creation.zeros_f64;`。
  - 运行 `../uya/bin/uya upm install --manifest-path tests/fixtures/upm_consumer/uya.toml`。
  - 运行 `../uya/bin/uya check tests/fixtures/upm_consumer/src/main.uya --manifest-path tests/fixtures/upm_consumer/uya.toml`。
  - 运行 `../uya/bin/uya test tests/fixtures/upm_consumer/src/main.uya --manifest-path tests/fixtures/upm_consumer/uya.toml`。
  - 验证：
    - `../uya/bin/uya upm install --manifest-path tests/fixtures/upm_consumer/uya.toml`：通过。
    - `../uya/bin/uya check tests/fixtures/upm_consumer/src/main.uya --manifest-path tests/fixtures/upm_consumer/uya.toml`：通过。
    - `../uya/bin/uya test tests/fixtures/upm_consumer/src/main.uya --manifest-path tests/fixtures/upm_consumer/uya.toml`：通过，1 个测试通过，0 个失败。
    - `../uya/bin/uya test src/numuya/_tests/test_testing_helpers.uya --manifest-path uya.toml`：通过，2 个测试 OK。

## Phase 0: 脚手架与测试基础

- [x] 验收：`src/numuya/_tests/test_testing_helpers.uya` 绿，外部 UPM consumer fixture 绿。
  - 验证：`make test-one TEST=src/numuya/_tests/test_testing_helpers.uya` 通过（2 tests passed）。
  - 验证：`make verify-upm-consumer` 通过（UPM install、consumer check、consumer run 均成功）。

## Phase 1: Shape、axis、size

- [x] 写 `src/numuya/_tests/test_shape.uya`。
  - 验证: `make test-one TEST=src/numuya/_tests/test_shape.uya` 通过，1 个测试 OK。
  - 验证: `make test` 通过，`test_shape.uya` 与 `test_testing_helpers.uya` 全部通过。
## Phase 1: Shape、axis、size

- [x] 实现 `src/numuya/shape.uya` 中的 `Shape`、`Strides`、`NUMUYA_MAX_DIMS`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_shape.uya` 通过（2 tests passed）。
  - 验证：`make test` 通过（当前 2 个测试文件均通过）。


## Phase 1: Shape、axis、size

- [x] TDD: `shape_scalar()`。
  - scalar rank 是 0。
  - scalar size 是 1。
  - 验证：`make test-one TEST=src/numuya/_tests/test_shape.uya` 通过（3 tests passed）。
  - 验证：`make test` 通过（test_shape 与 test_testing_helpers 均通过）。

## Phase 1: Shape、axis、size

- [x] TDD: `shape1/shape2/shape3`。
  - `shape2(2, 3)` rank 是 2，dims 为 `[2, 3]`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_shape.uya` 通过（4 tests passed）。
  - 验证：`make test` 通过（test_shape 与 test_testing_helpers 均通过）。

## Phase 1: Shape、axis、size

- [x] TDD: `shape_from_slice`。
  - rank 0 slice 创建 scalar。
  - rank 16 成功。
  - rank 17 返回 `NumuyaRankTooLarge`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_shape.uya`：通过，5 个 shape 测试 OK。
    - `make test`：通过，当前 2 个测试文件 OK。
# NumUya TDD Todo
## Phase 1: Shape、axis、size

- [x] TDD: `shape_size`。
  - `(2, 3, 4)` size 是 24。
  - `(0, 3)` size 是 0。
  - 溢出返回 `NumuyaShapeOverflow`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_shape.uya` 通过。
    - `make test` 通过。

## Phase 1: Shape、axis、size

- [x] TDD: `shape_eq`。
  - 相同 rank/dims 为 true。
  - rank 不同或 dims 不同为 false。
  - 验证：`make test-one TEST=src/numuya/_tests/test_shape.uya` 通过（7 tests passed）。
  - 验证：`make test` 通过（test_shape 与 test_testing_helpers 均通过）。

## Phase 1: Shape、axis、size

- [x] TDD: `normalize_axis`。
  - `normalize_axis(0, 3) == 0`。
  - `normalize_axis(-1, 3) == 2`。
  - `axis == 3` 或 `axis == -4` 返回 `NumuyaAxisOutOfBounds`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_shape.uya` 通过（8 tests passed）。
  - 验证：`make test` 通过（test_shape 8 tests passed；test_testing_helpers 2 tests passed）。

## Phase 1: Shape、axis、size

- [x] 验收：`src/numuya/_tests/test_shape.uya` 绿。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_shape.uya --manifest-path uya.toml` 通过（8 tests passed）。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_testing_helpers.uya --manifest-path uya.toml` 通过（2 tests passed）。

## Phase 2: Storage 与 Array handle

- [x] 写 `src/numuya/_tests/test_storage.uya`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_storage.uya` 通过（1 test passed）。
  - 验证：`make test` 通过（`test_shape` 8 tests passed；`test_storage` 1 test passed；`test_testing_helpers` 2 tests passed）。

## Phase 2: Storage 与 Array handle

- [x] 实现 `src/numuya/storage.uya`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_storage.uya`
  - 结果：通过；`Storage<f64>` 可初始化，`allocator`、`data`、`len`、`ref_count` 字段已暴露。
  - 验证：`make test`
  - 结果：通过；`test_shape`、`test_storage`、`test_testing_helpers` 全通过。
  - 验证：`make verify-upm-consumer`
  - 结果：通过；consumer fixture 的 `check` 与 `run` 均正常。

## Phase 2: Storage 与 Array handle

- [x] TDD: `storage_new<T>(allocator, len) !&Storage<T>`。
  - len 为 0 时允许成功。
  - len 为 3 时 data 非 null。
  - 初始 `ref_count == 1`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：通过。
    - `make test`：通过（`test_shape`、`test_storage`、`test_testing_helpers`）。

## Phase 2: Storage 与 Array handle

- [x] TDD: `storage_retain<T>`。
  - retain 后 ref_count 加 1。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：先失败，链接错误 `undefined reference to 'storage_retain_f64'`；实现后通过，3 个 storage 测试通过。
    - `make test`：通过（`test_shape` 8 tests passed；`test_storage` 3 tests passed；`test_testing_helpers` 2 tests passed）。

## Phase 2: Storage 与 Array handle

- [x] TDD: `storage_release<T>`。
  - release 非最后引用只减计数。
  - 最后引用释放 data/header。
  - 测试不要读取已释放内存，只检查计数路径和无崩溃。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：先失败，链接错误 `undefined reference to 'storage_release_f64'`；实现后通过，`test_storage` 4 tests passed。
    - `make test`：通过（`test_shape` 8 tests passed；`test_storage` 4 tests passed；`test_testing_helpers` 2 tests passed）。
## Phase 2: Storage 与 Array handle

- [x] 实现 `src/numuya/array.uya` 的 `Array<T>` 与 `ArrayFlags`。
  - 验证命令：`make check-one TEST=src/numuya/array.uya`
  - 结果：通过，package-mode checker 通过。
  - 验证命令：`make test`
  - 结果：通过，`test_shape`、`test_storage`、`test_testing_helpers` 全部通过；`test_shape` 仍有既存 const qualifier warning，但无新增失败。

## Phase 2: Storage 与 Array handle

- [x] TDD: `array_rank/array_size/array_shape`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：先失败，宿主工具链链接阶段报缺失 `array_rank_f64`、`array_size_f64`、`array_shape_f64`；实现后通过，`test_storage` 5 个测试通过。
    - `make test`：通过；`test_shape` 8 个测试通过，`test_storage` 5 个测试通过，`test_testing_helpers` 2 个测试通过。`test_shape` 仍有既存 `const` qualifier warning，无新增失败。

## Phase 2: Storage 与 Array handle

- [x] TDD: `array_is_c_contiguous`。
  - contiguous owner 为 true。
  - 手动构造 stride 不连续时为 false。
  - 验证：
    - `make upm-install`：通过。
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：首次失败，链接错误 `undefined reference to 'array_is_c_contiguous_f64'`。
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：通过，7 个测试全绿。
    - `make test`：通过，`test_shape`、`test_storage`、`test_testing_helpers` 全绿。

## Phase 2: Storage 与 Array handle

- [x] 验收：`src/numuya/_tests/test_storage.uya` 绿。
  - 验证：`make test-one TEST=src/numuya/_tests/test_storage.uya`
  - 结果：7/7 tests passed。
  - 验证：`make test`
  - 结果：`test_shape.uya` 8/8、`test_storage.uya` 7/7、`test_testing_helpers.uya` 2/2 全部通过。

## Phase 3: 创建数组与基础 get/set

- [x] 写 `src/numuya/_tests/test_array_creation.uya`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`
  - 结果：通过，1 个测试通过。
  - 验证：`make test`
  - 结果：通过，`test_array_creation.uya` 1/1、`test_shape.uya` 8/8、`test_storage.uya` 7/7、`test_testing_helpers.uya` 2/2 全绿；`test_shape.uya` 仍有既存 `const` qualifier warning，无新增失败。

## Phase 3: 创建数组与基础 get/set

- [x] 写 `src/numuya/_tests/test_indexing.uya`。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_indexing.uya`
  - 结果：按预期失败；新增索引 TDD 用例成功编译到宿主 C 阶段，并因 `set1_f64/get1_f64/set2_f64/get2_f64/get3_f64/getn_f64/setn_f64` 尚未实现而失败。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_storage.uya`
  - 结果：通过，7 tests passed。

## Phase 3: 创建数组与基础 get/set

- [x] 实现 `src/numuya/creation.uya`。
  - 实现 `creation.uya` 的 `f64` owner 创建路径，提供 `full_f64`、`zeros_f64`、`ones_f64` 与共享 shape/stride/flags helper。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_testing_helpers.uya`：通过
    - `make test-one TEST=src/numuya/_tests/test_shape.uya`：通过
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：通过
    - `make test-one TEST=src/numuya/_tests/test_array_creation.uya`：通过

## Phase 3: 创建数组与基础 get/set

- [x] 抽最小复现并修复 Uya C99 codegen：导出泛型 `!Array<T>` 时缺失 `Array<T>` / `Storage<T>` 完整特化定义。
  - 以 `empty<f64>(allocator, shape2(2, 3))` 为最小入口。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`。
  - 完成条件：`empty<T>` 的新增测试能编译运行，且不破坏现有 `full_f64` 行为。
  - 实际验证：
    - `make -C ../uya uya`：通过。
    - `make test-one TEST=src/numuya/_tests/test_array_creation.uya`：通过，3 个测试全部通过，覆盖 `empty<f64>` 与现有 `full_f64` 行为。
    - `make test-one TEST=src/numuya/_tests/test_shape.uya`：通过。
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`：通过。
    - `make test-one TEST=src/numuya/_tests/test_testing_helpers.uya`：通过。

## Phase 3: 创建数组与基础 get/set

- [x] TDD: `full<T>`。
  - `full_f64(shape2(2, 3), 7.5)` 六个元素都是 7.5。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_array_creation.uya`（先失败：`try full<f64>(...)` 报错“try 的操作数必须是错误联合类型 !T”）
    - `make test-one TEST=src/numuya/_tests/test_array_creation.uya`（通过，4/4 tests passed）
    - `make test`（在既有后续测试 `src/numuya/_tests/test_indexing.uya` 失败；链接错误 `set1_f64/get1_f64/set2_f64/get2_f64/getn_f64/setn_f64/get3_f64` 未定义，属后续 todo，非本任务回归）
    - `make test-one TEST=src/numuya/_tests/test_testing_helpers.uya`（通过，2/2 tests passed）
    - `make test-one TEST=src/numuya/_tests/test_shape.uya`（通过，8/8 tests passed）
    - `make test-one TEST=src/numuya/_tests/test_storage.uya`（通过，7/7 tests passed）
    - `make test-one TEST=src/numuya/_tests/test_array_creation.uya`（通过，4/4 tests passed）
## Phase 3: 创建数组与基础 get/set

- [x] TDD: `zeros_f64/ones_f64/full_f64`。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`
  - 结果：通过，4/4 tests passed；新增覆盖 `zeros_f64`、`ones_f64` 非空数组填充值，并补齐 `full_f64` 值断言。
  - 验证命令：`make test`
  - 结果：失败，现有 `src/numuya/_tests/test_indexing.uya` 仍缺少 `set1_f64/get1_f64/set2_f64/get2_f64/getn_f64/setn_f64/get3_f64` 实现，与本任务无关。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_shape.uya`
  - 结果：通过，8/8 tests passed。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_storage.uya`
  - 结果：通过，7/7 tests passed。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_testing_helpers.uya`
  - 结果：通过，2/2 tests passed。

## Phase 3: 创建数组与基础 get/set

- [x] TDD: `from_slice<T>`。
  - slice 长度等于 shape size 时成功并复制。
  - 长度不等返回 `NumuyaShapeMismatch`。
  - 修改源 slice 不影响 array。
  - 验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya` 通过（6 tests passed）。
  - 验证：`make test` 失败，`src/numuya/_tests/test_indexing.uya` 因 `set1_f64/get1_f64/set2_f64/get2_f64/setn_f64/getn_f64/get3_f64` 未实现导致宿主工具链链接失败；`test_array_creation` 已通过。

## Phase 3: 创建数组与基础 get/set

- [x] 实现 `src/numuya/indexing.uya`。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_indexing.uya`
  - 结果：通过，5 个 indexing 测试全部通过。
  - 验证命令：`make test`
  - 结果：通过，`test_array_creation`、`test_indexing`、`test_shape`、`test_storage`、`test_testing_helpers` 全绿。

## Phase 3: 创建数组与基础 get/set

- [x] TDD: `get1/get2/get3/getn`。
  - 正常读。
  - rank 不匹配返回 `NumuyaInvalidArgument`。
  - index 越界返回 `NumuyaIndexOutOfBounds`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_indexing.uya`（先失败：`get helpers reject bounds and rank mismatches`，因 `getn` rank mismatch 返回 `NumuyaShapeMismatch`）
    - `make test-one TEST=src/numuya/_tests/test_indexing.uya`（通过）
    - `make test`（通过；`test_array_creation`、`test_indexing` 与其余当前默认单测全绿）

## Phase 3: 创建数组与基础 get/set
- [x] TDD: `set1/set2/setn`。
  - 正常写后能读回。
  - 只读 array 返回 `NumuyaReadOnly`。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_indexing.uya`
      - 结果：通过，6 tests passed。
    - `make test`
      - 结果：通过，`test_array_creation` 6 tests、`test_indexing` 6 tests、`test_shape` 8 tests、`test_storage` 7 tests、`test_testing_helpers` 2 tests。
## Phase 3: 创建数组与基础 get/set

- [x] 验收：`test_array_creation`、`test_indexing` 绿。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`
  - 结果：通过，6/6 tests passed。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_indexing.uya`
  - 结果：通过，6/6 tests passed。
  - 回归命令：`make test`
  - 结果：通过，`test_array_creation`、`test_indexing`、`test_shape`、`test_storage`、`test_testing_helpers` 全绿。

## Phase 4: Stride、reshape、transpose、view

- [x] 写 `src/numuya/_tests/test_stride_views.uya`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`
  - 验证结果：测试文件已创建；checker 失败原因为 `模块不存在`（`use stride;` 引用的 `src/numuya/stride.uya` 尚未实现），属于预期的 TDD 先失败状态，待下一任务实现 `stride.uya` 后解决。

## Phase 4: Stride、reshape、transpose、view

- [x] 实现 `src/numuya/stride.uya`。
  - 验证命令：
    ```bash
    ../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml
    make test
    ```
  - 结果：`test_stride_views.uya` 10/10 通过；`make test` 全部 6 个测试文件均通过（39 个测试）。
  - 实现内容：`c_order_strides`、`physical_index`、`reshape`、`ravel`、`transpose`、`swapaxes`。
  - 附加改动：修复 `test_stride_views.uya` 的模块调用语法；重命名 `indexing.uya` 内部私有 `physical_index` 为 `compute_physical_index` 以避免与 `stride.physical_index` 命名冲突。
