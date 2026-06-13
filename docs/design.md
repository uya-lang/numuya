# NumUya 设计文档

本文档定义 `numuya`：一个用纯 Uya 实现、接口尽量靠近 NumPy、但更符合 Uya 类型系统和错误处理习惯的 n 维数组与数值计算库。

当前阶段先写设计与 todo，后续所有实现必须按 TDD 执行：先写失败测试，再写最小实现，再补边界测试和重构。

## 1. 目标

### 1.1 总目标

- 用纯 Uya 复刻 NumPy 的核心能力：`ndarray`、shape/stride/view、broadcasting、ufunc、reduction、indexing、sorting/searching、linear algebra、random、FFT、`.npy` I/O。
- API 靠近 NumPy 的命名和语义，同时利用 Uya 的泛型、显式错误联合、无 GC、编译期安全证明和 SIMD 内建，做得更明确、更少魔法。
- 默认实现不依赖 Python、CPython C API、NumPy、BLAS、LAPACK、libm 或其他外部数值库。后续可加可选 backend，但纯 Uya backend 必须始终可用，且测试必须能只跑纯 Uya backend。
- 必须能充分使用本机 NVIDIA GeForce RTX 3060：提供 CUDA backend，热路径支持 device array、异步拷贝、memory pool、stream、fused elementwise、GPU reduction、GPU matmul、GPU random，并保留 CPU fallback。
- 错误全部显式返回 `!T`，不使用 panic 式控制流。
- 内存所有权、view 生命周期、shape 溢出、广播失败、axis 越界都必须有测试覆盖。

### 1.2 非目标

- 不实现 Python 解释器对象模型。
- 不支持 Python `object` dtype。
- 不追求逐字节兼容 NumPy 的每个异常文本。
- 不在核心库中偷偷 FFI 到 NumPy、BLAS 或平台私有库。
- 不为了跑过单个 benchmark 写特殊硬编码。

## 2. 项目布局

推荐仓库布局如下：

```text
numuya/
  docs/
    design.md
    todo.md
  src/
    numuya/
      types.uya
      errors.uya
      shape.uya
      storage.uya
      array.uya
      creation.uya
      indexing.uya
      stride.uya
      broadcast.uya
      ufunc.uya
      reductions.uya
      math.uya
      stats.uya
      sorting.uya
      linalg.uya
      random.uya
      fft.uya
      io_npy.uya
      testing.uya
      backend.uya
      cuda/
        driver.uya
        context.uya
        memory.uya
        module.uya
        stream.uya
        device_array.uya
        kernels.uya
        kernels_ptx.uya
        ufunc.uya
        reductions.uya
        linalg.uya
        random.uya
        ptx/
          core_sm86.ptx
          matmul_sm86.ptx
  tools/
    embed_ptx.uya
    ptx_validate.uya
  benchmarks/
    bench_cuda.uya
  tests/
    test_shape.uya
    test_storage.uya
    test_array_creation.uya
    test_indexing.uya
    test_stride_views.uya
    test_broadcast.uya
    test_ufunc.uya
    test_reductions.uya
    test_linalg.uya
    test_random.uya
    test_fft.uya
    test_io_npy.uya
    test_backend.uya
    test_cuda_driver.uya
    test_cuda_device_array.uya
    test_cuda_ufunc.uya
    test_cuda_reductions.uya
    test_cuda_linalg.uya
    test_cuda_random.uya
```

测试与示例从仓库根执行，模块根固定为 `src`：

```bash
../uya/bin/uya check tests/test_shape.uya --project-root src
../uya/bin/uya test tests/test_shape.uya --project-root src
../uya/bin/uya test tests/test_array_creation.uya --project-root src
```

如后续添加 `Makefile`，必须把上述命令封装为：

```bash
make test-one TEST=tests/test_shape.uya
make test
```

## 3. 模块与命名

模块路径以 `numuya.*` 为根：

```uya
use numuya.shape.Shape;
use numuya.array.Array;
use numuya.creation.zeros_f64;
use numuya.ufunc.add_f64;
use numuya.cuda.device_array.to_device_f64;
```

顶层聚合模块可以在后期添加，但早期实现优先直接导入具体文件模块，降低模块解析不确定性。

命名规则：

- 类型使用 `PascalCase`：`Array<T>`、`Shape`、`SliceSpec`。
- 函数使用 `snake_case`：`from_slice`、`zeros_f64`、`broadcast_shapes`。
- NumPy 同名函数尽量保留：`reshape`、`transpose`、`ravel`、`arange`、`linspace`、`matmul`、`sum`。
- Uya 无默认参数；NumPy 的默认参数拆成更明确的函数或配置结构。
- 早期对数值类型使用后缀特化：`sum_f64`、`add_i32`。泛型版本在编译器能力确认后补齐。

## 4. 核心语义

### 4.1 Array 是主要对象

`Array<T>` 对应 NumPy 的 `ndarray`：

- `T` 是编译期 dtype，例：`Array<f64>`、`Array<i32>`。
- shape 和 stride 是运行期元数据。
- data 由显式 allocator 管理。
- view 与 owner 共用同一个 storage，通过显式引用计数释放。
- 默认 C-order 行主序。

设计上不把 dtype 作为每个元素的运行期 tag。Uya 泛型是主要 dtype 机制，这比 NumPy 在 Python 层的动态 dtype 更简洁、更快，也更符合 Uya。

后期为了 `.npy` I/O、动态 dispatch、调试打印，可以添加：

