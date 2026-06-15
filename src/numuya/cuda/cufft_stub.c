/* Optional cuFFT backend loader.
 *
 * When <cufft.h> and <cuda.h> are available this stub dynamically loads
 * libcufft at runtime and forwards calls through function pointers.  This
 * keeps NumUya free of a hard link-time dependency on the vendor library:
 * builds without cuFFT still compile and simply receive
 * NUMUYA_CUFFT_UNAVAILABLE at runtime.
 *
 * When the headers are absent the stub compiles to no-op functions that
 * report unavailability, so the package can be built on machines without
 * the CUDA toolkit.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <dlfcn.h>

#define NUMUYA_CUFFT_OK 0
#define NUMUYA_CUFFT_UNAVAILABLE 1
#define NUMUYA_CUFFT_ERROR 2

#if defined(__has_include)
#  if __has_include(<cufft.h>) && __has_include(<cuda.h>)
#    define NUMUYA_HAVE_CUFFT_HEADERS 1
#  endif
#endif

#if NUMUYA_HAVE_CUFFT_HEADERS

#include <cuda.h>
#include <cufft.h>

static void* numuya_cufft_handle = NULL;

static cufftResult (*pfn_cufftPlan1d)(cufftHandle*, int, cufftType, int) = NULL;
static cufftResult (*pfn_cufftDestroy)(cufftHandle) = NULL;
static cufftResult (*pfn_cufftExecZ2Z)(cufftHandle, cufftDoubleComplex*, cufftDoubleComplex*, int) = NULL;
static cufftResult (*pfn_cufftSetStream)(cufftHandle, cudaStream_t) = NULL;

static int numuya_cufft_load(void) {
    if (numuya_cufft_handle != NULL) {
        return NUMUYA_CUFFT_OK;
    }

    numuya_cufft_handle = dlopen("libcufft.so.10", RTLD_NOW | RTLD_NODELETE);
    if (numuya_cufft_handle == NULL) {
        numuya_cufft_handle = dlopen("libcufft.so.11", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cufft_handle == NULL) {
        numuya_cufft_handle = dlopen("libcufft.so.12", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cufft_handle == NULL) {
        numuya_cufft_handle = dlopen("libcufft.so.1", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cufft_handle == NULL) {
        numuya_cufft_handle = dlopen("libcufft.so", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cufft_handle == NULL) {
        return NUMUYA_CUFFT_UNAVAILABLE;
    }

    pfn_cufftPlan1d = (cufftResult (*)(cufftHandle*, int, cufftType, int))dlsym(numuya_cufft_handle, "cufftPlan1d");
    pfn_cufftDestroy = (cufftResult (*)(cufftHandle))dlsym(numuya_cufft_handle, "cufftDestroy");
    pfn_cufftExecZ2Z = (cufftResult (*)(cufftHandle, cufftDoubleComplex*, cufftDoubleComplex*, int))dlsym(numuya_cufft_handle, "cufftExecZ2Z");
    pfn_cufftSetStream = (cufftResult (*)(cufftHandle, cudaStream_t))dlsym(numuya_cufft_handle, "cufftSetStream");

    if (pfn_cufftPlan1d == NULL ||
        pfn_cufftDestroy == NULL ||
        pfn_cufftExecZ2Z == NULL ||
        pfn_cufftSetStream == NULL) {
        return NUMUYA_CUFFT_UNAVAILABLE;
    }

    return NUMUYA_CUFFT_OK;
}

int numuya_cufft_available(void) {
    return numuya_cufft_load();
}

int numuya_cufft_plan_z2z_1d(int n, size_t* handle) {
    const int load_status = numuya_cufft_load();
    if (load_status != NUMUYA_CUFFT_OK) {
        return load_status;
    }

    cufftHandle plan = 0;
    const cufftResult status = pfn_cufftPlan1d(&plan, n, CUFFT_Z2Z, 1);
    if (status != CUFFT_SUCCESS) {
        return NUMUYA_CUFFT_ERROR;
    }

    *handle = (size_t)plan;
    return NUMUYA_CUFFT_OK;
}

int numuya_cufft_destroy(size_t handle) {
    if (handle == 0) {
        return NUMUYA_CUFFT_OK;
    }

    const int load_status = numuya_cufft_load();
    if (load_status != NUMUYA_CUFFT_OK) {
        return load_status;
    }

    const cufftResult status = pfn_cufftDestroy((cufftHandle)handle);
    if (status != CUFFT_SUCCESS) {
        return NUMUYA_CUFFT_ERROR;
    }
    return NUMUYA_CUFFT_OK;
}

int numuya_cufft_set_stream(size_t handle, void* stream) {
    const int load_status = numuya_cufft_load();
    if (load_status != NUMUYA_CUFFT_OK) {
        return load_status;
    }

    const cufftResult status = pfn_cufftSetStream((cufftHandle)handle, (cudaStream_t)stream);
    if (status != CUFFT_SUCCESS) {
        return NUMUYA_CUFFT_ERROR;
    }
    return NUMUYA_CUFFT_OK;
}

int numuya_cufft_exec_z2z(size_t handle, void* idata, void* odata, int direction) {
    const int load_status = numuya_cufft_load();
    if (load_status != NUMUYA_CUFFT_OK) {
        return load_status;
    }

    const cufftResult status = pfn_cufftExecZ2Z(
        (cufftHandle)handle,
        (cufftDoubleComplex*)idata,
        (cufftDoubleComplex*)odata,
        direction);
    if (status != CUFFT_SUCCESS) {
        return NUMUYA_CUFFT_ERROR;
    }
    return NUMUYA_CUFFT_OK;
}

#else /* NUMUYA_HAVE_CUFFT_HEADERS */

int numuya_cufft_available(void) {
    return NUMUYA_CUFFT_UNAVAILABLE;
}

int numuya_cufft_plan_z2z_1d(int n, size_t* handle) {
    (void)n;
    (void)handle;
    return NUMUYA_CUFFT_UNAVAILABLE;
}

int numuya_cufft_destroy(size_t handle) {
    (void)handle;
    return NUMUYA_CUFFT_UNAVAILABLE;
}

int numuya_cufft_set_stream(size_t handle, void* stream) {
    (void)handle;
    (void)stream;
    return NUMUYA_CUFFT_UNAVAILABLE;
}

int numuya_cufft_exec_z2z(size_t handle, void* idata, void* odata, int direction) {
    (void)handle;
    (void)idata;
    (void)odata;
    (void)direction;
    return NUMUYA_CUFFT_UNAVAILABLE;
}

#endif /* NUMUYA_HAVE_CUFFT_HEADERS */
