# Contribution guidelines

## Ansible best practices

We try hard to follow [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/index.html).

### Include vs Import

Usually, we should rely on `ansible.builtin.import_(tasks|role)` instead of
`ansible.builtin.include_(tasks|role)`.

While both are mostly doing the same, the time and support is different.

#### Include

The `include_*` directives allow to load content dynamically. This is usually
mandatory when we want to `loop` on items, and include multiple time the same
tasks or role. The inclusion is done mostly runtime, and makes some usages a
bit more complicated.

For instance, `tags` aren't passed along, unless we use `apply` keyword.

The `include_*` directives may also have an impact on performances.

#### Import

The `import_*` directives allow to load content statically. It's usually
"compiled" internally when the play environment is built, meaning we may get
small performances improvements. They fully support `tags` so that we may
get a more convenient way to filter tasks in the play.

~~~{admonition} What to use then?
:class: tip
A simple rule of thumb: if I intend to run the tasks/role multiple time
over the same play, I'll use `include_*` module. For the rest, I'll use
`import_*`.
~~~

## Testing

### Ansible role

Please take the time to ensure [molecule tests](./02_molecule.md) are present
and cover as many corner cases as possible.

### Ansible custom plugins

Please take the time to consider how to test your custom plugins. You may
either rely on [molecule](./02_molecule.md) or, maybe,
[ansible-test](https://github.com/openstack-k8s-operators/ci-framework/tree/main/tests/integration).

## Review workflow

### Auto draft status automation

When a PR is opened or reopened on the CI-Framework repo the Github bot will enable the draft status.
Once your patch is passing CI and you would be happy with it merging, click the "Ready for review" button,
this will trigger the review ready workflow.

If you have a small patch you would like to skip the auto-draft workflow, you can prefix your git commit title
with `nit:`

### Review ready automation

Once your PR is out of draft status it will be evaluated by the review ready workflow, if your patch passes
the following evaluations the "Ready for Review" label will be added informing the Ci-Framework maintainers
to review your patch.

The evaluation steps are:

- There are no failed CI jobs
- There are no Pending CI jobs excluding Tide
- The PR isn't in draft state
- The commit isn't found in more than one PR

If at any time your patch no longer meets this criteria the label will be removed.

### Escalating your review

If you would like to bring attention to your patch before a reviewer has made it to your patch
reach out in our [slack channel](https://redhat.enterprise.slack.com/archives/C03MD4LG22Z)
