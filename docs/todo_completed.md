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