```uya
enum DType {
    bool_,
    i8,
    i16,
    i32,
    i64,
    u8,
    u16,
    u32,
    u64,
    f32,
    f64,
    complex64,
    complex128,
}
```

动态 dtype 只用于元信息、I/O 和 type-erased wrapper，不替代 `Array<T>`。

### 4.2 Shape 与 rank

第一版使用固定上限 rank，降低内存管理复杂度：

```uya
const NUMUYA_MAX_DIMS: usize = 16;

export struct Shape {
    rank: usize,
    dims: [usize: 16],
}

export struct Strides {
    rank: usize,
    steps: [isize: 16],
}
```

约束：

- `rank <= NUMUYA_MAX_DIMS`，否则返回 `error.NumuyaRankTooLarge`。
- scalar 使用 `rank == 0`，`size == 1`。
- 空数组允许某个 dim 为 `0`，总元素数为 `0`。
- 所有 size 乘法必须检查溢出。
- 所有 axis 都支持负数风格 helper：`normalize_axis(axis, rank) !usize`，其中 `-1` 表示最后一维。

后续如果需要无限 rank，可在不破坏 API 的情况下把 `Shape` 内部换成小对象优化：短 shape 走内联数组，长 shape 走 heap。

### 4.3 Storage

`Storage<T>` 是数组数据的所有权对象：

```uya
export struct Storage<T> {
    allocator: IAllocator,
    data: &T,
    len: usize,
    ref_count: atomic usize,
}
```

`Array<T>` 保存指向 storage 的引用：

```uya
export struct Array<T> {
    storage: &Storage<T>,
    offset: isize,
    shape: Shape,
    strides: Strides,
    flags: ArrayFlags,
}
```

规则：

- 创建 owner 时 `ref_count = 1`。
- 创建 view 时调用 `storage_retain`。
- `Array<T>.drop` 调用 `storage_release`。
- release 后 `ref_count == 0` 时释放 data 和 storage header。
- 空数组可以有 `storage.data == null` 且 `storage.len == 0`，但 `storage` 本身仍然有效。
- `Array<T>` 不允许裸拷贝后两个 handle 都 drop 同一引用；需要复制 handle 时必须调用 `array_view` 或 `array_clone_ref` 一类显式 retain API。

这比“borrowed view 依赖调用方保证 owner 活着”更接近 NumPy，也更适合小模型实现时不踩 use-after-free。

### 4.4 Stride 与视图

元素地址按元素步长计算：

```text
physical_index = offset + sum(indices[i] * strides.steps[i])
```

约束：

- stride 单位是元素，不是字节。
- 正常 C-order contiguous stride：最后一维 stride 为 1，向前累乘。
- broadcast view 对 dim 为 1 的轴使用 stride 0。
- reverse/slice view 可以使用负 stride。
- 所有内部地址计算必须先验证 index 在 shape 范围内，再计算物理位置。
- 对非 contiguous view，禁止直接当连续 slice 暴露，必须通过迭代器或 `copy`。

### 4.5 ArrayFlags

```uya
export struct ArrayFlags {
    c_contiguous: bool,
    f_contiguous: bool,
    writeable: bool,
    owns_data: bool,
}
```

`owns_data` 对 view 为 `false`，但 view 仍然 retain storage。`writeable == false` 用于只读 broadcast、只读外部 buffer、未来 mmap。

## 5. 错误模型

所有 fallible API 返回 `!T`。错误名统一放在 `src/numuya/errors.uya`：

```uya
error NumuyaRankTooLarge;
error NumuyaShapeMismatch;
error NumuyaShapeOverflow;
error NumuyaAxisOutOfBounds;
error NumuyaIndexOutOfBounds;
error NumuyaBroadcastError;
error NumuyaNotContiguous;
error NumuyaReadOnly;
error NumuyaAllocFailed;
error NumuyaInvalidArgument;
error NumuyaSingularMatrix;
error NumuyaUnsupportedDType;
error NumuyaParseError;
error NumuyaUnsupportedBackend;
error NumuyaGpuUnavailable;
error NumuyaGpuOutOfMemory;
error NumuyaCudaError;
error NumuyaDeviceMismatch;
error NumuyaKernelLaunchFailed;
```

约定：

- shape/rank/axis/index 错误必须在访问内存前返回。
- allocator 错误从 `std.mem.allocator` 捕获后映射到 `NumuyaAllocFailed` 或原样传递，整个库保持一致。
- 浮点非法值不默认报错，遵守 IEEE 行为：`NaN` 传播，除非具体函数文档要求返回错误。
- CUDA Driver API 返回值统一映射到 `NumuyaCudaError`，其中 device 不存在映射到 `NumuyaGpuUnavailable`，显存不足映射到 `NumuyaGpuOutOfMemory`，kernel launch/sync 失败映射到 `NumuyaKernelLaunchFailed`。

## 6. API 设计

### 6.1 Shape API

必须先实现这些函数：

```uya
export fn shape_scalar() Shape;
export fn shape1(n0: usize) Shape;
export fn shape2(n0: usize, n1: usize) Shape;
export fn shape3(n0: usize, n1: usize, n2: usize) Shape;
export fn shape_from_slice(dims: &[usize]) !Shape;
export fn shape_size(shape: Shape) !usize;
export fn shape_eq(a: Shape, b: Shape) bool;
export fn normalize_axis(axis: isize, rank: usize) !usize;
```

