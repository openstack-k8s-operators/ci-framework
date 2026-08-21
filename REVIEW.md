# CI-Framework Best Practices

Guidelines for developing Ansible roles, playbooks, and plugins in the
ci-framework collection. Qodo uses this file to review your changes
before you submit a merge request.

> **Already enforced by CI linters (not covered here):**
> FQCN, variable naming regex, YAML formatting, trailing whitespace,
> Python formatting (black), shell scripts (shellcheck).
> Run `make pre_commit` to catch those locally.

---

## [Critical] Idempotency

Every task must produce the same result whether run once or ten times.

```yaml
# Bad - will fail on second run
- name: Create user
  ansible.builtin.command: "useradd appuser"

# Good - declarative, idempotent
- name: Create user
  ansible.builtin.user:
    name: appuser
    state: present

# Good - guarded command
- name: Initialize database
  ansible.builtin.command: "db-init --setup"
  args:
    creates: /var/lib/db/.initialized
```

Shell/command tasks that mutate state must have `creates:`, `removes:`,
or a `when:` condition checking current state.

---

## [Critical] Error Handling

Use `block`/`rescue`/`always` — never `ignore_errors: true`.
Always dump context in the rescue block before failing.

```yaml
# Bad
- name: Deploy thing
  kubernetes.core.k8s:
    state: present
    definition: "{{ _manifest }}"
  ignore_errors: true

# Good
- name: Deploy and verify
  block:
    - name: Apply manifest
      kubernetes.core.k8s:
        state: present
        definition: "{{ _manifest }}"

    - name: Wait for ready state
      kubernetes.core.k8s_info:
        kind: Deployment
        name: my-app
      register: _deploy
      retries: 30
      delay: 10
      until:
        - _deploy.resources | length > 0
        - _deploy.resources[0].status.readyReplicas | default(0) > 0
  rescue:
    - name: Show what failed
      ansible.builtin.debug:
        var: _deploy

    - name: Fail with context
      ansible.builtin.fail:
        msg: "Deployment failed — see debug output above"
```

---

## [Critical] External Service Calls Must Be Retried

Any call to k8s API, container registries, HTTP endpoints, or DLRN
needs `retries`/`delay`/`until`. CI networks are flaky.

```yaml
# Bad - single shot, will randomly fail in CI
- name: Pull image
  ansible.builtin.command: "podman pull {{ _image }}"

# Good
- name: Pull image
  ansible.builtin.command: "podman pull {{ _image }}"
  register: _pull
  retries: 5
  delay: 15
  until: _pull.rc == 0
```

Make retry counts realistic. 5–10 retries with 10–30s delay covers
most transient failures; anything longer needs a comment justifying why.
`retries: 100` with `delay: 60` is a 100-minute silent hang — that
masks real failures and stalls the entire pipeline.

---

## [Critical] Secrets and Credentials

Tasks handling secrets must use `no_log`. Secret files must be `"0600"`.

```yaml
# Bad - token visible in CI logs
- name: Write auth token
  ansible.builtin.copy:
    content: "{{ cifmw_manage_secrets_citoken_content }}"
    dest: "{{ _token_path }}"
    mode: "0644"

# Good
- name: Write auth token
  ansible.builtin.copy:
    content: "{{ cifmw_manage_secrets_citoken_content }}"
    dest: "{{ _token_path }}"
    mode: "0600"
  no_log: "{{ cifmw_nolog | default(true) | bool }}"
```

Never use `ansible.builtin.debug` to print registered variables that
may contain secrets.

---

## [Critical] No Hardcoded Paths or Hosts

Use variables and filters — never absolute paths or hostnames.

```yaml
# Bad
dest: /home/zuul/ci-framework-data/secrets/pull_secret.json
url: https://titan042.lab.eng.tlv2.redhat.com

# Good
dest: "{{ (cifmw_basedir, 'secrets', 'pull_secret.json') | path_join }}"
url: "{{ cifmw_registry_url }}"
```

If a value might vary between environments, put it in `defaults/main.yml`.

---

## [Critical] Backward Compatibility

Renaming or removing a variable from `defaults/main.yml` breaks
downstream jobs in `ci-framework-jobs`. Before changing a public variable:

1. Add the new variable alongside the old one
2. Default the new variable to the old one: `cifmw_role_new_param: "{{ cifmw_role_old_param | default('value') }}"`
3. Coordinate removal of the old variable with a `ci-framework-jobs` MR

A diff that deletes a `cifmw_*` variable from defaults is a red flag.

---

## [Critical] Import vs Include

Get this wrong and you get silent bugs.

