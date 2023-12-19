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
* `cifmw_tempest_tempestconf_profile`: (Dictionary) List of settings to be overwritten in tempest.conf.
* `cifmw_tempest_concurrency`: (Integer) Tempest concurrency value.
* `cifmw_tempest_tests_allowed_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_allowed` definition. Default to `false`
* `cifmw_tempest_tests_skipped_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_skipped` definition. Default to `false`

## Use of cifmw_tempest_tempestconf_profile

You can pass arguments to tempestconf and also override tempest config options.
The tempest config options goes under overrides, while the tempestconf options
goes in the root of the dictionary, for example:

```
cifmw_tempest_tempestconf_profile:
debug: true
deployer-input: /etc/tempest-deployer-input.conf
overrides:
    validation.run_ssh: false
    telemetry.alarm_granularity: '60'
```

Where debug is the same as passing `--debug` to cli and deployer-input is the
same as `--deployer-input`. Under overrides, you have validation.run_ssh as
false, this will create in tempest.conf under validation section an option
run_ssh as false. The same with telemetry.alarm_granularity, it will create
under telemetry section an option alarm_granularity set to 60.