NumPy 对照：

- `shape_scalar()` 对应 `np.array(1).shape == ()`。
- `shape_size(shape2(2, 3)) == 6`。
- `shape_size(shape1(0)) == 0`。
- `normalize_axis(-1, 3) == 2`。

### 6.2 Creation API

创建函数的第一阶段：

```uya
export fn empty<T>(allocator: IAllocator, shape: Shape) !Array<T>;
export fn full<T>(allocator: IAllocator, shape: Shape, value: T) !Array<T>;
export fn from_slice<T>(allocator: IAllocator, values: &[T], shape: Shape) !Array<T>;

export fn zeros_f64(allocator: IAllocator, shape: Shape) !Array<f64>;
export fn ones_f64(allocator: IAllocator, shape: Shape) !Array<f64>;
export fn full_f64(allocator: IAllocator, shape: Shape, value: f64) !Array<f64>;
export fn arange_f64(allocator: IAllocator, start: f64, stop: f64, step: f64) !Array<f64>;
export fn linspace_f64(allocator: IAllocator, start: f64, stop: f64, num: usize) !Array<f64>;
```

`empty<T>` 不初始化元素；测试不得读取 empty 内容。`zeros_*`、`ones_*`、`full_*` 必须初始化所有元素。

### 6.3 Indexing API

早期不要先实现花式 indexing，先完成安全的基础 indexing：

```uya
export fn get1<T>(a: &Array<T>, i0: usize) !T;
export fn get2<T>(a: &Array<T>, i0: usize, i1: usize) !T;
export fn get3<T>(a: &Array<T>, i0: usize, i1: usize, i2: usize) !T;
export fn getn<T>(a: &Array<T>, indices: &[usize]) !T;

export fn set1<T>(a: &Array<T>, i0: usize, value: T) !void;
export fn set2<T>(a: &Array<T>, i0: usize, i1: usize, value: T) !void;
export fn setn<T>(a: &Array<T>, indices: &[usize], value: T) !void;
```

后续添加：

```uya
export struct SliceSpec {
    start: isize,
    stop: isize,
    step: isize,
}

export fn slice_axis<T>(a: &Array<T>, axis: isize, spec: SliceSpec) !Array<T>;
export fn take<T>(allocator: IAllocator, a: &Array<T>, indices: &[usize], axis: isize) !Array<T>;
export fn boolean_mask<T>(allocator: IAllocator, a: &Array<T>, mask: &Array<bool>) !Array<T>;
```

### 6.4 Shape manipulation

```uya
export fn reshape<T>(a: &Array<T>, new_shape: Shape) !Array<T>;
export fn ravel<T>(a: &Array<T>) !Array<T>;
export fn copy<T>(allocator: IAllocator, a: &Array<T>) !Array<T>;
export fn transpose<T>(a: &Array<T>) !Array<T>;
export fn swapaxes<T>(a: &Array<T>, axis1: isize, axis2: isize) !Array<T>;
export fn moveaxis<T>(a: &Array<T>, source: isize, dest: isize) !Array<T>;
```

规则：

- `reshape` 对 contiguous array 返回 view。
- `reshape` 对非 contiguous array 第一阶段返回 `NumuyaNotContiguous`，后续可实现 copy-on-reshape 变体。
- `ravel` 对 contiguous 返回 view，非 contiguous 返回 `NumuyaNotContiguous`；后续提供 `flatten` 强制 copy。
- `transpose` 只交换 shape 与 stride，不复制数据。

### 6.5 Broadcasting

核心函数：

```uya
export fn broadcast_shapes(a: Shape, b: Shape) !Shape;
export fn broadcast_to<T>(a: &Array<T>, shape: Shape) !Array<T>;
```

二元广播规则与 NumPy 一致：

- 从最后一维向前对齐。
- 两个维度相等，或其中一个为 1，则兼容。
- 缺失的前导维等价于 1。
- 输出维度取较大值。
- 被扩展的轴 stride 设为 0。

例：

```text
(3,)      + (2, 3) -> (2, 3)
(4, 1, 3) + (1, 5, 3) -> (4, 5, 3)
(2,)      + (3,) -> NumuyaBroadcastError
```

### 6.6 UFunc 与 elementwise

第一阶段实现 f64/i32 特化：

```uya
export fn add_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn sub_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn mul_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn div_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn neg_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;

export fn add_i32(allocator: IAllocator, a: &Array<i32>, b: &Array<i32>) !Array<i32>;
```

第二阶段抽象为内部 loop kernel：

```uya
export fn unary_f64(
    allocator: IAllocator,
    a: &Array<f64>,
    op: fn(x: f64) f64,
) !Array<f64>;

export fn binary_f64(
    allocator: IAllocator,
    a: &Array<f64>,
    b: &Array<f64>,
    op: fn(x: f64, y: f64) f64,
) !Array<f64>;
```

Uya 不提供隐式捕获闭包，因此回调只允许函数指针；需要状态时使用显式 context 结构和专门 API。

### 6.7 Reductions

第一阶段：

```uya
export fn sum_all_f64(a: &Array<f64>) f64;
export fn prod_all_f64(a: &Array<f64>) f64;
export fn min_all_f64(a: &Array<f64>) !f64;
export fn max_all_f64(a: &Array<f64>) !f64;
export fn mean_all_f64(a: &Array<f64>) !f64;
```

第二阶段：

