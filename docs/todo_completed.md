## Phase 13: Linear algebra advanced

- [x] TDD: `inv_f64`。
  - 新增测试：`src/numuya/_tests/test_linalg.uya` 中添加 5 个测试：
    - `inv_f64 inverts identity matrix`
    - `inv_f64 inverts 2x2 matrix`
    - `inv_f64 product with original yields identity`
    - `inv_f64 returns singular matrix error`
    - `inv_f64 rejects non-square matrix`
  - 实现：`src/numuya/linalg.uya` 新增 `inv_impl<T>` 与导出 `inv_f64`，使用 Gauss-Jordan 消元法对增广矩阵 `[A | I]` 进行行变换得到逆矩阵。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml` — 23/23 通过
    - `make test` — 全部测试文件通过


## Phase 13: Linear algebra advanced

- [x] TDD: `qr_f64`。
  - 新增测试：`src/numuya/_tests/test_linalg.uya` 中添加 `qr_f64 decomposes square matrix into q and r`，使用 Wikipedia 经典 3x3 矩阵验证 Q/R 元素。
  - 实现：`src/numuya/linalg.uya` 新增 `QRResult` 结构与导出 `qr_f64`，使用 modified Gram-Schmidt 对 m×n（m ≥ n）矩阵进行 QR 分解；通过 `@c_import("math_stub.c", "", "-lm")` 链接数学库以使用 `sqrt`。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml` — 24/24 通过
    - `make test` — 全部测试文件通过


## Phase 13: Linear algebra advanced

- [x] TDD: `svd_f64`。
  - 新增测试：`src/numuya/_tests/test_linalg.uya` 中添加 6 个测试：
    - `svd_f64 returns correct shapes for square matrix`
    - `svd_f64 reconstructs square matrix`
    - `svd_f64 produces orthogonal factors`
    - `svd_f64 returns sorted singular values for diagonal matrix`
    - `svd_f64 handles tall rectangular matrix`
    - `svd_f64 rejects non-2-D input`
  - 实现：`src/numuya/linalg.uya` 新增 `SVDResult` 结构与导出 `svd_f64`，使用 one-sided Jacobi 算法对 m×n（m ≥ n）矩阵进行经济型 SVD 分解；奇异值按降序排列，U 与 Vt 正交并满足 A = U·diag(S)·Vt。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml` — 30/30 通过
    - `make test` — 全部测试文件通过

## Phase 13: Linear algebra advanced

- [x] TDD: `svd_f64`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml`
  - 验证结果：`svd_f64` 相关 6 个测试全部通过；`test_linalg.uya` 共 30 个测试通过，0 失败。

## Phase 13: Linear algebra advanced

- [x] 验收：advanced linalg tests 绿。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml` — 30/30 通过
    - `make test` — 全部测试文件通过（test_array_creation/test_broadcast/test_indexing/test_linalg/test_math/test_reductions/test_shape/test_slicing/test_sorting/test_stats/test_storage/test_stride_views/test_testing_helpers/test_ufunc）
  - 验证结果：advanced linalg 测试全部通过，无失败。


## Phase 14: Random

- [x] 写 `src/numuya/_tests/test_random.uya`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_random.uya --manifest-path uya.toml`
  - 结果：按预期失败；`random.uya` 尚未实现，类型检查报 `random_array_f64` / `normal_array_f64` 的 `try` 操作数不是错误联合类型。

## Phase 14: Random

- [x] 实现 `src/numuya/random.uya`。
  - 新增 `src/numuya/random.uya`：导出 `PCG64`、`pcg64_seed`、`random_u64`、`random_f64`、`random_array_f64`、`normal_array_f64`。
  - PCG64 使用 64 位 LCG，乘数 `6364136223846793005`，增量 `inc = (init_seq << 1) | 1`，输出置换为 `state ^ (state >> 17)`。
  - `random_f64` 将 `u64` 映射到 `[0, 1)`：`value / 2^64`。
  - `random_array_f64` 用 `empty<f64>` 分配数组并填充均匀随机数。
  - `normal_array_f64` 使用 Box-Muller 变换生成正态分布；调用 `sqrt`/`log`/`sin`/`cos` 需要 `@c_import("math_stub.c", "", "-lm")`。
  - 包含 `materialize_storage_release<T>`  workaround，规避当前 Uya codegen 对跨模块 `Array<f64>` drop 的实例化缺失。
- [x] TDD: `pcg64_seed` deterministic。
  - 测试：`pcg64_seed produces deterministic u64 sequence`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_random.uya --manifest-path uya.toml`
- [x] TDD: `random_u64` golden values。
  - 测试：`random_u64 golden values for fixed seed`。
  - 固定 seed `(42, 0)` 前 5 个值：15403552597630628382、16168177009217139338、11128129689875903247、121274658106355247、8960200607924515427。
- [x] TDD: `random_f64` 范围 `[0, 1)`。
  - 测试：`random_f64 returns values in half open interval zero one`。
- [x] TDD: `random_array_f64` shape 和范围。
  - 测试：`random_array_f64 produces array with requested shape and values in range`。
- [x] TDD: `normal_array_f64` 固定 seed golden。
  - 测试：`normal_array_f64 produces deterministic golden values for fixed seed`。
  - 固定 seed `(12345, 1)`、shape `(2, 3)`、mean 0、stddev 1 的 golden 与 Python 参考实现一致。
- [x] 验收：`src/numuya/_tests/test_random.uya` 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_random.uya --manifest-path uya.toml` — 6/6 通过
  - 验证命令：`make test` — 全部测试文件通过（test_array_creation/test_broadcast/test_indexing/test_linalg/test_math/test_random/test_reductions/test_shape/test_slicing/test_sorting/test_stats/test_storage/test_stride_views/test_testing_helpers/test_ufunc）


## Phase 15: FFT

- [x] 写 `src/numuya/_tests/test_fft.uya`。
  - 交付物：`src/numuya/_tests/test_fft.uya`
  - 验证：
    - `../uya/bin/uya check src/numuya/_tests/test_fft.uya --manifest-path uya.toml`：checker 通过
    - `../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`：7 个测试中 3 个通过、4 个因 `fft_f64`/`ifft` 尚未实现而预期失败
    - 代表性回归测试（`test_shape.uya`、`test_array_creation.uya`、`test_math.uya`、`test_linalg.uya`、`test_stats.uya`）全部通过
  - 说明：为避免 `Array<Complex>` 的 codegen 限制，FFT 输出采用 `ComplexArray`（并行的 `re`/`im` 两个 `Array<f64>`）；为让测试可编译运行，同时创建了最小 `src/numuya/fft.uya` stub（仅导出类型与函数签名，`fft_f64`/`ifft` 暂返回 `NumuyaInvalidArgument`）。

