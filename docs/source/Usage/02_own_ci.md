# Use in your own CI job

## In Prow
The CI Framework provides a container exposing the whole framework as well as
all of the helpers. You may leverage it like this:
```YAML
build_root:
  cifmw:
    name: "ci-framework-image"
    tag: "latest"
    namespace: "openstack-k8s-operators"
tests:
- as: pre-commit
  from: cifmw
  clone: true
  commands: |
    export HOME=/tmp
    export ANSIBLE_LOCAL_TMP=/tmp
    export ANSIBLE_REMOTE_TMP=/tmp
    make -C ../ci-framework pre_commit_nodeps BASEDIR ./
```
Please refer to the `make` manpage for more fun! Please refer to the
[openshift CI doc](https://docs.ci.openshift.org/docs/getting-started/examples/#how-do-i-write-a-simple-execute-this-command-in-a-container-test)
as well as the [ci-operator](https://docs.ci.openshift.org/docs/architecture/ci-operator/) for more details.

## In Zuul
The Framework exposes various jobs you may re-use as parent. Please have a look
at the [zuul.d](https://github.com/openstack-k8s-operators/ci-framework/tree/main/zuul.d)
content for more details.
