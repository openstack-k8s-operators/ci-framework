# REVIEW.md

Review guidelines for Qodo's agentic review agents. These rules are
distilled from `best_practices.md` — see that file for full examples
and rationale.

## Out of scope

Do not raise findings for these specific paths:

- `custom/` — Gitignored local overrides, never committed.
- `docs/` — Sphinx documentation, not runtime code.
- `containerfiles/` — Podman image definitions.
- `.github/` — GitHub Actions workflows.
- Generated files: `zuul.d/molecule.yaml`, `zuul.d/projects.yaml` — these
  are overwritten by `make role_molecule`, never hand-edit.

Do not apply Ansible-specific rules (FQCN, variable naming, retries,
`changed_when`, etc.) to `zuul.d/` files — they are Zuul job definitions,
not Ansible playbooks. However, still review `zuul.d/` for logical issues
such as incorrect variable overrides, missing parent job settings, or
wrong job dependencies.

Review `scripts/` for logic and correctness. Do not flag shell style
issues already caught by shellcheck or Python formatting caught by black.

## Critical — flag as High severity

### Idempotency

Shell/command tasks that mutate state must have `creates:`, `removes:`,
or a `when:` condition checking current state. Do not flag read-only
commands that already declare `changed_when: false` — those are not
mutating and do not need idempotency guards.

### Error handling

Flag any use of `ignore_errors: true`. The correct pattern is
`block`/`rescue`/`always` with context dumped in the rescue block
before failing. A `# noqa: ignore-errors` comment does not make it
acceptable — it only suppresses the linter; the code still needs
proper error handling.

### K8s and external API calls must have retry logic

Any task using `kubernetes.core.k8s`, `kubernetes.core.k8s_info`, or
calling `oc`/`kubectl` via `command`/`shell` must have `retries`,
`delay`, and `until`. The same applies to HTTP calls, container registry
pulls, and DLRN API calls. A single-shot external call will randomly
fail in CI.

### Secrets and credentials

Tasks handling secrets or credentials must have `no_log: true` (or
`no_log: "{{ cifmw_nolog | default(true) | bool }}"`). Files containing
secrets must use mode `"0600"`. Flag any `ansible.builtin.debug` that
prints a variable which may contain credentials.

### No hardcoded paths or hostnames

Flag absolute paths like `/home/zuul/...` or hardcoded hostnames like
`titan042.lab.eng.tlv2.redhat.com`. Use variables and `path_join`.

### Backward compatibility

Flag any diff that deletes a `cifmw_*` variable from `defaults/main.yml`.
This breaks downstream consumers in `ci-framework-jobs`.

### Import vs include

Flag `import_tasks` or `import_role` used inside a `loop`. Only
`include_tasks`/`include_role` works correctly in loops.

### Race conditions in wait loops

Flag `until:` conditions that index into a resource list
(e.g., `resources[0].status.phase`) without first checking
`resources | length > 0`.

### Jinja2 safety

Flag `when:` conditions on flag variables that lack `| bool` (should be
`variable | default(false) | bool`). Flag access to nested dictionary
keys without `| default()`.

### Variable naming

Public variables in `defaults/main.yml` must use the `cifmw_<role>_`
prefix. Internal variables from `register:` or `set_fact` in task files
must use a leading underscore (`_var` or `_role_var`). Flag registered
variables using the `cifmw_` prefix — that pollutes the public namespace.

### Debug tasks in production code

Flag any `ansible.builtin.debug` task without a `verbosity:` level or a
`when: ... _debug | default(false) | bool` guard. Unguarded debug tasks
clutter CI logs and may expose secrets. Debug dumps in `rescue` blocks
are fine.

## Suggestion — flag as Medium severity

### Input validation

Roles should validate required inputs early with `ansible.builtin.assert`
using `quiet: true`.

### Privilege escalation

`become: true` should be on individual tasks, not at play level.

### Cross-role variable coupling

Flag `set_fact` that writes into another role's `cifmw_<other_role>_`
namespace without a comment explaining the interface contract.

### Cleanup in always blocks

Tasks creating temporary resources (namespaces, temp files, test data)
should be wrapped in `block`/`always` to ensure cleanup on failure.

### Task granularity

Flag shell/command tasks with multiple unrelated operations in a single
script block. Each operation should be a separate task for debuggability.

### changed_when and failed_when

Flag `command`/`shell` tasks missing `changed_when`. Read-only commands
need `changed_when: false`. Mutating commands need a meaningful condition.

### Loop control

Flag `include_tasks` inside a loop without `loop_control` setting
`loop_var`. Flag loops over large data structures (K8s resources, dicts)
without `label` to reduce log noise.

### File modes must be quoted strings

Flag unquoted file mode values (e.g., `mode: 0644`). Must be quoted:
`mode: "0644"`.

### Log artifacts

Output files should be written under `{{ cifmw_basedir }}/artifacts/`
for Zuul log collection.

### set_fact vs vars

Flag `set_fact` for values only used in the immediately following task.
Prefer `vars:` on the task or block to limit scope.

### Documentation

New variables in `defaults/main.yml` should have a corresponding entry
in the role's `README.md`. New roles must have a complete README.

### Patch size

Flag PRs exceeding ~300 lines of meaningful diff that mix unrelated
concerns. Each MR should be reviewable and mergeable on its own.
