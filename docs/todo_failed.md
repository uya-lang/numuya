# Failed Todo

当前暂无未修复失败项。

## 每次提交前检查

- [f] CUDA backend 没有 Python/NumPy/PyTorch/C helper 依赖；CUDA Driver API 绑定和可选 cuBLAS/cuFFT/cuRAND backend 必须在文档与配置中显式开启。
  - 失败原因：当前工作区存在未提交的 `src/numuya/cuda/driver_loader.uya` 以及 `src/numuya/cuda/driver.uya` / `src/numuya/cuda/module.uya` 改动，尝试用纯 Uya `@asm` 间接调用替换 `driver_stub.c` 的 CUDA Driver API 封装，但运行聚焦测试时发生段错误，未能验证无 C helper 依赖。
  - 阻塞命令：
    ```bash
    ../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml
    ```
  - 关键错误：
    - 类型检查通过
    - 链接成功
    - 程序运行返回 `Segmentation fault`，退出码 139
  - 后续重开条件：
    - 修复 `driver_loader.uya` 中 `@asm` 调用约定/寄存器/栈参数传递问题，使 `test_cuda_driver.uya` 通过；或
    - 确认保留 `driver_stub.c` 作为运行时 `dlopen` 薄封装的合法方案，并在设计文档中显式说明其边界；并
    - 在 `docs/design.md` 与 `uya.toml`/Makefile 中显式说明可选 cuBLAS/cuFFT/cuRAND 通过 `BackendConfig.prefer_vendor_libs=true` / `make test-cuda-vendor` 开启，且纯 Uya CUDA kernel backend 始终可用。
