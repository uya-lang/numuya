/* Minimal CUDA driver wrappers with runtime dynamic loading.
 *
 * This stub avoids a hard link-time dependency on libcuda so that
 * `make test` (which must not require a GPU) can still build and run.
 * When CUDA is unavailable the wrappers return NUMUYA_CUDA_UNAVAILABLE.
 */

#include <stddef.h>
#include <stdint.h>
#include <dlfcn.h>

#define NUMUYA_CUDA_OK 0
#define NUMUYA_CUDA_UNAVAILABLE 1
#define NUMUYA_CUDA_ERROR 2

typedef int CUresult;
typedef int CUdevice;

typedef CUresult (*numuya_cuInit_t)(unsigned int);
typedef CUresult (*numuya_cuDeviceGet_t)(CUdevice*, int);
typedef CUresult (*numuya_cuDeviceGetAttribute_t)(int*, int, CUdevice);
typedef CUresult (*numuya_cuDeviceTotalMem_t)(size_t*, CUdevice);

#define NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR 75
#define NUMUYA_CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR 76

static void* numuya_cuda_handle = NULL;
static numuya_cuInit_t numuya_pfn_cuInit = NULL;
static numuya_cuDeviceGet_t numuya_pfn_cuDeviceGet = NULL;
static numuya_cuDeviceGetAttribute_t numuya_pfn_cuDeviceGetAttribute = NULL;
static numuya_cuDeviceTotalMem_t numuya_pfn_cuDeviceTotalMem = NULL;

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

    if (numuya_pfn_cuInit == NULL ||
        numuya_pfn_cuDeviceGet == NULL ||
        numuya_pfn_cuDeviceGetAttribute == NULL ||
        numuya_pfn_cuDeviceTotalMem == NULL) {
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
