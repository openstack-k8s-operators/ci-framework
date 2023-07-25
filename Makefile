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
# Ansible options for the local_env_vm target
LOCAL_ENV_OPTS ?= ""

# target vars for generic operator install info 1: target name , 2: operator name
define vars
${1}: export ROLE_DIR=${ROLE_DIR}
${1}: export BASEDIR=${BASEDIR}
${1}: export USE_VENV=${USE_VENV}
${1}: export BUILD_VENV_CTX=${BUILD_VENV_CTX}
${1}: export MOLECULE_CONFIG=${MOLECULE_CONFIG}
${1}: export TEST_ALL_ROLES=${TEST_ALL_ROLES}
endef

# Macro allowing to check if a variable is defined or not
check-var-defined = $(if $(strip $($1)),,$(error "$1" is not defined))

##@ General
.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: create_new_role
create_new_role:
	$(call check-var-defined,ROLE_NAME)
	ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ci_framework/roles ${ROLE_NAME}

.PHONY: role_molecule
role_molecule: ## Regenerate the molecule jobs configuration
	scripts/create_role_molecule.py

.PHONY: new_role
new_role: create_new_role role_molecule ## Create a new Ansible role and related molecule Zuul job - ROLE_NAME parameter is mandatory

##@ Setup steps
.PHONY: setup_tests
setup_tests: ## Setup the environment
	bash scripts/setup_env

.PHONY: setup_molecule
setup_molecule: setup_tests ## Setup molecule environment
	bash scripts/setup_molecule

##@ General testing
.PHONY: tests
tests: pre_commit molecule ## Run all tests with dependencies install

.PHONY: tests_nodeps
tests_nodeps: pre_commit_nodeps molecule_nodeps ## Run all tests without installing dependencies

.PHONY: tox
tox: ## Run tox based on the tox.ini file
	tox -v

##@ Molecule testing
.PHONY: molecule
molecule: setup_molecule molecule_nodeps ## Run molecule tests with dependencies install

.PHONY: molecule_nodeps
molecule_nodeps: ## Run molecule without installing dependencies
	bash scripts/run_molecule $(ROLE_DIR)

##@ Pre-commit testing
.PHONY: pre_commit
pre_commit: setup_tests pre_commit_nodeps ## Runs pre-commit tests with dependencies install

.PHONY: pre_commit_nodeps
pre_commit_nodeps: ## Run pre-commit tests without installing dependencies
	pushd $(BASEDIR); \
	git config --global safe.directory '*'; \
	if [ "x$(USE_VENV)" ==  'xyes' ]; then \
		${HOME}/test-python/bin/pre-commit run --all-files; \
	else \
		pre-commit run --all-files; \
	fi

##@ Ansible-test testing
.PHONY: ansible_test
ansible_test: setup_tests ansible_test_nodeps ## Runs ansible-test with dependencies install

.PHONY: ansible_test_nodeps
ansible_test_nodeps: ## Run ansible-test without installing dependencies
	bash scripts/run_ansible_test

##@ Container targets
.PHONY: ci_ctx
ci_ctx: ## Build CI container with podman
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman image exists localhost/cifmw-build:latest || \
		podman build -t localhost/cifmw-build:latest -f containerfiles/Containerfile.ci .; \
		buildah bud -t ${CI_CTX_NAME} -f containerfiles/Containerfile.tests .; \
	fi

.PHONY: run_ctx_all_tests
run_ctx_all_tests: export BUILD_VENV_CTX=no
run_ctx_all_tests: export MOLECULE_CONFIG=".config/molecule/config_local.yml"
run_ctx_all_tests: run_ctx_pre_commit run_ctx_molecule run_ctx_ansible_test run_ctx_tox ## Run all tests in container

.PHONY: run_ctx_pre_commit
run_ctx_pre_commit: ci_ctx ## Run pre-commit check in a container
	podman run --rm --security-opt label=disable \
		-v .:/opt/sources \
		-e BASEDIR=$(BASEDIR) \
		-e HOME=/tmp \
		--user root \
		${CI_CTX_NAME} bash -c "make pre_commit_nodeps  BASEDIR=$(BASEDIR)" ;

.PHONY: run_ctx_molecule
run_ctx_molecule: ci_ctx ## Run molecule check in a container
	podman run --rm \
		-e MOLECULE_CONFIG=${MOLECULE_CONFIG} \
		-e TEST_ALL_ROLES=$(TEST_ALL_ROLES) \
		--security-opt label=disable -v .:/opt/sources \
		--user root \
		${CI_CTX_NAME} \
		bash -c "make molecule_nodeps MOLECULE_CONFIG=${MOLECULE_CONFIG}" ;

.PHONY: run_ctx_ansible_test
run_ctx_ansible_test: ci_ctx ## Run molecule check in a container
	podman run --rm --security-opt label=disable -v .:/opt/sources \
		-e HOME=/tmp \
		-e ANSIBLE_LOCAL_TMP=/tmp \
		-e ANSIBLE_REMOTE_TMP=/tmp \
		${CI_CTX_NAME} bash -c "make ansible_test_nodeps" ;

.PHONY: enable-git-hooks
enable-git-hooks:
	git config core.hooksPath "./.githooks"
	$(warning REMEMBER, YOU MUST HAVE REVIEWED THE CUSTOM HOOKS in .githooks!)

##@ Developer environments
.PHONY: local_env_create
local_env_create: ## Create a virtualized lab on your local machine. Nested virt MUST be supported by your system. Use LOCAL_ENV_OPTS param to pass options to ansible-playbook
	if [ "x${LOCAL_ENV_OPTS}" == "x" ]; then \
		ansible-playbook -i localhost, -c local dev-local-env.yml; \
	else \
		ansible-playbook -i localhost, -c local dev-local-env.yml ${LOCAL_ENV_OPTS}; \
	fi

.PHONY: local_env_vm_cleanup
local_env_vm_cleanup: ## Cleanup virtualized lab on your local machine.
	bash scripts/local_env_vm_cleanup.sh

##@ Generate documentation
.PHONY: docs
docs: ## Create documentation under docs/build/html
	./docs/source/build-docs.sh
