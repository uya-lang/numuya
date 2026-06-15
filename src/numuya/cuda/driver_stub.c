/* Minimal CUDA driver wrappers with runtime dynamic loading.
 *
 * This stub avoids a hard link-time dependency on libcuda so that
 * `make test` (which must not require a GPU) can still build and run.
 * When CUDA is unavailable the wrappers return NUMUYA_CUDA_UNAVAILABLE.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <dlfcn.h>

#define NUMUYA_CUDA_OK 0
#define NUMUYA_CUDA_UNAVAILABLE 1
#define NUMUYA_CUDA_ERROR 2
#define NUMUYA_CUDA_DEVICE_MISMATCH 3

typedef enum CUresult_enum {
    CUDA_SUCCESS = 0
} CUresult;
typedef int CUdevice;

typedef struct CUctx_st* CUcontext;

typedef struct CUstream_st* CUstream;

typedef CUresult (*numuya_cuInit_t)(unsigned int);
typedef CUresult (*numuya_cuDeviceGet_t)(CUdevice*, int);
typedef CUresult (*numuya_cuDeviceGetAttribute_t)(int*, int, CUdevice);
typedef CUresult (*numuya_cuDeviceTotalMem_t)(size_t*, CUdevice);
typedef CUresult (*numuya_cuCtxCreate_t)(CUcontext*, unsigned int, CUdevice);
typedef CUresult (*numuya_cuCtxDestroy_t)(CUcontext);
typedef CUresult (*numuya_cuCtxSetCurrent_t)(CUcontext);
typedef CUresult (*numuya_cuStreamCreate_t)(CUstream*, unsigned int);
typedef CUresult (*numuya_cuStreamSynchronize_t)(CUstream);
typedef CUresult (*numuya_cuStreamDestroy_t)(CUstream);
typedef CUresult (*numuya_cuMemAlloc_t)(size_t*, size_t);
typedef CUresult (*numuya_cuMemFree_t)(size_t);
typedef CUresult (*numuya_cuMemcpyHtoD_t)(size_t, const void*, size_t);
typedef CUresult (*numuya_cuMemcpyDtoH_t)(void*, size_t, size_t);
typedef CUresult (*numuya_cuMemcpyHtoDAsync_t)(size_t, const void*, size_t, CUstream);
typedef CUresult (*numuya_cuMemcpyDtoHAsync_t)(void*, size_t, size_t, CUstream);

typedef struct CUmod_st* CUmodule;
typedef struct CUfunc_st* CUfunction;

typedef CUresult (*numuya_cuModuleLoadData_t)(CUmodule*, const void*);
typedef CUresult (*numuya_cuModuleGetFunction_t)(CUfunction*, CUmodule, const char*);
typedef CUresult (*numuya_cuModuleUnload_t)(CUmodule);
typedef CUresult (*numuya_cuLaunchKernel_t)(CUfunction, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, CUstream, void**, void**);

#define NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR 75
#define NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR 76

static void* numuya_cuda_handle = NULL;
static numuya_cuInit_t numuya_pfn_cuInit = NULL;
static numuya_cuDeviceGet_t numuya_pfn_cuDeviceGet = NULL;
static numuya_cuDeviceGetAttribute_t numuya_pfn_cuDeviceGetAttribute = NULL;
static numuya_cuDeviceTotalMem_t numuya_pfn_cuDeviceTotalMem = NULL;
static numuya_cuCtxCreate_t numuya_pfn_cuCtxCreate = NULL;
static numuya_cuCtxDestroy_t numuya_pfn_cuCtxDestroy = NULL;
static numuya_cuCtxSetCurrent_t numuya_pfn_cuCtxSetCurrent = NULL;
static numuya_cuStreamCreate_t numuya_pfn_cuStreamCreate = NULL;
static numuya_cuStreamSynchronize_t numuya_pfn_cuStreamSynchronize = NULL;
static numuya_cuStreamDestroy_t numuya_pfn_cuStreamDestroy = NULL;
static numuya_cuMemAlloc_t numuya_pfn_cuMemAlloc = NULL;
static numuya_cuMemFree_t numuya_pfn_cuMemFree = NULL;
static numuya_cuMemcpyHtoD_t numuya_pfn_cuMemcpyHtoD = NULL;
static numuya_cuMemcpyDtoH_t numuya_pfn_cuMemcpyDtoH = NULL;
static numuya_cuMemcpyHtoDAsync_t numuya_pfn_cuMemcpyHtoDAsync = NULL;
static numuya_cuMemcpyDtoHAsync_t numuya_pfn_cuMemcpyDtoHAsync = NULL;

static numuya_cuModuleLoadData_t numuya_pfn_cuModuleLoadData = NULL;
static numuya_cuModuleGetFunction_t numuya_pfn_cuModuleGetFunction = NULL;
static numuya_cuModuleUnload_t numuya_pfn_cuModuleUnload = NULL;
static numuya_cuLaunchKernel_t numuya_pfn_cuLaunchKernel = NULL;

static CUcontext numuya_current_context = NULL;

#define NUMUYA_MAX_STREAMS 256
typedef struct {
    size_t handle;
    void* context;
} numuya_stream_entry_t;
static numuya_stream_entry_t numuya_stream_entries[NUMUYA_MAX_STREAMS];
static int numuya_stream_count = 0;

static void numuya_stream_record(void* context, size_t stream) {
    for (int i = 0; i < NUMUYA_MAX_STREAMS; i++) {
        if (numuya_stream_entries[i].handle == 0) {
            numuya_stream_entries[i].handle = stream;
            numuya_stream_entries[i].context = context;
            if (i >= numuya_stream_count) {
                numuya_stream_count = i + 1;
            }
            return;
        }
    }
}

static void* numuya_stream_get_context(size_t stream) {
    for (int i = 0; i < numuya_stream_count; i++) {
        if (numuya_stream_entries[i].handle == stream) {
            return numuya_stream_entries[i].context;
        }
    }
    return NULL;
}

static void numuya_stream_remove(size_t stream) {
    for (int i = 0; i < NUMUYA_MAX_STREAMS; i++) {
        if (numuya_stream_entries[i].handle == stream) {
            numuya_stream_entries[i].handle = 0;
            numuya_stream_entries[i].context = NULL;
            return;
        }
    }
}

static int numuya_cuda_load(void) {
    if (numuya_cuda_handle != NULL) {
        return NUMUYA_CUDA_OK;
    }

    numuya_cuda_handle = dlopen("libcuda.so.1", RTLD_NOW | RTLD_NODELETE);
    if (numuya_cuda_handle == NULL) {
        numuya_cuda_handle = dlopen("libcuda.so", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_cuda_handle == NULL) {
        return NUMUYA_CUDA_UNAVAILABLE;
    }

    numuya_pfn_cuInit = (numuya_cuInit_t)dlsym(numuya_cuda_handle, "cuInit");
    numuya_pfn_cuDeviceGet = (numuya_cuDeviceGet_t)dlsym(numuya_cuda_handle, "cuDeviceGet");
    numuya_pfn_cuDeviceGetAttribute = (numuya_cuDeviceGetAttribute_t)dlsym(numuya_cuda_handle, "cuDeviceGetAttribute");
    numuya_pfn_cuDeviceTotalMem = (numuya_cuDeviceTotalMem_t)dlsym(numuya_cuda_handle, "cuDeviceTotalMem_v2");
    if (numuya_pfn_cuDeviceTotalMem == NULL) {
        numuya_pfn_cuDeviceTotalMem = (numuya_cuDeviceTotalMem_t)dlsym(numuya_cuda_handle, "cuDeviceTotalMem");
    }
    numuya_pfn_cuCtxCreate = (numuya_cuCtxCreate_t)dlsym(numuya_cuda_handle, "cuCtxCreate_v2");
    if (numuya_pfn_cuCtxCreate == NULL) {
        numuya_pfn_cuCtxCreate = (numuya_cuCtxCreate_t)dlsym(numuya_cuda_handle, "cuCtxCreate");
    }
    numuya_pfn_cuCtxDestroy = (numuya_cuCtxDestroy_t)dlsym(numuya_cuda_handle, "cuCtxDestroy_v2");
    if (numuya_pfn_cuCtxDestroy == NULL) {
        numuya_pfn_cuCtxDestroy = (numuya_cuCtxDestroy_t)dlsym(numuya_cuda_handle, "cuCtxDestroy");
    }
    numuya_pfn_cuCtxSetCurrent = (numuya_cuCtxSetCurrent_t)dlsym(numuya_cuda_handle, "cuCtxSetCurrent");
    numuya_pfn_cuStreamCreate = (numuya_cuStreamCreate_t)dlsym(numuya_cuda_handle, "cuStreamCreate");
    numuya_pfn_cuStreamSynchronize = (numuya_cuStreamSynchronize_t)dlsym(numuya_cuda_handle, "cuStreamSynchronize");
    numuya_pfn_cuStreamDestroy = (numuya_cuStreamDestroy_t)dlsym(numuya_cuda_handle, "cuStreamDestroy_v2");
    if (numuya_pfn_cuStreamDestroy == NULL) {
        numuya_pfn_cuStreamDestroy = (numuya_cuStreamDestroy_t)dlsym(numuya_cuda_handle, "cuStreamDestroy");
    }
    numuya_pfn_cuMemAlloc = (numuya_cuMemAlloc_t)dlsym(numuya_cuda_handle, "cuMemAlloc_v2");
    if (numuya_pfn_cuMemAlloc == NULL) {
        numuya_pfn_cuMemAlloc = (numuya_cuMemAlloc_t)dlsym(numuya_cuda_handle, "cuMemAlloc");
    }
    numuya_pfn_cuMemFree = (numuya_cuMemFree_t)dlsym(numuya_cuda_handle, "cuMemFree_v2");
    if (numuya_pfn_cuMemFree == NULL) {
        numuya_pfn_cuMemFree = (numuya_cuMemFree_t)dlsym(numuya_cuda_handle, "cuMemFree");
    }
    numuya_pfn_cuMemcpyHtoD = (numuya_cuMemcpyHtoD_t)dlsym(numuya_cuda_handle, "cuMemcpyHtoD_v2");
    if (numuya_pfn_cuMemcpyHtoD == NULL) {
        numuya_pfn_cuMemcpyHtoD = (numuya_cuMemcpyHtoD_t)dlsym(numuya_cuda_handle, "cuMemcpyHtoD");
    }
    numuya_pfn_cuMemcpyDtoH = (numuya_cuMemcpyDtoH_t)dlsym(numuya_cuda_handle, "cuMemcpyDtoH_v2");
    if (numuya_pfn_cuMemcpyDtoH == NULL) {
        numuya_pfn_cuMemcpyDtoH = (numuya_cuMemcpyDtoH_t)dlsym(numuya_cuda_handle, "cuMemcpyDtoH");
    }
    numuya_pfn_cuMemcpyHtoDAsync = (numuya_cuMemcpyHtoDAsync_t)dlsym(numuya_cuda_handle, "cuMemcpyHtoDAsync_v2");
    if (numuya_pfn_cuMemcpyHtoDAsync == NULL) {
        numuya_pfn_cuMemcpyHtoDAsync = (numuya_cuMemcpyHtoDAsync_t)dlsym(numuya_cuda_handle, "cuMemcpyHtoDAsync");
    }
    numuya_pfn_cuMemcpyDtoHAsync = (numuya_cuMemcpyDtoHAsync_t)dlsym(numuya_cuda_handle, "cuMemcpyDtoHAsync_v2");
    if (numuya_pfn_cuMemcpyDtoHAsync == NULL) {
        numuya_pfn_cuMemcpyDtoHAsync = (numuya_cuMemcpyDtoHAsync_t)dlsym(numuya_cuda_handle, "cuMemcpyDtoHAsync");
    }

    numuya_pfn_cuModuleLoadData = (numuya_cuModuleLoadData_t)dlsym(numuya_cuda_handle, "cuModuleLoadData");
    numuya_pfn_cuModuleGetFunction = (numuya_cuModuleGetFunction_t)dlsym(numuya_cuda_handle, "cuModuleGetFunction");
    numuya_pfn_cuModuleUnload = (numuya_cuModuleUnload_t)dlsym(numuya_cuda_handle, "cuModuleUnload");
    numuya_pfn_cuLaunchKernel = (numuya_cuLaunchKernel_t)dlsym(numuya_cuda_handle, "cuLaunchKernel");

    if (numuya_pfn_cuInit == NULL ||
        numuya_pfn_cuDeviceGet == NULL ||
        numuya_pfn_cuDeviceGetAttribute == NULL ||
        numuya_pfn_cuDeviceTotalMem == NULL ||
        numuya_pfn_cuCtxCreate == NULL ||
        numuya_pfn_cuCtxDestroy == NULL ||
        numuya_pfn_cuCtxSetCurrent == NULL ||
        numuya_pfn_cuStreamCreate == NULL ||
        numuya_pfn_cuStreamSynchronize == NULL ||
        numuya_pfn_cuStreamDestroy == NULL ||
        numuya_pfn_cuMemAlloc == NULL ||
        numuya_pfn_cuMemFree == NULL ||
        numuya_pfn_cuMemcpyHtoD == NULL ||
        numuya_pfn_cuMemcpyDtoH == NULL ||
        numuya_pfn_cuMemcpyHtoDAsync == NULL ||
        numuya_pfn_cuMemcpyDtoHAsync == NULL ||
        numuya_pfn_cuModuleLoadData == NULL ||
        numuya_pfn_cuModuleGetFunction == NULL ||
        numuya_pfn_cuModuleUnload == NULL ||
        numuya_pfn_cuLaunchKernel == NULL) {
        return NUMUYA_CUDA_UNAVAILABLE;
    }

    return NUMUYA_CUDA_OK;
}

int numuya_cuda_init(void) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult res = numuya_pfn_cuInit(0);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    /* Create a default context for device 0 so that consumers such as
     * cuda_malloc can allocate device memory without explicit context
     * management in simple test scenarios. */
    if (numuya_current_context == NULL) {
        CUdevice device = 0;
        const CUresult device_res = numuya_pfn_cuDeviceGet(&device, 0);
        if (device_res == 0) {
            CUcontext ctx = NULL;
            const CUresult ctx_res = numuya_pfn_cuCtxCreate(&ctx, 0, device);
            if (ctx_res == 0) {
                numuya_current_context = ctx;
                numuya_pfn_cuCtxSetCurrent(ctx);
            }
        }
    }

    return NUMUYA_CUDA_OK;
}

