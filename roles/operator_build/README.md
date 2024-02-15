# operator_build
Builds OpenStack k8s operators and push them to a registry.
When building an operator from a Pull Request, it is mandatory to provide the PR Owner and the PR SHA *only* if
you want to build meta-operator too, so the role can properly replace api references in meta-operator.

## Parameters
* `cifmw_operator_build_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_operator_build_dryrun`: (Boolean) Toggle `ci_make` `dry_run` flag. Defaults to `False`.
* `cifmw_operator_build_golang_ct`: (String) Reference to the golang container. Defaults to `docker.io/library/golang:1.20`.
* `cifmw_operator_build_golang_alt_ct`: (String) Reference to an alternative golang container. Defaults to `quay.io/projectquay/golang:1.20`.
* `cifmw_operator_build_org`: (String) Operator's organization on GitHub. Defaults to `openstack-k8s-operators`.
* `cifmw_operator_build_push_registry`: (String) Registry used to push images. Defaults to `quay.rdoproject.org`.
* `cifmw_operator_build_push_org`: (String) Registry's organization to push image to. Defaults to `openstack-k8s-operators`.
* `cifmw_operator_build_push_ct`: (Boolean) Push generated containers. Defaults to `True`.
* `cifmw_operator_build_operators`: (List) List of operators to build (it should not include meta-operator). Defaults to `[]`.
* `cifmw_operator_build_meta_name`: (String) Meta operator's name. Defaults to `openstack-operator`.
* `cifmw_operator_build_meta_src`: (String) Directory with src code for meta operator. Defaults to `"{{ ansible_user_dir }}/src/github.com/{{ cifmw_operator_build_org }}/{{ cifmw_operator_build_meta_name }}"`
* `cifmw_operator_build_meta_build`: (Boolean) When set to `true` updates meta-operator's go.mod when build operators and builds meta-operator in the end. Default to `true`.
* `cifmw_operator_build_meta_image_base`: (String) Name of the service added to be added to meta-operator build. Still limited to a single service (and operator). Default to `""`
* `cifmw_operator_build_push_registry_tls_verify`: (Boolean) Variable to control whether to enable/disable TLS verification for push registry . Defaults to `true`.

## TODO
* Include tasks to get PR Owner and PR SHA info from **Prow** environment.
* Support build in dev environment (build with gowork without GitHub)

## Examples
### 1 - Building mariadb-operator checked-out from a PR and meta-operator
```yaml
- hosts: all
  tasks:
    - name: Builds mariadb-operator and meta-operator
      include_role:
        name: operator_build
      vars:
        cifmw_operator_build_push_registry: "quay.io"
        cifmw_operator_build_push_org: "myorg"
        cifmw_operator_build_meta_build: true
        cifmw_operator_build_meta_src: "/home/user/openstack-operator"
        cifmw_operator_build_operators:
          - name: "mariadb-operator"
            src: "/home/user/mariadb-operator"
            pr_owner: "ci-framework/openstack-operator"
            pr_sha: "ea971d4a445e524b9fa55e3a0f99d11a2f118cb9"
```

### 2 - Building mariadb-operator and keystone-operator. Skip meta-operator build.
```yaml
- hosts: all
  tasks:
    - name: Building mariadb-operator and keystone-operator
      include_role:
        name: operator_build
      vars:
        cifmw_operator_build_push_registry: "quay.io"
        cifmw_operator_build_push_org: "myorg"
        cifmw_operator_build_meta_build: false
        cifmw_operator_build_operators:
          - name: "mariadb-operator"
            src: "/home/user/mariadb-operator"
            pr_owner:
          - name: "keystone-operator"
            src: "/home/user/keystone-operator"
```
