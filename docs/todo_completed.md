# Completed Todo

## Phase 7: UFunc 基础

- [x] 验收：`src/numuya/_tests/test_ufunc.uya` 绿，并回跑 `broadcast`、`stride_views`。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml`（17/17 通过）
    - `../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`（7/7 通过）
    - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`（13/13 通过）

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

## NumUya TDD Todo / Phase 4: Stride、reshape、transpose、view

- [x] TDD: `c_order_strides(shape)`。
  - `(2, 3, 4)` strides 是 `[12, 4, 1]`。
  - scalar strides rank 为 0。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` 10/10 通过。

## Phase 4: Stride、reshape、transpose、view

- [x] TDD: `physical_index(shape, strides, offset, indices)`.
  - `(2, 3)` C-order 下 `(1, 2)` 物理 index 是 5。
  - 验证：
    - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`
    - 结果：通过；`physical_index computes row-major offset for rank-2 shape` OK，返回 index 5。

## NumUya TDD Todo / Phase 4: Stride、reshape、transpose、view

- [x] TDD: `reshape`.
  - `(2, 3)` reshape 到 `(3, 2)` 不复制，storage ref_count 增加。
  - size 不同返回 `NumuyaShapeMismatch`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` 通过（10/10 tests passed），其中 `reshape returns a view sharing storage when total size matches` 与 `reshape rejects mismatched total size` 覆盖上述两点。
  - 回归：`../uya/bin/uya test src/numuya/_tests/test_shape.uya --manifest-path uya.toml`、`test_array_creation.uya`、`test_storage.uya`、`test_indexing.uya`、`test_stride_views.uya` 均通过。

## Phase 4: Stride、reshape、transpose、view

- [x] TDD: `ravel`.
  - contiguous 返回 shape `(size,)` view。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` 通过（`ravel returns a rank-1 view of a contiguous array` 等 10 个测试全绿）。
  - 说明：实现已在 `src/numuya/stride.uya` 中提供，`ravel<T>` 对 contiguous 数组返回 shape `(size,)` 的 view；本轮主要完成验证与状态归档。

## Phase 4: Stride、reshape、transpose、view

- [x] TDD: `transpose`.
  - `(2, 3)` transpose 得 `(3, 2)`。
  - 读转置 view 的 `(2, 1)` 等于原 `(1, 2)`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`
  - 结果：通过，10/10 tests passed；其中 `transpose reverses dimensions and maps indices` 覆盖 shape 反转与索引映射，`writing through a transpose view updates the owner` 覆盖 view 写入回写 owner。
  - 说明：实现已存在于 `src/numuya/stride.uya` 的 `transpose<T>`，测试已存在于 `src/numuya/_tests/test_stride_views.uya`；本回合主要完成验证与状态归档。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_array_creation.uya --manifest-path uya.toml`、`test_indexing.uya`、`test_shape.uya`、`test_storage.uya`、`test_stride_views.uya` 均通过。

## Phase 4: Stride、reshape、transpose、view

- [x] TDD: `swapaxes`.
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`
  - 结果：`test_stride_views.uya` 13 个测试全部通过，其中 swapaxes 相关测试包括：
    - `swapaxes exchanges two axes`
    - `swapaxes rejects out-of-bounds axes`
    - `swapaxes supports negative axes`
    - `writing through a swapaxes view updates the owner`
    - `swapaxes with identical axes is a no-op view`
  - 更广泛验证：`make test` 通过全部 5 个测试文件（test_array_creation、test_indexing、test_shape、test_storage、test_stride_views、test_testing_helpers），共 42 个测试。

## NumUya TDD Todo / Phase 4: Stride、reshape、transpose、view

- [x] TDD: view 写入。
  - 通过 transpose view set 后，owner 对应元素变化。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` 通过，13 个测试全部通过（含 `writing through a transpose view updates the owner` 与 `writing through a swapaxes view updates the owner`）。
  - 验证：`make test` 通过，当前 6 个测试文件（test_array_creation、test_indexing、test_shape、test_storage、test_stride_views、test_testing_helpers）全部通过，无失败。

## Phase 4: Stride、reshape、transpose、view

