# cifmw_snr_nhc

Apply Self Node Remediation and Node Health Check Custom Resources on OpenShift.

## Overview

This Ansible role automates the deployment and configuration of:
- **Self Node Remediation (SNR)** - Automatically remediates unhealthy nodes
- **Node Health Check (NHC)** - Monitors node health and triggers remediation

The role creates the necessary operators, subscriptions, and custom resources to enable automatic node remediation in OpenShift clusters.

## Privilege escalation

None - all actions use the provided kubeconfig and require no additional host privileges.

## Parameters

* `cifmw_snr_nhc_kubeconfig`: (String) Path to the kubeconfig file.
* `cifmw_snr_nhc_kubeadmin_password_file`: (String) Path to the kubeadmin password file.
* `cifmw_snr_nhc_namespace`: (String) Namespace used for SNR and NHC resources. Default: `openshift-workload-availability`
* `cifmw_snr_nhc_cleanup_before_install`: (Boolean) If true, removes existing SNR and NHC resources before installation. Default: `false`
* `cifmw_snr_nhc_cleanup_namespace`: (Boolean) If true, deletes the entire namespace before installation. Default: `false`

## Role Tasks

The role performs the following tasks in sequence:

1. **Cleanup (Optional)** - Removes existing resources if cleanup is enabled
2. **Create Namespace** - Creates the target namespace if it doesn't exist
3. **Create OperatorGroup** - Sets up the OperatorGroup for operator deployment
4. **Create SNR Subscription** - Deploys the Self Node Remediation operator
5. **Wait for SNR Deployment** - Waits for the SNR operator to be ready
6. **Create NHC Subscription** - Deploys the Node Health Check operator
7. **Wait for CSV** - Waits for the ClusterServiceVersion to be ready
8. **Create NHC CR** - Creates the NodeHealthCheck custom resource

## Examples

### Basic Usage

```yaml
- name: Configure SNR and NHC
  hosts: masters
  roles:
    - role: cifmw_snr_nhc
      cifmw_snr_nhc_kubeconfig: "/home/zuul/.kube/config"
      cifmw_snr_nhc_kubeadmin_password_file: "/home/zuul/.kube/kubeadmin-password"
      cifmw_snr_nhc_namespace: openshift-workload-availability
```

### Custom Namespace

```yaml
- name: Configure SNR and NHC in custom namespace
  hosts: masters
  roles:
    - role: cifmw_snr_nhc
      cifmw_snr_nhc_kubeconfig: "/path/to/kubeconfig"
      cifmw_snr_nhc_kubeadmin_password_file: "/path/to/password"
      cifmw_snr_nhc_namespace: custom-workload-namespace
```

### With Cleanup

```yaml
- name: Configure SNR and NHC with cleanup
  hosts: masters
  roles:
    - role: cifmw_snr_nhc
      cifmw_snr_nhc_kubeconfig: "/home/zuul/.kube/config"
      cifmw_snr_nhc_cleanup_before_install: true
      cifmw_snr_nhc_cleanup_namespace: false
```

### Complete Cleanup and Reinstall

```yaml
- name: Complete cleanup and reinstall SNR and NHC
  hosts: masters
  roles:
    - role: cifmw_snr_nhc
      cifmw_snr_nhc_kubeconfig: "/home/zuul/.kube/config"
      cifmw_snr_nhc_cleanup_before_install: true
      cifmw_snr_nhc_cleanup_namespace: true
```

## Testing

This role includes comprehensive testing using Molecule and pytest. Tests validate:
- Role syntax and structure
- Individual task execution
- Idempotency
- Error handling
- Integration with Kubernetes APIs

### Quick Test Run

```bash
# Install test dependencies
pip install --user -r molecule/requirements.txt
ansible-galaxy collection install -r molecule/default/requirements.yml --force

# Run all tests
molecule test

# Run specific test phases
molecule converge  # Execute role
molecule verify    # Run verification tests
```

### Development Testing

```bash
# Quick development cycle
molecule converge  # Apply changes
molecule verify    # Check results
molecule destroy   # Clean up
```

For detailed testing information, see [TESTING.md](TESTING.md).

## Requirements

### System Requirements

- Python 3.9+
- Ansible 2.14+
- Access to OpenShift/Kubernetes cluster

### Ansible Collections

- `kubernetes.core` (>=6.0.0)
- `ansible.posix`
- `community.general`

### Python Dependencies

- `kubernetes` (>=24.0.0)
- `pyyaml` (>=6.0.0)
- `jsonpatch` (>=1.32)

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `molecule test`
5. Submit a pull request

### Code Style

- Follow Ansible best practices
- Use descriptive task names
- Include proper error handling
- Test all changes with molecule

### Linting

```bash
# Run linting checks
ansible-lint tasks/main.yml
yamllint .
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure kubeconfig has proper permissions
2. **Namespace already exists**: Role handles existing namespaces gracefully
3. **Operator not ready**: Check cluster resources and connectivity

### Debug Mode

```bash
# Run with debug output
ansible-playbook -vvv your-playbook.yml
```

## License

This role is distributed under the terms of the Apache License 2.0.

## Support

For issues and questions:
- Check the [TESTING.md](TESTING.md) for testing guidance
- Review the troubleshooting section above
- Submit issues to the project repository
