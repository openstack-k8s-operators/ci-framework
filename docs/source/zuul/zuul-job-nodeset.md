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
    nodeset: centos-9-medium-crc-extracted-2-36-0-3xl
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