- [x] 验收：`src/numuya/_tests/test_stride_views.uya` 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml`
  - 结果：通过，13 个测试全部 OK。
  - 验证命令：`make test`
  - 结果：通过，当前所有 6 个测试文件（test_array_creation.uya、test_indexing.uya、test_shape.uya、test_storage.uya、test_stride_views.uya、test_testing_helpers.uya）全部通过。

## Phase 5: Slicing

- [x] 写 `src/numuya/_tests/test_slicing.uya`。
  验证命令：
  - `../uya/bin/uya check src/numuya/_tests/test_slicing.uya --manifest-path uya.toml`
  - `../uya/bin/uya test src/numuya/_tests/test_slicing.uya --manifest-path uya.toml`
  结果：
  - 新测试文件编译失败，原因是 `indexing.uya` 尚未导出 `SliceSpec` 与 `slice_axis`，符合 TDD 先写失败测试的预期。
  - 失败信息（摘要）：`try 的操作数必须是错误联合类型 !T`（调用 `slice_axis` 处）。
  - 回归测试全部通过：`test_shape.uya`、`test_storage.uya`、`test_array_creation.uya`、`test_indexing.uya`、`test_stride_views.uya`、`test_testing_helpers.uya`。

## Phase 5: Slicing

- [x] 实现 `SliceSpec`。
  - [x] 重构 `Strides` 以支持负 stride（与设计文档 `steps: [isize]` 对齐）。
    - 修改 `src/numuya/shape.uya`：`Strides.steps` 从 `[usize]` 改为 `[isize]`。
    - 同步更新 `src/numuya/array.uya`、`src/numuya/creation.uya`、`src/numuya/stride.uya`、`src/numuya/indexing.uya` 及所有相关测试中的 `.strides` 引用为 `.steps`，并使用带符号算术计算物理索引。
  - [x] 创建 `src/numuya/slicing.uya`，实现 `SliceSpec` 与 `slice_axis`。  
    - `SliceSpec { start: isize, stop: isize, step: isize }`。
    - `slice_axis<T>(a: &Array<T>, axis: isize, spec: SliceSpec) !Array<T>`：按 Python/NumPy 语义对指定轴切片，返回共享 storage 的 view；支持正/负 step、负 start/stop、空切片、step 为 0 错误、axis 越界错误。
  - [x] TDD: `slice_axis`。
    - `0:3:1`。
    - `1:5:2`。
    - 负 start/stop。
    - 负 step reverse。
    - 空 slice。
- [x] TDD: slice 返回 view。
  - storage ref_count 增加。
  - view 写入反映到 owner。
- [x] TDD: invalid slice。
  - step 为 0 返回 `NumuyaInvalidArgument`。
  - axis 越界返回 `NumuyaAxisOutOfBounds`。
- [x] 验收：`src/numuya/_tests/test_slicing.uya` 绿。
  验证命令：
  - `../uya/bin/uya test src/numuya/_tests/test_slicing.uya --manifest-path uya.toml`
  - `for f in src/numuya/_tests/test_*.uya; do ../uya/bin/uya test "$f" --manifest-path uya.toml; done`
  结果：
  - `test_slicing.uya` 通过，10 个测试全部 OK。
  - 回归测试全部通过：`test_array_creation.uya`（6 个）、`test_indexing.uya`（6 个）、`test_shape.uya`（8 个）、`test_storage.uya`（7 个）、`test_stride_views.uya`（13 个）、`test_testing_helpers.uya`（2 个）。

## Phase 6: Broadcasting

- [x] 写 `src/numuya/_tests/test_broadcast.uya`。
  - 覆盖 `broadcast_shapes`：对齐尾部维度、size-1 匹配更大维度、不兼容返回 `NumuyaBroadcastError`。
  - 覆盖 `broadcast_to`：rank 扩展产生 stride 0、前导 size-1 产生 stride 0、不兼容返回 `NumuyaBroadcastError`。
  - 覆盖 broadcast view 默认只读：`flags.writeable` 为 false，`set` 返回 `NumuyaReadOnly`。
  - 验证命令：
    - `../uya/bin/uya check src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`（临时 stub `src/numuya/broadcast.uya`）
  - 结果：checker 通过，测试文件类型与语义正确。
  - 当前 TDD 状态：移除 stub 后同一命令失败，因 `src/numuya/broadcast.uya` 尚未实现；符合预期，等待下一轮实现。

## Phase 6: Broadcasting

- [x] 实现 `src/numuya/broadcast.uya`。
  - 新增 `src/numuya/errors.uya` 导出 `NumuyaBroadcastError`。
  - 实现 `broadcast_shapes(left, right) !Shape`：从右侧对齐维度，相等或 size-1 可广播，否则返回 `NumuyaBroadcastError`。
  - 实现 `broadcast_to<T>(array, target_shape) !Array<T>`：按 NumPy 语义在左侧补 size-1 轴，对应 stride 置 0；返回 view 的 `flags.writeable` 为 false。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`
  - 验证结果：通过，7/7 tests passed。
