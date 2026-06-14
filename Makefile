UPM := ../uya/bin/cmd/upm
UYA := ../uya/bin/uya
MANIFEST := uya.toml
CONSUMER_MANIFEST := tests/fixtures/upm_consumer/uya.toml
CONSUMER_MAIN := tests/fixtures/upm_consumer/src/main.uya
TEST ?= src/numuya/_tests/test_testing_helpers.uya
TESTS := $(sort $(wildcard src/numuya/_tests/test_*.uya))

.PHONY: bootstrap-upm upm-install test-one test check-one verify-upm-consumer require-upm

require-upm:
	@test -x "$(UPM)" || { echo "missing executable $(UPM)"; exit 1; }

bootstrap-upm: require-upm
	$(UPM) install --manifest-path $(MANIFEST)

upm-install: require-upm
	$(UPM) install --manifest-path $(MANIFEST)

test-one: require-upm
	$(UYA) test "$(TEST)" --manifest-path $(MANIFEST)

test: require-upm
	@test -n "$(TESTS)" || { echo "no test files found"; exit 1; }
	@for test in $(TESTS); do \
		echo "$(UYA) test $$test --manifest-path $(MANIFEST)"; \
		$(UYA) test "$$test" --manifest-path $(MANIFEST) || exit $$?; \
	done

check-one: require-upm
	$(UYA) check "$(TEST)" --manifest-path $(MANIFEST)

verify-upm-consumer: require-upm
	$(UPM) install --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) check $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
	$(UYA) run $(CONSUMER_MAIN) --manifest-path $(CONSUMER_MANIFEST)
