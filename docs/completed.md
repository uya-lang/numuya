# Completed Items

## CUDA backend 没有 C helper 依赖（纯 Uya 方案）

- **原始失败原因**：尝试用纯 Uya `@asm` 间接调用替换 `driver_stub.c` 的 CUDA Driver API 封装，运行时段错误（退出码 139）。
- **根因分析**：1) `@asm` 指令格式错误（多行字符串不被 lexer 支持）；2) `@asm` 每条指令最多 8 个输入操作数，`cuLaunchKernel` 需要 10+ 个参数；3) 之前用多行格式写 @asm 但 parser 要求 `"instruction" (operands)` 格式。
- **最终修复方案**：纯 Uya + 极简 `dl_stub.c` passthrough。
  - `driver.uya` 用纯 Uya 实现所有 CUDA Driver API 业务逻辑（dlsym 函数指针缓存、版本兼容、stream-context 管理、默认 context 创建、错误转换）。
  - `dl_stub.c`（约 100 行 C）仅提供 FFI passthrough（`dlopen/dlsym/dlclose/dlerror` + `numuya_call_0`~`numuya_call_6` 通用间接调用 + `numuya_cuda_launch_kernel` 专用 helper + `numuya_cublaslt_matmul` 16-arg 专用 helper），不含任何 CUDA 业务逻辑。
  - `driver_stub.c`（650 行 C）、`cublaslt_stub.c`（270 行）、`cufft_stub.c`（177 行）、`curand_stub.c`（130 行）——均已删除。所有逻辑移到纯 Uya（`driver.uya`、`cublaslt.uya`、`cufft.uya`、`curand.uya`）。
  - `module.uya` 通过 `use cuda.driver` 调用 `driver.uya` 导出的函数，不再用 `extern fn` 绑定 C stub。
  - 每个 vendor 模块各自 `@c_import("dl_stub.c")` 声明需要的 `extern fn`，用内联值 `4098` 替代共享 `const RTLD_NOW_NODELETE`（避免多模块合并时的重复定义冲突）。
  - CUDA/cuBLAS/cuFFT/cuRAND 类型常量（`CUBLAS_OP_N`、`CUFFT_Z2Z`、`CURAND_RNG_PSEUDO_DEFAULT` 等）在纯 Uya 中硬编码，无需 CUDA 头文件。

## 每次提交前检查（已完成）

- [x] `dl_stub.c` 仅做 dlopen/dlsym passthrough 和通用间接调用 helper，不含 CUDA 类型、不含函数指针缓存、不含版本兼容逻辑、不硬链接 CUDA 库。
- [x] 可选 cuBLAS/cuFFT/cuRAND 通过 `BackendConfig.prefer_vendor_libs=true` / `make test-cuda-vendor` 开启，纯 Uya CUDA kernel backend 始终可通过测试。