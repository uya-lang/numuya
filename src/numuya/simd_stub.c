/* SIMD fast-path stubs for add/mul/sum on f64 arrays.
 *
 * The public C functions below are compiled as baseline x86_64 code so the
 * binary does not require AVX2 at load time.  The AVX2-specific helpers are
 * marked with __attribute__((target("avx2"))) and are only entered after a
 * runtime __builtin_cpu_supports("avx2") check.  On non-x86_64 platforms the
 * functions fall back to a plain scalar loop.
 */

#include <stddef.h>

#if defined(__x86_64__)
#include <immintrin.h>

__attribute__((target("avx2")))
static void numuya_simd_add_f64_avx2(const double* left, const double* right, double* result, size_t n) {
    size_t i = 0;
    for (; i + 4 <= n; i += 4) {
        __m256d a = _mm256_loadu_pd(left + i);
        __m256d b = _mm256_loadu_pd(right + i);
        __m256d c = _mm256_add_pd(a, b);
        _mm256_storeu_pd(result + i, c);
    }
    for (; i < n; i++) {
        result[i] = left[i] + right[i];
    }
}

__attribute__((target("avx2")))
static void numuya_simd_mul_f64_avx2(const double* left, const double* right, double* result, size_t n) {
    size_t i = 0;
    for (; i + 4 <= n; i += 4) {
        __m256d a = _mm256_loadu_pd(left + i);
        __m256d b = _mm256_loadu_pd(right + i);
        __m256d c = _mm256_mul_pd(a, b);
        _mm256_storeu_pd(result + i, c);
    }
    for (; i < n; i++) {
        result[i] = left[i] * right[i];
    }
}

__attribute__((target("avx2")))
static double numuya_simd_sum_f64_avx2(const double* data, size_t n) {
    __m256d vec_sum = _mm256_setzero_pd();
    size_t i = 0;
    for (; i + 4 <= n; i += 4) {
        __m256d v = _mm256_loadu_pd(data + i);
        vec_sum = _mm256_add_pd(vec_sum, v);
    }
    double temp[4];
    _mm256_storeu_pd(temp, vec_sum);
    double total = temp[0] + temp[1] + temp[2] + temp[3];
    for (; i < n; i++) {
        total += data[i];
    }
    return total;
}
#endif

void numuya_simd_add_f64(const double* left, const double* right, double* result, size_t n) {
#if defined(__x86_64__)
    if (__builtin_cpu_supports("avx2")) {
        numuya_simd_add_f64_avx2(left, right, result, n);
        return;
    }
#endif
    for (size_t i = 0; i < n; i++) {
        result[i] = left[i] + right[i];
    }
}

void numuya_simd_mul_f64(const double* left, const double* right, double* result, size_t n) {
#if defined(__x86_64__)
    if (__builtin_cpu_supports("avx2")) {
        numuya_simd_mul_f64_avx2(left, right, result, n);
        return;
    }
#endif
    for (size_t i = 0; i < n; i++) {
        result[i] = left[i] * right[i];
    }
}

double numuya_simd_sum_f64(const double* data, size_t n) {
#if defined(__x86_64__)
    if (__builtin_cpu_supports("avx2")) {
        return numuya_simd_sum_f64_avx2(data, n);
    }
#endif
    double total = 0.0;
    for (size_t i = 0; i < n; i++) {
        total += data[i];
    }
    return total;
}