## Phase 15: FFT

- [x] 实现 `src/numuya/fft.uya`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml` 7/7 通过；`make test` 全量测试通过。

## Phase 15: FFT

- [x] TDD: complex add/mul/conj helper。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`
  - 结果：7/7 tests passed，其中 `complex add multiply and conjugate helpers` 测试验证 `complex_add`、`complex_mul`、`complex_conj` 返回正确结果。

## Phase 15: FFT

- [x] TDD: `fft_f64` 长度 1。
  验证命令：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`
  结果：7/7 测试通过，包含 `fft_f64 length 1 returns constant`。

## Phase 15: FFT

- [x] TDD: `fft_f64` 长度 2。
  - 验证命令：`TEST=src/numuya/_tests/test_fft.uya make test-one`
  - 结果：7/7 测试通过，包含 `fft_f64 length 2 on impulse`。

## Phase 15: FFT

- [x] TDD: impulse 输入。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`
  - 结果：8 tests passed，包含新增 `fft_f64 on eight point impulse`。

## Phase 15: FFT

- [x] TDD: `ifft(fft(x)) ~= x`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`
  - 结果：9 tests passed, 0 failed（新增 `ifft inverts fft for complex input`）
  - 回归验证：`make test` 全绿

## Phase 15: FFT

- [x] TDD: 非 power-of-two 返回 `NumuyaInvalidArgument`，直到 fallback 实现完成。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml` 通过 11/11；`make test` 全绿。

## Phase 15: FFT

- [x] 验收：`src/numuya/_tests/test_fft.uya` 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_fft.uya --manifest-path uya.toml`
  - 结果：11/11 测试通过，0 失败。
  - 回归验证：`make test` 全绿（如 Makefile 可用）。

## Phase 16: `.npy` I/O

- [x] 写 `src/numuya/_tests/test_io_npy.uya`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_io_npy.uya`
  - 结果：通过，3 个测试全部通过。
  - 验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya`
  - 结果：通过，6 个测试全部通过。

## Phase 16: `.npy` I/O

- [x] 准备小型 `.npy` fixture。
  - 1-D f64。
  - 2-D f64。
  - empty f64。
  - 产物：
    - `tests/fixtures/npy/generate.py`
    - `tests/fixtures/npy/verify.py`
    - `tests/fixtures/npy/f64_1d.npy`
    - `tests/fixtures/npy/f64_2d.npy`
    - `tests/fixtures/npy/f64_empty.npy`
  - 验证：
    - `python3 tests/fixtures/npy/generate.py` -> exit 0。
    - `python3 tests/fixtures/npy/verify.py` -> `verified 3 npy fixtures`。
    - `make test-one TEST=src/numuya/_tests/test_io_npy.uya` -> 3 个测试通过。

## Phase 16: `.npy` I/O

- [x] 实现 `src/numuya/io_npy.uya`。
  - 产物：
    - `src/numuya/io_npy.uya`
  - 验证：
    - `../uya/bin/uya check src/numuya/io_npy.uya --manifest-path uya.toml` -> checker 通过。
    - `make test-one TEST=src/numuya/_tests/test_io_npy.uya` -> 4 个测试通过。
    - `make test-one TEST=src/numuya/_tests/test_shape.uya` -> 8 个测试通过。

## Phase 16: `.npy` I/O

- [x] TDD: `load_npy_f64`。
  - magic/header 解析。
  - shape 正确。
  - 数据正确。
  - 验证：`make test-one TEST=src/numuya/_tests/test_io_npy.uya` -> 7 个测试通过。
  - 验证：`../uya/bin/uya check src/numuya/io_npy.uya --manifest-path uya.toml` -> checker 通过。
## Phase 16: `.npy` I/O

- [x] TDD: `save_npy_f64`。
  - 保存后再加载 roundtrip。
  - 验证：`make test-one TEST=src/numuya/_tests/test_io_npy.uya` — 8/8 通过。
  - 回归验证：`make test` — 全量测试通过。

## Phase 16: `.npy` I/O

- [x] TDD: unsupported dtype 返回 `NumuyaUnsupportedDType`。
  - 说明：新增 unsupported dtype 回归测试直接通过，当前实现无需生产代码改动。
  - 验证：`python3 tests/fixtures/npy/generate.py` -> exit 0。
  - 验证：`python3 tests/fixtures/npy/verify.py` -> `verified 4 npy fixtures`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_io_npy.uya` -> 9/9 通过，新增 unsupported dtype 用例通过。
  - 验证：`../uya/bin/uya check src/numuya/io_npy.uya --manifest-path uya.toml` -> checker 通过。

## Phase 16: `.npy` I/O

- [x] 验收：`src/numuya/_tests/test_io_npy.uya` 绿。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_io_npy.uya` — 9/9 通过。
  - 回归验证：`make test` — 全量测试通过。

# NumUya TDD Todo
## Phase 17: Advanced indexing

- [x] 写 `src/numuya/_tests/test_advanced_indexing.uya`。
  验证：
  `../uya/bin/uya check src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` -> 通过
  `../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` -> 1 passed, 0 failed

## Phase 17: Advanced indexing

- [x] TDD: `take` 1-D。
  - 说明：新增 1-D `take` 测试，支持 rank-1 输入，按归一化后的 axis 选择并复制元素。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 2/2 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_indexing.uya --manifest-path uya.toml` — 6/6 通过。
  - 检查：`../uya/bin/uya check src/numuya/indexing.uya --manifest-path uya.toml` — checker 通过。

## Phase 17: Advanced indexing

- [x] TDD: `take` axis 0/1。
  - 说明：为二维 `take` 新增 axis 0 行选择和 axis 1 列选择测试，并将实现扩展为按输出坐标映射回源坐标的通用 rank 复制路径。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 4/4 通过。
  - 回归验证：`../uya/bin/uya check src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — checker 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_indexing.uya --manifest-path uya.toml` — 6/6 通过。

## Phase 17: Advanced indexing

