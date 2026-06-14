UPM := ../uya/bin/cmd/upm
UYA := ../uya/bin/uya
MANIFEST := uya.toml
CONSUMER_MANIFEST := tests/fixtures/upm_consumer/uya.toml
CONSUMER_MAIN := tests/fixtures/upm_consumer/src/main.uya
TEST ?= src/numuya/_tests/test_testing_helpers.uya
TESTS := $(sort $(wildcard src/numuya/_tests/test_*.uya))
BENCH ?= src/numuya/_benchmarks/bench_simd.uya
BENCHES := $(sort $(wildcard src/numuya/_benchmarks/bench_*.uya))

.PHONY: bootstrap-upm upm-install test-one test test-cuda test-cuda-vendor check-one verify-upm-consumer require-upm bench

require-upm:
	@test -x "$(UPM)" || { echo "missing executable $(UPM)"; exit 1; }

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
	@test -n "$(CUDA_TESTS)" || { echo "no cuda test files found"; exit 1; }
	@for test in $(CUDA_TESTS); do \
		echo "NUMUYA_CUDA_REQUIRED=1 LDFLAGS=\"-lcuda\" $(UYA) test $$test --manifest-path $(MANIFEST)"; \
		NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcuda" $(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

test-cuda-vendor: bootstrap-upm
	@test -n "$(CUDA_TESTS)" || { echo "no cuda test files found"; exit 1; }
	@for test in $(CUDA_TESTS); do \
		echo "NUMUYA_CUDA_REQUIRED=1 LDFLAGS=\"-lcublasLt -lcublas -lcufft -lcurand -lcuda\" $(UYA) test $$test --manifest-path $(MANIFEST)"; \
		NUMUYA_CUDA_REQUIRED=1 LDFLAGS="-lcublasLt -lcublas -lcufft -lcurand -lcuda" $(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

check-one: require-upm
	$(UYA) check "$(TEST)" --manifest-path $(MANIFEST)

bench: require-upm
	@test -n "$(BENCHES)" || { echo "no benchmark files found"; exit 1; }
	@for bench in $(BENCHES); do \
		echo "$(UYA) run $$bench --manifest-path $(MANIFEST)"; \
		$(UYA) run "$$bench" --manifest-path $(MANIFEST) || exit $$?; \
	done

verify-upm-consumer: require-upm
	$(UPM) install --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) check $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) run $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
