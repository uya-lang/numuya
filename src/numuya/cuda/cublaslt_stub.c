/* Optional cuBLASLt backend loader.
 *
 * When <cublasLt.h> and <cuda.h> are available this stub dynamically loads
 * libcublasLt at runtime and forwards calls through function pointers.  This
 * keeps NumUya free of a hard link-time dependency on the vendor library:
 * builds without cuBLASLt still compile and simply receive
 * NUMUYA_CUBLASLT_UNAVAILABLE at runtime.
 *
 * When the headers are absent the stub compiles to no-op functions that
 * report unavailability, so the package can be built on machines without
 * the CUDA toolkit.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <dlfcn.h>

#define NUMUYA_CUBLASLT_OK 0
#define NUMUYA_CUBLASLT_UNAVAILABLE 1
#define NUMUYA_CUBLASLT_ERROR 2

#if defined(__has_include)
#  if __has_include(<cublasLt.h>) && __has_include(<cuda.h>)
#    define NUMUYA_HAVE_CUBLASLT_HEADERS 1
#  endif
#endif

#if NUMUYA_HAVE_CUBLASLT_HEADERS

#include <cuda.h>
#include <cublasLt.h>

static void* numuya_cublaslt_handle = NULL;

static cublasStatus_t (*pfn_cublasLtCreate)(cublasLtHandle_t*) = NULL;
static cublasStatus_t (*pfn_cublasLtDestroy)(cublasLtHandle_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatmulDescCreate)(cublasLtMatmulDesc_t*, cublasComputeType_t, cudaDataType_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatmulDescDestroy)(cublasLtMatmulDesc_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatmulDescSetAttribute)(cublasLtMatmulDesc_t, cublasLtMatmulDescAttributes_t, const void*, size_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatrixLayoutCreate)(cublasLtMatrixLayout_t*, cudaDataType_t, uint64_t, uint64_t, int64_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatrixLayoutDestroy)(cublasLtMatrixLayout_t) = NULL;
static cublasStatus_t (*pfn_cublasLtMatmul)(
    cublasLtHandle_t,
    cublasLtMatmulDesc_t,
    const void*,
    const void*, cublasLtMatrixLayout_t,
    const void*, cublasLtMatrixLayout_t,
    const void*,
    const void*, cublasLtMatrixLayout_t,
    void*, cublasLtMatrixLayout_t,
    const cublasLtMatmulAlgo_t*,
    void*, size_t,
    CUstream) = NULL;

static int numuya_cublaslt_load(void) {
    if (numuya_cublaslt_handle != NULL) {
        return NUMUYA_CUBLASLT_OK;
    }

    numuya_cublaslt_handle = dlopen("libcublasLt.so.12", RTLD_NOW | RTLD_NODELETE);
    if (numuya_cublaslt_handle == NULL) {
        numuya_cublaslt_handle = dlopen("libcublasLt.so.1", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cublaslt_handle == NULL) {
        numuya_cublaslt_handle = dlopen("libcublasLt.so", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cublaslt_handle == NULL) {
        return NUMUYA_CUBLASLT_UNAVAILABLE;
    }

    pfn_cublasLtCreate = (cublasStatus_t (*)(cublasLtHandle_t*))dlsym(numuya_cublaslt_handle, "cublasLtCreate");
    pfn_cublasLtDestroy = (cublasStatus_t (*)(cublasLtHandle_t))dlsym(numuya_cublaslt_handle, "cublasLtDestroy");
    pfn_cublasLtMatmulDescCreate = (cublasStatus_t (*)(cublasLtMatmulDesc_t*, cublasComputeType_t, cudaDataType_t))dlsym(numuya_cublaslt_handle, "cublasLtMatmulDescCreate");
    pfn_cublasLtMatmulDescDestroy = (cublasStatus_t (*)(cublasLtMatmulDesc_t))dlsym(numuya_cublaslt_handle, "cublasLtMatmulDescDestroy");
    pfn_cublasLtMatmulDescSetAttribute = (cublasStatus_t (*)(cublasLtMatmulDesc_t, cublasLtMatmulDescAttributes_t, const void*, size_t))dlsym(numuya_cublaslt_handle, "cublasLtMatmulDescSetAttribute");
    pfn_cublasLtMatrixLayoutCreate = (cublasStatus_t (*)(cublasLtMatrixLayout_t*, cudaDataType_t, uint64_t, uint64_t, int64_t))dlsym(numuya_cublaslt_handle, "cublasLtMatrixLayoutCreate");
    pfn_cublasLtMatrixLayoutDestroy = (cublasStatus_t (*)(cublasLtMatrixLayout_t))dlsym(numuya_cublaslt_handle, "cublasLtMatrixLayoutDestroy");
    pfn_cublasLtMatmul = (cublasStatus_t (*)(
        cublasLtHandle_t,
        cublasLtMatmulDesc_t,
        const void*,
        const void*, cublasLtMatrixLayout_t,
        const void*, cublasLtMatrixLayout_t,
        const void*,
        const void*, cublasLtMatrixLayout_t,
        void*, cublasLtMatrixLayout_t,
        const cublasLtMatmulAlgo_t*,
        void*, size_t,
        CUstream))dlsym(numuya_cublaslt_handle, "cublasLtMatmul");

    if (pfn_cublasLtCreate == NULL ||
        pfn_cublasLtDestroy == NULL ||
        pfn_cublasLtMatmulDescCreate == NULL ||
        pfn_cublasLtMatmulDescDestroy == NULL ||
        pfn_cublasLtMatmulDescSetAttribute == NULL ||
        pfn_cublasLtMatrixLayoutCreate == NULL ||
        pfn_cublasLtMatrixLayoutDestroy == NULL ||
        pfn_cublasLtMatmul == NULL) {
        return NUMUYA_CUBLASLT_UNAVAILABLE;
    }

    return NUMUYA_CUBLASLT_OK;
}

int numuya_cublaslt_available(void) {
    return numuya_cublaslt_load();
}

int numuya_cublaslt_init(void** handle) {
    const int load_status = numuya_cublaslt_load();
    if (load_status != NUMUYA_CUBLASLT_OK) {
        return load_status;
    }

    const cublasStatus_t status = pfn_cublasLtCreate((cublasLtHandle_t*)handle);
    if (status != 0) {
        return NUMUYA_CUBLASLT_ERROR;
    }
    return NUMUYA_CUBLASLT_OK;
}

int numuya_cublaslt_destroy(void* handle) {
    if (handle == NULL) {
        return NUMUYA_CUBLASLT_OK;
    }

    const int load_status = numuya_cublaslt_load();
    if (load_status != NUMUYA_CUBLASLT_OK) {
        return load_status;
    }

    const cublasStatus_t status = pfn_cublasLtDestroy((cublasLtHandle_t)handle);
    if (status != 0) {
        return NUMUYA_CUBLASLT_ERROR;
    }
    return NUMUYA_CUBLASLT_OK;
}

int numuya_cublaslt_matmul_f32(
    void* stream,
    void* handle,
    int m, int n, int k,
    void* a_ptr,
    void* b_ptr,
    void* c_ptr,
    int allow_tf32) {

    const int load_status = numuya_cublaslt_load();
    if (load_status != NUMUYA_CUBLASLT_OK) {
        return load_status;
    }

    cublasComputeType_t compute_type = allow_tf32 ? CUBLAS_COMPUTE_32F_FAST_TF32 : CUBLAS_COMPUTE_32F;

    cublasLtMatmulDesc_t desc = NULL;
    cublasStatus_t status = pfn_cublasLtMatmulDescCreate(&desc, compute_type, CUDA_R_32F);
    if (status != 0) {
        return NUMUYA_CUBLASLT_ERROR;
    }

    cublasOperation_t transa = CUBLAS_OP_N;
    cublasOperation_t transb = CUBLAS_OP_N;
    status = pfn_cublasLtMatmulDescSetAttribute(desc, CUBLASLT_MATMUL_DESC_TRANSA, &transa, sizeof(transa));
    if (status != 0) {
        pfn_cublasLtMatmulDescDestroy(desc);
        return NUMUYA_CUBLASLT_ERROR;
    }
    status = pfn_cublasLtMatmulDescSetAttribute(desc, CUBLASLT_MATMUL_DESC_TRANSB, &transb, sizeof(transb));
    if (status != 0) {
        pfn_cublasLtMatmulDescDestroy(desc);
        return NUMUYA_CUBLASLT_ERROR;
    }

    cublasLtMatrixLayout_t a_layout = NULL;
    cublasLtMatrixLayout_t b_layout = NULL;
    cublasLtMatrixLayout_t c_layout = NULL;

    /* NumUya matrices are row-major.  Present them to cuBLASLt as the
     * equivalent column-major transposed multiplication:
     *
     *   C_row(m,n) = A_row(m,k) * B_row(k,n)
     *   C_col(n,m) = B_col(n,k) * A_col(k,m)
     *
     * This keeps the public row-major result while letting cuBLASLt use its
     * native column-major fast paths.
     */
    status = pfn_cublasLtMatrixLayoutCreate(&a_layout, CUDA_R_32F, (uint64_t)n, (uint64_t)k, (int64_t)n);
    if (status != 0) {
        pfn_cublasLtMatmulDescDestroy(desc);
        return NUMUYA_CUBLASLT_ERROR;
    }
    status = pfn_cublasLtMatrixLayoutCreate(&b_layout, CUDA_R_32F, (uint64_t)k, (uint64_t)m, (int64_t)k);
    if (status != 0) {
        pfn_cublasLtMatrixLayoutDestroy(a_layout);
        pfn_cublasLtMatmulDescDestroy(desc);
        return NUMUYA_CUBLASLT_ERROR;
    }
    status = pfn_cublasLtMatrixLayoutCreate(&c_layout, CUDA_R_32F, (uint64_t)n, (uint64_t)m, (int64_t)n);
    if (status != 0) {
        pfn_cublasLtMatrixLayoutDestroy(b_layout);
        pfn_cublasLtMatrixLayoutDestroy(a_layout);
        pfn_cublasLtMatmulDescDestroy(desc);
        return NUMUYA_CUBLASLT_ERROR;
    }

    const float alpha = 1.0f;
    const float beta = 0.0f;

    status = pfn_cublasLtMatmul(
        (cublasLtHandle_t)handle,
        desc,
        &alpha,
        b_ptr, a_layout,
        a_ptr, b_layout,
        &beta,
        c_ptr, c_layout,
        c_ptr, c_layout,
        NULL,
        NULL, 0,
        (CUstream)stream);

    pfn_cublasLtMatrixLayoutDestroy(c_layout);
    pfn_cublasLtMatrixLayoutDestroy(b_layout);
    pfn_cublasLtMatrixLayoutDestroy(a_layout);
    pfn_cublasLtMatmulDescDestroy(desc);

    if (status != 0) {
        return NUMUYA_CUBLASLT_ERROR;
    }
    return NUMUYA_CUBLASLT_OK;
}

#else /* NUMUYA_HAVE_CUBLASLT_HEADERS */

int numuya_cublaslt_available(void) {
    return NUMUYA_CUBLASLT_UNAVAILABLE;
}

int numuya_cublaslt_init(void** handle) {
    (void)handle;
    return NUMUYA_CUBLASLT_UNAVAILABLE;
}

int numuya_cublaslt_destroy(void* handle) {
    (void)handle;
    return NUMUYA_CUBLASLT_UNAVAILABLE;
}

int numuya_cublaslt_matmul_f32(
    void* stream,
    void* handle,
    int m, int n, int k,
    void* a_ptr,
    void* b_ptr,
    void* c_ptr,
    int allow_tf32) {
    (void)stream;
    (void)handle;
    (void)m;
    (void)n;
    (void)k;
    (void)a_ptr;
    (void)b_ptr;
    (void)c_ptr;
    (void)allow_tf32;
    return NUMUYA_CUBLASLT_UNAVAILABLE;
}

#endif /* NUMUYA_HAVE_CUBLASLT_HEADERS */