```uya
export fn sum_axis_f64(allocator: IAllocator, a: &Array<f64>, axis: isize, keepdims: bool) !Array<f64>;
export fn mean_axis_f64(allocator: IAllocator, a: &Array<f64>, axis: isize, keepdims: bool) !Array<f64>;
export fn argmax_axis_f64(allocator: IAllocator, a: &Array<f64>, axis: isize) !Array<usize>;
```

空数组规则：

- `sum_all_f64(empty) == 0.0`。
- `prod_all_f64(empty) == 1.0`。
- `min/max/mean` 对空数组返回 `NumuyaInvalidArgument`。

### 6.8 Math 与 stats

Math 第一批：

```uya
export fn abs_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn sqrt_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn exp_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn log_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn sin_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn cos_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
```

第一版 math kernel 必须用纯 Uya 标量实现。若未来接入平台 `libm` 或硬件库，只能作为可选 backend，且必须保留同语义的纯 Uya fallback。

纯 Uya math kernel 的最低算法规格：

- `sqrt_f64`：Newton-Raphson 或等价迭代；`x < 0` 返回 IEEE NaN，`x == 0` 返回 `0`，相对/绝对误差目标 `1e-12`。
- `exp_f64`：范围缩减到 `k * ln2 + r`，`r` 上用多项式或 Padé 近似；普通有限输入误差目标 `1e-10`。
- `log_f64`：尾数/指数拆分后多项式近似；`x < 0` 返回 NaN，`x == 0` 返回负无穷，普通有限输入误差目标 `1e-10`。
- `sin_f64/cos_f64`：Cody-Waite 风格范围缩减到 `[-pi/4, pi/4]` 后多项式近似；误差目标 `1e-10`。
- NaN/Inf 构造若当前 Uya 还没有内建 helper，先在 `types.uya` 或 `math.uya` 中集中提供位模式 helper，测试覆盖 NaN/Inf 传播。

Stats 第一批：

```uya
export fn var_all_f64(a: &Array<f64>, ddof: usize) !f64;
export fn std_all_f64(a: &Array<f64>, ddof: usize) !f64;
export fn percentile_f64(allocator: IAllocator, a: &Array<f64>, q: f64) !f64;
```

`ddof` 规则与 NumPy 类似：分母为 `N - ddof`，如果 `N <= ddof` 返回 `NumuyaInvalidArgument`。

### 6.9 Sorting 与 searching

```uya
export fn sort_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn argsort_f64(allocator: IAllocator, a: &Array<f64>) !Array<usize>;
export fn searchsorted_f64(a: &Array<f64>, value: f64) !usize;
export fn unique_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
```

早期只要求 1-D contiguous，后续扩展 axis。

### 6.10 Linear algebra

第一阶段：

```uya
export fn dot_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn matmul_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn eye_f64(allocator: IAllocator, n: usize, m: usize, k: isize) !Array<f64>;
export fn diag_f64(allocator: IAllocator, a: &Array<f64>, k: isize) !Array<f64>;
```

第二阶段：

```uya
export fn transpose2_f64(a: &Array<f64>) !Array<f64>;
export fn det_f64(a: &Array<f64>) !f64;
export fn solve_f64(allocator: IAllocator, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn inv_f64(allocator: IAllocator, a: &Array<f64>) !Array<f64>;
export fn qr_f64(allocator: IAllocator, a: &Array<f64>) !QRResult<f64>;
export fn svd_f64(allocator: IAllocator, a: &Array<f64>) !SVDResult<f64>;
```

最低实现要求：

- `matmul` 支持 2-D x 2-D。
- 后续再支持 1-D 规则和 batched matmul broadcasting。
- 线性方程第一版使用带部分主元的高斯消元，奇异矩阵返回 `NumuyaSingularMatrix`。

### 6.11 Random

纯 Uya PRNG：

```uya
export struct PCG64 {
    state: u64,
    inc: u64,
}

export fn pcg64_seed(seed: u64, stream: u64) PCG64;
export fn random_u64(rng: &PCG64) u64;
export fn random_f64(rng: &PCG64) f64;
export fn random_array_f64(allocator: IAllocator, rng: &PCG64, shape: Shape) !Array<f64>;
export fn normal_array_f64(allocator: IAllocator, rng: &PCG64, shape: Shape, mean: f64, std: f64) !Array<f64>;
```

规则：

- 固定 seed 必须跨平台产生相同序列。
- `random_f64` 输出 `[0, 1)`。
- `normal` 第一版可用 Box-Muller。

### 6.12 FFT

第一版实现 power-of-two 1-D complex FFT。

```uya
export struct Complex64 {
    re: f64,
    im: f64,
}

export fn fft_f64(allocator: IAllocator, real: &Array<f64>) !Array<Complex64>;
export fn ifft_complex64(allocator: IAllocator, freq: &Array<Complex64>) !Array<Complex64>;
```

后续扩展：

- complex input。
- non power-of-two fallback。
- `rfft` / `irfft`。
- axis 参数。

### 6.13 `.npy` I/O

第一版支持 NumPy `.npy` v1.0/v2.0 的小端 numeric dtype：

```uya
export fn save_npy_f64(path: &const byte, a: &Array<f64>) !void;
export fn load_npy_f64(allocator: IAllocator, path: &const byte) !Array<f64>;
```

支持项：

