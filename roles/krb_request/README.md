# krb_request

This role is a plain wrapper of the cifmw krb_request.
Specially meant to be used by zuul or similar tools
that cannot directly load our modules and/or plugins but
are able to load a role.

## Privilege escalation

Not required.

## Parameters

* `cifmw_krb_request_url`: (String) URL of the request. This variable is mandatory.
* `cifmw_krb_request_dest`: (String) Path where the request result should be dumped, if given.
* `cifmw_krb_request_dest_mode`: (String) Path where the request result should be dumped, if given.
* `cifmw_krb_verify_ssl`: (Boolean) Verify or not the SSL certificate of the server. Defaults to `true`.
* `cifmw_krb_request_method`: (String) HTTP method to use. Defaults to `GET`.

## Examples

```yaml
- name: Download the content from a remote URL
  vars:
    cifmw_krb_request_url: "https://example.com/downloads/1"
    cifmw_krb_request_dest: "~/download-output.bin"
    cifmw_krb_request_dest_mode: "0644"
  ansible.builtin.include_role:
    name: krb_request

- name: Debug output
  ansible.builtin.debug:
    msg: "{{ cifmw_krb_request_out }}"

```
