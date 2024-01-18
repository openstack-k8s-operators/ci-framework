# tobiko
Role to setup and run tobiko tests

## Privilege escalation
become - Required to install required rpm packages

## Parameters
* `cifmw_tobiko_artifacts_basedir`: (String) Directory where we will have all tobiko files. Default to `cifmw_basedir/artifacts/tobiko` which defaults to `~/ci-framework-data/tests/tobiko`.
* `cifmw_tobiko_image`: (String) Name of the tobiko image to be used. Default to `quay.io/podified-antelope-centos9/openstack-tobiko`
* `cifmw_tobiko_image_tag`: (String) Tag for the `cifmw_tobiko_image`. Default to `current-podified`
* `cifmw_tobiko_dry_run`: (Boolean) Whether tobiko should run or not. Default to `false`
* `cifmw_tobiko_remove_container`: (Boolean) Cleanup tobiko container after it is done. Default to `false`
* `cifmw_tobiko_testenv`: (String) Executed tobiko testenv. See tobiko `tox.ini` file for further details. Some allowed values: scenario, sanity, faults, neutron, octavia, py3, etc

## Parameters with default values from tcib or tobiko default configurations
The default values from the following parameters are not taken from this tobiko role, but from the tobiko image defined on the tcib project or from the config.py files within the tobiko project.
* `cifmw_tobiko_version`: (String) Tobiko version to install. It could refer to a branch (master, osp-16.2), a tag (0.6.x, 0.7.x) or an sha-1. Default value: master
* `cifmw_tobiko_pytest_addopts`: (String) `PYTEST_ADDOPTS` env variable with input pytest args. Example: `-m <markers> --maxfail <max-failed-tests> --skipregex <regex>`. Default value is empty string
* `cifmw_tobiko_prevent_create`: (Boolean) Sets the value of the env variable `TOBIKO_PREVENT_CREATE` that specifies whether tobiko scenario tests create new resources or expect that those resource had been created before
* `cifmw_tobiko_num_processes`: (Integer) Sets the value of the env variable `TOX_NUM_PROCESSES` that is used to run pytest with `--numprocesses $TOX_NUM_PROCESSES`. Default value: auto
* `cifmw_tobiko_tobikoconf`: (Dict) Overrides the default configuration that will be used to generate the tobiko.conf file
