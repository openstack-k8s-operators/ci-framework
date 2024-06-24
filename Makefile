SHELL := /bin/bash -o pipefail -e
# Roles directory location. May point outside of this repository
ROLE_DIR ?= roles/
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
# Log output location
LOG_DIR ?= /tmp
# Specific parameter for architecture_test
ANSIBLE_OPTS ?=

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
create_new_role: ## Please call `new_role ROLE_NAME=your_role` instead.
	$(if $(strip $(INTER_CALL)),,$(error Please call make new_role ROLE_NAME=${ROLE_NAME}))
	$(call check-var-defined,ROLE_NAME)
	ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ./roles ${ROLE_NAME}

.PHONY: role_molecule
role_molecule: ## Regenerate the molecule jobs configuration
	scripts/create_role_molecule.py

.PHONY: new_role
new_role: export INTER_CALL=yes
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
		${HOME}/test-python/bin/pre-commit run --all-files 2>&1 | ansi2txt | tee $(LOG_DIR)/pre_commit.log; \
	else \
		pre-commit run --all-files 2>&1 | ansi2txt | tee $(LOG_DIR)/pre_commit.log; \
	fi

.PHONY: check_zuul_files
check_zuul_files: role_molecule ## Regenerate zuul files and check if they have not been modified manually
	./scripts/check_zuul_files.sh 2>&1 | ansi2txt | tee $(LOG_DIR)/check_zuul_files.log

.PHONY: check_k8s_snippets_comment
check_k8s_snippets_comment: ## Check template snippets in ci_gen_kustomize_values to ensure proper source is set
	./scripts/check_k8s_snippets_comment.sh 2>&1 | ansi2txt | tee $(LOG_DIR)/check_k8s_snippets_comment.log

##@ Architecture tests
.PHONY: architecture_test
architecture_test: setup_tests architecture_test_nodeps ## Run architecture-test with dependency install. Refer to run_ctx_architecture_test for more parameters/information.

.PHONY: architecture_test_nodeps
architecture_test_nodeps: export PATH=/tmp/bin:/usr/bin:/usr/sbin:/bin:/sbin:/usr/local/bin:/usr/local/sbin
architecture_test_nodeps: ## Run architecture-test without any dependency install. run_ctx_architecture_test for more parameters/information
	$(call check-var-defined,SCENARIO_NAME)
	$(call check-var-defined,ARCH_REPO)
	$(call check-var-defined,NET_ENV_FILE)
	cp -r ${ARCH_REPO} /tmp/local-arch-repo;
	ansible-playbook -i localhost, -c local \
		ci/playbooks/architecture/validate-architecture.yml \
		-e cifmw_zuul_target_host=localhost \
		-e ansible_user_dir=/tmp \
		-e cifmw_architecture_repo=/tmp/local-arch-repo \
		-e cifmw_architecture_scenario=${SCENARIO_NAME} \
		-e cifmw_networking_mapper_networking_env_def_path=${NET_ENV_FILE} \
		${ANSIBLE_OPTS}

##@ Ansible-test testing
.PHONY: ansible_test
ansible_test: setup_tests ansible_test_nodeps ## Runs ansible-test with dependencies install

.PHONY: ansible_test_nodeps
ansible_test_nodeps: export HOME=/tmp
ansible_test_nodeps: export ANSIBLE_LOCAL_TMP=/tmp
ansible_test_nodeps: export ANSIBLE_REMOTE_TMP=/tmp
ansible_test_nodeps: ## Run ansible-test without installing dependencies
	bash scripts/run_ansible_test 2>&1 | ansi2txt | tee $(LOG_DIR)/ansible_test.log

##@ Container targets
.PHONY: ci_ctx
ci_ctx: ## Build CI container with podman
	if [ "x$(BUILD_VENV_CTX)" == 'xyes' ]; then \
		podman image exists localhost/cifmw-build:latest || \
		podman build --security-opt label=disable -t localhost/cifmw-build:latest -f containerfiles/Containerfile.ci .; \
		podman build --security-opt label=disable -t ${CI_CTX_NAME} -f containerfiles/Containerfile.tests .; \
	fi

.PHONY: run_ctx_all_tests
run_ctx_all_tests: export BUILD_VENV_CTX=no
run_ctx_all_tests: export MOLECULE_CONFIG=".config/molecule/config_local.yml"
run_ctx_all_tests: run_ctx_pre_commit run_ctx_molecule run_ctx_ansible_test run_ctx_tox ## Run all tests in container

