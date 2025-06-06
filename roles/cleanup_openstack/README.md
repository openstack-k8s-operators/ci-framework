# cifmw_ceph_client

Renders `ceph.conf` and `ceph.client.openstack.keyring` files
and encodes them into k8s secret CR (`k8s_ceph_secret.yml`).
To be used after deploying Ceph with the `cifmw_cephadm` role.

After running `oc create -f k8s_ceph_secret.yml` the OpenStack pods
deployed by `openstack-k8s-operators` should be able to connect to
Ceph.

## Privilege escalation
None

## Parameters