- [x] TDD: boolean mask 1-D。
  - 新增测试：`src/numuya/_tests/test_advanced_indexing.uya` 添加 `boolean_mask selects true entries from 1-D vector`，验证 `[true, false, true, false, true, false]` 会从 `[10, 20, 30, 40, 50, 60]` 选出 `[10, 30, 50]`。
  - 实现：`src/numuya/indexing.uya` 新增导出 `boolean_mask<T>(allocator, a, mask)`，当前支持 1-D 输入与 1-D mask；mask 长度不一致返回 `NumuyaShapeMismatch`。同时加入 `Storage<bool>` materialization workaround，修复不含 bool fixture 的目标在 codegen 阶段缺少 `bool` 特化定义的问题。
  - 失败确认：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 失败，新增测试中的 `try boolean_mask<f64>(...)` 报 `try` 操作数不是错误联合类型，说明 API 尚未实现。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — checker 通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 5/5 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_indexing.uya --manifest-path uya.toml` — 6/6 通过。
## Phase 17: Advanced indexing

- [x] TDD: boolean mask shape mismatch。
  - 新增测试：`src/numuya/_tests/test_advanced_indexing.uya` 添加 `boolean_mask reports shape mismatch for rank-mismatched mask`，验证 1-D 向量配 2-D 布尔 mask 会返回 `NumuyaShapeMismatch`。
  - 实现：`src/numuya/indexing.uya` 调整 `boolean_mask<T>` 前置校验，先比较完整 shape；shape 不一致统一返回 `NumuyaShapeMismatch`，只有 shape 相等但当前仍不支持的非 1-D 输入才返回 `NumuyaInvalidArgument`。
  - 失败确认：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 新增用例失败，当前实现把 rank 不匹配报成 `NumuyaInvalidArgument`，未命中预期 `NumuyaShapeMismatch`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — checker 通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 6/6 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_indexing.uya --manifest-path uya.toml` — 6/6 通过。
  - 回归验证：`make test` — 全量测试通过。

## Phase 17: Advanced indexing

- [x] TDD: fancy indexing copy 语义。
  - 新增测试：`src/numuya/_tests/test_advanced_indexing.uya` 添加 `fancy indexing returns writeable copies with independent storage`，验证 `take`/`boolean_mask` 返回可写、自有 storage 的副本，并且源与结果互不影响。
  - 失败确认：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 新增用例直接通过，说明现有实现已满足 copy 语义，无需生产代码改动。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — checker 通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml` — 7/7 通过。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_indexing.uya --manifest-path uya.toml` — 6/6 通过。
  - 回归验证：`../uya/bin/uya check src/numuya/indexing.uya --manifest-path uya.toml` — checker 通过。

## Phase 17: Advanced indexing

- [x] 验收：advanced indexing tests 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml`
  - 结果：7/7 tests passed
  - 回归测试：test_indexing.uya (6/6), test_slicing.uya (10/10), test_shape.uya (8/8), test_array_creation.uya (6/6), test_storage.uya (7/7) 均通过

## Phase 17: Advanced indexing

- [x] 验收：advanced indexing tests 绿。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_advanced_indexing.uya --manifest-path uya.toml`
  - 结果：7/7 tests passed, 0 failed

## Phase 18: DType 与 type-erased ArrayAny

- [x] 写 `src/numuya/_tests/test_dtype.uya`。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_dtype.uya --manifest-path uya.toml`
  - 结果：测试文件已创建；因 `src/numuya/types.uya` 尚未实现，类型检查失败（预期内的 TDD 失败）。失败摘要：`DTypeKind` 非枚举 / `array_any_try_as_f64` 非错误联合。

## Phase 18: DType 与 type-erased ArrayAny

- [x] 实现 `src/numuya/types.uya`。
  - 验证：
    ```bash
    ../uya/bin/uya test src/numuya/_tests/test_dtype.uya --manifest-path uya.toml
    make test
    ```
  - 结果：`test_dtype.uya` 9/9 通过；`make test` 全绿。

## Phase 18: DType 与 type-erased ArrayAny

- [x] 实现 `src/numuya/types.uya`。
  - 实现：`src/numuya/types.uya` 新增 `DTypeKind`、`Endian`、`DType` 枚举，导出 `dtype_f64/f32/i64/i32/u8`、`dtype_size`、`dtype_name`、`dtype_kind`、`dtype_endian`，以及 `ArrayAny` 结构与 `array_any_from_f64`、`array_any_shape`、`array_any_try_as_f64/f32/i32`。
  - 验证命令：
    - `../uya/bin/uya check src/numuya/types.uya --manifest-path uya.toml` — 类型检查通过

## Phase 18: DType 与 type-erased ArrayAny

- [x] TDD: `DType` size/name/endian helpers。
  - 说明：本轮进入任务时，`src/numuya/types.uya` 已导出 `DTypeKind`、`Endian`、`DType` 枚举及 `dtype_size`、`dtype_name`、`dtype_kind`、`dtype_endian`；`src/numuya/_tests/test_dtype.uya` 已包含针对 f64/f32/i64/i32/u8 的 size/name/endian/kind 测试。本轮未修改生产代码，仅验证并通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_dtype.uya --manifest-path uya.toml`
  - 验证结果：9/9 测试通过，0 失败。
  - 回归验证：`make test` 全量测试通过。

## Phase 18: DType 与 type-erased ArrayAny

- [x] TDD: `ArrayAny` 包装 `Array<f64>`。
  - 说明：本轮进入任务时，`src/numuya/types.uya` 已导出 `ArrayAny` 结构及 `array_any_from_f64`、`array_any_shape`、`array_any_try_as_f64/f32/i32`；`src/numuya/_tests/test_dtype.uya` 已包含 `ArrayAny wraps Array<f64> and preserves shape and data`、`ArrayAny try_as_f32 on f64 array returns unsupported dtype`、`ArrayAny try_as_i32 on f64 array returns unsupported dtype` 测试。本轮未修改生产代码，仅验证并通过。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_dtype.uya --manifest-path uya.toml`
  - 验证结果：9/9 测试通过，0 失败（含 3 个 ArrayAny 相关测试）。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_io_npy.uya --manifest-path uya.toml` — 9/9 通过。
  - 回归验证：`make test` 全量测试通过。

## Phase 18: DType 与 type-erased ArrayAny

