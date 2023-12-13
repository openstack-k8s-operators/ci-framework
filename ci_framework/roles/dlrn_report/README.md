# dlrn_report
This Ansible role uses the repo_setup role to get information
from the repos installed and the hash under test.
It uses that information, along with the Zuul job status
and log location to report the job result to the
DLRN api.

This role allows for DLRN reporting using either a
DLRN user name and password or Kerberos authentication.

## Privilege escalation
This role does not need privilege escalation.

## Parameters
* `cifmw_dlrn_report_workspace`: (string) Directory where the reporting is executed. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`
* `cifmw_dlrn_report_dlrnapi_user`: (string) DLRN user to report results. Default: `{{ dlrnapi_user | default('review_rdoproject_org') }}`
* `cifmw_dlrn_report_kerberos_auth`: (boolean) Whether to use Kerberos authentication when reporting results to DLRN. Default: `false`
* `cifmw_dlrn_report_dlrnapi_host_principal`: (string) DLRN principal to use with Kerberos authentication. Default `""`
* `cifmw_dlrn_report_result`: (boolean) Whether to report DLRN results. Can be disabled if a test run should not be registered to DLRN. Default `true`
* `cifmw_dlrn_report_krb_user_realm`: (string) Name of valid Kerberos REALM.
* `cifmw_dlrn_report_keytab`: (string) file path to valid keytab file for performing kinit.

## Dependencies

This role depends on ci-framework [repo-setup](https://github.com/openstack-k8s-operators/ci-framework/tree/main/ci_framework/roles/repo_setup)
and [set-zuul-log-path-fact](https://opendev.org/zuul/zuul-jobs/src/branch/master/roles/set-zuul-log-path-fact) roles.

## Example
```YAML
---
- hosts: localhost
  gather_facts: true
  tasks:
    - name: Report DLRN results
      ansible.builtin.import_role:
        name: dlrn_report
