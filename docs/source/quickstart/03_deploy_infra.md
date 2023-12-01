# Deploy the infrastructure

The Framework works in a 2-step approach. Let's first get the needed infrastructure for your tests.

## Lightweight infrastructure

As said, this infrastructure involves [CRC](https://crc.dev/crc/getting_started/getting_started/introducing/).

~~~{tip}
For the lightweight infrastructure, you may be able to deploy it on your laptop/desktop directly.
In such a case, additional notes will be provided.
~~~

In order to deploy that infrastructure, you have to:

- Retrieve your [pull-secret](https://console.redhat.com/openshift/create/local) (chose "Download pull secret")
- Prepare an inventory file
- Prepare a custom variables file
- run `ansible-playbook`

### Inventory file

It must expose at least two hosts:

1. localhost
2. the hypervisor

You can take this as a template:

~~~{code-block} YAML
:caption: inventory.yml
:linenos:
all:
  hosts:
    localhost:
      ansible_connection: local
    hypervisor-1:
      ansible_user: my_remote_user
      ansible_host: hypervisor.localnet
~~~

~~~{tip}
In case you want to run the framework against your laptop/desktop, you can avoid the `hypervisor-1` host.
~~~

### Custom variables file

You may want to override some of the default settings provided in the
[3-node.yml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/scenarios/reproducers/3-nodes.yml)
scenario file.

Among the needed overrides, the pull-secret has to be passed down, for instance:

~~~{code-block} YAML
:caption: custom/private-params.yml
cifmw_manage_secrets_pullsecret_file: "{{ lookup('env', 'HOME') }}/pull-secret.txt"
~~~

### Run the deployment

Once you're ready, run:

```Bash
[laptop]$ cd ci-framework
[laptop]$ ansible-playbook -i custom-inventory.yml \
    -e @scenarios/reproducers/3-nodes.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @custom/private-params.yml
    reproducer.yml
```

#### Explanations

The `custom-inventory.yml` is your custom inventory. If you're deploying on your laptop/desktop, you don't need to
pass it.

The `@scenarios/reproducers/3-nodes.yml` extra variable file is the base of the lightweight infrastructure.

The `cifmw_target_host` allows to run the framework against your hypervisor. If you're deploying against your
laptop/desktop, you do not need to pass it.