- [x] TDD: `ArrayAny` 包装 `Array<f64>`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_dtype.uya --manifest-path uya.toml`
  - 验证结果：9/9 测试通过，0 失败（含 3 个 ArrayAny 相关测试）。
  - 回归验证：`../uya/bin/uya test src/numuya/_tests/test_io_npy.uya --manifest-path uya.toml` — 9/9 通过。

## Phase 18: DType 与 type-erased ArrayAny

- [x] TDD: dtype mismatch 返回 `NumuyaUnsupportedDType` 或 `NumuyaInvalidArgument`。
  - 实现：`src/numuya/types.uya` 扩展 `ArrayAny` 支持 f64/f32/i32/i64/u8 五种 dtype；新增 `array_any_from_f32/i32/i64/u8` 与 `array_any_try_as_f64/f32/i32/i64/u8`；dtype 不匹配时统一返回 `error.NumuyaUnsupportedDType`。
  - 测试：`src/numuya/_tests/test_dtype.uya` 新增 f32/i32 roundtrip 与 f32/i32/i64/u8 mismatch 测试。
  - 验证命令：`make test-one TEST=src/numuya/_tests/test_dtype.uya`（15/15 通过），`make test`（全量测试通过，I/O 回归绿）。

## Phase 18: DType 与 type-erased ArrayAny

- [x] 把 `.npy` 逐步扩展到 f32/i32/i64/u8。
  - 新增 fixture：`tests/fixtures/npy/generate.py` 生成 f32/i32/i64/u8 的 1D/2D/empty npy。
  - 新增测试：`src/numuya/_tests/test_io_npy.uya` 覆盖加载 fixture、跨 dtype 拒绝、save/load roundtrip。
  - 实现：`src/numuya/io_npy.uya` 新增 `save_npy_f32/load_npy_f32`、`save_npy_i32/load_npy_i32`、`save_npy_i64/load_npy_i64`、`save_npy_u8/load_npy_u8`；重构 header/descr 校验以支持多 dtype（u8 同时兼容 numpy 的 `|u1` 与 `<u1`）。
  - 验证命令：
    - `make test-one TEST=src/numuya/_tests/test_io_npy.uya`：27/27 通过。
    - `make test-one TEST=src/numuya/_tests/test_dtype.uya`：15/15 通过。
    - `make test`：全绿，无失败。
- [x] 验收：dtype tests 绿，I/O 回归绿。

## Phase 19: SIMD 与性能

- [x] 写 `src/numuya/_tests/test_simd_equivalence.uya`。
  - 交付物：`src/numuya/_tests/test_simd_equivalence.uya`
  - 新增测试覆盖：
    - `simd add_f64 matches scalar add_f64 on vector-width multiples`
    - `simd add_f64 matches scalar add_f64 with non-multiple tail`
    - `simd mul_f64 matches scalar mul_f64 on vector-width multiples`
    - `simd mul_f64 matches scalar mul_f64 with non-multiple tail`
    - `simd sum_all_f64 matches scalar sum_all_f64 on vector-width multiples`
    - `simd sum_all_f64 matches scalar sum_all_f64 with non-multiple tail`
    - `simd paths reject non-contiguous transpose input`
  - 测试期望新增 SIMD 专用 API：`ufunc.add_f64_scalar`、`ufunc.add_f64_simd`、`ufunc.mul_f64_scalar`、`ufunc.mul_f64_simd`、`reductions.sum_all_f64_scalar`、`reductions.sum_all_f64_simd`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_simd_equivalence.uya --manifest-path uya.toml`
  - 验证结果：测试文件自身无结构/导入错误；因 SIMD 专用函数尚未实现，类型检查阶段按预期失败（`模块不存在`）。


## Phase 19: SIMD 与性能

- [x] 为 add/mul/sum 增加 SIMD fast path。
- [x] TDD: SIMD path 与标量 path 结果一致。
- [x] TDD: 长度不是 vector width 倍数时尾部正确。
- [x] TDD: 非 contiguous 输入仍走标量 path。
- [x] 验收：correctness tests 全绿。

验证记录：
- 聚焦测试：
  ```bash
  ../uya/bin/uya test src/numuya/_tests/test_simd_equivalence.uya --manifest-path uya.toml
  ```
  结果：7 tests passed, 0 failed。
- 相关回归测试：
  ```bash
  ../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml
  ../uya/bin/uya test src/numuya/_tests/test_reductions.uya --manifest-path uya.toml
  ```
  结果：ufunc 20/20 passed；reductions 23/23 passed。
- 全量 correctness tests：
  ```bash
  make test
  ```
  结果：全部 20 个测试文件通过，exit code 0。

实现要点：
- 新增 `src/numuya/simd_stub.c`，使用 AVX2 intrinsics（4-wide f64）并提供运行时 `__builtin_cpu_supports("avx2")` 检测；非 x86_64 平台回退到标量循环。
- `src/numuya/ufunc.uya` 新增 `add_f64_scalar`、`add_f64_simd`、`mul_f64_scalar`、`mul_f64_simd`；公共 `add_f64`/`mul_f64` 在 contiguous 时走 SIMD fast path，否则保持原标量 stride path。
- `src/numuya/reductions.uya` 新增 `sum_all_f64_scalar`、`sum_all_f64_simd`；公共 `sum_all_f64` 在 contiguous 时走 SIMD fast path。
- `src/numuya/errors.uya` 新增 `NumuyaNotContiguous`；`_simd` 变体对非 contiguous 输入返回该错误。
- 修复 `src/numuya/_tests/test_simd_equivalence.uya` 中的 Uya 语法问题（模块前缀调用、`array_size` 泛型参数、helper 函数返回 codegen 问题），并补充 `force_storage_release_usize` 以触发 Uya 生成所需 `Storage<usize>` release 函数。


## Phase 19: SIMD 与性能

- [x] 添加 benchmark，但 benchmark 不代替测试。
  - 交付物：
    - `src/numuya/_benchmarks/bench_simd.uya`：测量 `add_f64`/`mul_f64`/`sum_all_f64` 标量与 SIMD 路径的耗时与加速比。
    - `Makefile` 新增 `bench` target，遍历 `src/numuya/_benchmarks/bench_*.uya`。
  - 验证命令：
    - `make bench`
    - `../uya/bin/uya run src/numuya/_benchmarks/bench_simd.uya --manifest-path uya.toml`
    - `make test`
  - 验证结果：
    - `make bench` 成功输出（示例）：add_f64 speedup≈1.73x，mul_f64 speedup≈1.75x，sum_all_f64 speedup≈2.19x。
    - `make test` 全部通过，无失败。

## Phase 20: CUDA backend 基础

- [x] 写 `src/numuya/_tests/test_cuda_driver.uya`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`
  - 结果：文件已创建；`uya check` 因依赖模块 `backend` 与 `cuda/driver` 尚未实现而失败，属于预期失败，文件本身词法/语法解析通过。


## Phase 20: CUDA backend 基础

- [x] 写 `src/numuya/_tests/test_cuda_driver.uya`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`
  - 结果：文件已创建；`uya check` 因依赖模块 `backend` 与 `cuda/driver` 尚未实现而失败，属于预期失败，文件本身词法/语法解析通过。