- magic `\x93NUMPY`。
- header dict 解析：`descr`、`fortran_order`、`shape`。
- little-endian `<f8`、`<f4`、`<i4` 等逐步扩展。
- C-order 第一版必须支持。
- Fortran-order 第一版可返回 `NumuyaUnsupportedDType` 或 `NumuyaInvalidArgument`，后续补全。

## 7. 迭代器与内部循环

所有高层操作最终走内部 iterator，避免每个函数重复复杂 stride 逻辑。

### 7.1 FlatIter

```uya
export struct FlatIter<T> {
    array: &Array<T>,
    index: usize,
    total: usize,
    coord: [usize: 16],
}

export fn flat_iter<T>(a: &Array<T>) FlatIter<T>;
export fn flat_next<T>(it: &FlatIter<T>) !T;
```

对于 contiguous array，允许 fast path 线性访问。对于非 contiguous array，按 shape/stride 计算。

### 7.2 BinaryBroadcastIter

```uya
export struct BinaryBroadcastIter<T> {
    a: &Array<T>,
    b: &Array<T>,
    out_shape: Shape,
    index: usize,
    coord: [usize: 16],
}
```

二元 ufunc 不应先 materialize broadcast view，除非实现简单阶段需要；最终版本应直接迭代两个输入与输出。

## 8. 数值正确性

浮点测试使用容差：

```uya
export fn expect_close_f64(actual: f64, expected: f64, tol: f64, msg: &const byte) !void;
export fn expect_array_close_f64(a: &Array<f64>, expected: &[f64], tol: f64, msg: &const byte) !void;
```

规则：

- 基础算术容差 `1e-12`。
- 三角/exp/log 容差 `1e-10`。
- linalg 容差按矩阵规模放宽。
- NaN 比较需要专门 helper，普通 close 不把 NaN 当相等。

## 9. TDD 流程

每个任务都按下面顺序：

1. 在对应 `tests/test_*.uya` 增加失败测试。
2. 运行 `../uya/bin/uya test tests/test_xxx.uya --project-root src`，确认失败原因是缺函数或断言失败。
3. 写最小实现。
4. 跑单测直到绿。
5. 跑已完成模块的相关测试。
6. 如果改了通用 helper，跑全部测试。
7. 只在测试变绿后重构。

测试文件模板：

```uya
use std.runtime.entry;
use std.testing.assert_eq_i32;
use std.testing.expect;
use std.testing.run_test;
use std.testing.test_suite_begin;
use std.testing.test_suite_end;

fn test_example() !void {
    try expect(true);
}

export fn main() i32 {
    test_suite_begin("NumUya example");
    run_test("example", test_example);
    return test_suite_end();
}
```

## 10. 实现约束

- 所有 public API 必须在文档中出现，不能临时发明名字。
- 所有数组访问必须经由 checked helper 或经过明确边界检查。
- 所有 shape size 乘法必须检查 overflow。
- 所有分配必须有 drop/release 路径测试。
- 不要把 `usize` 与 `isize` 混用；shape/size 用 `usize`，stride/offset/axis 用 `isize`。
- CPU core 不要使用 Python、NumPy、BLAS、LAPACK、libm 或 C helper。
- CUDA backend 只允许 Uya `extern` 直连 CUDA Driver API；可选 cuBLAS/cuFFT/cuRAND 必须由配置显式开启，且不得通过 C/C++ helper 间接调用。
- 可以使用 Uya 标准库：`std.mem.allocator`、`std.testing`、`std.collections.vec` 等。
- SIMD 只能作为优化层；标量实现和测试必须先完整存在。
- 性能优化必须保持与标量路径同测试。

## 11. NumPy 兼容边界

### 11.1 必须兼容的行为

- C-order 默认布局。
- shape、size、ndim 语义。
- basic slicing 产生 view。
- reshape/transpose 尽量产生 view。
- broadcasting 规则。
- elementwise 输出 shape。
- reductions 的空数组规则。
- matrix multiplication 维度规则。
- `.npy` 基本格式。

### 11.2 可以更简洁的地方

- dtype 通过 `Array<T>` 静态表达，不默认接受运行期 dtype 参数。
- 无默认参数；使用明确函数名或 option struct。
- 错误通过 `!T` 返回，不抛异常。
- axis normalization 由公共 helper 明确暴露。
- object/string/unicode dtype 不进入第一版。

### 11.3 后续可选兼容

- `ArrayAny` 动态 dtype wrapper。
- complex dtype。
- structured dtype。
- memory mapped `.npy`。
- advanced/fancy indexing。
- masked arrays。
- polynomial、histogram、einsum、tensor contraction。

## 12. 性能路线

性能按四层递进：

1. 正确标量实现：所有功能先走安全、清晰的 loop。
2. contiguous fast path：对 `c_contiguous` 且 dtype 符合的数组使用线性循环。
3. SIMD/tile path：用 Uya `@vector(T, N)` 优化 add/mul/reduce/matmul 内核。
4. CUDA path：对大数组、已在 device 上的数组、矩阵乘法、批量随机数、FFT/reduction 等热路径使用 RTX 3060。

每个优化必须满足：

- 同一 API 不改变错误语义。
- 非 contiguous/broadcast/stride 0 路径仍可工作。
- 保留标量 fallback。
- CUDA fallback 必须能在没有 GPU 或 CUDA 初始化失败时返回明确错误，自动 backend 才允许回退 CPU。
- benchmark 不代替 correctness test。

## 13. RTX 3060 / CUDA backend

本机目标环境：

