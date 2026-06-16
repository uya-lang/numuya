/* Minimal dlopen/dlsym/dlclose passthrough + generic indirect-call helpers.
 *
 * This is the ONLY C helper in NumUya's CUDA backend.
 * It contains zero business logic, no CUDA types, no function pointer caching,
 * no version compatibility, no stream-context management.
 * All of that logic lives in pure Uya (driver.uya, etc.).
 *
 * The indirect-call helpers exist only because @asm has an 8-input-per-instruction
 * limit, and cuLaunchKernel needs 10+ parameters. These helpers are purely FFI
 * infrastructure — they cast all arguments to unsigned long, call the function
 * pointer with correct ABI, and return the result as int32.
 * No CUDA-specific logic whatsoever.
 */

#include <dlfcn.h>

/* Use unsigned long instead of size_t to avoid stddef.h dependency issues.
 * On x86-64 Linux: sizeof(unsigned long) == sizeof(size_t) == 8. */
typedef unsigned long numuya_ulong;

/* dlopen passthrough */
void* numuya_dlopen(const char* filename, int flags) {
    return dlopen(filename, flags);
}

/* dlsym passthrough */
void* numuya_dlsym(void* handle, const char* symbol) {
    return dlsym(handle, symbol);
}

/* dlclose passthrough */
int numuya_dlclose(void* handle) {
    return (int)dlclose(handle);
}

/* dlerror passthrough */
const char* numuya_dlerror(void) {
    return dlerror();
}

/* Generic indirect-call helpers.
 * All args are passed as numuya_ulong (8 bytes on x86-64).
 * Return value is cast to int (CUresult = int on CUDA).
 */

int numuya_call_0(numuya_ulong func_ptr) {
    return (int)((int(*)(void))(void*)func_ptr)();
}

int numuya_call_1(numuya_ulong func_ptr, numuya_ulong a0) {
    return (int)((int(*)(numuya_ulong))(void*)func_ptr)(a0);
}

int numuya_call_2(numuya_ulong func_ptr, numuya_ulong a0, numuya_ulong a1) {
    return (int)((int(*)(numuya_ulong, numuya_ulong))(void*)func_ptr)(a0, a1);
}

int numuya_call_3(numuya_ulong func_ptr, numuya_ulong a0, numuya_ulong a1, numuya_ulong a2) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong))(void*)func_ptr)(a0, a1, a2);
}

int numuya_call_4(numuya_ulong func_ptr, numuya_ulong a0, numuya_ulong a1, numuya_ulong a2, numuya_ulong a3) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong))(void*)func_ptr)(a0, a1, a2, a3);
}

int numuya_call_5(numuya_ulong func_ptr, numuya_ulong a0, numuya_ulong a1, numuya_ulong a2, numuya_ulong a3, numuya_ulong a4) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong))(void*)func_ptr)(a0, a1, a2, a3, a4);
}

int numuya_call_6(numuya_ulong func_ptr, numuya_ulong a0, numuya_ulong a1, numuya_ulong a2, numuya_ulong a3, numuya_ulong a4, numuya_ulong a5) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong))(void*)func_ptr)(a0, a1, a2, a3, a4, a5);
}

/* cuLaunchKernel专用: 10 CUDA params + 自动添加 extra=NULL (第11个参数) */
int numuya_cuda_launch_kernel(numuya_ulong func_ptr,
    numuya_ulong a0, numuya_ulong a1, numuya_ulong a2, numuya_ulong a3,
    numuya_ulong a4, numuya_ulong a5, numuya_ulong a6, numuya_ulong a7,
    numuya_ulong a8, numuya_ulong a9) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong,
                         numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong,
                         numuya_ulong))(void*)func_ptr)(
        a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, 0);
}

/* cublasLtMatmul专用: 16-arg cuBLASLt matmul call.
 * Full signature:
 *   cublasLtMatmul(handle, desc, alpha, A, Adesc, B, Bdesc, beta,
 *                  C, Cdesc, D, Ddesc, algo, workspace, workspaceSize, stream)
 * Uya passes all 16 args; D=C and Ddesc=Cdesc for in-place matmul.
 */
int numuya_cublaslt_matmul(numuya_ulong func_ptr,
    numuya_ulong a0, numuya_ulong a1, numuya_ulong a2, numuya_ulong a3,
    numuya_ulong a4, numuya_ulong a5, numuya_ulong a6, numuya_ulong a7,
    numuya_ulong a8, numuya_ulong a9, numuya_ulong a10, numuya_ulong a11,
    numuya_ulong a12, numuya_ulong a13, numuya_ulong a14, numuya_ulong a15) {
    return (int)((int(*)(numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong,
                         numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong,
                         numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong, numuya_ulong,
                         numuya_ulong))(void*)func_ptr)(
        a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15);
}