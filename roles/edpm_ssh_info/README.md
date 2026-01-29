# edpm_ssh_info

This Ansible role retrieves EDPM (External Data Plane Management) SSH connectivity information.

## Description

The role performs the following tasks:

1. Queries OpenShift for OpenStackDataPlaneNodeSet resources
2. Retrieves the dataplane SSH private key from OpenShift secrets (if not already present locally)
3. Extracts compute node names and their control plane IP addresses
4. Returns all information in a structured format for use in subsequent plays

## Requirements

- Ansible collection `kubernetes.core` must be installed
- Valid kubeconfig file at `{{ ansible_user_dir }}/.kube/config`
- Access to the OpenShift/Kubernetes namespace containing EDPM resources
- Appropriate permissions to read OpenStackDataPlaneNodeSet resources and secrets

## Variables

### Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `edpm_ssh_info_openstack_namespace` | `openstack` | OpenShift namespace where EDPM resources are deployed |
| `edpm_ssh_info_kubeconfig_path` | `{{ ansible_user_dir }}/.kube/config` | Path to kubeconfig file |
| `edpm_ssh_info_oc_auth_required` | `true` | Whether to authenticate to OpenShift cluster before querying resources |
| `edpm_ssh_info_oc_username` | `kubeadmin` | OpenShift username for authentication |
| `edpm_ssh_info_oc_password_file` | `{{ ansible_user_dir }}/.kube/kubeadmin-password` | Path to file containing OpenShift password |
| `edpm_ssh_info_oc_api_url` | `https://api.ocp.openstack.lab:6443/` | OpenShift API URL |
| `edpm_ssh_info_node_prefix` | `compute-` | Node name prefix to filter (e.g., 'compute-', 'networker-') |
| `edpm_ssh_info_ssh_secret_name` | `dataplane-ansible-ssh-private-key-secret` | Name of the secret containing SSH private key |
| `edpm_ssh_info_ssh_key_path` | `{{ ansible_user_dir }}/.ssh/compute_id` | Destination path for SSH private key |

## Output

### Facts Set

The role sets a fact named `edpm_ssh_info` with the following structure:

```yaml
edpm_ssh_info:
  ssh_key_path: "/path/to/ssh/key"
  nodes:
    - name: compute-0
      host: 192.168.122.100
    - name: compute-1
      host: 192.168.122.101
```

**Fields:**
- `ssh_key_path` (string): Path to the SSH private key file
- `nodes` (list): List of discovered dataplane nodes
  - `name` (string): Node name (e.g., "compute-0")
  - `host` (string): Control plane IP address

## Usage

### Basic Usage (with defaults)

```yaml
- name: Get EDPM SSH information
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Retrieve dataplane info
      ansible.builtin.include_role:
        name: edpm_ssh_info

    - name: Display discovered nodes
      ansible.builtin.debug:
        msg: "Found {{ edpm_ssh_info.nodes | length }} nodes"
```

### Custom Configuration

```yaml
- name: Get EDPM SSH information
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Retrieve dataplane info
      ansible.builtin.include_role:
        name: edpm_ssh_info
      vars:
        edpm_ssh_info_openstack_namespace: my-openstack
        edpm_ssh_info_node_prefix: networker-
        edpm_ssh_info_ssh_key_path: /custom/path/to/key
```

### Custom Password File

```yaml
- name: Get EDPM SSH information with custom password file
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Retrieve dataplane info
      ansible.builtin.include_role:
        name: edpm_ssh_info
      vars:
        edpm_ssh_info_oc_password_file: /custom/path/to/password-file
```

### Using with Dynamic Inventory

```yaml
- name: Get EDPM SSH information
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Retrieve dataplane info
      ansible.builtin.include_role:
        name: edpm_ssh_info

- name: Add nodes to inventory
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Add compute nodes to dynamic inventory
      ansible.builtin.add_host:
        name: "{{ item.name }}"
        ansible_host: "{{ item.host }}"
        ansible_ssh_private_key_file: "{{ edpm_ssh_info.ssh_key_path }}"
        groups:
          - compute_nodes
      loop: "{{ edpm_ssh_info.nodes }}"

- name: Configure compute nodes
  hosts: compute_nodes
  tasks:
    - name: Run configuration tasks
      ansible.builtin.debug:
        msg: "Configuring {{ inventory_hostname }}"
```

## Notes

- If your kubeconfig is already authenticated, set `edpm_ssh_info_oc_auth_required: false` to skip the `oc login` step
- The OpenShift password is read from the file specified in `edpm_ssh_info_oc_password_file` (defaults to `~/.kube/kubeadmin-password`)
- You can set a custom password file path via `edpm_ssh_info_oc_password_file` if your password is stored elsewhere
- The role will fail if no OpenStackDataPlaneNodeSet resources are found
- SSH key retrieval is skipped if the key file already exists at the destination path
- SSH key is saved with `0600` permissions for security
- The role is idempotent - it can be run multiple times safely
- Only nodes matching the specified prefix and having a control plane IP are included
