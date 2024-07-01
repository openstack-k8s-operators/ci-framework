# dnsmasq

Create a standalone dnsmasq service and manage its configuration.

The main usage of this role is to expose a DHCP service for libvirt
networks, to properly support fixed IPv4 *and* IPv6 (the latter isn't
supported in libvirt).

## Privilege escalation

- Package installation
- Writing in protected locations `/etc/systemd/system`, `/etc/cifmw-dnsmasq.conf`, `/etc/cifmw-dnsmasq.d`

## Common Parameters

* `cifmw_dnsmasq_basedir`: (String) Configuration directory location. Defaults to `/etc/cifmw-dnsmasq.d`.
* `cifmw_dnsmasq_enable_dns`: (Bool) Toggle to enable DNS features of dnsmasq. Defaults to `false`.
* `cifmw_dnsmasq_exclude_lo`: (Bool) Toggle to disable binding on loopback interface to avoid conflicts. Defaults to `false`.
* `cifmw_dnsmasq_dns_config_file`: (String) DNS related settings configuration file path. Defaults to `{{ cifmw_dnsmasq_basedir }}/dns.conf`.
* `cifmw_dnsmasq_listener_config_file`: (String) listener related settings configuration file path. Defaults to `{{ cifmw_dnsmasq_basedir }}/listener.conf`.
* `cifmw_dnsmasq_raw_config`: (String) Raw configure options for dnsmasq. Should be passed as a (multiline) string. Defaults to `""`.

### New network parameters

* `cifmw_dnsmasq_network_name`: (String) Network name.
* `cifmw_dnsmasq_network_state`: (String) Network status. Must be either `present` or `absent`.
* `cifmw_dnsmasq_network_definition`: (Dict) Mapping representing the network definition.
* `cifmw_dnsmasq_network_definition.ranges`: (List[mapping]) List of ranges associated to the network.
* `cifmw_dnsmasq_forwarders`: (List) List of upstream DNS servers used as forwarders. Defaults to `[]`
* `cifmw_dnsmasq_interfaces`: (List) List of interfaces on which dnsmasq should be enabled. Defaults to `[]`.
* `cifmw_dnsmasq_listen_addresses`: (List) List of IP addresses on which dnsmasq should be enabled. Defaults to `[]`.
* `cifmw_dnsmasq_addresses`: (List) Specify a list of IP addresses to return for any host in the given domains. Defaults to `[]`.

#### Ranges mapping

* `label`: (String) Network label ("tag" in dnsmasq manual).
* `domain`: (String) domain name associated to the dhcp range.
* `start_v4`: (String) IPv4 starting IP.
* `start_v6`: (String) IPv6 starting IP.
* `prefix_length_v4`: (Int) IPv4 prefix length. Defaults to `24`.
* `prefix_length_v6`: (Int) IPv6 prefix length. Defaults to `64`.
* `ttl`: (String) Subnet TTL. Defaults to `1h`.
* `options`: (List) List of options associated to the network.
* `options_force`: (List) List of forced options associated to the network.

#### Examples

```YAML
    - name: Create network
      vars:
        cifmw_dnsmasq_network_name: starwars
        cifmw_dnsmasq_network_state: present
        cifmw_dnsmasq_network_listen_dns:
          - 192.168.199.9
          - ff99:abcd::9
          - ''  # empty string is supported as "no entry"
        cifmw_dnsmasq_network_definition:
          ranges:
            - label: ian
              start_v4: 192.168.254.10
              start_v6: "2345:0425:2CA1::0567:5673:23b5"
              options:
                - "3,192.168.254.1"
                - "option6:ntp-server,[1234::56]"
              options_force:
                - "vendor:PXEClient,1,0.0.0.0"
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_network.yml
```

### Host record parameters

* `cifmw_dnsmasq_host_record`: (List[mapping]) List of host records to add.

#### Host record mapping

* `state`: (String) Host record status. Must be either `present` or `absent`.
* `ips`: (List[string]) List of IP addresses for the host record.
* `names`: (List[string]) List of names for the host record.

#### Examples

```yaml
- name: Add host-records
  vars:
    cifmw_dnsmasq_host_record:
      - state: present
        ips:
          - 192.0.2.3
          - '2001:db8::3'
        names:
          - enterprise.staralliance.startrek.lan
      - state: present
        ips:
          - 192.0.2.4
          - '2001:db8::4'
        names:
          - voyager.staralliance.startrek.lan
  ansible.builtin.include_role:
    name: dnsmasq
    tasks_from: manage_host_record.yml
```

### New forwarder parameters

* `cifmw_dnsmasq_forwarder`: (List[mapping]) List of forwarders, server address and domains the forwarder should used for.

#### Forwarder mapping

* `state`: (String) Forwarder status. Must be either `present` or `absent`.
* `server`: (String) IP address of the dns server to forward lookups to.
* `domains`: (List[string]) List of domains to use this server for.

#### Examples

```yaml
- name: Add forwarder
  vars:
    cifmw_dnsmasq_forwarder:
      - state: present
        server: 192.0.2.10
        domains:
         - theborg.startrek.lab
         - staralliance.startrek.lab
  ansible.builtin.include_role:
    name: dnsmasq
    tasks_from: manage_forwarder.yml
```

### New address parameters

* `cifmw_dnsmasq_address`: (List[mapping]) List for address to return for any host in the given domains.

#### Address mapping

* `state`: (String) Address status. Must be either `present` or `absent`.
* `ipaddr`: (String) IP address to return for hosts in the given domains.
* `domains`: (List[string]) List of domains.

#### Examples

```yaml
    - name: Add addresses
      vars:
        cifmw_dnsmasq_address:
          - state: present
            ipaddr: 192.0.2.20
            domains:
              - apps.ocp.theborg.startrek.lab
          - state: present
            ipaddr: 192.0.2.30
            domains:
              - apps.ocp.staralliance.startrek.lab
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_address.yml
```

### New host parameters

* `cifmw_dnsmasq_host_network`: (String) Existing network name.
* `cifmw_dnsmasq_host_state`: (String) Host status. Must be either `present` or `absent`.
* `cifmw_dnsmasq_host_mac`: (String) Host MAC address.
* `cifmw_dnsmasq_host_ips`: (List) Host IP addressees.
* `cifmw_dnsmasq_host_name`: (String) Host name. Optional.

#### Examples

```yaml
    - name: Inject some node in starwars network
      vars:
        cifmw_dnsmasq_host_network: starwars
        cifmw_dnsmasq_host_state: present
        cifmw_dnsmasq_host_mac: "0a:19:02:f8:4c:a7"
        cifmw_dnsmasq_host_ips:
          - "2345:0425:2CA1::0567:5673:cafe"
          - "192.168.254.11"
        cifmw_dnsmasq_host_name: r2d2
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_host.yml
```
