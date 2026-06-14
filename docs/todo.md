# NumUya TDD Todo

本文档是实现顺序。每个条目都必须先写测试，确认失败，再实现。状态标记约定：

- `[ ]` 未开始
- `[~]` 进行中
- `[x]` 已完成
- `[f]` 暂时失败，需要记录 blocker 和最小复现

通用命令：

```bash
test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm
../uya/bin/uya upm install --manifest-path uya.toml
../uya/bin/uya check src/numuya/_tests/test_shape.uya --manifest-path uya.toml
../uya/bin/uya test src/numuya/_tests/test_shape.uya --manifest-path uya.toml
```

完成一个阶段后，至少运行该阶段及之前所有测试。添加 Makefile 后改用 `make test`，但 Makefile 内部必须先确认 `../uya/bin/cmd/upm` 存在，再调用 `../uya/bin/uya ... --manifest-path uya.toml` 或等价 UPM/package-mode 命令。`--project-root src` 只允许用于编译器最小复现，不作为项目常规测试入口。

测试布局约定：

- NumUya 的默认 TDD 单测放在 `src/numuya/_tests/`，因为新版 package-mode 只会把 root source root 物化到临时 build root。
- 包内测试按 source-root 相对路径导入，例如 `use shape.Shape;`、`use creation.zeros_f64;`，不要依赖根包自别名 `numuya.*`。
- 外部 consumer fixture 才使用 `use numuya.*`，用于验证其他项目通过 UPM 使用 NumUya。
- `_tests`、`_tools`、`_benchmarks` 是内部模块，外部 consumer fixture 不得导入 `numuya._tests.*`、`numuya._tools.*` 或 `numuya._benchmarks.*`。

## Phase 3: 创建数组与基础 get/set

- 注：当前 Uya codegen 对导出泛型 `!Array<T>` 路径仍有实例化限制；后续 `empty<T>/full<T>/from_slice<T>` 先用失败测试锁定可行写法，必要时抽最小复现。

## Phase 10: Statistics

## Phase 17: Advanced indexing

- [ ] 验收：advanced indexing tests 绿。

## Phase 18: DType 与 type-erased ArrayAny

- [ ] 写 `src/numuya/_tests/test_dtype.uya`。
- [ ] 实现 `src/numuya/types.uya`。
- [ ] TDD: `DType` size/name/endian helpers。
- [ ] TDD: `ArrayAny` 包装 `Array<f64>`。
- [ ] TDD: dtype mismatch 返回 `NumuyaUnsupportedDType` 或 `NumuyaInvalidArgument`。
- [ ] 把 `.npy` 逐步扩展到 f32/i32/i64/u8。
- [ ] 验收：dtype tests 绿，I/O 回归绿。

## Phase 19: SIMD 与性能

- [ ] 写 `src/numuya/_tests/test_simd_equivalence.uya`。
- [ ] 为 add/mul/sum 增加 SIMD fast path。
- [ ] TDD: SIMD path 与标量 path 结果一致。
- [ ] TDD: 长度不是 vector width 倍数时尾部正确。
- [ ] TDD: 非 contiguous 输入仍走标量 path。
- [ ] 添加 benchmark，但 benchmark 不代替测试。
- [ ] 验收：correctness tests 全绿。

## Phase 20: CUDA backend 基础

- [ ] 写 `src/numuya/_tests/test_cuda_driver.uya`。
- [ ] 创建 `src/numuya/backend.uya`。
- [ ] 创建 `src/numuya/cuda/driver.uya`。
- [ ] 创建 CUDA 测试命令约定。
  - `make test` 默认不要求 GPU，且依赖 `make bootstrap-upm`。
  - `make test-cuda` 依赖 `make bootstrap-upm`，设置 `NUMUYA_CUDA_REQUIRED=1` 并链接 `-lcuda`。
  - `make test-cuda-vendor` 依赖 `make bootstrap-upm`，额外链接 `-lcublasLt -lcublas -lcufft -lcurand`。
  - 无 Makefile 时直接命令为 `test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm` 后执行 `LDFLAGS="-lcuda" NUMUYA_CUDA_REQUIRED=1 ../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`。
- [ ] TDD: `backend_is_cuda_available()`。
  - 本机 RTX 3060 应返回 true。
  - 无 CUDA 环境时不能崩溃。
- [ ] TDD: `cuda_init()`。
  - 成功时返回 ok。
  - driver 初始化失败映射为 `NumuyaGpuUnavailable` 或 `NumuyaCudaError`。