| Use `import_tasks` / `import_role` when | Use `include_tasks` / `include_role` when |
|---|---|
| No loop on the inclusion | Looping over the inclusion |
| No conditional on the include itself | Conditional on whether to include at all |
| You need tags to propagate | Filename determined at runtime |

```yaml
# WRONG - import inside a loop silently runs only once
- name: Process scenarios
  ansible.builtin.import_tasks: process.yml
  loop: "{{ scenarios }}"

# RIGHT
- name: Process scenarios
  ansible.builtin.include_tasks: process.yml
  loop: "{{ scenarios }}"
  loop_control:
    loop_var: _scenario
```

---

## [Critical] Race Conditions in Wait Loops

Always guard against empty resource lists in `until:` conditions.

```yaml
# Bad - IndexError when no pods exist yet
until: _pods.resources[0].status.phase == 'Running'

# Good - handles empty list
until:
  - _pods.resources | length > 0
  - _pods.resources | map(attribute='status.phase') | select('eq', 'Running') | list | length == _pods.resources | length
```

---

## [Suggestion] Input Validation

Validate required inputs early. Use `quiet: true` to reduce log noise.

```yaml
- name: Validate required parameters
  ansible.builtin.assert:
    that:
      - cifmw_my_role_target_host is defined
      - cifmw_my_role_target_host | length > 0
      - cifmw_my_role_manifest_path is defined
      - cifmw_my_role_manifest_path[0] == '/'
    quiet: true
    msg: >-
      cifmw_my_role_target_host must be defined and non-empty,
      cifmw_my_role_manifest_path must be an absolute path.
```

Check: paths are absolute when expected, required variables are defined
and non-empty, mutually exclusive options aren't both set.

---

## [Critical] Jinja2 Safety

Handle missing keys and empty lists.

```yaml
# Bad - KeyError if nested doesn't exist
value: "{{ my_dict.nested.key }}"

# Good
value: "{{ my_dict.nested.key | default('fallback') }}"

# Bad - boolean check on a string variable
when: cifmw_some_flag

# Good - explicit bool coercion
when: cifmw_some_flag | default(false) | bool
```

---

## [Suggestion] Privilege Escalation

Only escalate where needed, never at play level.

```yaml
# Bad - everything runs as root unnecessarily
- hosts: all
  become: true
  tasks:
    - name: Read a config file
      ansible.builtin.slurp:
        src: /etc/app/config.yml

# Good - escalate only the task that needs it
- hosts: all
  tasks:
    - name: Install required packages
      become: true
      ansible.builtin.dnf:
        name: "{{ _packages }}"
        state: present
```

Document privilege escalation in the role README under a
"Privilege escalation" section.

---

## [Suggestion] Cross-Role Variable Coupling

Don't reach into another role's namespace without documenting it.

```yaml
# Bad - role "foo" silently overriding role "bar" internals
- name: Override bar's setting
  ansible.builtin.set_fact:
    cifmw_bar_internal_flag: true

# Good - pass through a documented interface
# In defaults/main.yml of role foo:
# cifmw_foo_bar_override: null
# In tasks, only set bar's variable if explicitly configured:
- name: Configure bar if override requested
  ansible.builtin.set_fact:
    cifmw_bar_internal_flag: "{{ cifmw_foo_bar_override }}"
  when: cifmw_foo_bar_override is not none
```

---

## [Suggestion] Cleanup in Always Blocks

Tasks creating temporary resources need cleanup paths.

```yaml
- name: Run integration test
  block:
    - name: Create test namespace
      kubernetes.core.k8s:
        state: present
        definition:
          kind: Namespace
          metadata:
            name: "{{ _test_ns }}"

    - name: Run tests
      ansible.builtin.include_tasks: run_tests.yml

  always:
    - name: Remove test namespace
      kubernetes.core.k8s:
        state: absent
        definition:
          kind: Namespace
          metadata:
            name: "{{ _test_ns }}"
```

---

## [Suggestion] Task Granularity

Keep tasks focused. A single task that does too many things is hard
to debug on failure.

```yaml
# Bad - one mega-task, unclear what failed
- name: Setup everything
  ansible.builtin.shell: |
    mkdir -p /opt/app
    cp config.yml /opt/app/
    chown -R app:app /opt/app
    systemctl restart app

# Good - each step visible in logs on failure
- name: Create application directory
  ansible.builtin.file:
    path: /opt/app
    state: directory
    owner: app
    group: app

- name: Deploy configuration
  ansible.builtin.copy:
    src: config.yml
    dest: /opt/app/config.yml
    owner: app
    group: app

- name: Restart application
  become: true
  ansible.builtin.systemd:
    name: app
    state: restarted
```

