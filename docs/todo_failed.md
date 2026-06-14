# Failed Todo

## Phase 0: 脚手架与测试基础

- [f] 验证外部项目通过 `upm add` 使用 NumUya。
  - 在临时目录执行 `../uya/bin/uya upm init --src-layout consumer_smoke` 或等价初始化。
  - 执行 `../uya/bin/uya upm add numuya --path <numuya_repo> --manifest-path <tmp>/consumer_smoke/uya.toml`。
  - consumer 源码只写 `use numuya.*`，不设置 `UYA_ROOT`，不传 `--project-root`。
  - `../uya/bin/uya upm install --manifest-path <tmp>/consumer_smoke/uya.toml` 和 `../uya/bin/uya test <tmp>/consumer_smoke/src/main.uya --manifest-path <tmp>/consumer_smoke/uya.toml` 成功。
  - 失败原因：当前 Uya 语言/解析器不支持通配符导入，consumer 源码中的 `use numuya.*;` 被解析器拒绝；上游文档 `../uya/docs/uya.md` 也说明不支持 `use math.*;`。
  - 阻塞命令：
    - `tmpdir=$(mktemp -d); ../uya/bin/uya upm init --src-layout "$tmpdir/consumer_smoke"; ../uya/bin/uya upm add numuya --path "$PWD" --manifest-path "$tmpdir/consumer_smoke/uya.toml"; printf 'use numuya.*;\\n\\nexport fn main() i32 {\\n    return 0;\\n}\\n' > "$tmpdir/consumer_smoke/src/main.uya"; ../uya/bin/uya upm install --manifest-path "$tmpdir/consumer_smoke/uya.toml"; ../uya/bin/uya test "$tmpdir/consumer_smoke/src/main.uya" --manifest-path "$tmpdir/consumer_smoke/uya.toml"`
  - 关键错误：
    - `错误: 语法分析失败 (.../root/main.uya:1:12): 意外的 token '*'`
    - `错误: 语法分析失败 (.../root/main.uya:1:12): 'use' 语句后期望 ';'`
  - 后续重开条件：上游 Uya 支持 `use <module>.*;` 通配符导入，或 todo 明确允许改用当前语言支持的显式 public API 导入，例如 `use numuya.shape.Shape;` 和 `use numuya.creation.zeros_f64;`。
