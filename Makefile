UPM := ../uya/bin/cmd/upm
UYA := ../uya/bin/uya
MANIFEST := uya.toml
CONSUMER_MANIFEST := tests/fixtures/upm_consumer/uya.toml
CONSUMER_MAIN := tests/fixtures/upm_consumer/src/main.uya
TEST ?= src/numuya/_tests/test_testing_helpers.uya
TESTS := $(sort $(wildcard src/numuya/_tests/test_*.uya))
BENCH ?= src/numuya/_benchmarks/bench_simd.uya
BENCHES := $(sort $(wildcard src/numuya/_benchmarks/bench_*.uya))

.PHONY: bootstrap-upm upm-install test-one test test-cuda test-cuda-vendor check-one check-cpu-core-deps verify-upm-consumer require-upm bench bench-numpy-cpu bench-numpy-gpu-ref bench-compare bench-spotcheck bench-spotcheck-gpu bench-guardrails-cpu bench-guardrails-gpu bench-guardrails-gpu-vendor cuda-ptx-embed cuda-cubin-embed cuda-ptx-validate

require-upm:
	@test -x "$(UPM)" || { echo "missing executable $(UPM)"; exit 1; }

cuda-ptx-embed: require-upm
	$(UYA) run src/numuya/_tools/embed_ptx.uya --manifest-path $(MANIFEST)

CUDA_PTX_SRC := src/numuya/cuda/ptx/core_sm86.ptx
CUDA_CUBIN_CACHE := src/numuya/cuda/ptx/core_sm86.cubin

cuda-ptx-validate: require-upm
	@test -f "$(CUDA_PTX_SRC)" || { echo "PTX source-of-truth missing: $(CUDA_PTX_SRC)"; exit 1; }
	ptxas -arch=sm_86 "$(CUDA_PTX_SRC)" -o /tmp/numuya_core_sm86.cubin
	@echo "ptxas -arch=sm_86 OK: $(CUDA_PTX_SRC)"
	@if [ -f "$(CUDA_CUBIN_CACHE)" ]; then \
		echo "cubin cache exists but is not required: $(CUDA_CUBIN_CACHE)"; \
	else \
		echo "cubin cache absent; PTX remains source-of-truth"; \
	fi

cuda-cubin-embed: require-upm
	ptxas -arch=sm_86 "$(CUDA_PTX_SRC)" -o "$(CUDA_CUBIN_CACHE)"
	$(UYA) run src/numuya/_tools/embed_cubin.uya --manifest-path $(MANIFEST)

bootstrap-upm: require-upm
	$(UPM) install --manifest-path $(MANIFEST)

upm-install: require-upm
	$(UPM) install --manifest-path $(MANIFEST)

test-one: require-upm
	$(UYA) test "$(TEST)" --manifest-path $(MANIFEST)

CUDA_TESTS := $(sort $(wildcard src/numuya/_tests/test_cuda_*.uya))
TESTS_NON_CUDA := $(filter-out $(CUDA_TESTS),$(TESTS))

test: bootstrap-upm
	@test -n "$(TESTS_NON_CUDA)" || { echo "no test files found"; exit 1; }
	@for test in $(TESTS_NON_CUDA); do \
		echo "$(UYA) test $$test --manifest-path $(MANIFEST)"; \
		$(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

test-cuda: bootstrap-upm
	@echo "CUDA driver tests use the pure NumUya CUDA kernel backend; vendor libraries stay disabled."
	@test -n "$(CUDA_TESTS)" || { echo "no cuda test files found"; exit 1; }
	@for test in $(CUDA_TESTS); do \
		echo "NUMUYA_CUDA_REQUIRED=1 LDFLAGS=\"-lcuda\" $(UYA) test $$test --manifest-path $(MANIFEST)"; \
		NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" $(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

test-cuda-vendor: bootstrap-upm
	@echo "CUDA vendor tests explicitly enable cuBLAS/cuFFT/cuRAND coverage."
	@test -n "$(CUDA_TESTS)" || { echo "no cuda test files found"; exit 1; }
	@for test in $(CUDA_TESTS); do \
		echo "NUMUYA_CUDA_REQUIRED=1 NUMUYA_CUDA_VENDOR=1 LDFLAGS=\"-lcublasLt -lcublas -lcufft -lcurand -lcuda\" $(UYA) test $$test --manifest-path $(MANIFEST)"; \
		NUMUYA_CUDA_REQUIRED=1 NUMUYA_CUDA_VENDOR=1 LDFLAGS="-lcublasLt -lcublas -lcufft -lcurand -lcuda" $(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

check-one: require-upm
	$(UYA) check "$(TEST)" --manifest-path $(MANIFEST)

check-cpu-core-deps:
	@! rg -n '@c_import|extern "libc" fn (sqrt|exp|log|sin|cos)\b|math_stub\.c|simd_stub\.c|-lm|\b(Python|python|NumPy|numpy|BLAS|blas|LAPACK|lapack)\b' src/numuya \
		-g '*.uya' \
		-g '!**/cuda/**' \
		-g '!**/_tests/**' \
		-g '!**/_benchmarks/**' \
		-g '!**/_tools/**'

bench: require-upm
	@test -n "$(BENCHES)" || { echo "no benchmark files found"; exit 1; }
	@for bench in $(BENCHES); do \
		echo "$(UYA) run $$bench --manifest-path $(MANIFEST)"; \
		$(UYA) run "$$bench" --manifest-path $(MANIFEST) || exit $$?; \
	done

bench-numpy-cpu:
	python benchmarks/python/bench_numpy_cpu.py

bench-numpy-gpu-ref:
	python benchmarks/python/bench_gpu_reference.py

bench-spotcheck: require-upm
	python benchmarks/python/spotcheck_benchmarks.py --json

bench-spotcheck-gpu: require-upm
	python benchmarks/python/spotcheck_benchmarks.py --json

bench-guardrails-cpu: test bench-spotcheck

bench-guardrails-gpu: test-cuda bench-spotcheck-gpu

bench-guardrails-gpu-vendor: test-cuda-vendor bench-spotcheck-gpu

bench-compare: bench bench-numpy-cpu bench-numpy-gpu-ref

verify-upm-consumer: require-upm
	$(UPM) install --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) check $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) run $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