---

## [Suggestion] Documentation for New Code

Before submitting your MR, verify:

- [ ] New variables in `defaults/main.yml` are documented in the role README
- [ ] New roles have a complete README (purpose, privilege escalation, parameters, examples)
- [ ] New task files are covered by a Molecule scenario (or README explains why not)
- [ ] If you changed a base role used by many jobs, the MR description states the impact scope

---

## [Suggestion] Molecule Tests

New behavior needs test coverage. Tests should assert outcomes,
not just "run without error."

```yaml
# Weak - only proves it didn't crash
- name: Converge
  hosts: all
  roles:
    - role: my_role

# Better - verifies the role actually did what it claims
- name: Verify
  hosts: all
  tasks:
    - name: Check output file exists
      ansible.builtin.stat:
        path: "{{ cifmw_my_role_output_path }}"
      register: _output

    - name: Assert file was created with correct permissions
      ansible.builtin.assert:
        that:
          - _output.stat.exists
          - _output.stat.mode == '0600'
```

Use `cifmw_*_dryrun: true` variables to make roles testable in
Molecule without external dependencies.

---

## [Suggestion] Generated Files

Never hand-edit these files — they're overwritten by `make role_molecule`:
- `zuul.d/molecule.yaml`
- `zuul.d/projects.yaml`

---

## [Suggestion] Register Variable Naming

Use a leading underscore for task-local registered variables. This
signals they are private to the current file and not part of the role's
public interface.

```yaml
# Bad - looks like a public role variable
- name: Get pod list
  kubernetes.core.k8s_info:
    kind: Pod
  register: pod_list

# Good - clearly scoped to this file
- name: Get pod list
  kubernetes.core.k8s_info:
    kind: Pod
  register: _pod_list
```

Reserve unprefixed names for `set_fact` values that intentionally
persist across roles or plays.

---

## [Suggestion] set_fact vs vars

Prefer `vars:` on a task or block when the value is only needed locally.
`set_fact` persists for the entire play and pollutes the fact cache.

```yaml
# Bad - fact lingers unnecessarily
- name: Build manifest path
  ansible.builtin.set_fact:
    _manifest_path: "{{ (cifmw_basedir, 'manifests', _name) | path_join }}"

- name: Apply manifest
  kubernetes.core.k8s:
    src: "{{ _manifest_path }}"

# Good - scoped to the task
- name: Apply manifest
  vars:
    _manifest_path: "{{ (cifmw_basedir, 'manifests', _name) | path_join }}"
  kubernetes.core.k8s:
    src: "{{ _manifest_path }}"
```

Use `set_fact` only when:
- The value is needed across multiple subsequent tasks without a block
- The value must survive across includes
- You're building up state in a loop

---

## [Suggestion] changed_when and failed_when

Command/shell tasks that are idempotent by design should declare
`changed_when: false` to avoid misleading "changed" reports.

```yaml
# Bad - always reports "changed" even when nothing happened
- name: Check cluster status
  ansible.builtin.command: "oc get clusterversion"
  register: _cv

# Good - read-only command, never changes state
- name: Check cluster status
  ansible.builtin.command: "oc get clusterversion"
  register: _cv
  changed_when: false

# Good - changed only when output confirms a mutation
- name: Apply sysctl settings
  ansible.builtin.command: "sysctl -w net.ipv4.ip_forward=1"
  register: _sysctl
  changed_when: "'net.ipv4.ip_forward = 1' not in _sysctl.stdout"
```

Use `failed_when` to override default failure detection when a non-zero
exit code is acceptable:

```yaml
- name: Check if service exists
  ansible.builtin.command: "systemctl is-active my-service"
  register: _svc
  changed_when: false
  failed_when: _svc.rc not in [0, 3]
```

---

## [Suggestion] Loop Control

Always set `loop_var` on includes to prevent variable shadowing in
nested loops. Use `label` to reduce log noise on large data structures.

```yaml
# Bad - default loop_var 'item' can be shadowed by inner loops
- name: Configure networks
  ansible.builtin.include_tasks: configure_network.yml
  loop: "{{ cifmw_my_role_networks }}"

# Good
- name: Configure networks
  ansible.builtin.include_tasks: configure_network.yml
  loop: "{{ cifmw_my_role_networks }}"
  loop_control:
    loop_var: _network
    label: "{{ _network.name }}"
```

Inside `configure_network.yml`, use `_network` — not `item`.

---

## [Suggestion] File Mode Must Be a Quoted String

Ansible interprets unquoted numeric modes as decimal integers, not
octal. Always quote file mode values.

