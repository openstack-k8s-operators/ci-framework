# Deploy the infrastructure

The Framework works in a 2-step approach. Let's first get the needed infrastructure for your tests.

## Lightweight infrastructure

As said, this infrastructure involves [CRC](https://crc.dev/crc/getting_started/getting_started/introducing/)
and fewer resources than the Validated Architecture.

Note: for the lightweight infrastructure, you may be able to deploy it on your laptop/desktop directly.
In such a case, additional notes will be provided.

In order to deploy that infrastructure, you have to:

- Retrieve your [pull-secret](https://console.redhat.com/openshift/create/local) (chose "Download pull secret")
- Push it onto the hypervisor (`scp pull-secret user@hypervisor:pull-secret` for instance)
- Prepare an inventory file
- Maybe prepare a custom variables file
- run `ansible-playbook`

### Inventory file

It must expose at least two hosts:

1. localhost
2. the hypervisor

You can take this as a template:

```YAML
all:
  hosts:
    localhost:
      ansible_connection: local
    hypervisor-1:
      ansible_user: my_remote_user
      ansible_host: hypervisor.localnet
```

Note: in case you want to run the framework against your laptop/desktop, you can avoid the `hypervisor-1` host.

### Custom variables file

You may want to override some of the default settings provided in the
[3-node.yml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/scenarios/reproducers/3-nodes.yml)
scenario file.

### Run the deployment

Once you're ready, run:

```Bash
$ cd ci-framework
$ ansible-playbook -i custom-inventory.yml \
    -e @scenarios/reproducers/3-nodes.yml \
    -e cifmw_target_host=hypervisor-1 \
    [-e @custom-env-file.yml] \
    reproducer.yml
```

#### Explanations

The `custom-inventory.yml` is your custom inventory. If you're deploying on your laptop/desktop, you don't need to
pass it.

The `@scenarios/reproducers/3-nodes.yml` extra variable file is the base of the lightweight infrastructure.

The `cifmw_target_host` allows to run the framework against your hypervisor. If you're deploying against your
laptop/desktop, you do not need to pass it.

## Validated Architecture

As said, this infrastructure involves a 3-node
[OCP](https://www.redhat.com/en/technologies/cloud-computing/openshift/container-platform)
cluster - meaning there's little chance you can deploy it on your laptop/desktop.

In order to deploy that infrastructure, you have to:

- Retrieve your [pull-secret](https://console.redhat.com/openshift/create/local) (chose "Download pull secret")
- Retrieve your [CI Token](https://console-openshift-console.apps.ci.l2s4.p1.openshiftapps.com/) (chose
  "Copy login command" from your user menu, authenticate using "RedHat_Internal_SSO", then "Display Token")
- Prepare an inventory file
- Prepare a custom variables file
- run `ansible-playbook`

### Inventory file
Since there's little chance you can run this against your laptop/desktop, you have to provide at least 2 hosts in
the inventory:

- localhost
- the hypervisor

You can take this as a template, replacing the needed bits such as `ansible_user` and `ansible_host`.

```YAML
all:
  hosts:
    localhost:
      ansible_connection: local
    hypervisor-1:
      ansible_user: my_remote_user
      ansible_host: hypervisor.localnet
```

### Custom variables file

Here, you will have to provide a series of information to be able to deploy. Most of them are internal to Red Hat,
and will also require your secrets (pull-secret and CI Token):

```YAML
cifmw_reproducer_hp_rhos_release: "true|false"  # if your hypervisor isn't subscribed, you will need rhos-release
cifmw_repo_setup_promotion: "podified-ci-testing"  # or any valid release you want to test
cifmw_repo_setup_branch: osp18  # or any valid branch
cifmw_repo_setup_dlrn_uri: "SOME_URI"  # URI to the internal Delorean service
cifmw_repo_setup_os_release: "rhel"  # mandatory for rhos-release setup
cifmw_repo_setup_enable_rhos_release: true  #  mandatory, especially on the controller-0 node
cifmw_repo_setup_rhos_release_rpm: "SOME_URI"  # URI to the rhos-release RPM
cifmw_reproducer_internal_ca: "SOME_URI"  # URI to the internal CA RPM
cifmw_repo_setup_rhos_release_args: "ceph-6.0 -r 9.2"  # parameters needed for rhos-release
cifmw_repo_setup_dist_major_version: "{{ ansible_distribution_major_version }}"
cifmw_repo_setup_env:
  CURL_CA_BUNDLE: "/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt"
cifmw_discover_latest_image_base_url: "SOME_URI"  # URI to the internal image repository
cifmw_discover_latest_image_qcow_prefix: "rhel-guest-image-9.2-"
cifmw_discover_latest_image_images_file: "SHA256SUM"
insecure_registry: 'INTERNAL_REGISTRY'  # internal registry hostname
# OpenStack Operator index images
ci_openstack_operator_catalog_img_latest: "quay.io/openstack-k8s-operators/openstack-operator-index:latest"
cifmw_devscripts_ci_token: 'TOKEN'  # your private CI Token
cifmw_devscripts_pull_secret: 'my-content'  # your private pull-secret content
```

### Run the deployment

Once you're ready, run:

```Bash
$ cd ci-framework
$ ansible-playbook -i custom-inventory.yml \
    -e @scenarios/reproducers/validated-architecture-1.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @custom-env-file.yml \
    reproducer.yml
```
