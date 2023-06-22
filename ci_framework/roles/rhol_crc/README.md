# rhol_crc

Role to deploy get, configure and start RHOL/CRC instance.

## Privilege escalation

Become - required for the tasks in `sudoers_grant.yml` and `sudoers_revoke.yml` since these ones add and remove under `/etc/sudoers.d/` folder.

## Parameters

* `cifmw_rhol_crc_basedir`: (String) Directory where we will have the RHOL/CRC binary and the configuration (e.g. `artifacts/.rhol_crc_pull_secret.txt`). Default to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_edpm_deploy_installyamls`: (String) install_yamls root location. Defaults to `cifmw_installyamls_repos` which defaults to `../..`.
* `cifmw_rhol_crc_use_installyamls`: (Boolean) Tell the role to leverage install_yamls `crc` related targets. Defaults to `False`.
* `cifmw_rhol_crc_dryrun`: (Boolean) Toggle the `ci_make` `dry_run` parameter. Defaults to `False`.
* `cifmw_rhol_crc_config`: (Dict) This structure is merged with the `cifmw_rhol_crc_config_defaults` dictionary. We can add extra properties or override the existing one using this parameter. We can know the parameters that can be used with the output of the `crc config --help` command. Defaults to `{}`.
* `cifmw_rhol_crc_version`: (String) RHOL/CRC binary version we wanna use. Default: `latest`.
* `cifmw_rhol_crc_tarball_name`: (String) RHOL/CRC tarball name depending of the architecture. Defaults to `crc-linux-amd64.tar.xz`.
* `cifmw_rhol_crc_tarball_checksum_name`: (String) RHOL/CRC tarball file checksum name. Defaults to `crc-linux-amd64.tar.xz.sha256`.
* `cifmw_rhol_crc_base_url`: (String) RHOL/CRC URL base. Defaults to `https://mirror.openshift.com/pub/openshift-v4/clients/crc/2.14.0`.
* `cifmw_rhol_crc_binary_folder`: (String) Folder that will be used to store the RHOL/CRC binary. Defaults to `{{ cifmw_rhol_crc_basedir }}/bin`.
* `cifmw_rhol_crc_binary`: (String) Path of the RHOL/CRC downloaded binary for executing the commands. Defaults to `{{ cifmw_rhol_crc_basedir }}/bin/crc`.
* `cifmw_rhol_crc_force_cleanup`: (Boolean) In case this variable is `true` it will delete if exists the actual crc instance, domain and linked resources and recreate it with the new configuration. Defaults to `False`.
* `cifmw_rhol_crc_reuse`: (Boolean) In case RHOL/CRC is detected, just reuse it. Defaults to `True`
* `cifmw_rhol_crc_kubeconfig`: (String) Path to crc kubeconfig file. Defaults to `~/.crc/machines/crc/kubeconfig`.
* `cifmw_rhol_crc_creds`: (Boolean) Add crc creds to bashrc. Defaults to `False`.
* `cifmw_rhol_crc_post_customize`: (Boolean) Apply custom definitions after crc started. Defaults to `True`.
## Cleanup

You may call the `cleanup.yml` role in order to delete the `crc` instance and all the associated configuration like networking, volume, virsh domain, etc.
