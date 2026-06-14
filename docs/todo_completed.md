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
