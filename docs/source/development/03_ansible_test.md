# Run ansible-tests

Most of the modules have unit jobs to verify if functions
returns what they should to avoid potential errors after modification.

## Testing

The Ansible units job tests are located in `tests/unit/modules/`.
To run the tests, follow the guide:

```shell
podman run -it centos:stream9 bash

###  inside the container ###

# install basic deps
yum install -y git make sudo python3.11-pip

# clone CI framework
git clone https://github.com/openstack-k8s-operators/ci-framework && cd ci-framework

# prepare venv dir
make setup_tests

# source venv
source $HOME/test-python/bin/activate

# install test-requirements.txt via pip
pip3 install -r test-requirements.txt

# run script that execute ansible tests
bash scripts/run_ansible_test
```