- [x] TDD: `broadcast_shapes`.
  - `(3,)` 与 `(2, 3)` -> `(2, 3)`。
  - `(4, 1, 3)` 与 `(1, 5, 3)` -> `(4, 5, 3)`。
  - `(2,)` 与 `(3,)` 返回 `NumuyaBroadcastError`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`
  - 验证结果：通过，覆盖上述 3 个用例。
- [x] TDD: `broadcast_to`.
  - `(3,)` broadcast 到 `(2, 3)`，新 axis stride 为 0。
  - `(1, 3)` 到 `(2, 3)`，第一轴 stride 为 0。
  - 不兼容返回 `NumuyaBroadcastError`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`
  - 验证结果：通过，覆盖上述 3 个用例。
- [x] TDD: broadcast view 默认只读或写保护。
  - 如果设置只读，`set` 返回 `NumuyaReadOnly`。
  - 如果允许写入，必须证明 stride 0 写入语义清楚；第一版推荐只读。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`
  - 验证结果：通过，`broadcast view is read-only by default` OK。
- [x] 验收：`src/numuya/_tests/test_broadcast.uya` 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml`
  - 验证结果：通过，7/7 tests passed。
  - 回归命令：`make test`
  - 回归结果：通过，当前所有 7 个测试文件（test_array_creation.uya、test_broadcast.uya、test_indexing.uya、test_shape.uya、test_slicing.uya、test_storage.uya、test_stride_views.uya、test_testing_helpers.uya）全部通过。

## Phase 7: UFunc 基础

- [x] 写 `src/numuya/_tests/test_ufunc.uya`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml`
  - 结果：类型检查失败，因为 `src/numuya/ufunc.uya` 尚未实现，`add_f64/sub_f64/mul_f64/div_f64/neg_f64/add_i32` 未定义；符合 TDD 先写测试再实现的预期失败。
  - 相关既有测试回跑通过：`test_shape.uya`、`test_array_creation.uya`、`test_broadcast.uya`、`test_stride_views.uya`。

## Phase 7: UFunc 基础

- [x] 实现 `src/numuya/ufunc.uya`。
  验证：
  - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` → 11/11 通过
  - `../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml` → 7/7 通过
  - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` → 13/13 通过
  说明：实现了 `add_f64/sub_f64/mul_f64/div_f64/neg_f64/add_i32`，支持同 shape、broadcast 与非连续输入；为绕过当前 Uya C 后端对 `return local Array<T>` 的生成错误，返回前显式 `storage_retain` 并以结构体字面量返回；`test_ufunc.uya` 中 `add_i32` 测试的比较写法因类型检查问题调整为先赋值到 `i32` 局部变量再比较。

## Phase 7: UFunc 基础

- [x] 实现 `src/numuya/ufunc.uya`。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya`
    - `../uya/bin/uya test src/numuya/_tests/test_broadcast.uya`
    - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya`
  - 验证结果：全部通过。
    - `test_ufunc.uya`：11/11 tests passed。
    - `test_broadcast.uya`：7/7 tests passed。
    - `test_stride_views.uya`：13/13 tests passed。
  - 备注：编译 `test_ufunc.uya` 时 storage 模块有一个既有的 C 指针类型警告（`assignment to 'int32_t *' from incompatible pointer type 'double *'`），不影响测试通过。

## Phase 7: UFunc 基础

- [x] TDD: `add_f64/sub_f64/mul_f64/div_f64`。
  - 同 shape。
  - broadcast shape。
  - scalar array 与 vector。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` → 11/11 passed
    - `../uya/bin/uya test src/numuya/_tests/test_broadcast.uya --manifest-path uya.toml` → 7/7 passed
    - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` → 13/13 passed

## Phase 7: UFunc 基础

- [x] TDD: `neg_f64`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml`
  - 结果：11 tests passed, 0 failed；包含 `neg_f64 negates each element` 通过。

## Phase 7: UFunc 基础

- [x] TDD: `neg_f64`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml`
  - 结果：`neg_f64 negates each element` 通过；整份 `test_ufunc.uya` 11/11 测试通过，0 失败。

## NumUya TDD Todo / Phase 7: UFunc 基础

- [x] TDD: `add_i32`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` 通过；`make test` 全部通过。

## Phase 7: UFunc 基础

- [x] TDD: non-contiguous input。
  - transpose view 输入仍能正确运算。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml`
    - 11 tests passed, `add_f64 handles non-contiguous transpose input` OK。

## Phase 7: UFunc 基础

- [x] TDD: output 是新 owner。
  - 修改 output 不影响 input。
  - 验证：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` 通过 16 个测试，包括 add_f64/sub_f64/mul_f64/div_f64/neg_f64/add_i32 的 output owner 独立性与修改隔离测试。
    - 回跑 `test_broadcast.uya`（7 测）、`test_stride_views.uya`（13 测）、`test_slicing.uya`（10 测）、`test_indexing.uya`（6 测）、`test_array_creation.uya`（6 测）均通过。

## Phase 7: UFunc 基础

