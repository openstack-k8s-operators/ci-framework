# Reproducer scenarios

These environment files define validated architecture scenarios for the
virtual reproducer (reproducer.yml playbook). Each file sets
`cifmw_libvirt_manager_configuration` (libvirt networks and VMs),
`cifmw_devscripts_config_overrides`, and other deployment parameters for
a specific architecture variant (e.g. HCI, SNO, multi-site).

The `cifmw_architecture_scenario` variable selects which file to load.
For example, `cifmw_architecture_scenario: va-hci-minimal-sno` loads
`va-hci-minimal-sno.yml`.

Baremetal deployments (e.g. ci-framework-jobs BM SNO) do not use the
`cifmw_libvirt_manager_configuration` from these files. They provide
their own networking, kustomization, and scenario variables via Zuul
`variable_files` / `variable_files_dirs`, which take precedence as
Ansible extra vars.

Please refer to [the reproducer documentation](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html)
for usage details.
