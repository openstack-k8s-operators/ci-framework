## Role: hive_cluster
This role can be used to claim clusters from a clusterpool. 
It assumes that oc_cli > 4 is installed and configured
It assumes cifw_hive_cluster_platform variable is defined. It switches which cluster claim tasks to include based on this variavle.

### Privilege escalation
If apply, please explain the privilege escalation done in this role.

### Parameters
* `cifw_hive_cluster_platform`: Which cloud/baremetal provider to use for hive cluster claims. Defaults to openstack