- [x] TDD: output 是新 owner。
  - 修改 output 不影响 input。
  - 验证：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` 通过 16 个测试，包括 add_f64/sub_f64/mul_f64/div_f64/neg_f64/add_i32 的 output owner 独立性与修改隔离测试。
    - 回跑 `test_broadcast.uya`（7 测）、`test_stride_views.uya`（13 测）、`test_slicing.uya`（10 测）、`test_indexing.uya`（6 测）、`test_array_creation.uya`（6 测）均通过。

## Phase 7: UFunc 基础

- [x] 内部重构：提取 contiguous fast path 与 generic stride path。
  验证：
  - `make test-one TEST=src/numuya/_tests/test_ufunc.uya` → 17/17 通过
  - `make test-one TEST=src/numuya/_tests/test_broadcast.uya` → 7/7 通过
  - `make test-one TEST=src/numuya/_tests/test_stride_views.uya` → 13/13 通过
  - `make test` → 全部通过，0 失败


## NumUya TDD Todo / Phase 8: Reductions

- [x] 写 `src/numuya/_tests/test_reductions.uya`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`
  - 验证结果：测试文件已创建；checker 失败原因为 `reductions.uya` 尚未实现，`sum_all_f64/prod_all_f64/min_all_f64/max_all_f64/mean_all_f64/sum_axis_f64/mean_axis_f64/argmax_axis_f64` 等函数未定义，符合 TDD 先写失败测试的预期。
  - 回归验证：
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` → 17/17 通过
    - `../uya/bin/uya test src/numuya/_tests/test_stride_views.uya --manifest-path uya.toml` → 13/13 通过
    - `../uya/bin/uya test src/numuya/_tests/test_array_creation.uya --manifest-path uya.toml` → 6/6 通过

## NumUya TDD Todo / Phase 8: Reductions

- [x] 实现 `src/numuya/reductions.uya`。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`（20/20 通过）
    - `make test`（所有既有测试文件通过）

## NumUya TDD Todo / Phase 8: Reductions

- [x] 实现 `src/numuya/reductions.uya`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`
  - 验证结果：20/20 通过。
  - 回归命令：`make test`
  - 回归结果：全部既有测试文件通过（test_array_creation 6、test_broadcast 7、test_indexing 6、test_reductions 20、test_shape 8、test_slicing 10、test_storage 7、test_stride_views 13、test_testing_helpers 2、test_ufunc 17）。

## Phase 8: Reductions

- [x] TDD: `sum_all_f64/prod_all_f64`。
  - 普通数组。
  - 空数组。
  - non-contiguous view。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`
  - 结果：20/20 通过，包含 `sum_all_f64` 普通数组、空数组、non-contiguous transpose view 及 `prod_all_f64` 对应三项。

## Phase 8: Reductions

- [x] TDD: `min_all_f64/max_all_f64`。
  - 普通数组。
  - 空数组返回 `NumuyaInvalidArgument`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`
  - 验证结果：20/20 通过，其中 `min_all_f64 finds the smallest element`、`min_all_f64 rejects an empty array`、`max_all_f64 finds the largest element`、`max_all_f64 rejects an empty array` 均通过。

## Phase 8: Reductions

- [x] TDD: `mean_all_f64`。
  - 普通数组。
  - 空数组返回 `NumuyaInvalidArgument`。

验证命令：
```bash
test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm
../uya/bin/uya upm install --manifest-path uya.toml
../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml
```

验证结果：20/20 测试通过；其中 `mean_all_f64 computes the arithmetic mean` 与 `mean_all_f64 rejects an empty array` 均通过。

## NumUya TDD Todo / Phase 8: Reductions

- [x] TDD: `sum_axis_f64`。
  - axis 0、axis 1。
  - negative axis。
  - keepdims true/false。
  - 验证：
    - `../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`
    - 结果：20/20 测试通过，其中 `sum_axis_f64 reduces along axis 0`、`sum_axis_f64 reduces along axis 1`、`sum_axis_f64 supports negative axis`、`sum_axis_f64 keepdims preserves reduced axes` 均通过。

## Phase 8: Reductions

- [x] TDD: `mean_axis_f64`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya`
  - 结果：20 个测试全部通过，包含 `mean_axis_f64` 沿 axis 0 和 keepdims 两个测试。

# NumUya TDD Todo
## Phase 8: Reductions

- [x] TDD: `argmax_axis_f64`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml`（23/23 通过）、`make test`（全部通过）。
  - 实现/测试变更：在 `src/numuya/_tests/test_reductions.uya` 补充 `argmax_axis_f64` 的负轴、`keepdims` 和零长度规约轴错误测试；在 `src/numuya/reductions.uya` 的 `argmax_axis_f64` 中增加 `axis_dim == 0` 时返回 `NumuyaInvalidArgument`。
