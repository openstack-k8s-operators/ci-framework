ROLE_LIST := ./ci_framework/roles/*

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: setup_tests
setup_tests: ## Setup the environment
	bash scripts/setup_env

.PHONY: setup_molecule
setup_molecule: setup_tests ## Setup molecule environment
	bash scripts/setup_molecule

.PHONY: molecule
molecule: setup_molecule ## Run molecule tests
	for role in ${ROLE_LIST}; do \
		bash scripts/run-local-test "$$(basename $${role})" ; \
	done

.PHONY: pre_commit
pre_commit: setup_tests ## Runs pre-commit tests
	${HOME}/test-python/bin/pip3 install pre-commit
	${HOME}/test-python/bin/pre-commit run


.PHONY: tests
tests: setup_tests pre_commit ## Run all tests