int numuya_cuda_get_device(int ordinal, int* major, int* minor, size_t* total_memory_bytes) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    CUdevice device = 0;
    CUresult res = numuya_pfn_cuDeviceGet(&device, ordinal);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    int major_value = 0;
    int minor_value = 0;
    res = numuya_pfn_cuDeviceGetAttribute(&major_value, NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR, device);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    res = numuya_pfn_cuDeviceGetAttribute(&minor_value, NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR, device);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    size_t memory = 0;
    res = numuya_pfn_cuDeviceTotalMem(&memory, device);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *major = major_value;
    *minor = minor_value;
    *total_memory_bytes = memory;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_create_context(int ordinal, void** context) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    CUdevice device = 0;
    CUresult res = numuya_pfn_cuDeviceGet(&device, ordinal);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    CUcontext ctx = NULL;
    res = numuya_pfn_cuCtxCreate(&ctx, 0, device);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *context = ctx;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_destroy_context(void* context) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult res = numuya_pfn_cuCtxDestroy((CUcontext)context);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    if (numuya_current_context == context) {
        numuya_current_context = NULL;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_set_current_context(void* context) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult res = numuya_pfn_cuCtxSetCurrent((CUcontext)context);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    numuya_current_context = context;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_create_stream(void* context, size_t* stream) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult set_res = numuya_pfn_cuCtxSetCurrent((CUcontext)context);
    if (set_res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    numuya_current_context = context;

    CUstream s = NULL;
    const CUresult res = numuya_pfn_cuStreamCreate(&s, 0);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *stream = (size_t)s;
    numuya_stream_record(context, (size_t)s);
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_synchronize_stream(void* context, size_t stream) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const void* owning_context = numuya_stream_get_context(stream);
    if (owning_context != NULL && owning_context != context) {
        return NUMUYA_CUDA_DEVICE_MISMATCH;
    }

    const CUresult set_res = numuya_pfn_cuCtxSetCurrent((CUcontext)context);
    if (set_res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    numuya_current_context = context;

    const CUresult res = numuya_pfn_cuStreamSynchronize((CUstream)stream);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_destroy_stream(void* context, size_t stream) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const void* owning_context = numuya_stream_get_context(stream);
    if (owning_context != NULL && owning_context != context) {
        return NUMUYA_CUDA_DEVICE_MISMATCH;
    }

    const CUresult set_res = numuya_pfn_cuCtxSetCurrent((CUcontext)context);
    if (set_res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    numuya_current_context = context;

    const CUresult res = numuya_pfn_cuStreamDestroy((CUstream)stream);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    numuya_stream_remove(stream);
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_malloc(size_t size, size_t* ptr) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (numuya_current_context == NULL) {
        return NUMUYA_CUDA_ERROR;
    }

    size_t device_ptr = 0;
    const CUresult res = numuya_pfn_cuMemAlloc(&device_ptr, size);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *ptr = device_ptr;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_free(size_t ptr) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (ptr == 0) {
        return NUMUYA_CUDA_OK;
    }

    const CUresult res = numuya_pfn_cuMemFree(ptr);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_memcpy_htod(size_t dst, const void* src, size_t size) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (size == 0) {
        return NUMUYA_CUDA_OK;
    }

    if (numuya_current_context == NULL) {
        return NUMUYA_CUDA_ERROR;
    }

    const CUresult res = numuya_pfn_cuMemcpyHtoD(dst, src, size);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_memcpy_dtoh(void* dst, size_t src, size_t size) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (size == 0) {
        return NUMUYA_CUDA_OK;
    }

    if (numuya_current_context == NULL) {
        return NUMUYA_CUDA_ERROR;
    }

    const CUresult res = numuya_pfn_cuMemcpyDtoH(dst, src, size);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_memcpy_htod_async(size_t dst, const void* src, size_t size, size_t stream) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (size == 0) {
        return NUMUYA_CUDA_OK;
    }

    if (numuya_current_context == NULL) {
        return NUMUYA_CUDA_ERROR;
    }

    const CUresult res = numuya_pfn_cuMemcpyHtoDAsync(dst, src, size, (CUstream)stream);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_memcpy_dtoh_async(void* dst, size_t src, size_t size, size_t stream) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (size == 0) {
        return NUMUYA_CUDA_OK;
    }

    if (numuya_current_context == NULL) {
        return NUMUYA_CUDA_ERROR;
    }

    const CUresult res = numuya_pfn_cuMemcpyDtoHAsync(dst, src, size, (CUstream)stream);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_module_load_data(void* context, const void* image, void** module) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult set_res = numuya_pfn_cuCtxSetCurrent((CUcontext)context);
    if (set_res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    numuya_current_context = context;

    CUmodule mod = NULL;
    const CUresult res = numuya_pfn_cuModuleLoadData(&mod, image);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *module = mod;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_module_load_ptx(void* context, const char* ptx, void** module) {
    return numuya_cuda_module_load_data(context, ptx, module);
}

int numuya_cuda_module_get_function(void* module, const char* name, void** func) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    CUfunction f = NULL;
    const CUresult res = numuya_pfn_cuModuleGetFunction(&f, (CUmodule)module, name);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }

    *func = f;
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_module_unload(void* module) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    if (module == NULL) {
        return NUMUYA_CUDA_OK;
    }

    const CUresult res = numuya_pfn_cuModuleUnload((CUmodule)module);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}

int numuya_cuda_launch_kernel(
        void* func,
        unsigned int grid_dim_x, unsigned int grid_dim_y, unsigned int grid_dim_z,
        unsigned int block_dim_x, unsigned int block_dim_y, unsigned int block_dim_z,
        unsigned int shared_mem_bytes,
        size_t stream,
        void** args) {
    const int status = numuya_cuda_load();
    if (status != NUMUYA_CUDA_OK) {
        return status;
    }

    const CUresult res = numuya_pfn_cuLaunchKernel(
        (CUfunction)func,
        grid_dim_x, grid_dim_y, grid_dim_z,
        block_dim_x, block_dim_y, block_dim_z,
        shared_mem_bytes,
        (CUstream)stream,
        args,
        NULL);
    if (res != 0) {
        return NUMUYA_CUDA_ERROR;
    }
    return NUMUYA_CUDA_OK;
}
