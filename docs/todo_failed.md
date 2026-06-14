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