```yaml
# Bad - 0644 without quotes is decimal 420, Ansible may misinterpret
- name: Write config
  ansible.builtin.copy:
    src: app.conf
    dest: /etc/app/app.conf
    mode: 0644

# Good
- name: Write config
  ansible.builtin.copy:
    src: app.conf
    dest: /etc/app/app.conf
    mode: "0644"
```

---

## [Suggestion] Log Artifacts

Tasks that produce output files (logs, reports, collected state) should
write them under `{{ cifmw_basedir }}/artifacts/` so Zuul's log
collection picks them up and they're available for post-job debugging.

```yaml
- name: Collect service logs
  ansible.builtin.shell:
    cmd: "oc logs deployment/my-app --all-containers"
  register: _app_logs
  changed_when: false
  failed_when: false

- name: Save logs to artifacts
  ansible.builtin.copy:
    content: "{{ _app_logs.stdout }}"
    dest: "{{ cifmw_basedir }}/artifacts/my-app-logs.txt"
    mode: "0644"
```

For large collections (e.g., must-gather), write a directory:

```yaml
- name: Run must-gather
  ansible.builtin.command:
    cmd: "oc adm must-gather --dest-dir={{ cifmw_basedir }}/artifacts/must-gather"
  changed_when: true
```

---

## [Suggestion] Verbose Comments

Do not add comments that narrate what the code does. Comments should explain
non-obvious *why*, not obvious *what*.

```yaml
# Bad - restates the task name
- name: Create the directory  # create the application directory
  ansible.builtin.file:
    path: /opt/app
    state: directory

# Bad - restates the module purpose
- name: Install packages
  ansible.builtin.dnf:
    name: httpd  # install httpd package
    state: present

# Good - explains a non-obvious constraint
- name: Set memory limit
  # OOM-killed below 512Mi under load with 50+ concurrent connections
  ansible.builtin.set_fact:
    _mem_limit: "1Gi"
```

---

## [Suggestion] Excessive Variables

Do not create a variable for a static value used only once. Inline it.

```yaml
# Bad - one-shot variable adds indirection
- name: Set namespace
  ansible.builtin.set_fact:
    _ns: "openstack"

- name: Get pods
  kubernetes.core.k8s_info:
    kind: Pod
    namespace: "{{ _ns }}"

# Good - value used once, inline it
- name: Get pods
  kubernetes.core.k8s_info:
    kind: Pod
    namespace: "openstack"
```

Only create a variable when the value is reused, computed, or externally
configurable.

---

## [Critical] Debug and Diagnostic Tasks in Production Code

Do not leave `ansible.builtin.debug` tasks in production task files
unless they are guarded by a verbosity level or a debug flag. Unguarded
debug tasks clutter CI logs and may accidentally expose sensitive data.

```yaml
# Bad - always prints, clutters logs
- name: Show current config
  ansible.builtin.debug:
    var: _config

# Good - only shows at high verbosity
- name: Show current config
  ansible.builtin.debug:
    var: _config
    verbosity: 2

# Good - gated behind a role-level flag
- name: Show current config
  ansible.builtin.debug:
    var: _config
  when: cifmw_my_role_debug | default(false) | bool
```

In `rescue` blocks, debug dumps are expected and encouraged — that is the
right place to emit diagnostic output.

---

## [Suggestion] Patch Size

Large changes must be broken into smaller, self-contained merge requests.
A single MR that touches too many files or mixes unrelated concerns is
hard to review, risky to merge, and painful to revert.

**When to split:**

- The MR introduces a new role **and** modifies existing roles — submit the
  new role first, then the integration changes separately.
- The MR refactors existing code **and** adds new behavior — land the
  refactor first so the new feature diff is clean.
- The MR touches multiple unrelated subsystems (e.g., a playbook change,
  a criteria update, and a documentation fix) — each belongs in its own MR.
- The MR exceeds ~300 lines of meaningful diff (excluding generated files
  and test data). This is a guideline, not a hard limit — a 500-line MR
  that changes one coherent thing is fine; a 200-line MR that does three
  unrelated things is not.

**How to split effectively:**

1. Each MR should be reviewable and mergeable on its own without breaking
   the build or existing behavior.
2. Use `Depends-On:` in the MR description to express ordering between
   related MRs that must merge in sequence.
3. Prefer vertical slices (one complete feature end-to-end) over horizontal
   slices (all tasks first, then all tests, then all docs).

**Why this matters:**

- Smaller MRs get reviewed faster and more thoroughly.
- Smaller MRs are easier to bisect when something breaks.
- Smaller MRs reduce merge conflicts with other contributors.
- Reviewers lose focus and miss bugs in large diffs.
