# Report portal
The `reportportal` role uses Data Router tool for uploading XML test results to Report portal. Access to the specific Report portal instance including URL and credentials has to be specified via Data router web interface.

## Parameters
* `cifmw_reportportal_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_reportportal_datarouter_url`: (String) URL with running Data router service (mandatory).
* `cifmw_reportportal_droute_client_url`: (String) URL of Data router client repository (mandatory).
* `cifmw_reportportal_datarouter_username`: (String) username for Data router client (mandatory).
* `cifmw_reportportal_datarouter_password`: (String) password for Data router client (mandatory).
* `cifmw_reportportal_datarouter_result_dir`: (String) Test results directory. Based on `cifmw_run_test_role` defaults to `~/ci-framework-data/tests/tempest/` or `~/ci-framework-data/tests/test_operator/`. One or more properly formatted xml results files are expected to be found in this directory.
* `cifmw_reportportal_project`: (String) Report portal project for uploading results (mandatory).
* `cifmw_reportportal_launch_name`: (String) Name of the Report portal launch defaults to `Dummy launch`.
* `cifmw_reportportal_launch_description`: (String) Description of the Report portal launch defaults to `Test results sent via Data router`.
* `cifmw_reportportal_droute_version`: (String) Data router client version defaults to `1.2.1`.
* `cifmw_reportportal_droute_binary`: (String) Data router binary name defaults to `droute-linux-amd64`.

## Examples
```YAML
- name: Play
  hosts: localhost
  vars:
    cifmw_reportportal_droute_client_url: "https://example.com/data_router_client"
    cifmw_reportportal_datarouter_url: "https://data-router.example.service.com"
    cifmw_reportportal_datarouter_username: "<username>"
    cifmw_reportportal_datarouter_password: "<password>"
    cifmw_reportportal_project: "Example"

  roles:
    - reportportal
```

## Note
This role exclusively relies on the internal Report portal and Data router instances and other internal repositories.
