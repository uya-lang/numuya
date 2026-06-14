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
