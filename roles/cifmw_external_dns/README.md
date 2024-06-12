# cifmw_external_dns

If an openstack-k8s-operators pod needs to securely access
an HTTPS endpoint which is hosted outside of k8s, then this
role can create a DNS domain and certificate for that endpoint.

The `cifmw_external_dns` role creates a `DNSData` domain like
`myservice.local` so that pods can map hostnames to IPs for
services which are not hosted on k8s. It then configures
[DNS Forwarding](https://docs.openshift.com/container-platform/latest/networking/dns-operator.html#nw-dns-forward_dns-operator)
for that domain with the CoreDNS service.

It also creates a `Certificate`, with the OpenStack public root
CA, with subject alternative names from the `DNSData` domain.
Assuming the external endpoint is hosted on EDPM nodes, a copy
of the certificate and key are placed in paths on the EDPM nodes.

This role can be used to help configure Ceph RGW to mimic Swift
object storage. A URL like `https://rgw-external.ceph.local:8080`
can be a registered Keystone endpoint and OpenStack clients running
on k8s can resolve the host and trust the certificate.

## Privilege escalation

Requires `{{ cifmw_openshift_kubeconfig }}` in order to create k8s CRs
of kind `Certificate` which use the existing OpenStack root CA. The
same credential is also required to create a a CR of kind `DNSData`
and configure DNS Forwarding.

Uses become when necessary to install certificates on EDPM nodes in
`/etc/pki/tls`.

## Parameters

* `cifmw_external_dns_domain`: The DNS domain created by this
  role. E.g. `example.com`. This parameter must be set or the role will
  fail. (default: `""`)

* `cifmw_external_dns_name`: Name of the k8s resource of kind
  `DNSData`. E.g. `example-com-dns`. (default: `"{{
  cifmw_external_dns_domain | regex_replace('\\.','-')}}-dns"`)

* `cifmw_external_dns_labels`: Dictionary of labels for the
  metadata section of the k8s manifest of kind `DNSData`
  (default: `{}`)

* `cifmw_external_dns_cert_name`: Name of the k8s resource of kind
  `Certificate`. E.g. `example-com-cert`. (default: `"{{
  cifmw_external_dns_domain | regex_replace('\\.','-')}}-cert"`)

* `cifmw_external_dns_ns`:  The k8s namespace where the `Certificate`
  and `DNSData` objects will be created (default: `openstack`)

* `cifmw_external_dns_check_mode`: Create k8s manifests in the
  `cifmw_external_dns_manifests_dir` directory but do not apply them.
  (default: `false`)

* `cifmw_external_dns_certificate_dir`: The directory where the
  certificate will be copied to on the Ansible hosts (default:
  `/etc/pki/tls/`). After this role runs, `/etc/pki/tls/` should
  contain files like `example.com.crt` and `example.com.key` which
  can then be used to configure an HTTPS service hosted on the
  Ansible target host.

* `cifmw_external_dns_certificate`: The absolute path of the
  certificate (default `"{{ cifmw_external_dns_certificate_dir ~
  cifmw_external_dns_domain }}.crt"`)

* `cifmw_external_dns_key`: The absolute path of the private key of
  the certificate (default `"{{ cifmw_external_dns_certificate_dir ~
  cifmw_external_dns_domain }}.key"`)

* `cifmw_external_dns_basedir`: Installation base directory. Defaults to
  `cifmw_basedir` which defaults to `~/ci-framework-data`.

* `cifmw_external_dns_manifests_dir`: Directory where OCP manifests for
   for cifmw_external_dns role will be placed. Defaults to
  `"{{ cifmw_manifests | default(cifmw_cls_basedir ~
  '/artifacts/manifests') }}/cifmw_external_dns"`

* `cifmw_external_dns_cert_issuer_ref`: dictionary passed to `issuerRef`
  inside k8s manifest of kind `Certificate` for the certificate. (Default:
  `{"group": "cert-manager.io", "kind": "Issuer", "name": rootca-public}`).
  By using the existing public root CA for OpenStack (`rootca-public`)
  OpenStack clients in pods will trust the HTTPS connection.

* `cifmw_external_dns_cert_issuer_duration`: How long the certificate
  will be valid (default: `43800h0m0s`)

* `cifmw_external_dns_retries`: Ansible `retries` passed to tasks
  which wait for `kubernetes.core.k8s_info` when applying manifests
  (default `60`)

* `cifmw_external_dns_delay`: Ansible `delay` passed to tasks
  which wait for `kubernetes.core.k8s_info` when applying manifests
  (default `10`)

* `cifmw_external_dns_clean_cert`: When `tasks_from: cleanup.yml`
  is used, the DNS files and k8s objects created by this role will
  always be removed. However, the certificate DNS files and k8s
  objects will only be removed if this boolean is `true` (default:
  `true`)

* `cifmw_external_dns_masq_cluster_ip`: The IP address of the
  OpenShift DNS service in the `cifmw_external_dns_ns` namespace. If
  empty, this value will be looked up through a call like `oc -n
  openstack get svc dnsmasq-dns -o jsonpath='{.spec.clusterIP}'`
  (default: `""`)

* `cifmw_external_dns_vip_ext`: Dictionary mapping the IP address
  (or VIP) of the service to a hostname for which a DNS entry will
  be created. The IP address should point to a HTTPS service end
  point which will be configured independently of this role.
  Some OpenStack services have internal and external endpoints
  and this variable is intended for external endpoints (so `_ext` is
  in the name). The hostname will be added as a subject alternative
  name of the certificate. (default: `{}`)

* `cifmw_external_dns_vip_int`: Dictionary mapping the IP address
  (or VIP) of the service to a hostname for which a DNS entry will
  be created. The IP address should point to a HTTPS service end
  point which will be configured independently of this role.
  Some OpenStack services have internal and external endpoints and
  this variable is intended for internal endpoints (so `_int` is in
  the name). The hostname will be added as a subject alternative name
  of the certificate. (default: `{}`)

* `cifmw_external_dns_extra_subj_alt_names`: Dictionary mapping IP
  addresses to hostnames. The IP addresses should point to HTTPS
  service end points which will be configured independently of this
  role. Each hostname should end with the `cifmw_external_dns_domain`
  value. Each hostname will be added as a subject alternative name of
  the certificate. (default: `{}`)

One of `cifmw_external_dns_vip_ext`, `cifmw_external_dns_vip_int` or
`cifmw_external_dns_extra_subj_alt_names` must be non-empty or the
role will fail. I.e. if there is no DNS mapping defined, then it is
pointless to create a DNS zone.

## Examples

The following playbook calls the `cifmw_external_dns`. Note that it
has the `cifmw_openshift_kubeconfig` variable which is required in
order to apply k8s manifests against an existing k8s cluster.

```yaml
- name: Playbook to test cifmw_external_dns role
  gather_facts: false
  hosts: computes[0]
  vars:
    cifmw_openshift_kubeconfig: "~/.kube/config"
    cifmw_external_dns_domain: example.com
    cifmw_external_dns_vip_ext:
      192.168.122.2: "external-endpoint-vip.{{ cifmw_external_dns_domain }}"
    cifmw_external_dns_vip_int:
      192.168.122.3: "internal-endpoint-vip.{{ cifmw_external_dns_domain }}"
    cifmw_external_dns_extra_subj_alt_names:
      192.168.122.100: "host0.{{ cifmw_external_dns_domain }}"
      192.168.122.101: "host1.{{ cifmw_external_dns_domain }}"
      192.168.122.102: "host2.{{ cifmw_external_dns_domain }}"
  tasks:
    - name: Create DNS domain and certificate
      ansible.builtin.include_role:
        name: cifmw_external_dns
```

After the above playbook runs the following changes should be
observable.

- `example.com.crt` and `example.com.key` will be on the first node
  the ansible hosts group called `computes` in the directory
  `/etc/pki/tls/`.

- On the system where the playbook was run the directory
  `~/ci-framework-data/artifacts/manifests/cifmw_external_dns/`
  should contain manifests of kind `Certificate` and `DNSData`.

- `oc get cert example-com-cert` should show that a certificate was created

- `oc get dnsdata example-com-dns` should show that a DNS zone was created

- A [DNS Forward](https://docs.openshift.com/container-platform/latest/networking/dns-operator.html#nw-dns-forward_dns-operator)
  will have been created for the `example.com` zone.
  ```
  $ oc get -n openshift-dns dns.operator/default -o yaml | grep example -B 5
  servers:
  - forwardPlugin:
      policy: Random
      upstreams:
      - 172.30.248.195:53
    name: example-com-dns
    zones:
    - example.com
  $
  ```

- Within the `openstackclient` pod it should be possible to resolve
  `external-endpoint-vip.example.com` and `internal-endpoint-vip.example.com`
  to their respective IPs (`192.168.122.2` and `192.168.122.3`)

- After the HTTPS service hosted on the IP of
  `external-endpoint-vip.example.com` has been configured with the
  certificates in `cifmw_external_dns_certificate` and the key in
  `cifmw_external_dns_key`, the `openstackclient` pod should be
  able to `curl https://external-endpoint-vip.example.com` and not
  get an `SSLCertVerificationError` (the same should be the case
  for `internal-endpoint-vip.example.com` provided the
  `openstackclient` can reach the network).

## Testing

The `test_dns.yml` tasks file within the role may be used to test the
role.

The role needs to be run on k8s cluster which has an openstackclient
pod (which can be set up by ci-framework) and an endpoint must exist
at an IP address that the pod can ping.

The following playbook can be used to confirm that the openstackclient
pod can use the DNS configured by the `cifmw_external_dns` role to
ping a host by DNS name.

```yaml
- name: Playbook to clean up after the cifmw_external_dns role
  gather_facts: false
  hosts: computes[0]
  vars:
    cifmw_openshift_kubeconfig: "~/.kube/config"
    cifmw_external_dns_domain: example.com
    cifmw_external_dns_vip_ext:
      192.168.122.2: "external-endpoint-vip.{{ cifmw_external_dns_domain }}"
  tasks:
    - name: Test DNS Domain
      ansible.builtin.include_role:
        name: cifmw_external_dns
        tasks_from: test_dns.yml
```
In the correct environment the above playbook should have output like this:
```
TASK [cifmw_external_dns : Try to ping hostnames from inside openstackclient pod namespace={{ cifmw_external_dns_ns }}, kubeconfig={{ cifmw_openshift_kubeconfig }}, api_key={{ cifmw_openshift_token | default(omit) }}, context={{ cifmw_openshift_context | default(omit) }}, pod=openstackclient, command=ping -c 1 {{ item.value }}] ***
Saturday 29 June 2024  12:54:50 -0400 (0:00:00.041)       0:00:00.251 *********
changed: [compute-0 -> localhost] => (item=rgw-external.ceph.local)

TASK [cifmw_external_dns : Show results of ping tests msg={{ item.stdout | regex_search('(\d+ packets transmitted, \d+ received, \d+% packet loss, time \d+ms)') }}] ***
Saturday 29 June 2024  12:54:57 -0400 (0:00:06.931)       0:00:07.183 *********
ok: [compute-0] => (item=ping -c 1 rgw-external.ceph.local) =>
  msg: 1 packets transmitted, 1 received, 0% packet loss, time 0ms
```

## Cleaning

The `cleanup.yml` tasks file within the role may be used to undo the
changes made by the role.

The following playbook may be used to delete the certificate file and
its private key file from the target hosts. It will also remove the
certificate from k8s. The DNSData object and forward will also be
removed.

```yaml
- name: Playbook to clean up after the cifmw_external_dns role
  gather_facts: false
  hosts: computes[0]
  vars:
    cifmw_openshift_kubeconfig: "~/.kube/config"
    cifmw_external_dns_domain: example.com
    cifmw_external_dns_vip_ext:
      192.168.122.2: "external-endpoint-vip.{{ cifmw_external_dns_domain }}"
  tasks:
    - name: Delete certificate, DNS domain and DNS forward
      ansible.builtin.include_role:
        name: cifmw_external_dns
        tasks_from: cleanup.yml
```