## Phase 20: CUDA backend 基础

- [x] 创建 `src/numuya/backend.uya`。
  - 实现：新增 `src/numuya/backend.uya`，导出 `BackendKind` 枚举（`Auto`、`Cpu`、`Cuda`）、`BackendState` 结构体，以及 `backend_is_cuda_available`、`backend_init`、`backend_deinit` 占位实现，供后续 TDD 任务填充 CUDA 相关逻辑。
  - 验证命令：
    - `../uya/bin/uya check src/numuya/backend.uya --manifest-path uya.toml` — 类型检查通过

## Phase 20: CUDA backend 基础

- [x] 创建 `src/numuya/cuda/driver.uya`。
  - 实现：
    - 新增 `src/numuya/cuda/driver.uya`，导出 `CudaDevice` 结构体、`cuda_init()`、`cuda_get_device(ordinal)`，以及错误 `NumuyaGpuUnavailable` / `NumuyaCudaError`。
    - 新增 `src/numuya/cuda/driver_stub.c`，通过 `dlopen`/`dlsym` 运行时动态加载 `libcuda.so.1`，避免 `make test` 默认路径产生硬链接依赖；CUDA 不可用时返回 `NUMUYA_CUDA_UNAVAILABLE`，Driver API 调用失败返回 `NUMUYA_CUDA_ERROR`。
    - `src/numuya/errors.uya` 新增 `NumuyaGpuUnavailable`、`NumuyaCudaError` 两个共享错误。
    - 修复 `src/numuya/_tests/test_cuda_driver.uya` 中不支持的 `match result { ok => {} else => {} }` 语法，改为 Uya 支持的 `_ = result catch {};`。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 6/6 通过
    - `../uya/bin/uya test src/numuya/_tests/test_linalg.uya --manifest-path uya.toml` — 30/30 通过
    - `../uya/bin/uya test src/numuya/_tests/test_array_creation.uya --manifest-path uya.toml` — 6/6 通过
    - `LDFLAGS="-lcuda" NUMUYA_CUDA_REQUIRED=1 ../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 6/6 通过

## Phase 20: CUDA backend 基础

- [x] 创建 CUDA 测试命令约定。
  - `make test` 默认不要求 GPU，且依赖 `make bootstrap-upm`。
  - `make test-cuda` 依赖 `make bootstrap-upm`，设置 `NUMUYA_CUDA_REQUIRED=1` 并链接 `-lcuda`。
  - `make test-cuda-vendor` 依赖 `make bootstrap-upm`，额外链接 `-lcublasLt -lcublas -lcufft -lcurand`。
  - 无 Makefile 时直接命令为 `test -x ../uya/bin/cmd/upm || make -C ../uya cmd-upm` 后执行 `LDFLAGS="-lcuda" NUMUYA_CUDA_REQUIRED=1 ../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`。

验证：
- `make test` 通过且未运行 CUDA 测试（退出码 0）。
- `make test-cuda` 在 RTX 3060 上通过 6/6 测试，链接 `-lcuda`。
- `make test-cuda-vendor` 在 RTX 3060 上通过 6/6 测试，链接 `-lcublasLt -lcublas -lcufft -lcurand -lcuda`。

## Phase 20: CUDA backend 基础

- [x] TDD: `backend_is_cuda_available()`。
  - 本机 RTX 3060 应返回 true。
  - 无 CUDA 环境时不能崩溃。
  - 实现改动：
    - `src/numuya/backend.uya` 新增 `use cuda.driver;`，`backend_is_cuda_available()` 通过 `cuda_init()` 是否成功判断 CUDA 可用性，出错时返回 false 不崩溃。
    - `src/numuya/cuda/driver_stub.c` 优先加载 `cuDeviceTotalMem_v2`，否则回退 `cuDeviceTotalMem`，修复 RTX 3060 显存识别为 4GB 的问题。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 6/6 通过
    - `make test` — 非 CUDA 测试全部通过
    - `make test-cuda` — RTX 3060 上 6/6 通过


## Phase 20: CUDA backend 基础

- [x] TDD: `cuda_init()`。
  - 成功时返回 ok。
  - driver 初始化失败映射为 `NumuyaGpuUnavailable` 或 `NumuyaCudaError`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`
  - 验证结果：6/6 测试通过，0 失败（含 `cuda_init succeeds when cuda is available and errors gracefully otherwise`）。


## Phase 20: CUDA backend 基础

- [x] TDD: `cuda_init()`。
  - 成功时返回 ok。
  - driver 初始化失败映射为 `NumuyaGpuUnavailable` 或 `NumuyaCudaError`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`
  - 验证结果：6/6 测试通过，0 失败（含 `cuda_init succeeds when cuda is available and errors gracefully otherwise`）。

## Phase 20: CUDA backend 基础

- [x] TDD: `cuda_get_device(0)`。
  - device ordinal 是 0。
  - compute capability 应识别为 Ampere `sm_86` 或至少 major/minor 非 0。
  - total memory 应大于 8GB。
  - 验证命令：
    ```bash
    make test-cuda TEST=src/numuya/_tests/test_cuda_driver.uya
    ```
  - 验证结果：通过 6/6 tests；`cuda_get_device(0)` 返回 ordinal=0、major/minor 非 0、total_memory_bytes > 8 GiB。


## Phase 20: CUDA backend 基础

- [x] TDD: `backend_init` / `backend_deinit`。
  - 验证：`TEST=src/numuya/_tests/test_cuda_driver.uya make test-one` 11/11 通过；`make test` 非 CUDA 测试全绿；`make test-cuda` RTX 3060 上 11/11 通过。

## Phase 20: CUDA backend 基础

- [x] TDD: `cuda_create_context` / destroy。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml`
  - 结果：14/14 测试通过，新增 `cuda_create_context(0) returns non-zero handle when cuda is available`、`cuda_destroy_context returns error for null handle`、`cuda_create_context returns error when cuda is unavailable` 均通过。

## Phase 20: CUDA backend 基础

- [x] TDD: `cuda_create_stream` / synchronize / destroy。
  - 验证命令：`make test-cuda TEST=src/numuya/_tests/test_cuda_driver.uya`
  - 结果：18 tests passed, 0 failed
  - 改动文件：`src/numuya/cuda/driver.uya`、`src/numuya/cuda/driver_stub.c`、`src/numuya/_tests/test_cuda_driver.uya`

## Phase 20: CUDA backend 基础

