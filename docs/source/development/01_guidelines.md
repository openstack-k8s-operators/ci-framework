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

Once your patch is passing CI and not in draft status a reviewer will review your patch.
If you would like to bring attention to your patch before a reviewer has made it to your patch
reached out in our [slack channel](https://redhat.enterprise.slack.com/archives/C03MD4LG22Z)

### Auto Draft status

When a PR is opened or reopened the Github bot will enable the draft status. Once your patch is
passing CI and you would be happy with it merging, click the "Ready for review" button, this will
then trigger the Review workflow mentioned above.
