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

- [ ] 写 `src/numuya/_tests/test_array_creation.uya`。
- [ ] 写 `src/numuya/_tests/test_indexing.uya`。
- [ ] 实现 `src/numuya/creation.uya`。
- [ ] TDD: `empty<T>`。
  - shape 正确。
  - size 正确。
  - contiguous flags 正确。
  - 不读取元素值。
- [ ] TDD: `full<T>`。
  - `full_f64(shape2(2, 3), 7.5)` 六个元素都是 7.5。
- [ ] TDD: `zeros_f64/ones_f64/full_f64`。
- [ ] TDD: `from_slice<T>`。
  - slice 长度等于 shape size 时成功并复制。
  - 长度不等返回 `NumuyaShapeMismatch`。
  - 修改源 slice 不影响 array。
- [ ] 实现 `src/numuya/indexing.uya`。
- [ ] TDD: `get1/get2/get3/getn`。
  - 正常读。
  - rank 不匹配返回 `NumuyaInvalidArgument`。
  - index 越界返回 `NumuyaIndexOutOfBounds`。
- [ ] TDD: `set1/set2/setn`。
  - 正常写后能读回。
  - 只读 array 返回 `NumuyaReadOnly`。
- [ ] 验收：`test_array_creation`、`test_indexing` 绿。

## Phase 4: Stride、reshape、transpose、view

- [ ] 写 `src/numuya/_tests/test_stride_views.uya`。
- [ ] 实现 `src/numuya/stride.uya`。
- [ ] TDD: `c_order_strides(shape)`.
  - `(2, 3, 4)` strides 是 `[12, 4, 1]`。
  - scalar strides rank 为 0。
- [ ] TDD: `physical_index(shape, strides, offset, indices)`.
  - `(2, 3)` C-order 下 `(1, 2)` 物理 index 是 5。
- [ ] TDD: `reshape`.
  - `(2, 3)` reshape 到 `(3, 2)` 不复制，storage ref_count 增加。
  - size 不同返回 `NumuyaShapeMismatch`。
- [ ] TDD: `ravel`.
  - contiguous 返回 shape `(size,)` view。
- [ ] TDD: `transpose`.
  - `(2, 3)` transpose 得 `(3, 2)`。
  - 读转置 view 的 `(2, 1)` 等于原 `(1, 2)`。
- [ ] TDD: `swapaxes`.
- [ ] TDD: view 写入。
  - 通过 transpose view set 后，owner 对应元素变化。
- [ ] 验收：`src/numuya/_tests/test_stride_views.uya` 绿。

## Phase 5: Slicing

- [ ] 写 `src/numuya/_tests/test_slicing.uya`。
- [ ] 实现 `SliceSpec`。
- [ ] TDD: `slice_axis`.
  - `0:3:1`。
  - `1:5:2`。
  - 负 start/stop。
  - 负 step reverse。
  - 空 slice。
- [ ] TDD: slice 返回 view。
  - storage ref_count 增加。
  - view 写入反映到 owner。
- [ ] TDD: invalid slice。
  - step 为 0 返回 `NumuyaInvalidArgument`。
  - axis 越界返回 `NumuyaAxisOutOfBounds`。
- [ ] 验收：`src/numuya/_tests/test_slicing.uya` 绿。

## Phase 6: Broadcasting

- [ ] 写 `src/numuya/_tests/test_broadcast.uya`。
- [ ] 实现 `src/numuya/broadcast.uya`。
- [ ] TDD: `broadcast_shapes`.
  - `(3,)` 与 `(2, 3)` -> `(2, 3)`。
  - `(4, 1, 3)` 与 `(1, 5, 3)` -> `(4, 5, 3)`。
  - `(2,)` 与 `(3,)` 返回 `NumuyaBroadcastError`。
- [ ] TDD: `broadcast_to`.
  - `(3,)` broadcast 到 `(2, 3)`，新 axis stride 为 0。
  - `(1, 3)` 到 `(2, 3)`，第一轴 stride 为 0。
  - 不兼容返回 `NumuyaBroadcastError`。
- [ ] TDD: broadcast view 默认只读或写保护。
  - 如果设置只读，`set` 返回 `NumuyaReadOnly`。
  - 如果允许写入，必须证明 stride 0 写入语义清楚；第一版推荐只读。
- [ ] 验收：`src/numuya/_tests/test_broadcast.uya` 绿。

## Phase 7: UFunc 基础

- [ ] 写 `src/numuya/_tests/test_ufunc.uya`。
- [ ] 实现 `src/numuya/ufunc.uya`。
- [ ] TDD: `add_f64/sub_f64/mul_f64/div_f64`。
  - 同 shape。
  - broadcast shape。
  - scalar array 与 vector。
- [ ] TDD: `neg_f64`。
- [ ] TDD: `add_i32`。
- [ ] TDD: non-contiguous input。
  - transpose view 输入仍能正确运算。
- [ ] TDD: output 是新 owner。
  - 修改 output 不影响 input。
- [ ] 内部重构：提取 contiguous fast path 与 generic stride path。
- [ ] 验收：`src/numuya/_tests/test_ufunc.uya` 绿，并回跑 `broadcast`、`stride_views`。

## Phase 8: Reductions

- [ ] 写 `src/numuya/_tests/test_reductions.uya`。
- [ ] 实现 `src/numuya/reductions.uya`。
- [ ] TDD: `sum_all_f64/prod_all_f64`。
  - 普通数组。
  - 空数组。
  - non-contiguous view。
- [ ] TDD: `min_all_f64/max_all_f64`。
  - 普通数组。
  - 空数组返回 `NumuyaInvalidArgument`。
- [ ] TDD: `mean_all_f64`。
  - 普通数组。
  - 空数组返回 `NumuyaInvalidArgument`。
