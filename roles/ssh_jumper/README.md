# ssh_jumper
Configure SSH client configuration host specifications.

## Parameters
* `cifmw_ssh_jumper_config: (List) SSH client host configuration.

### `cifmw_ssh_jumper_config` parameters

Required:
* `hostname`: (String) Hostname (or IP address).

Optional:
* `target`: (String) Inventory host target to configure. Defaults to: `omit`.
* `ssh_dir`: (String) SSH directory. Defaults to: `{{ ansible_user_dir }}/.ssh`.
* `patterns`: (List) Patterns to match the host.
* `user`: (String) Specifies the user to log in as. Defaults to: `zuul`.
* `proxy_host`: (String) SSH jump proxy hostname.
* `proxy_user`: (String) SSH jump proxy username. Defaults to: `zuul`.
* `identity_file`: (String) File from which identity is read.
* `strict_host_key_checking`: (String) If set to `yes` host keys are checked. Defaults to: `no`.
* `user_known_hosts_file`: (String)' File to use for user host key database. Defaults to: `/dev/null`.

#### cleanup.yml dedicated parameter

* `cifmw_ssh_jumper_target`: (String) Target host to run the cleanup commands. Defaults to `omit`.
* `cifmw_ssh_jumper_config_dir`: (String) .ssh path on the target host. Defaults to `{{ cifmw_ssh_jumper_config.ssh_dir }}`.

## Examples

```yaml
- name: "Add SSH jumper entries"
  vars:
    cifmw_ssh_jumper_config:
      # Will delegate_to: localhost to push the configuration
      - target: localhost
        ssh_dir: "/home/zuul/.ssh"
        hostname: '192.168.250.10'
        proxy_host: "proxy.example.com"
        proxy_user: zuul
        patterns:
          - test
          - test.node
      # Will push the configuration on the remote host
      - ssh_dir: "/home/zuul/.ssh"
        hostname: '192.168.250.10'
        identity_file: "/home/zuul/.ssh/id_foo"
        patterns:
          - test
          - test.node
  ansible.builtin.include_role:
    name: ssh_jumper
```
