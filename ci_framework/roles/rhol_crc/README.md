# rhol_crc

Role to deploy get, configure and start RHOL/CRC instance.

## Privilege escalation

Become - required for the tasks in `sudoers_grant.yml` and `sudoers_revoke.yml` since these ones add and remove under `/etc/sudoers.d/` folder.

### Parameters

* `cifmw_rhol_crc_basedir`: Directory where we will have the RHOL/CRC binary and the configuration (e.g. artifacts/.rhol_crc_pull_secret.txt). Default to `cifmw_basedir` which defaults to ~/ci-framework.
* `cifmw_rhol_crc_installyamls`: Location of install_yamls repository root. Defaults to `../..`.
* `cifmw_rhol_crc_use_installyamls`: Tell the role to leverage install_yamls `crc` related targets. Defaults to `false`.
* `cifmw_rhol_crc_dryrun`: Toggle the `ci_make` `dry_run` parameter. Defaults to `false`.
* `cifmw_rhol_crc_config`: This dictionary is merged with the `cifmw_rhol_crc_config_defaults` dictionary. We can add extra properties or override the existing one using this parameter. We can know the parameters that can be used with the output of the `crc config --help` command. Default: `{}`
* `cifmw_rhol_crc_version`: RHOL/CRC binary version we wanna use. Default: `latest`
* `cifmw_rhol_crc_tarball_name`: RHOL/CRC tarball name depending of the architecture.
* `cifmw_rhol_crc_tarball_checksum_name`: RHOL/CRC tarball file checksum name. Default: `crc-linux-amd64.tar.xz.sha256`
* `cifmw_rhol_crc_base_url`: RHOL/CRC URL base. Default: `https://mirror.openshift.com/pub/openshift-v4/clients/crc/2.14.0`
* `cifmw_rhol_crc_binary_folder`: Folder that will be used to store the RHOL/CRC binary. Default: `bin` folder under the `cifmw_rhol_crc_basedir`.
* `cifmw_rhol_crc_binary`: Path of the RHOL/CRC downloaded binary for executing the commands. Default: `bin/crc` binary file under the `cifmw_rhol_crc_basedir`.
* `cifmw_rhol_crc_force_cleanup`: In case this variable is `true` it will delete if exists the actual crc instance, domain and linked resources and recreate it with the new configuration. Default: `false`
* `cifmw_rhol_crc_kubeconfig`: Path to crc kubeconfig file. Default to `~/.crc/machines/crc/kubeconfig`
* `cifmw_rhol_crc_creds`: Add crc creds to bashrc. Default to `False`

## Cleanup

You may call the `cleanup.yml` role in order to delete the `crc` instance and all the associated configuration like networking, volume, virsh domain, etc.
