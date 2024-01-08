# Molecule configuration/testing

All of the roles should get proper molecule tests. When you generate a new
role using `make new_role ROLE_NAME=my_role`, you will end with a basic role
structure, including the molecule part.

[More information about molecule](https://molecule.readthedocs.io/)

## Testing

Any extra configuration required for any Zuul CI job will be added in the following file [ci/config/molecule.yaml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/ci/config/molecule.yaml).

For example if we need to set a timeout to the job `cifmw-molecule-rhol_crc` then we need to append the following lines:

~~~{code-block} YAML
:caption: zuul.d/job.yaml
:linenos:
- job:
    name: cifmw-molecule-rhol_crc
    timeout: 3600
~~~

These directives will be merged with the job definition created in the script [scripts/create_role_molecule.py](https://github.com/openstack-k8s-operators/ci-framework/blob/main/scripts/create_role_molecule.py)


## My test needs CRC
By default, molecule tests are configured to consume a simple CentOS Stream 9
node in Zuul. But it may happen you need to talk to an OpenShift API within
your role.

In order to consume a CRC node, you have to edit the following file:
[ci/config/molecule.yaml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/ci/config/molecule.yaml)
and add the directive `nodeset: centos-9-stream-crc-2-19-0-xl` under the related job.
For now, we "only" support the crc-xl nodeset. It should cover most of the
needs for molecule. It matches the **centos-9-stream-crc-2-19-0-xl**
[label in rdoproject](https://review.rdoproject.org/zuul/labels).

Once you have edited the script, re-generate the molecule job:
`make role_molecule`.
