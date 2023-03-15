SHELL := /bin/bash
# Roles directory location. May point outside of this repository
ROLE_DIR ?= ci_framework/roles/
# Code base directory - used for pre-commit check
BASEDIR ?= ./
# Create python virtualenv and use it?
USE_VENV ?= ${USE_VENV:-yes}
# Build container?
BUILD_VENV_CTX ?= yes
# CI container name
CI_CTX_NAME ?= localhost/cifmw:latest
# Molecule test configuration file
MOLECULE_CONFIG ?= ${MOLECULE_CONFIG:-.config/molecule/config_podman.yml}
# Run molecule against all tests
TEST_ALL_ROLES ?= ${TEST_ALL_ROLES:-no}

# target vars for generic operator install info 1: target name , 2: operator name
define vars
${1}: export ROLE_DIR=${ROLE_DIR}
${1}: export BASEDIR=${BASEDIR}
${1}: export USE_VENV=${USE_VENV}
${1}: export BUILD_VENV_CTX=${BUILD_VENV_CTX}
${1}: export MOLECULE_CONFIG=${MOLECULE_CONFIG}
${1}: export TEST_ALL_ROLES=${TEST_ALL_ROLES}
endef

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
	bash scripts/run_molecule $(ROLE_DIR)

.PHONY: pre_commit
pre_commit: setup_tests pre_commit_nodeps ## Runs pre-commit tests with dependencies install

.PHONY: pre_commit_nodeps
pre_commit_nodeps: ## Run pre-commit tests without installing dependencies
	pushd $(BASEDIR)
	git config --global safe.directory '*'
	if [ "x$(USE_VENV)" ==  'xyes' ]; then \
		${HOME}/test-python/bin/pre-commit run --all-files ; \
	else \
		pre-commit run --all-files ; \
	fi

.PHONY: ansible_test
ansible_test: setup_tests ansible_tests_nodeps ## Runs ansible-test with dependencies install

.PHONY: ansible_test_nodeps
ansible_test_nodeps: ## Run ansible-test without installing dependencies
	bash scripts/run_ansible_test

.PHONY: tests
tests: pre_commit molecule ## Run all tests with dependencies install

.PHONY: tests_nodeps
tests_nodeps: pre_commit_nodeps molecule_nodeps ## Run all tests without installing dependencies

.PHONY: ci_ctx
ci_ctx: ## Build CI container with podman
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman image exists localhost/cifmw-build:latest || \
		podman build -t localhost/cifmw-build:latest -f containerfiles/Containerfile.ci .; \
		buildah bud -t ${CI_CTX_NAME} -f containerfiles/Containerfile.tests .; \
	fi

.PHONY: run_ctx_pre_commit
run_ctx_pre_commit: ci_ctx ## Run pre-commit check in a container
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman run --rm \
			-e BASEDIR=$(BASEDIR) \
			-e HOME=/tmp \
			${CI_CTX_NAME} bash -c "make pre_commit_nodeps BASEDIR=$(BASEDIR)" ; \
	else \
		podman run --rm --security-opt label=disable \
			-v .:/opt/sources \
			-e BASEDIR=$(BASEDIR) \
			-e HOME=/tmp \
			${CI_CTX_NAME} bash -c "make pre_commit_nodeps  BASEDIR=$(BASEDIR)" ; \
	fi

.PHONY: run_ctx_molecule
run_ctx_molecule: ci_ctx ## Run molecule check in a container
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman run --rm \
			-e MOLECULE_CONFIG=$(MOLECULE_CONFIG) \
			-e TEST_ALL_ROLES=$(TEST_ALL_ROLES) \
			--user root \
			${CI_CTX_NAME} \
			bash -c "make molecule_nodeps MOLECULE_CONFIG=$(MOLECULE_CONFIG)" ; \
	else \
		podman run --rm \
			-e MOLECULE_CONFIG=$(MOLECULE_CONFIG) \
			-e TEST_ALL_ROLES=$(TEST_ALL_ROLES) \
			--security-opt label=disable -v .:/opt/sources \
			--user root \
			${CI_CTX_NAME} \
			bash -c "make molecule_nodeps MOLECULE_CONFIG=$(MOLECULE_CONFIG)" ; \
	fi

.PHONY: run_ctx_ansible_test
run_ctx_ansible_test: ci_ctx ## Run molecule check in a container
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman run --rm \
			-e HOME=/tmp \
			-e ANSIBLE_LOCAL_TMP=/tmp \
			-e ANSIBLE_REMOTE_TMP=/tmp \
			${CI_CTX_NAME} \
			bash -c "make ansible_test_nodeps" ; \
	else \
		podman run --rm --security-opt label=disable -v .:/opt/sources \
			-e HOME=/tmp \
			-e ANSIBLE_LOCAL_TMP=/tmp \
			-e ANSIBLE_REMOTE_TMP=/tmp \
			${CI_CTX_NAME} bash -c "make ansible_test_nodeps" ; \
	fi
