# CI-Framework

Still under heavy development - more info coming soon.

## Use Makefile for your own CI

### Container available for Prow
You can point to our container in your project:
```YAML
base_image:
  cifwm:
    name: "ci-framework-image"
    tag: "latest"
    namespace: "openstack-k8s-operators"
tests:
- as: pre-commit
  commands: |
    export HOME=/tmp
    export ANSIBLE_LOCAL_TMP=/tmp
    export ANSIBLE_REMOTE_TMP=/tmp
    make -C ../ci-framework pre_commit_nodeps BASEDIR ./
- as: molecule
  commands: |
    export HOME=/tmp
    export ANSIBLE_LOCAL_TMP=/tmp
    export ANSIBLE_REMOTE_TMP=/tmp
    make -C ../ci-framework molecule_nodeps ROLE_DIR=../your-project/
```
Please refer to the `make` manpage for more fun!

### Targets of interest
#### ci_ctx
That one will build you a container in order to run the checks
#### run_ctx_pre_commit
That one will run the pre-commit check in a container.
#### run_ctx_molecule
That one will run molecule against the role. Note That, if needed, you can
pass different parameters:
```Bash
$ make run_ctx_molecule BUILD_VENV_CTX=yes MOLECULE_CONFIG=.config/molecule/config_local.yml
```
Run molecule in a freshly built container, using the "config_local.yml" file. Note that
this configuration file is *mandatory* for running molecule from within the container
#### molecule_nodeps
```Bash
$ make molecule_nodeps BUILD_VENV_CTX=no \
    MOLECULE_CONFIG=.config/molecule/config_local.yml \
    ROLE_DIR=../my-repo/roles
```
This one is a bit more tricky: it means you are in a deployed env (for instance
a container built using ```make ci_ctx```) with a 3rd-party repository
available in /opt/my-repo. You can get this by running the following:
```Bash
$ podman run --rm -ti --security-opt label=disable \
    -v .:/opt/sources \
    -v ../my-repo:/opt/my-repo \
    cfwm:latest bash
```
Then, just run the ```make``` command with the right parameters.

## Contribute
### Add a new Ansible role
Run the following command to get your new role in:
```Bash
$ ansible-galaxy role init \
    --init-path ci_framework/roles \
    --role-skeleton _skeleton_role_ \
    YOUR_ROLE_NAME
```


### Run tests
#### Makefile
Run ```make help``` to list the available targets. Usually, you'll want to run
```make run_ctx_pre_commit``` or ```make run_ctx_molecule``` to run the tests
in a local container.


## License
Copyright 2023.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
