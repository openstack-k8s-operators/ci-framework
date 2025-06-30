# cifmw_snr_nhc
Apply Self Node Remediation and Node Health Check Custom Resources on OpenShift.

## Privilege escalation
None - all actions use the provided kubeconfig and require no additional host privileges.

## Parameters
* `cifmw_snr_nhc_kubeconfig`: (String) Path to the kubeconfig file.
* `cifmw_snr_nhc_kubeadmin_password_file`: (String) Path to the kubeadmin password file.
* `cifmw_snr_nhc_namespace`: (String) Namespace used for SNR and NHC resources.

## Examples
```yaml
- name: Configure SNR and NHC
  hosts: masters
  roles:
    - role: cifmw_snr_nhc
      cifmw_snr_nhc_kubeconfig: "/home/zuul/.kube/config"
      cifmw_snr_nhc_kubeadmin_password_file: "/home/zuul/.kube/kubeadmin-password"
      cifmw_snr_nhc_namespace: openshift-workload-availability
