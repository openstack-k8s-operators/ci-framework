# dlrn_promote
This Ansible role that checks DLRN for jobs reporting
SUCCESS on a hash and promotes the hash based on
predefined criteria.

This role allows for DLRN promotion using either a
DLRN user name and password or Kerberos authentication.

## Privilege escalation
This role does not need privilege escalation.

## Parameters
* `cifmw_dlrn_promote_workspace`: (string) Directory where the reporting is executed. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`
* `cifmw_dlrn_promote_dlrnapi_user`: (string) DLRN user to report results. Default: `{{ dlrnapi_user | default('review_rdoproject_org') }}`
* `cifmw_dlrn_promote_kerberos_auth`: (boolean) Whether to use Kerberos authentication when reporting results to DLRN. Default: `false`
* `cifmw_dlrn_promote_dlrnapi_host_principal`: (string) DLRN principal to use with Kerberos authentication. Default `""`
* `cifmw_dlrn_promote_criteria_file`: (string) DLRN promote criteria file. Default `""`
* `cifmw_dlrn_promote_hash`: (boolean) Whether to run DLRN promote hash. Default: `false`
* `cifmw_dlrn_promote_ssl_ca_bundle`: (string) Path to SSL CA cert. Default: `"/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt"`
* `cifmw_dlrn_promote_hash_promote_content`: (boolean) Whether to promote DLRN content. Default: `false`
* `cifmw_dlrn_promote_dlrnrepo_filename`: (String) Name of the delorean repo file. Default: `delorean.repo`
* `cifmw_dlrn_promote_dlrnrepo_path`: (String) Path to delorean repo file. Default: `{{ cifmw_dlrn_promote_workspace }}/artifacts/repositories/{{ cifmw_dlrn_promote_dlrnrepo_filename }}`

## Notes

The sample `cifmw_dlrn_promote_criteria_file` criteria file can be found in `files` directory.

## Dependencies

This role depends on ci-framework [repo-setup](https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/repo_setup)
and [set-zuul-log-path-fact](https://opendev.org/zuul/zuul-jobs/src/branch/master/roles/set-zuul-log-path-fact) roles.

## Example
```YAML
---
- hosts: localhost
  gather_facts: true
  tasks:
    - name: Promote DLRN hash
      ansible.builtin.import_role:
        name: dlrn_promote
