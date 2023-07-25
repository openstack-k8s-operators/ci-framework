# tempest
Role to setup and run tempest tests

## Privilege escalation
become - Required to install required rpm packages

## Parameters

* `cifmw_tempest_artifacts_basedir`: (String) Directory where we will have all tempest files. Default to `cifmw_basedir/artifacts/tempest` which defaults to `~/ci-framework-data/artifacts/tempest`.
* `cifmw_tempest_default_groups`: (List) List of groups in the include list to search for tests to be executed
* `cifmw_tempest_default_jobs`: (List) List of jobs in the exclude list to search for tests to be excluded
* `cifmw_tempest_image`: (String) Name of the tempest image to be used. Default to `quay.io/podified-antelope-centos9/openstack-tempest`
* `cifmw_tempest_image_tag`: (String) Tag for the `cifmw_tempest_image`. Default to `current-podified`
* `cifmw_tempest_dry_run`: (Boolean) Whether tempest should run or not. Default to `false`
* `cifmw_tempest_remove_container`: (Boolean) Cleanup tempest container after it is done. Default to `false`
* `cifmw_tempest_tests_skipped`: (List) List of tests to be skipped. Setting this will not use the `list_skipped` plugin
* `cifmw_tempest_tests_allowed`: (List) List of tests to be executed. Setting this will not use the `list_allowed` plugin