- [x] TDD: context current 规则。
  - 任意 Driver API wrapper 调用前设置正确 context。
  - 跨 backend stream 使用返回 `NumuyaDeviceMismatch`。
  - 新增错误：`src/numuya/errors.uya` 添加 `NumuyaDeviceMismatch`。
  - 新增 Driver API：`src/numuya/cuda/driver.uya` 添加 `cuda_set_current_context`，并修改 `cuda_create_stream`/`cuda_synchronize_stream`/`cuda_destroy_stream` 为 context-aware API，调用前通过 stub 设置当前 context；跨 context stream 操作返回 `NumuyaDeviceMismatch`。
  - 更新 stub：`src/numuya/cuda/driver_stub.c` 动态加载 `cuCtxSetCurrent`，维护 stream 到 context 的映射，在 stream 操作前 set current context 并检测 mismatch。
  - 更新 backend：`src/numuya/backend.uya` 中 `backend_init(Cuda)`/`backend_init(Auto)` 创建 context 和 stream，`backend_deinit` 按正确顺序销毁 stream 和 context。
  - 新增测试：`src/numuya/_tests/test_cuda_driver.uya` 添加：
    - `cuda_synchronize_stream returns NumuyaDeviceMismatch for cross context stream`
    - `backend_init with Cuda kind creates context and stream`
    - `cross backend stream use returns NumuyaDeviceMismatch`
  - 验证命令：
    - `make test-cuda TEST=src/numuya/_tests/test_cuda_driver.uya` — 21/21 通过
    - `make test-cuda-vendor TEST=src/numuya/_tests/test_cuda_driver.uya` — 21/21 通过
    - `make test` — 非 CUDA 测试全绿，exit code 0
## Phase 20: CUDA backend 基础

- [x] 验收：`src/numuya/_tests/test_cuda_driver.uya` 在本机 RTX 3060 上绿；没有 CUDA 时测试可标记 skip 或返回明确错误。
  - 验证命令：`make test-cuda TEST=src/numuya/_tests/test_cuda_driver.uya`
  - 验证结果：21/21 tests passed on RTX 3060


## Phase 21: CUDA DeviceArray 与拷贝

- [x] 写 `src/numuya/_tests/test_cuda_device_array.uya`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml`
  - 结果：checker 通过，类型检查通过。
  - 验证命令：`NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" ../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml`
  - 结果：编译、链接、运行均成功；7 个测试全部按预期失败（ERROR），因为本轮仅交付测试文件及最小可编译骨架，`src/numuya/cuda/memory.uya` 与 `src/numuya/cuda/device_array.uya` 尚未实现真正的 CUDA 设备内存分配/释放与拷贝。



## Phase 21: CUDA DeviceArray 与拷贝

- [x] 实现 `src/numuya/cuda/memory.uya`。
  - 实现 `MemoryPool` 预算跟踪：新增 `AllocationNode` 链表记录每次 `cuda_malloc` 的 `(ptr, size)`，`cuda_free` 按指针查找并扣减 `used_bytes`。
  - `cuda_malloc` 在 `used_bytes + size > budget_bytes` 时返回 `NumuyaGpuOutOfMemory`；否则通过 `cuda_driver_malloc` 调用 CUDA driver 的 `cuMemAlloc`。
  - `cuda_free` 处理 `null` 指针、查找失败返回 `NumuyaInvalidArgument`、成功时释放 device memory 并归还节点。
  - 为支持无显式 context 的测试场景，同步扩展 `src/numuya/cuda/driver_stub.c` 与 `src/numuya/cuda/driver.uya`：
    - `driver_stub.c` 动态加载 `cuMemAlloc`/`cuMemFree`，并在 `numuya_cuda_init` 时为 device 0 创建默认 context。
    - `driver.uya` 导出 `cuda_driver_malloc`/`cuda_driver_free` 供 `memory.uya` 使用。
  - 验证命令：
    - `../uya/bin/uya check src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` — 类型检查通过
    - `NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" ../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` — 7 个测试中 `cuda_malloc`/`cuda_free` 相关 2 个通过（其余 5 个依赖尚未实现的 `device_array.uya`）
    - `make test` — 全部非 CUDA 测试文件通过

## Phase 21: CUDA DeviceArray 与拷贝

