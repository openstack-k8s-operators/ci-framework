## Role: edpm_deploy
Update EDPM CRD and deploy the services on provided openshift infra (being CRC
or anything supported by `oc`).

### Privilege escalation
None

### Parameters
* `cifmw_edpm_deploy_basedir`: Base directory. Defaults to `cifmw_basedir`
which defaults to `~/ci-framework`.
* `cifmw_edpm_deploy_installyamls`: install_yamls root location. Since
ci-framework should be cloned within that other repository, it defaults to `../..`.
* `cifmw_edpm_deploy_crd`: Path to the CRD the role will use as a base.
Defaults to install_yamls CRD.
* `cifmw_edpm_deploy_inventory`: Path to the generated inventory holding the
external nodes.
* `cifmw_edpm_deploy_oc`: Directory path where the `oc` binary is located.
Defaults to `cifmw_oc`, which defaults to `~/.crc/bin/oc/`

### Resources
* [ci_framework](https://github.com/openstack-k8s-operators/install_yamls)
* [Default CRD](https://github.com/openstack-k8s-operators/install_yamls/blob/master/devsetup/edpm/edpm-play.yaml)
