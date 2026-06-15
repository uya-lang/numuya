/* Optional cuRAND backend loader.
 *
 * When <curand.h> and <cuda.h> are available this stub dynamically loads
 * libcurand at runtime and forwards calls through function pointers.  This
 * keeps NumUya free of a hard link-time dependency on the vendor library:
 * builds without cuRAND still compile and simply receive
 * NUMUYA_CURAND_UNAVAILABLE at runtime.
 *
 * When the headers are absent the stub compiles to no-op functions that
 * report unavailability, so the package can be built on machines without
 * the CUDA toolkit.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <dlfcn.h>

#define NUMUYA_CURAND_OK 0
#define NUMUYA_CURAND_UNAVAILABLE 1
#define NUMUYA_CURAND_ERROR 2

#if defined(__has_include)
#  if __has_include(<curand.h>) && __has_include(<cuda.h>)
#    define NUMUYA_HAVE_CURAND_HEADERS 1
#  endif
#endif

#if NUMUYA_HAVE_CURAND_HEADERS

#include <cuda.h>
#include <curand.h>

static void* numuya_curand_handle = NULL;

static curandStatus_t (*pfn_curandCreateGenerator)(curandGenerator_t*, curandRngType_t) = NULL;
static curandStatus_t (*pfn_curandDestroyGenerator)(curandGenerator_t) = NULL;
static curandStatus_t (*pfn_curandSetStream)(curandGenerator_t, CUstream) = NULL;
static curandStatus_t (*pfn_curandSetPseudoRandomGeneratorSeed)(curandGenerator_t, unsigned long long) = NULL;
static curandStatus_t (*pfn_curandGenerateUniform)(curandGenerator_t, float*, size_t) = NULL;

static int numuya_curand_load(void) {
    if (numuya_curand_handle != NULL) {
        return NUMUYA_CURAND_OK;
    }

    numuya_curand_handle = dlopen("libcurand.so.10", RTLD_NOW | RTLD_NODELETE);
    if (numuya_curand_handle == NULL) {
        numuya_curand_handle = dlopen("libcurand.so.11", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_curand_handle == NULL) {
        numuya_curand_handle = dlopen("libcurand.so.1", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_curand_handle == NULL) {
        numuya_curand_handle = dlopen("libcurand.so", RTLD_NOW | RTLD_NODELETE);
    }
    if (numuya_curand_handle == NULL) {
        return NUMUYA_CURAND_UNAVAILABLE;
    }

    pfn_curandCreateGenerator = (curandStatus_t (*)(curandGenerator_t*, curandRngType_t))dlsym(numuya_curand_handle, "curandCreateGenerator");
    pfn_curandDestroyGenerator = (curandStatus_t (*)(curandGenerator_t))dlsym(numuya_curand_handle, "curandDestroyGenerator");
    pfn_curandSetStream = (curandStatus_t (*)(curandGenerator_t, CUstream))dlsym(numuya_curand_handle, "curandSetStream");
    pfn_curandSetPseudoRandomGeneratorSeed = (curandStatus_t (*)(curandGenerator_t, unsigned long long))dlsym(numuya_curand_handle, "curandSetPseudoRandomGeneratorSeed");
    pfn_curandGenerateUniform = (curandStatus_t (*)(curandGenerator_t, float*, size_t))dlsym(numuya_curand_handle, "curandGenerateUniform");

    if (pfn_curandCreateGenerator == NULL ||
        pfn_curandDestroyGenerator == NULL ||
        pfn_curandSetStream == NULL ||
        pfn_curandSetPseudoRandomGeneratorSeed == NULL ||
        pfn_curandGenerateUniform == NULL) {
        return NUMUYA_CURAND_UNAVAILABLE;
    }

    return NUMUYA_CURAND_OK;
}

int numuya_curand_available(void) {
    return numuya_curand_load();
}

int numuya_curand_random_f32(void* stream, void* ptr, size_t n, unsigned long long seed) {
    const int load_status = numuya_curand_load();
    if (load_status != NUMUYA_CURAND_OK) {
        return load_status;
    }

    curandGenerator_t generator = NULL;
    curandStatus_t status = pfn_curandCreateGenerator(&generator, CURAND_RNG_PSEUDO_DEFAULT);
    if (status != CURAND_STATUS_SUCCESS) {
        return NUMUYA_CURAND_ERROR;
    }

    if (stream != NULL) {
        status = pfn_curandSetStream(generator, (CUstream)stream);
        if (status != CURAND_STATUS_SUCCESS) {
            pfn_curandDestroyGenerator(generator);
            return NUMUYA_CURAND_ERROR;
        }
    }

    status = pfn_curandSetPseudoRandomGeneratorSeed(generator, seed);
    if (status != CURAND_STATUS_SUCCESS) {
        pfn_curandDestroyGenerator(generator);
        return NUMUYA_CURAND_ERROR;
    }

    status = pfn_curandGenerateUniform(generator, (float*)ptr, n);
    const int generate_status = (status == CURAND_STATUS_SUCCESS) ? NUMUYA_CURAND_OK : NUMUYA_CURAND_ERROR;

    pfn_curandDestroyGenerator(generator);
    return generate_status;
}

#else /* NUMUYA_HAVE_CURAND_HEADERS */

int numuya_curand_available(void) {
    return NUMUYA_CURAND_UNAVAILABLE;
}

int numuya_curand_random_f32(void* stream, void* ptr, size_t n, unsigned long long seed) {
    (void)stream;
    (void)ptr;
    (void)n;
    (void)seed;
    return NUMUYA_CURAND_UNAVAILABLE;
}

#endif /* NUMUYA_HAVE_CURAND_HEADERS */