- [x] 实现 `src/numuya/cuda/device_array.uya`。
  - 验证：`make test-cuda` 通过（`test_cuda_device_array.uya` 7/7，`test_cuda_driver.uya` 21/21）；`make test` 通过。
  - 实现要点：补全 `DeviceStorage<T>` 分配/释放、`DeviceArray<T>` 构造/视图、H2D/D2H 拷贝；在 `cuda/driver.uya` 与 `driver_stub.c` 新增 `cuda_memcpy_htod/dtoh` 绑定；修复 `test_cuda_device_array.uya` 中 H2D/D2H 测试使用 `get1` 访问 rank-2 数组的笔误，改为 `getn`。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: `cuda_malloc/cuda_free`。
  - 申请 1MB 成功。
  - 超过 budget 返回 `NumuyaGpuOutOfMemory`。
  - 验证命令：`make test-cuda TEST=src/numuya/_tests/test_cuda_device_array.uya`
  - 验证结果：7 tests passed, 0 failed（其中 `cuda_malloc allocates 1MB from pool and cuda_free releases it` 与 `cuda_malloc returns NumuyaGpuOutOfMemory when exceeding budget` 通过）。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: `DeviceStorage<T>` 引用计数。
  - `device_storage_new` 初始 ref_count 为 1。
  - `device_storage_retain` 增加计数。
  - `device_storage_release` 非最后引用只减计数。
  - 最后引用释放 device memory，并更新 memory pool。
  - 实现位置：`src/numuya/cuda/device_array.uya` 中 `DeviceStorage<T>` 结构、`device_storage_new<T>`、`device_storage_retain<T>`、`device_storage_release<T>`；底层 device memory 分配/释放由 `src/numuya/cuda/memory.uya` 的 `MemoryPool` 跟踪。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` — 7/7 通过（含 `device_storage_new starts with ref_count 1`、`device_storage_retain increments ref_count`、`device_storage_release does not free device memory on non-final release`）
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_driver.uya --manifest-path uya.toml` — 21/21 通过，回归通过
    - `../uya/bin/uya test src/numuya/_tests/test_shape.uya --manifest-path uya.toml` — 8/8 通过
    - `../uya/bin/uya test src/numuya/_tests/test_storage.uya --manifest-path uya.toml` — 7/7 通过
    - `../uya/bin/uya test src/numuya/_tests/test_array_creation.uya --manifest-path uya.toml` — 6/6 通过

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: device view 语义。
  - `device_array_view` retain 同一 storage。
  - view drop 不释放 owner 的 buffer。
  - owner 和 view 全部 drop 后只释放一次。
  - 验证：
    - `make test-one TEST=src/numuya/_tests/test_cuda_device_array.uya`
    - 8 tests passed, 0 failed（含新增 `device_array owner and view drop releases buffer exactly once`）。
    - `make test-one TEST=src/numuya/_tests/test_cuda_driver.uya`
    - 21 tests passed, 0 failed。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: H2D/D2H copy。
  - host `Array<f64>` -> `DeviceArray<f64>` -> host。
  - 数据逐元素一致。
  - stream synchronize 后结果稳定。
  - 实现：
    - `src/numuya/cuda/driver_stub.c` 动态加载 `cuMemcpyHtoDAsync_v2` / `cuMemcpyDtoHAsync_v2`。
    - `src/numuya/cuda/driver.uya` 导出 `cuda_memcpy_htod_async` / `cuda_memcpy_dtoh_async`。
    - `src/numuya/cuda/device_array.uya` 为 `DeviceArray<T>` 增加 `context` / `stream` 字段；`device_array_from_host` / `device_array_to_host` 改用异步拷贝并在返回前 `cuda_synchronize_stream`。
    - `src/numuya/_tests/test_cuda_device_array.uya` 更新 `device_array_new` 调用并新增显式 stream synchronize 后的逐元素断言。
  - 验证：
    ```bash
    TEST=src/numuya/_tests/test_cuda_device_array.uya make test-one
    make test-cuda
    make test
    ```
  - 结果：聚焦测试 8/8 通过；CUDA 测试套件 29/29 通过；非 CUDA 测试套件全部通过。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: `device_empty_f64/device_zeros_f64`。
  - 新增测试：`src/numuya/_tests/test_cuda_device_array.uya`
    - `device_empty_f64 creates f64 device array with requested shape`
    - `device_zeros_f64 creates f64 device array filled with zeros`
  - 实现：`src/numuya/cuda/device_array.uya`
    - `device_empty_f64`：分配未初始化的 f64 设备数组。
    - `device_zeros_f64`：通过主机侧 `zeros_f64` + H2D 拷贝生成全零设备数组。
  - 验证命令：
    - `NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" ../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml`
    - `make test-cuda`
    - `make test`
  - 验证结果：
    - `test_cuda_device_array.uya`：10/10 通过（含新增 2 个测试）。
    - `make test-cuda`：31/31 通过（device_array 10 + driver 21）。
    - `make test`：所有非 CUDA 测试通过，无回归。


## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: shape/stride/flags 在 device array 上保持一致。
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` → 14/14 passed
    - `make test-cuda` → 全部 CUDA 测试通过
    - `make test` → 全部非 CUDA 测试通过
  - 改动摘要：
    - `DeviceArray<T>` 新增 `strides: Strides` 与 `flags: ArrayFlags` 字段。
    - 新增 `make_owned_device_flags` 与复用 `stride.c_order_strides`，确保 owner array 的 strides/flags 与 host `Array<T>` 一致。
    - `device_array_view` 继承 strides/flags 并将 `owns_data` 置为 `false`。
    - 更新 `device_array_new`、`device_empty_f64`、`device_zeros_f64`、`device_array_from_host`、`device_array_view` 以填充新字段。
    - 在 `test_cuda_device_array.uya` 新增 4 个测试覆盖 owner/view/zeros/empty 的 strides 与 flags 一致性。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] TDD: memory pool 统计。
  - alloc 后 used 增加。
  - free 后 used 减少。
  - 真实 allocation 改变 `live_allocations`，view retain/drop 不改变。
  - 验证：`../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` 通过 16/16（CUDA 不可用时测试 early-return，但仍编译链接并执行通过）。

## Phase 21: CUDA DeviceArray 与拷贝

- [x] 验收：`src/numuya/_tests/test_cuda_device_array.uya` 绿。
  - 验证命令：`NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcublasLt -lcublas -lcufft -lcurand -lcuda" ../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml`
  - 结果：16 tests passed, 0 failed。

## Phase 22: CUDA ufunc 与 reduction

- [x] 写 `src/numuya/_tests/test_cuda_ufunc.uya`。
  - 验证命令：`../uya/bin/uya check src/numuya/_tests/test_cuda_ufunc.uya --manifest-path uya.toml`
  - 结果：TDD 预期失败（exit code 1）。
  - 关键错误：
    - `test_cuda_ufunc.uya:(8:1): 错误: 模块中未找到导出项`（`use cuda.ufunc;` 引用的模块不存在）。
    - `try 的操作数必须是错误联合类型 !T`（`gpu_add_f64`、`gpu_mul_f64` 未定义）。
  - 失败原因/后续重开条件：需先实现 `src/numuya/cuda/ufunc.uya` 并提供 `gpu_add_f64` 与 `gpu_mul_f64`，之后本测试文件应能编译并进入运行时验证。

## Phase 22: CUDA ufunc 与 reduction

- [x] 写 `src/numuya/_tests/test_cuda_ufunc.uya`。
  - 验证：`ls -la src/numuya/_tests/test_cuda_ufunc.uya` 确认文件存在，包含 5 个测试用例：
    - `gpu_add_f64 contiguous matches CPU add_f64`
    - `gpu_mul_f64 contiguous matches CPU mul_f64`
    - `gpu_add_f64 broadcasts row vector across matrix`
    - `gpu_add_f64 handles non-contiguous transpose input`
    - `gpu_add_f64 output is a new owner independent of inputs`
  - 说明：测试文件按 TDD 先写，引用尚未实现的 `cuda.ufunc` API；完整编译/运行需等待后续 `cuda/ufunc.uya` 与 kernels 实现。

## Phase 22: CUDA ufunc 与 reduction

