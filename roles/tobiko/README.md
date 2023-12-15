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
* `cifmw_tobiko_debug`: (Boolean) Whether tobiko log level is debug or not
* `cifmw_tobiko_testenv`: (String) Executed tobiko testenv. See tobiko `tox.ini` file for further details. Some allowed values: scenario, sanity, faults, neutron, octavia, py3, etc

## Parameters with default values from tcib or tobiko default configurations
The default values from the following parameters are not taken from this tobiko role, but from the tobiko image defined on the tcib project or from the config.py files within the tobiko project.
* `cifmw_tobiko_version`: (String) Tobiko version to install. It could refer to a branch (master, osp-16.2), a tag (0.6.x, 0.7.x) or an sha-1. Default value: master
* `cifmw_tobiko_ubuntu_interface_name`: (String) Name of the primary interface created on the Ubuntu VM instances. Default value: enp3s0
* `cifmw_tobiko_keystone_interface`: (String) Name of the keystone interface to send the requests to. Default value: public
* `cifmw_tobiko_testcase_timeout`: (Float) Timeout (in seconds) used for interrupting test case execution. Default value: 1800.0
* `cifmw_tobiko_testrunner_timeout`: (Float) Timeout (in seconds) used for interrupting test runner execution. Default value: 14400.0
* `cifmw_tobiko_pytest_addopts`: (String) `PYTEST_ADDOPTS` env variable with input pytest args. Example: `-m <markers> --maxfail <max-failed-tests> --skipregex <regex>`. Default value is empty string
* `cifmw_tobiko_report_dir`: (String) Directory where tobiko logs and results are saved
* `cifmw_tobiko_manila_share_protocol`: (String) Share protocol needed for manila to create volumes
* `cifmw_tobiko_prevent_create`: (Boolean) Sets the value of the env variable TOBIKO_PREVENT_CREATE that specifies whether tobiko scenario tests create new resources or expect that those resource had been created before
