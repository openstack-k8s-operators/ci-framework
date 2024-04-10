# Baremetal hosts information

In order to make the framework aware of the existence of external
baremetal nodes that should be taken into consideration the user should
provide details about those nodes.

~~~{tip}
For fully virtualized environments the framework automatically
generates these details for the user.
~~~

## Structure

The BM hosts details are stored in the `cifmw_baremetal_hosts` variable that,
if not passed to the `ansible-playbook` command, is fetched from
`~/ci-framework-data/parameters/baremetal-info.yml`.
The structure of that variable is the following:

```yaml
cifmw_baremetal_hosts:
  compute-0:
    # Mandatory: (string) The BMC password of the host
    password: password
    # Mandatory: (string) The BMC username of the host
    username: user
    # Mandatory: (string) The BMC connection URL
    #   The format should be: <proto>://host:port
    connection: idrac://host-bmc.example.local
    # Mandatory: (string) The type of boot of the host
    #  One of: UEFI, UEFISecureBoot, or legacy
    boot_mode: UEFI
    # Optional: (list) Of dicts with the mac address of each
    #    network interface.
    nics:
      - mac: "aa:bb:cc:dd:ee:ff"
        # The provisioning network nic is used for Metal3 BMH
        #   bootMACAddress field rendering.
        network: provisioning
    # Optional: (string) The state of the machine
    status: running
    # Optional: (string) The storage device to use for provisioning.
    root_device_hint: /dev/sda
    # Optional: (dict) Nmstate to apply to the host when provisioned
    nmstate:
      # interfaces: # Sample nmstate state snippet
      #   - name: enp6s0f0.161

  compute-1:
    # Another BM host
```