- [ ] TDD: `cuda_get_device(0)`。
  - device ordinal 是 0。
  - compute capability 应识别为 Ampere `sm_86` 或至少 major/minor 非 0。
  - total memory 应大于 8GB。
- [ ] TDD: `backend_init` / `backend_deinit`。
  - `BackendKind.cpu` 不初始化 CUDA。
  - `BackendKind.cuda` 初始化 CUDA，失败时返回明确错误。
  - `BackendKind.auto` 可在无 CUDA 时回退 CPU。
  - 没有活跃 DeviceStorage 时，`backend_deinit` 后 stream/context/module/pool 均释放或置空。
  - 仍有活跃 DeviceStorage 时，`backend_deinit` 返回 `NumuyaInvalidArgument`。
- [ ] TDD: `cuda_create_context` / destroy。
- [ ] TDD: `cuda_create_stream` / synchronize / destroy。
- [ ] TDD: context current 规则。
  - 任意 Driver API wrapper 调用前设置正确 context。
  - 跨 backend stream 使用返回 `NumuyaDeviceMismatch`。
- [ ] 验收：`src/numuya/_tests/test_cuda_driver.uya` 在本机 RTX 3060 上绿；没有 CUDA 时测试可标记 skip 或返回明确错误。

## Phase 21: CUDA DeviceArray 与拷贝

- [ ] 写 `src/numuya/_tests/test_cuda_device_array.uya`。
- [ ] 实现 `src/numuya/cuda/memory.uya`。
- [ ] 实现 `src/numuya/cuda/device_array.uya`。
- [ ] TDD: `cuda_malloc/cuda_free`。
  - 申请 1MB 成功。
  - 超过 budget 返回 `NumuyaGpuOutOfMemory`。
- [ ] TDD: `DeviceStorage<T>` 引用计数。
  - `device_storage_new` 初始 ref_count 为 1。
  - `device_storage_retain` 增加计数。
  - `device_storage_release` 非最后引用只减计数。
  - 最后引用释放 device memory，并更新 memory pool。
- [ ] TDD: device view 语义。
  - `device_array_view` retain 同一 storage。
  - view drop 不释放 owner 的 buffer。
  - owner 和 view 全部 drop 后只释放一次。
- [ ] TDD: H2D/D2H copy。
  - host `Array<f64>` -> `DeviceArray<f64>` -> host。
  - 数据逐元素一致。
  - stream synchronize 后结果稳定。
- [ ] TDD: `device_empty_f64/device_zeros_f64`。
- [ ] TDD: shape/stride/flags 在 device array 上保持一致。
- [ ] TDD: memory pool 统计。
  - alloc 后 used 增加。
  - free 后 used 减少。
  - 真实 allocation 改变 `live_allocations`，view retain/drop 不改变。
- [ ] 验收：`src/numuya/_tests/test_cuda_device_array.uya` 绿。

## Phase 22: CUDA ufunc 与 reduction

- [ ] 写 `src/numuya/_tests/test_cuda_ufunc.uya`。
- [ ] 写 `src/numuya/_tests/test_cuda_reductions.uya`。
- [ ] 实现 `src/numuya/cuda/module.uya` 和 `kernels.uya`。
- [ ] 创建 PTX source-of-truth。
  - `src/numuya/cuda/ptx/core_sm86.ptx`。
  - `src/numuya/cuda/kernels_ptx.uya` 由 `src/numuya/_tools/embed_ptx.uya` 生成。
  - 不创建必需 `.cu` 源，不把 `nvcc` 放进 TDD 主路径。
- [ ] TDD: `make cuda-ptx-embed` 或等价命令。
  - PTX 文本嵌入到 `kernels_ptx.uya`。
  - 生成结果稳定可重复。
- [ ] TDD: `make cuda-ptx-validate` 或等价命令。
  - `ptxas -arch=sm_86` 校验通过。
  - cubin cache 不是唯一 source-of-truth。
- [ ] TDD: 加载 embedded PTX/cubin。
  - `sm_86` 优先。
  - PTX JIT fallback 可用。
- [ ] TDD: `gpu_add_f64` contiguous。
  - 与 CPU `add_f64` 完全同 shape，容差一致。
- [ ] TDD: `gpu_mul_f64` contiguous。
- [ ] TDD: broadcast add。
  - `(3,) + (2, 3)`。
  - stride 0 正确。
- [ ] TDD: non-contiguous input。
  - transpose view 输入正确。
- [ ] TDD: `gpu_sum_f64`。
  - 小数组。
  - 大数组。
  - 非 2 的幂长度。
