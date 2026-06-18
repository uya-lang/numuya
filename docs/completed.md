# Completed Items

## Phase 3: 创建数组与基础 get/set

- [x] `empty<T>` / `full<T>` / `from_slice<T>` — creation.uya
- [x] `zeros_f64` / `ones_f64` / `full_f64` — creation.uya
- [x] `arange_f64` / `linspace_f64` — creation.uya（新增；`arange_f64` 负步长路径已补测试）
- [x] `get1/get2/get3/getn` / `set1/set2/setn` — indexing.uya
- [x] boolean_mask / take / advanced indexing — indexing.uya
- [x] SliceSpec / slice_axis — slicing.uya
- [x] 泛型 `Array<T>` 目前用类型特化绕过 codegen 限制

## Phase 10: Statistics

- [x] `var_all_f64` / `std_all_f64` — stats.uya
- [x] `percentile_f64` — stats.uya
- [x] `histogram_f64` / `cov_f64` / `corrcoef_f64` — stats.uya（额外增加）

## Phase 19: SIMD 与性能

- [x] `numuya_simd_add_f64` / `numuya_simd_mul_f64` / `numuya_simd_sum_f64` — ufunc.uya / reductions.uya（已切换为 `@vector` 分块实现，保留 tail 标量收尾）
- [x] SIMD 等价性测试 — test_simd_equivalence.uya
- [x] SIMD benchmark — bench_simd.uya

## Phase 22: CUDA ufunc 与 reduction

- [x] `gpu_add_f32` / `gpu_add_f64`（strided + broadcast）— cuda/ufunc.uya
- [x] `gpu_mul_f64` — cuda/ufunc.uya
- [x] `gpu_sub_f64` / `gpu_neg_f64` / `gpu_div_f64` — cuda/ufunc.uya（`sub/div` 支持 broadcast + strided，`neg` 支持 strided view）
- [x] `gpu_sub_f64` / `gpu_neg_f64` / `gpu_div_f64` CUDA 测试 — _tests/test_cuda_ufunc.uya
- [x] `gpu_sum_all_f32/f64` — cuda/reductions.uya（两阶段 block reduction）
- [x] `gpu_sum_axis_f64` / `gpu_mean_axis_f64` / `gpu_argmax_axis_f64` — cuda/reductions.uya（contiguous 输入走纯 GPU kernel；非 contiguous 维持 host fallback）
- [x] `add_f64_auto` / `sum_all_f64_auto` / `sum_axis_f64_auto` — cuda/auto.uya
- [x] `add_f64_on` location-preserving API — cuda/auto.uya

## Phase 23: CUDA linalg、random、benchmark

- [x] `gpu_matmul_f32` (纯 kernel tiled SGEMM 16×16 + aligned 16×64) — cuda/linalg.uya
- [x] `gpu_matmul_f32` (cuBLASLt vendor TF32/FP32) — cuda/linalg.uya + cuda/cublaslt.uya
- [x] `gpu_random_f32` (纯 kernel + cuRAND vendor) — cuda/random.uya + cuda/curand.uya
- [x] FFT (cuFFT Z2Z vendor + CPU fallback) — cuda/fft.uya + cuda/cufft.uya（`ComplexArray` 已改为 `Array<Complex>` wrapper）
- [x] Benchmark (H2D/D2H/add/sum/matmul/random) — bench_cuda.uya

## Phase 24: NumPy 兼容面扩展

- [x] `ArrayAny` 动态 dtype wrapper (f64/f32/i32/i64/u8) — types.uya
- [x] einsum 简约记法 — einsum.uya
- [x] .npy v1/v2 多 dtype 读写 — io_npy.uya
- [x] .npz 压缩存档读写 — io_npz.uya
- [x] advanced/fancy indexing — indexing.uya

## CUDA backend 没有 C helper 依赖（纯 Uya 方案）

- **原始失败原因**：尝试用纯 Uya `@asm` 间接调用替换 `driver_stub.c` 的 CUDA Driver API 封装，运行时段错误（退出码 139）。
- **根因分析**：1) `@asm` 指令格式错误；2) `@asm` 每条指令最多 8 个输入操作数，`cuLaunchKernel` 需要 10+ 个参数。
- **最终修复方案**：纯 Uya + 极简 `dl_stub.c` passthrough。
  - `dl_stub.c`（约 100 行 C）仅提供 FFI passthrough，不含任何 CUDA 业务逻辑。
  - 所有 stub C 文件已删除，所有逻辑移到纯 Uya。
  - 每个 vendor 模块各自 `@c_import("dl_stub.c")` + `extern fn`（内联值 4098 替代共享 const）。

## 每次提交前检查（已完成）

- [x] `dl_stub.c` 仅做 dlopen/dlsym passthrough 和通用间接调用 helper，不含 CUDA 类型、不含函数指针缓存、不含版本兼容逻辑、不硬链接 CUDA 库。
- [x] 可选 cuBLAS/cuFFT/cuRAND 通过 `BackendConfig.prefer_vendor_libs=true` / `make test-cuda-vendor` 开启，纯 Uya CUDA kernel backend 始终可通过测试。
- [x] DeviceArray view/drop 路径经过 DeviceStorage refcount 测试（test_cuda_device_array.uya）。
- [x] host-return `_auto` API 与 location-preserving `_on` API 都有测试（test_cuda_auto.uya + test_cuda_location_preserving.uya）。
