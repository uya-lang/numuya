# Failed Todo

## Phase 0: 脚手架与测试基础

- [f] 运行 `../uya/bin/uya upm install --manifest-path uya.toml`。
  - 无依赖时仍应成功。
  - 若生成 `uya.lock`，保留并提交；后续依赖变更必须同步更新。
  - 失败命令：`../uya/bin/uya upm install --manifest-path uya.toml`
  - 关键错误：`错误: source root 不存在或不是目录: /media/winger/_dde_data/winger/uya/numuya/src/numuya/`
  - 失败原因：`uya.toml` 配置了 `source-dir = "src/numuya"`，但当前仓库尚未创建该目录。
  - 后续重开条件：先创建 `src/numuya/`，再重新运行安装命令并检查是否生成 `uya.lock`。