- [ ] TDD: auto backend。
  - 显式 `cuda` 走 GPU。
  - `auto` 在 GPU 可用时走 GPU。
  - 显存不足或 GPU unavailable 时按设计返回错误或回退 CPU。
- [ ] TDD: location-preserving API。
  - `add_f64_on(ArrayF64.Device, ArrayF64.Device)` 返回 `ArrayF64.Device`。
  - `add_f64_auto(Array<f64>, Array<f64>)` 返回 host `Array<f64>`，内部走 GPU 时同步并拷回。
  - 混合 Host/Device 输入按设计拷贝或返回明确错误，不能静默使用错误 device。
- [ ] 验收：CUDA ufunc/reduction tests 绿，并回跑 CPU ufunc/reduction tests。

## Phase 23: CUDA linalg、random、benchmark

- [ ] 写 `src/numuya/_tests/test_cuda_linalg.uya`。
- [ ] 写 `src/numuya/_tests/test_cuda_random.uya`。
- [ ] 写 `src/numuya/_benchmarks/bench_cuda.uya`。
- [ ] TDD: `gpu_matmul_f32` baseline。
  - 2x2。
  - 16x16。
  - 128x128 与 CPU 结果 close。
- [ ] TDD: incompatible matmul shape 返回 `NumuyaShapeMismatch`。
- [ ] TDD: `gpu_random_f32`。
  - 固定 seed 可复现。
  - 输出范围 `[0, 1)`。
- [ ] 可选 feature: cuBLASLt backend。
  - 通过配置 `prefer_vendor_libs=true` 启用。
  - 关闭时仍走纯 kernel backend。
  - correctness tests 与 baseline 共用。
- [ ] 可选 feature: cuFFT/cuRAND backend。
  - 必须有纯 kernel 或 CPU fallback。
- [ ] Benchmark: H2D/D2H bandwidth。
- [ ] Benchmark: `add_f32/add_f64` throughput。
- [ ] Benchmark: `sum_f32/sum_f64` throughput。
- [ ] Benchmark: `matmul_f32` 1024x1024、2048x2048。
- [ ] Benchmark 输出 RTX 3060、driver、CUDA、显存、backend 路径。
- [ ] Benchmark strict 阈值。
  - H2D/D2H pageable copy 各自 >= 6 GiB/s。
  - contiguous `add_f32` 有效内存带宽 >= 150 GiB/s。
  - contiguous `add_f64` 有效内存带宽 >= 100 GiB/s。
  - `sum_f32` 有效读带宽 >= 60 GiB/s。
  - pure kernel `matmul_f32` 1024x1024 >= 1.0 TFLOP/s。
  - vendor cuBLASLt + TF32 2048x2048 启用时 >= 6.0 TFLOP/s。
  - random fill f32 >= 40 GiB/s。
- [ ] 验收：correctness tests 绿；benchmark 可单独运行，不进入普通测试。

## Phase 24: NumPy 兼容面扩展

- [ ] `where`。
- [ ] `clip`。
- [ ] `maximum/minimum`。
- [ ] `cumsum/cumprod`。
- [ ] `concatenate/stack/vstack/hstack`。
- [ ] `squeeze/expand_dims`。
- [ ] `repeat/tile`。
- [ ] `histogram`。
- [ ] `cov/corrcoef`。
- [ ] `einsum` MVP。
- [ ] `rfft/irfft`。
- [ ] `.npz` zip 容器。

## 每次提交前检查

- [ ] 新功能有失败测试记录或 commit 顺序能看出 test-first。
- [ ] 单个相关测试绿。
- [ ] 已完成阶段全部测试绿。
- [ ] 没有把实现写进测试 helper 绕过 public API。
- [ ] CPU core 没有 runtime 依赖 Python/NumPy/BLAS/LAPACK/libm/C helper。
- [ ] CUDA backend 没有 Python/NumPy/PyTorch/C helper 依赖；CUDA Driver API 绑定和可选 cuBLAS/cuFFT/cuRAND backend 必须在文档与配置中显式开启。
- [ ] CUDA kernel source-of-truth 是 PTX/Uya 生成资产；没有把必需实现藏在 `.cu`/`nvcc` 路径。
- [ ] DeviceArray view/drop 路径经过 DeviceStorage refcount 测试。
- [ ] host-return `_auto` API 与 location-preserving `_on` API 都有测试。
- [ ] 没有硬编码只服务当前测试输入的分支。
- [ ] 文档中的 public API 与实际实现一致。
