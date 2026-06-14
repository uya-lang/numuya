# Completed Todo

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
