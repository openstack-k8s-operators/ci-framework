# sosreport
A role to gather openstack/openshift deployment logs using sos tool

## Parameters
* `cifmw_sosreport_nodes`: (List) List of nodes IPs for logs gathering. Defaults to `127.0.0.1`
* `cifmw_sosreport_nodes_sshkey`: (String) Path to the private SSH key to connect to nodes. Defaults to `~/.ssh/id_ecdsa`
* `cifmw_sosreport_tmp_dir`: (String) Location to store gathered logs. Defaults to `/tmp`
* `cifmw_sosreport_enable_plugins`: (List) Use this to enable a plugin that would otherwise not be run. Defaults to all plugins at the moment of creation.

## Examples
```
- name: Gather logs using sos tool
  ansible.builtin.include_role:
    role: sosreport
```