- GPU：NVIDIA GeForce RTX 3060，12GB 显存。
- 驱动：`580.119.02`，`nvidia-smi` 报告 CUDA runtime capability 13.0。
- 本机工具：`ptxas` 12.2 可用于离线校验/汇编 PTX；检测到 `nvcc` 12.2，但必须构建路径不依赖 `.cu` 源或 `nvcc`。
- GPU 架构目标：Ampere `sm_86`。所有预编译 PTX/SASS 资产优先按 `sm_86` 优化，同时保留 PTX JIT fallback。

### 13.1 约束与边界

CPU core 仍然是纯 Uya backend。CUDA backend 的 host 侧也必须用 Uya 编写，通过 `extern` 直接绑定 CUDA Driver API：

- 允许：`libcuda.so` Driver API，例如 `cuInit`、`cuDeviceGet`、`cuCtxCreate`、`cuMemAlloc`、`cuMemcpyHtoDAsync`、`cuLaunchKernel`。
- 允许：把 PTX/cubin 作为项目资产或 Uya 字节数组嵌入，由 Uya host code 加载。
- 不允许：用 Python/NumPy/PyTorch 作为运行期依赖。
- 不允许：写 C/C++ helper 包一层 CUDA 再给 Uya 调用。
- 不允许：把 `.cu`/CUDA C++ 当作必须的 kernel 源码；`nvcc` 只能用于实验对照，不进入 TDD 主路径。
- 可选：`cuBLAS/cuBLASLt`、`cuFFT`、`cuRAND` 作为 vendor-performance backend，必须有明确 feature flag，并且纯 Uya CUDA kernel backend 仍可通过测试。若用户要求“最大吞吐”，matmul/FFT/random 可优先走 vendor backend。

RTX 3060 的 FP64 吞吐远低于 FP32/TF32/F16。策略：

- correctness API 默认支持 `f64`，但性能重点放在 `f32`、`f16`/`bf16`、TF32 matmul。
- `f64` ufunc/reduction 可以上 GPU，但不承诺比 CPU 更快。
- `matmul_f32` 必须优先优化，后续再做 `matmul_f64`。

### 13.2 Kernel 资产与构建路径

CUDA kernel 的 source-of-truth 必须可复现且不依赖 C/C++ helper：

- MVP source-of-truth 是 `src/numuya/cuda/ptx/*.ptx` 中的 PTX 文本资产。
- `src/numuya/cuda/kernels_ptx.uya` 是由 `tools/embed_ptx.uya` 生成的 Uya 字节/字符串嵌入文件；生成结果可以提交，便于无文件 I/O 场景加载。
- `tools/ptx_validate.uya` 或脚本封装 `ptxas -arch=sm_86` 做离线校验，可生成 cubin cache，但 cubin 不是唯一 source-of-truth。
- 默认测试加载 embedded PTX 并让 CUDA Driver JIT；性能 benchmark 可优先加载 `sm_86` cubin cache。
- 后续可以新增 Uya kernel DSL/codegen 生成 PTX，但不能用 `.cu` 取代 PTX/Uya source-of-truth。

最小命令约定：

```bash
make cuda-ptx-embed
make cuda-ptx-validate
make test-cuda
make bench-cuda
```

若没有 `Makefile`，命令必须等价于：

```bash
LDFLAGS="-lcuda" NUMUYA_CUDA_REQUIRED=1 ../uya/bin/uya test tests/test_cuda_driver.uya --project-root src
ptxas -arch=sm_86 src/numuya/cuda/ptx/core_sm86.ptx -o build/cuda/core_sm86.cubin
```

### 13.3 Backend API

```uya
export enum BackendKind {
    cpu,
    cuda,
    auto,
}

export struct BackendConfig {
    kind: BackendKind,
    gpu_index: i32,
    memory_budget_bytes: usize,
    prefer_vendor_libs: bool,
    allow_tf32: bool,
}

export struct Backend {
    kind: BackendKind,
    config: BackendConfig,
    cuda: &CudaBackend,
}

export struct CudaBackend {
    device: CudaDevice,
    context: CudaContext,
    default_stream: CudaStream,
    pool: CudaMemoryPool,
    owns_context: bool,
}

export fn backend_default_config() BackendConfig;
export fn backend_init(config: BackendConfig) !Backend;
export fn backend_deinit(backend: &Backend) !void;
export fn backend_is_cuda_available() bool;
export fn backend_set_default(backend: &Backend) void;
export fn backend_cuda(backend: &Backend) !&CudaBackend;
```

默认策略：

- `cpu`：永远可用，完全纯 Uya。
- `cuda`：显式要求 GPU，初始化失败返回 `NumuyaGpuUnavailable`。
- `auto`：能初始化 RTX 3060 就用 CUDA；不能初始化时走 CPU。
- `Backend.kind == cpu` 时 `Backend.cuda == null`，调用 `backend_cuda` 必须返回 `NumuyaUnsupportedBackend`。
- `Backend.kind == cuda` 时 `Backend.cuda != null`，所有 device allocation 必须来自该 backend 的 pool。
- `backend_deinit` 负责释放 stream、module、memory pool 与 context；如果仍有活跃 `DeviceStorage`，必须返回 `NumuyaInvalidArgument`，调用方应先 drop device arrays。
- `backend_set_default` 只保存 borrowed handle；调用方必须保证默认 backend 活到 reset 或进程结束。第一版测试优先显式传 `&Backend`，少用全局默认。

### 13.4 CUDA Driver 封装

