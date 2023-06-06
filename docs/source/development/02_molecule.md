# Molecule configuration/testing

All of the roles should get proper molecule tests. When you generate a new
role using `make new_role ROLE_NAME=my_role`, you will end with a basic role
structure, including the molecule part.

[More information about molecule](https://molecule.readthedocs.io/)

## My test needs CRC
By default, molecule tests are configured to consume a simple CentOS Stream 9
node in Zuul. But it may happen you need to talk to an OpenShift API within
your role.

In order to consume a CRC node, you have to edit the following file:
[scripts/create_role_molecule](https://github.com/openstack-k8s-operators/ci-framework/blob/main/scripts/create_role_molecule)
and, on line 4, append your new job name to the `NEED_CRC_XL` list.

For now, we "only" support the crc-xl nodeset. It should cover most of the
needs for molecule. It matches the **centos-9-stream-crc-xl**
[label in rdoproject](https://review.rdoproject.org/zuul/labels).

Once you have edited the script, re-generate the molecule job:
`make role_molecule`.
