ROLE_LIST := ./ci_framework/roles/*
USE_VENV ?= ${USE_VENV:-yes}

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
molecule: setup_molecule molecule_nodeps ## Run molecule tests with dependencies install

.PHONY: molecule_nodeps
molecule_nodeps: ## Run molecule without installing dependencies
	for role in ${ROLE_LIST}; do \
		bash scripts/run-local-test "$$(basename $${role})" ; \
	done

.PHONY: pre_commit
pre_commit: setup_tests pre_commit_nodeps ## Runs pre-commit tests with dependencies install

.PHONY: pre_commit_nodeps
pre_commit_nodeps: ## Run pre-commit tests without installing dependencies
	if [ "x$(USE_VENV)" ==  'xyes' ]; then \
		${HOME}/test-python/bin/pre-commit run ; \
	else \
		pre-commit run ; \
	fi

.PHONY: tests
tests: pre_commit molecule ## Run all tests with dependencies install

.PHONY: tests_nodeps
tests_nodeps: pre_commit_nodeps molecule_nodeps ## Run all tests without installing dependencies

.PHONY: ci_ctx
ci_ctx: ## Build CI container with buildah
	buildah bud -t cfwm:latest -f containerfiles/Containerfile.ci
