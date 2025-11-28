# cifmw_setup_bootstrap

Bootstrap tasks for ci-framework host environment preparation.

## Purpose

This role provides atomic, idempotent bootstrap tasks that prepare the host environment for ci-framework operations. Each task can be executed independently or as part of a complete bootstrap workflow.

## Usage

This role uses the `tasks_from` pattern. Each task is atomic and checks actual system state for idempotency.

### Execute Individual Task

```yaml
- name: Install custom CA
  ansible.builtin.include_role:
    name: cifmw_setup_bootstrap
    tasks_from: install_ca.yml
```

### Execute Multiple Tasks

```yaml
- name: Complete bootstrap setup
  ansible.builtin.include_role:
    name: cifmw_setup_bootstrap
    tasks_from: "{{ item }}"
  loop:
    - install_yamls_make.yml
    - discover_latest_images.yml
    - artifacts_bootstrap.yml
```

### Execute the whole bootstrap

```yaml
- name: Complete bootstrap setup
  ansible.builtin.include_role:
    name: cifmw_setup_bootstrap
```

## Available Tasks

| Task ID | File | Description | Role Used |
|---------|------|-------------|-----------|
| BS-01 | `install_ca.yml` | Install custom Certificate Authorities | [install_ca](../install_ca/) |
| BS-02 | `repo_setup.yml` | Configure yum/dnf repositories | [repo_setup](../repo_setup/) |
| BS-03 | `ci_setup.yml` | Install required packages and tools | [ci_setup](../ci_setup/) |
| BS-04 | `install_yamls_make.yml` | Prepare install_yamls make targets | [install_yamls](../install_yamls/) |
| BS-05 | `discover_latest_images.yml` | Discover latest VM images | [discover_latest_image](../discover_latest_image/) |
| BS-06 | `artifacts_bootstrap.yml` | Collect and save custom parameters | (inline) |

## Prerequisites System

Tasks can run independently if their prerequisites are satisfied manually or through other means.

### Common Prerequisites

All tasks automatically include `common_prerequisites.yml` which sets:
- `cifmw_basedir` (default: `~/ci-framework-data`)
- `cifmw_path` (includes CRC, oc, user bins)
- `ci_framework_params` (filtered hostvars)
- Base directory structure

### Task Prerequisites

| Task | Requires |
|------|----------|
| BS-01 | None |
| BS-02 | None (optional: CA for https repos) |
| BS-03 | Repository configuration (BS-02 or manual) |
| BS-04 | CI packages (BS-03 or manual) |
| BS-05 | Network access to image repository |
| BS-06 | `ci_framework_params` fact (automatic) |

### Prerequisite Checks

Prerequisite checks are in `tasks/checks/` directory. Each check file sets internal facts prefixed with `_cifmw_setup_bootstrap_`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_basedir` | `~/ci-framework-data` | Base directory for artifacts |

Task-specific variables are passed through to the underlying roles. See individual role documentation linked in the "Available Tasks" table above.

## Dependencies

None at the role level. Individual tasks may depend on other bootstrap tasks or manual prerequisite satisfaction.
