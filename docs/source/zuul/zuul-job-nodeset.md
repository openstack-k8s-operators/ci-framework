# Consume ci-framework zuul base jobs

## Existing jobs

The CI Framework defines a small subset of jobs.

The one you may be interested in is the multinode layout, ensuring CRC is running
on a dedicated nodeset, with an external compute and an ansible-controller node.

In case you want to inherit from our base job, while still wanting to use only CRC
and the ansible-controller one, you have to override a parameter via the `extra_vars`
job parameter:

~~~{code-block} YAML
:caption: zuul.d/base.yaml
:linenos:
- job:
    name: my-job-with-2-nodes
    parent: podified-multinode-edpm-deployment-crc
    nodeset: centos-9-medium-crc-cloud-ocp-4-20-1-3xl
    vars:
      cifmw_deploy_edpm: false
      podified_validation: true
      cifmw_run_tests: false
    extra-vars:
      crc_ci_bootstrap_networking:
        networks:
          default:
            range: 192.168.122.0/24
            mtu: 1500
          internal-api:
            vlan: 20
            range: 172.17.0.0/24
          storage:
            vlan: 21
            range: 172.18.0.0/24
          tenant:
            vlan: 22
            range: 172.19.0.0/24
        instances:
          controller:
            networks:
              default:
                ip: 192.168.122.11
          crc:
            networks:
              default:
                ip: 192.168.122.10
              internal-api:
                ip: 172.17.0.5
              storage:
                ip: 172.18.0.5
              tenant:
                ip: 172.19.0.5
~~~

~~~{tip}
We have to use that `extra_vars` in order to properly override the `vars` we define in the
parent job - apparently, Zuul is merging mappings instead of properly overriding them like
it does with actual string parameters.
~~~

## Nodesets

Nodesets specify the sets of machines to be provisioned and used by Zuul
during the execution of a specific job. Jobs inherit their nodesets from their
parents, or can select their own nodesets to use by specifying `nodeset:`
values in their own definitions.

For example, the above example job, `my-job-with-2-nodes`
specifies the nodeset `centos-9-medium-crc-cloud-ocp-4-20-1-3xl`.
This and all other nodesets that are available to the ci-framework's jobs are
defined in
[zuul.d/nodeset.yaml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/zuul.d/nodeset.yaml).

~~~{code-block} YAML
:caption: zuul.d/nodeset.yaml
:linenos:
- nodeset:
    name: centos-9-medium-crc-cloud-ocp-4-20-1-3xl
    nodes:
      - name: controller
        label: cloud-centos-9-stream-tripleo-medium
      - name: crc
        label: crc-cloud-ocp-4-20-1-3xl
    groups:
      - name: computes
        nodes: []
      - name: ocps
        nodes:
          - crc
~~~

The `controller` and `crc` nodes in the above nodeset are assigned the labels
`cloud-centos-9-stream-tripleo-medium` and `crc-cloud-ocp-4-20-1-3xl`
respectively. These labels select which virtual machine flavors and disk
images to use when creating the virtual machines. Flavors define the number of
vCPUs and the amount of memory to allocate to a given node.
The complete list of labels available to our Zuul instance can be found on the
['Labels' tab](https://softwarefactory-project.io/zuul/t/rdoproject.org/labels)
of the Zuul web interface. The definition of these labels is found in our Zuul
instance's
[config project](https://softwarefactory-project.io/cgit/config/tree/) - see
[this commit](https://softwarefactory-project.io/cgit/config/commit/?id=23517ea396d9f602aec19625224eb71a8cd7642d)
for an example of how a label like `crc-cloud-ocp-4-20-1-3xl` from the above
nodeset is defined.