- [ ] TDD: `sum_axis_f64`.
  - axis 0、axis 1。
  - negative axis。
  - keepdims true/false。
- [ ] TDD: `mean_axis_f64`。
- [ ] TDD: `argmax_axis_f64`。
- [ ] 验收：`src/numuya/_tests/test_reductions.uya` 绿。

## Phase 9: Math functions

- [ ] 写 `src/numuya/_tests/test_math.uya`。
- [ ] 实现 `src/numuya/math.uya`。
- [ ] TDD: `abs_f64`。
- [ ] TDD: `sqrt_f64`。
- [ ] TDD: `exp_f64/log_f64`。
- [ ] TDD: `sin_f64/cos_f64`。
- [ ] TDD: broadcast/non-contiguous 输入通过 ufunc 内核复用。
- [ ] 验收：`src/numuya/_tests/test_math.uya` 绿。

## Phase 10: Statistics

- [ ] 写 `src/numuya/_tests/test_stats.uya`。
- [ ] 实现 `src/numuya/stats.uya`。
- [ ] TDD: `var_all_f64(ddof=0)`。
- [ ] TDD: `var_all_f64(ddof=1)`。
- [ ] TDD: `std_all_f64`。
- [ ] TDD: `percentile_f64`。
  - q=0、50、100。
  - q 越界返回 `NumuyaInvalidArgument`。
- [ ] 验收：`src/numuya/_tests/test_stats.uya` 绿。

## Phase 11: Sorting 与 searching

- [ ] 写 `src/numuya/_tests/test_sorting.uya`。
- [ ] 实现 `src/numuya/sorting.uya`。
- [ ] TDD: `sort_f64`。
  - 已排序、逆序、重复元素。
  - 输出是 copy。
- [ ] TDD: `argsort_f64`。
- [ ] TDD: `searchsorted_f64`。
- [ ] TDD: `unique_f64`。
- [ ] 第一版限制 1-D contiguous，并对其他输入返回 `NumuyaInvalidArgument` 或先 copy。
- [ ] 验收：`src/numuya/_tests/test_sorting.uya` 绿。

## Phase 12: Linear algebra MVP

- [ ] 写 `src/numuya/_tests/test_linalg.uya`。
- [ ] 实现 `src/numuya/linalg.uya`。
- [ ] TDD: `eye_f64`。
  - `eye(3, 3, 0)`。
  - `k=1`、`k=-1`。
- [ ] TDD: `diag_f64`。
  - 1-D -> 2-D diagonal matrix。
  - 2-D -> 1-D diagonal extraction。
- [ ] TDD: `dot_f64`。
  - 1-D dot 1-D 返回 scalar shape。
- [ ] TDD: `matmul_f64`。
  - 2-D x 2-D。
  - incompatible shape 返回 `NumuyaShapeMismatch`。
- [ ] TDD: non-contiguous matrix input。
- [ ] 验收：`src/numuya/_tests/test_linalg.uya` 绿。

## Phase 13: Linear algebra advanced

- [ ] TDD: `det_f64` 1x1、2x2、3x3。
- [ ] TDD: `solve_f64`。
  - identity。
  - 2x2 known system。
  - singular 返回 `NumuyaSingularMatrix`。
- [ ] TDD: `inv_f64`。
- [ ] TDD: `qr_f64`。
- [ ] TDD: `svd_f64`。
- [ ] 验收：advanced linalg tests 绿。

## Phase 14: Random

- [ ] 写 `src/numuya/_tests/test_random.uya`。
- [ ] 实现 `src/numuya/random.uya`。
- [ ] TDD: `pcg64_seed` deterministic。
  - 固定 seed 的前 5 个 `random_u64` 用硬编码 golden。
- [ ] TDD: `random_f64` 范围 `[0, 1)`。
- [ ] TDD: `random_array_f64` shape 和范围。
- [ ] TDD: `normal_array_f64` 固定 seed golden。
- [ ] 验收：`src/numuya/_tests/test_random.uya` 绿。

## Phase 15: FFT

- [ ] 写 `src/numuya/_tests/test_fft.uya`。
- [ ] 实现 `src/numuya/fft.uya`。
- [ ] TDD: complex add/mul/conj helper。
- [ ] TDD: `fft_f64` 长度 1。
- [ ] TDD: `fft_f64` 长度 2。
- [ ] TDD: impulse 输入。
- [ ] TDD: `ifft(fft(x)) ~= x`。
- [ ] TDD: 非 power-of-two 返回 `NumuyaInvalidArgument`，直到 fallback 实现完成。
- [ ] 验收：`src/numuya/_tests/test_fft.uya` 绿。

## Phase 16: `.npy` I/O

- [ ] 写 `src/numuya/_tests/test_io_npy.uya`。
- [ ] 准备小型 `.npy` fixture。
  - 1-D f64。
  - 2-D f64。
  - empty f64。
- [ ] 实现 `src/numuya/io_npy.uya`。
- [ ] TDD: `load_npy_f64`。
  - magic/header 解析。
  - shape 正确。
  - 数据正确。
- [ ] TDD: `save_npy_f64`。
  - 保存后再加载 roundtrip。
- [ ] TDD: unsupported dtype 返回 `NumuyaUnsupportedDType`。
- [ ] 验收：`src/numuya/_tests/test_io_npy.uya` 绿。

## Phase 17: Advanced indexing

- [ ] 写 `src/numuya/_tests/test_advanced_indexing.uya`。
- [ ] TDD: `take` 1-D。
- [ ] TDD: `take` axis 0/1。
- [ ] TDD: boolean mask 1-D。
- [ ] TDD: boolean mask shape mismatch。
- [ ] TDD: fancy indexing copy 语义。
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