- [x] 写 `src/numuya/_tests/test_cuda_reductions.uya`。
  - 验证命令：`../uya/bin/uya test src/numuya/_tests/test_cuda_reductions.uya --manifest-path uya.toml`
  - 结果：编译失败，符合 TDD 预期。核心错误为 `test_cuda_reductions.uya:(7:1): 错误: 模块中未找到导出项`，即 `cuda.reductions` 模块尚未实现；后续实现该模块后测试应通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] 实现 `src/numuya/cuda/module.uya` 和 `kernels.uya`。
  - 验证：`../uya/bin/uya check src/numuya/cuda/module.uya --manifest-path uya.toml` 与 `../uya/bin/uya check src/numuya/cuda/kernels.uya --manifest-path uya.toml` 类型检查通过；`../uya/bin/uya test src/numuya/_tests/test_cuda_module.uya --manifest-path uya.toml` 4/4 通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: `make cuda-ptx-embed` 或等价命令。
  - PTX 文本嵌入到 `kernels_ptx.uya`。
  - 生成结果稳定可重复。
  - 实现：`Makefile` 新增 `.PHONY` 目标 `cuda-ptx-embed`，调用 `../uya/bin/uya run src/numuya/_tools/embed_ptx.uya --manifest-path uya.toml`。
  - 测试：`src/numuya/_tests/test_ptx_embed.uya` 新增 3 个测试：
    - `make cuda-ptx-embed succeeds`
    - `embedded PTX begins with .version 7.8`
    - `embedded PTX contains expected kernel entries`
  - 验证命令：
    - `../uya/bin/uya test src/numuya/_tests/test_ptx_embed.uya --manifest-path uya.toml` — 3/3 通过
    - `make test` — 全部非 CUDA 测试文件通过
    - `make cuda-ptx-embed` 连续运行两次，`src/numuya/cuda/kernels_ptx.uya` sha256 均为 `26ae5abe809388639964a6b752f32e126760c7e9e606eb3f08a8d3a4841b0787`

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: `make cuda-ptx-validate` 或等价命令。
  - `ptxas -arch=sm_86` 校验通过。
  - cubin cache 不是唯一 source-of-truth。
  - 验证命令：
    - `make cuda-ptx-validate`
    - `../uya/bin/uya test src/numuya/_tests/test_ptx_embed.uya --manifest-path uya.toml`
    - `make test`
  - 关键改动：
    - 在 `Makefile` 新增 `cuda-ptx-validate` target，调用 `ptxas -arch=sm_86` 校验 `src/numuya/cuda/ptx/core_sm86.ptx`，并显式检查 cubin cache 不是唯一 source-of-truth。
    - 在 `src/numuya/_tests/test_ptx_embed.uya` 新增测试 `make cuda-ptx-validate assembles PTX for sm_86`。
    - 修正 `src/numuya/cuda/ptx/core_sm86.ptx` 中的寄存器声明语法：将 `.reg .u32 r32<4>` 等数组声明改为逐个寄存器声明（如 `.reg .u32 r32_0, r32_1, r32_2, r32_3`），使其符合 PTX 语法并通过 `ptxas` 校验。
    - 重新生成 `src/numuya/cuda/kernels_ptx.uya`。
  - 验证结果：
    - `make cuda-ptx-validate` 输出 `ptxas -arch=sm_86 OK`。
    - `test_ptx_embed.uya` 4 个测试全部通过。
    - `make test`（非 CUDA 测试）全部通过。
    - 相关 CUDA 测试 `test_cuda_driver.uya`、`test_cuda_device_array.uya`、`test_cuda_module.uya` 均通过。
    - 当前环境无 GPU，`test_cuda_ufunc.uya` 与 `test_cuda_reductions.uya` 因依赖尚未实现的 `cuda.ufunc` / `cuda.reductions` 模块而类型检查失败，与本任务无关。

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

## Phase 3: 创建数组与基础 get/set

- [x] TDD: `empty<T>`。
  - shape 正确。
  - size 正确。
  - contiguous flags 正确。
  - 不读取元素值。
  - 修复状态：当前 `creation.empty<T>`、`full<T>`、`from_slice<T>` 已能实例化 `Array<f64>`/`Storage<f64>`，旧的 C99 codegen blocker 未复现。
  - 验证：`make test-one TEST=src/numuya/_tests/test_array_creation.uya` 通过。

## Phase 10: Statistics

- [x] 写 `src/numuya/_tests/test_stats.uya`。
  - 覆盖：`var_all_f64`、`std_all_f64`、`percentile_f64` 的正常路径、空数组/非法参数，以及 non-contiguous transpose view。
  - 验证：`make test-one TEST=src/numuya/_tests/test_stats.uya` 通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] 创建 PTX source-of-truth。
  - `src/numuya/cuda/ptx/core_sm86.ptx`。
  - `src/numuya/cuda/kernels_ptx.uya` 由 `src/numuya/_tools/embed_ptx.uya` 生成。
  - 不创建必需 `.cu` 源，不把 `nvcc` 放进 TDD 主路径。
  - 修复：`embed_ptx.uya` 生成稳定的 PTX byte array，并追加 PTX 字符串加载所需的 trailing null byte。
  - 验证：
    - `make cuda-ptx-embed` 通过。
    - `make cuda-ptx-validate` 通过。
    - `make test-one TEST=src/numuya/_tests/test_ptx_embed.uya` 通过。

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: 加载 embedded PTX/cubin。
  - `sm_86` 优先。
  - PTX JIT fallback 可用。
  - 修复：`cuda_kernels_load` 优先尝试 embedded sm_86 cubin cache，失败或缺失时回退到 embedded PTX；`cuda.module` 新增 `cuda_module_load_data`，底层 Driver shim 统一走 `cuModuleLoadData`。
  - 验证：`make test-one TEST=src/numuya/_tests/test_cuda_module.uya` 通过。

# NumUya TDD Todo
## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: `gpu_add_f64` contiguous。
  - 与 CPU `add_f64` 完全同 shape，容差一致。
  - 验证：
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_ufunc.uya --manifest-path uya.toml`（聚焦运行：临时注释掉 gpu_mul_f64、broadcast、non-contiguous 测试）→ gpu_add_f64 相关 2 测试通过
    - `../uya/bin/uya test src/numuya/_tests/test_ufunc.uya --manifest-path uya.toml` → 20 passed, 0 failed
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_module.uya --manifest-path uya.toml` → 5 passed, 0 failed
    - `../uya/bin/uya test src/numuya/_tests/test_cuda_device_array.uya --manifest-path uya.toml` → 16 passed, 0 failed
  - 实现要点：新增 `src/numuya/cuda/ufunc.uya`，实现同 shape contiguous 路径；通过 `device_storage_retain` 绕过 Uya 返回时自动 drop 导致的 double free；CUDA kernel 参数按 driver API `void**` 约定传各参数变量的地址。

## Phase 22: CUDA ufunc 与 reduction

- [x] TDD: `gpu_mul_f64` contiguous。
  - 验证命令：`NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" ../uya/bin/uya test src/numuya/_tests/test_cuda_ufunc.uya --manifest-path uya.toml`
  - 结果：`gpu_mul_f64 contiguous matches CPU mul_f64 ... OK`