.PHONY: run_ctx_pre_commit
run_ctx_pre_commit: ci_ctx ## Run pre-commit check in a container
	@if [ -f .git ]; then \
		echo "" ; \
		echo 'If you are using git worktrees you must use \
		"make pre_commit" or "make pre_commit_nodeps" as \
		the git mapping fails inside the container.' ; \
		false ; \
	fi
	podman run \
		--rm \
		--security-opt label=disable \
		-v ${PWD}:/opt/sources \
		--user root \
		-e BASEDIR=$(BASEDIR) \
		-e HOME=/tmp \
		${CI_CTX_NAME} \
		bash -c \
		"make pre_commit_nodeps  BASEDIR=$(BASEDIR)" ;

.PHONY: run_ctx_molecule
run_ctx_molecule: ci_ctx ## Run molecule check in a container
	podman run \
		--rm \
		--security-opt label=disable \
		-v ${PWD}:/opt/sources \
		--user root \
		-e MOLECULE_CONFIG=${MOLECULE_CONFIG} \
		-e TEST_ALL_ROLES=$(TEST_ALL_ROLES) \
		${CI_CTX_NAME} \
		bash -c \
		"make molecule_nodeps MOLECULE_CONFIG=${MOLECULE_CONFIG}";

.PHONY: run_ctx_ansible_test
run_ctx_ansible_test: ci_ctx ## Run molecule check in a container
	podman run \
		--rm \
		--security-opt label=disable \
		-v ${PWD}:/opt/sources \
		-e HOME=/tmp \
		-e ANSIBLE_LOCAL_TMP=/tmp \
		-e ANSIBLE_REMOTE_TMP=/tmp \
		${CI_CTX_NAME} \
		bash -c \
		"make ansible_test_nodeps";

.PHONY: run_ctx_architecture_test
run_ctx_architecture_test: export _DIR="${HOME}/ci-framework-data/validate-${SCENARIO_NAME}"
run_ctx_architecture_test: ## Run architecture_test in a container. You can pass any ansible-playbook options using ANSIBLE_OPTS. Mandatory options are SCENARIO_NAME (such as hci), ARCH_REPO (architecture repository path) and NET_ENV_VILE (usually ./ci/playbooks/files/networking-env-definition.yml). Since this is running in container, be sure to prefix the paths with either "./" or "../" for relative paths.
	$(call check-var-defined,SCENARIO_NAME)
	$(call check-var-defined,ARCH_REPO)
	$(call check-var-defined,NET_ENV_FILE)
	@$(MAKE) ci_ctx
	@mkdir -p ${_DIR};
	podman unshare chown 1000:1000 ${_DIR};
	podman run \
		--rm \
		--security-opt label=disable \
		-v ${PWD}:/opt/sources \
		-v ${ARCH_REPO}:/architecture:ro \
		-v ${NET_ENV_FILE}:/net-env-file.yml:ro \
		-v ${_DIR}:/tmp/ci-framework-data:rw \
		-e HOME=/tmp \
		-e ANSIBLE_LOCAL_TMP=/tmp \
		-e ANSIBLE_REMOTE_TMP=/tmp \
		-e SCENARIO_NAME=${SCENARIO_NAME} \
		-e ARCH_REPO=/architecture \
		-e NET_ENV_FILE=/net-env-file.yml \
		${CI_CTX_NAME} \
		bash -c \
		"make architecture_test_nodeps ANSIBLE_OPTS=\"${ANSIBLE_OPTS}\""; \

.PHONY: enable-git-hooks
enable-git-hooks:
	git config core.hooksPath "./.githooks"
	$(warning REMEMBER, YOU MUST HAVE REVIEWED THE CUSTOM HOOKS in .githooks!)

##@ Generate documentation
.PHONY: docs
docs: ## Create documentation under docs/build/html
	./docs/source/build-docs.sh

.PHONY: spelling
spelling: docs ## Run spell check as in CI
	if [ -f docs/dictionary/tmp ]; then \
		cat docs/dictionary/en-custom.txt docs/dictionary/tmp | tr '[:upper:]' '[:lower:]' | sort -u > docs/dictionary/tmp-sorted; \
		mv docs/dictionary/tmp-sorted docs/dictionary/en-custom.txt; \
	fi

	pyspelling -c .spellcheck.yml -v -n documentation -S "docs/_build/html/**/*.html"