`src/numuya/cuda/driver.uya` 只做薄绑定与错误转换：

```uya
export struct CudaDevice {
    ordinal: i32,
    compute_major: i32,
    compute_minor: i32,
    total_mem: usize,
}

export struct CudaContext {
    device: CudaDevice,
    raw: usize,
}

export struct CudaStream {
    raw: usize,
}

export fn cuda_init() !void;
export fn cuda_get_device(ordinal: i32) !CudaDevice;
export fn cuda_create_context(device: CudaDevice) !CudaContext;
export fn cuda_destroy_context(ctx: &CudaContext) void;
export fn cuda_create_stream(ctx: &CudaContext) !CudaStream;
export fn cuda_destroy_stream(stream: &CudaStream) void;
export fn cuda_synchronize_stream(stream: &CudaStream) !void;
```

所有 `raw` 字段是 CUDA handle 的整数承载，避免 Uya 当前 FFI 指针类型与 opaque handle 互相污染。

Driver 调用规则：

- 所有需要 context 的 Driver API 调用前必须确保对应 context 为 current；封装层提供 `cuda_with_context(ctx, fn_ptr, context_ptr)` 或等价内部 helper。
- 每个 create API 必须有 destroy API，且 destroy 允许重复调用空 handle。
- stream 归属单个 context，不允许跨 backend 使用。

### 13.5 Device memory 与 memory pool

```uya
export struct DeviceBuffer {
    ptr: usize,
    bytes: usize,
    device_ordinal: i32,
}

export struct CudaMemoryPool {
    device_ordinal: i32,
    budget_bytes: usize,
    used_bytes: usize,
    live_allocations: usize,
}

export struct DeviceStorage<T> {
    pool: &CudaMemoryPool,
    buffer: DeviceBuffer,
    len: usize,
    dtype: DType,
    ref_count: atomic usize,
}

export fn cuda_malloc(pool: &CudaMemoryPool, bytes: usize) !DeviceBuffer;
export fn cuda_free(pool: &CudaMemoryPool, buf: DeviceBuffer) void;
export fn cuda_memcpy_h2d_async(dst: DeviceBuffer, src: &const byte, bytes: usize, stream: &CudaStream) !void;
export fn cuda_memcpy_d2h_async(dst: &byte, src: DeviceBuffer, bytes: usize, stream: &CudaStream) !void;
export fn device_storage_new<T>(backend: &Backend, len: usize, dtype: DType) !&DeviceStorage<T>;
export fn device_storage_retain<T>(storage: &DeviceStorage<T>) void;
export fn device_storage_release<T>(storage: &DeviceStorage<T>) void;
```

RTX 3060 是显示卡，默认不要抢满 12GB。`backend_default_config` 应查询 free/total memory 后保留安全余量；如果查询失败，默认预算不超过 10GB。

Device storage 规则：

- `DeviceBuffer` 只能由 `DeviceStorage<T>` 拥有；`DeviceArray<T>` 不直接拥有 buffer。
- device view 必须 retain 同一个 `DeviceStorage<T>`，与 CPU `Array<T>` 的 storage 语义一致。
- `device_storage_release` 的最后一个引用释放 device memory 并更新 memory pool 统计。
- `pool.used_bytes` 与 `pool.live_allocations` 必须只统计真实 device allocation，不因 view 增减。

### 13.6 DeviceArray

`DeviceArray<T>` 是 GPU 上的 ndarray：

```uya
export struct DeviceArray<T> {
    storage: &DeviceStorage<T>,
    offset: isize,
    shape: Shape,
    strides: Strides,
    flags: ArrayFlags,
    stream: CudaStream,
    dtype: DType,
}

export fn to_device_f64(backend: &Backend, a: &Array<f64>) !DeviceArray<f64>;
export fn to_host_f64(allocator: IAllocator, a: &DeviceArray<f64>) !Array<f64>;
export fn device_empty_f64(backend: &Backend, shape: Shape) !DeviceArray<f64>;
export fn device_zeros_f64(backend: &Backend, shape: Shape) !DeviceArray<f64>;
```

规则：

- `DeviceArray` 保留 shape/stride/view 语义。
- 第一版允许只支持 contiguous device output；non-contiguous input 通过 stride kernel 读。
- host/device 之间不隐式同步，除非 API 名称或文档明确说明。
- `to_host_*` 必须同步对应 stream。
- `DeviceArray<T>.drop` 调用 `device_storage_release`；需要复制 handle 时必须用 `device_array_view` 或 `device_array_clone_ref` 显式 retain。

### 13.7 GPU kernels

必须先有纯 Uya CPU reference，再实现 GPU kernel。GPU kernel 命名：

```uya
export fn gpu_add_f64(backend: &Backend, a: &DeviceArray<f64>, b: &DeviceArray<f64>) !DeviceArray<f64>;
export fn gpu_mul_f64(backend: &Backend, a: &DeviceArray<f64>, b: &DeviceArray<f64>) !DeviceArray<f64>;
export fn gpu_sum_f64(backend: &Backend, a: &DeviceArray<f64>) !DeviceArray<f64>;
export fn gpu_matmul_f32(backend: &Backend, a: &DeviceArray<f32>, b: &DeviceArray<f32>) !DeviceArray<f32>;
export fn gpu_random_f32(backend: &Backend, shape: Shape, seed: u64) !DeviceArray<f32>;
```

Kernel 路线：

