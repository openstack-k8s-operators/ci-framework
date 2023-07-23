# CI Framework Create Admin

A role to create an admin user who can SSH into EDPM nodes. Used to
in CI framework to create an account for cephadm but can be used for
any account.

## Privilege escalation

Requires root in order to create user on target host(s). Private key
may optionally be provided so that the admin users can SSH into EDPM
nodes as eachother. E.g. ceph-admin@host-0 can `ssh ceph-admin@host-1`.

## Paramters

| Name              | Default Value       | Description           |
|-------------------|---------------------|-----------------------|
| `cifmw_admin_user` | `cifmw-admin`     | Name of user to create|
| `cifmw_admin_pubkey` | `[undefined]`     | Public key for authorization|
| `cifmw_admin_prikey` | `[undefined]`     | Private key for authorization|
| `cifmw_admin_distribute_private_key` | `false`     | Boolean to distribute private key|

## Examples

```
- hosts: all
  gather_facts: false
  become: true
  pre_tasks:
    - name: Get local private key
      slurp:
        src: "{{ hostvars['localhost']['private_key'] }}"
      register: private_key_get
      delegate_to: localhost
      no_log: true
    - name: Get local public key
      slurp:
        src: "{{ hostvars['localhost']['public_key'] }}"
      register: public_key_get
      delegate_to: localhost
  roles:
    - role: cifmw_create_admin
      cifmw_admin_user: "{{ cifmw_admin_user }}"
      cifmw_admin_pubkey: "{{ public_key_get['content'] | b64decode }}"
      cifmw_admin_prikey: "{{ private_key_get['content'] | b64decode }}"
      cifmw_admin_distribute_private_key: true
      no_log: true
```