1. contiguous 1-D ufunc kernel：one thread per element。
2. broadcast/stride ufunc kernel：index 解码到 coord，再用 stride 读。
3. reduction：block reduction + second-stage reduction。
4. matmul baseline：shared-memory tiled SGEMM。
5. matmul optimized：TF32/Tensor Core 路径，优先通过 cuBLASLt optional backend；纯 kernel backend 保留 shared-memory tiled fallback。
6. random：GPU PCG/Xoroshiro，每个 thread 独立 counter/state。

### 13.8 自动调度

高层 API 分成 host-return 与 location-preserving 两类。host-return API 方便 NumPy 风格调用，必要时会把 GPU 结果拷回 host；location-preserving API 用于真正的 GPU pipeline。

```uya
export union ArrayF64 {
    Host: Array<f64>,
    Device: DeviceArray<f64>,
}

export union ArrayF32 {
    Host: Array<f32>,
    Device: DeviceArray<f32>,
}

export fn add_f64_auto(allocator: IAllocator, backend: &Backend, a: &Array<f64>, b: &Array<f64>) !Array<f64>;
export fn matmul_f32_auto(allocator: IAllocator, backend: &Backend, a: &Array<f32>, b: &Array<f32>) !Array<f32>;
export fn add_f64_on(allocator: IAllocator, backend: &Backend, a: &ArrayF64, b: &ArrayF64) !ArrayF64;
export fn matmul_f32_on(allocator: IAllocator, backend: &Backend, a: &ArrayF32, b: &ArrayF32) !ArrayF32;
```

调度策略：

- `_on` 输入已经在 `DeviceArray` 上：优先留在 GPU，返回 `ArrayF64.Device` 或 `ArrayF32.Device`。
- `_auto` 始终返回 host `Array<T>`；如果内部走 GPU，函数结束前必须同步并拷回 host。
- 小数组：CPU，避免 PCIe 拷贝开销。
- 大 contiguous elementwise：GPU。
- reduction/matmul/random/FFT：优先 GPU。
- GPU 显存不足：显式 `cuda` backend 返回错误；`auto` backend 可以回退 CPU 并记录状态。

### 13.9 CUDA 测试与链接约定

CUDA 测试分三档：

- `make test`：不要求 GPU；CUDA 不可用时相关测试必须 skip 或不进入默认集合。
- `make test-cuda`：要求本机 RTX 3060 可用；设置 `NUMUYA_CUDA_REQUIRED=1`，任何 CUDA 初始化失败都算失败。
- `make test-cuda-vendor`：额外链接 cuBLAS/cuFFT/cuRAND，设置 `NUMUYA_CUDA_VENDOR=1`。

链接约定：

```bash
LDFLAGS="-lcuda" NUMUYA_CUDA_REQUIRED=1 ../uya/bin/uya test tests/test_cuda_driver.uya --project-root src
LDFLAGS="-lcuda -lcublasLt -lcublas -lcufft -lcurand" NUMUYA_CUDA_VENDOR=1 ../uya/bin/uya test tests/test_cuda_linalg.uya --project-root src
```

CUDA 测试必须打印或断言：

- GPU name 包含 `RTX 3060` 或 compute capability 为 `8.6`。
- driver 初始化成功。
- free/total memory 查询成功；total memory 大于 8GB。
- embedded PTX 加载成功。

### 13.10 性能验收

正确性优先，但 RTX 3060 backend 必须有 benchmark：

- H2D/D2H bandwidth。
- `add_f32`/`add_f64` contiguous throughput。
- broadcast add throughput。
- `sum_f32`/`sum_f64` throughput。
- `matmul_f32` 1024x1024、2048x2048。
- random fill throughput。

基准要求：

- 每个 benchmark 先 warmup。
- 每个 kernel 使用 CUDA event 计时，不用 CPU wall time 估 kernel。
- benchmark 输出 GPU name、driver version、free/total memory、backend 路径。
- correctness test 与 benchmark 分离；benchmark 慢测默认不进普通 `make test`。

RTX 3060 初始性能门槛用于防止明显退化，`bench-cuda-strict` 才强制失败：

- H2D/D2H pageable copy：各自 >= 6 GiB/s。
- contiguous `add_f32`：有效内存带宽 >= 150 GiB/s。
- contiguous `add_f64`：有效内存带宽 >= 100 GiB/s。
- `sum_f32`：有效读带宽 >= 60 GiB/s。
- pure kernel `matmul_f32` 1024x1024：>= 1.0 TFLOP/s。
- vendor cuBLASLt + TF32 2048x2048：若启用 vendor backend，>= 6.0 TFLOP/s。
- random fill f32：>= 40 GiB/s。

这些阈值是第一版保守线；优化阶段可以上调，但不能用低阈值掩盖 kernel 没跑在 GPU 上。

## 14. 小模型实现提示

实现者如果不确定，从这条主线推进：

1. 先做 `Shape`，不要碰 allocator。
2. 再做 `Storage<T>` 和 contiguous `Array<T>`。
3. 再做 `from_slice/get/set`。
4. 再做 contiguous-only `reshape/ravel`。
5. 再做 view stride。
6. 再做 broadcasting。
7. 再做 ufunc/reduction。
8. CPU 全绿后再开 CUDA：先 driver smoke，再 DeviceArray copy，再 GPU add。

任何时候不要同时改三层抽象。比如实现 `add_f64` 时，如果发现 shape helper 不够，先给 shape helper 补测试和实现，再回到 `add_f64`。
