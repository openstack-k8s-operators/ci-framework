# Create a PSI instance

## ⚠️ Deprecated
This is **deprecated** since it uses nested virtualization. Please refer to
[Validated Architecture reproducer](../reproducers/04-validated-architecture.md) documentation.

## Steps

1. **Download openrc.sh**

```
source openrc.sh
```

2. **Create VM**

Find a flavor satisfying [preferred requirements](../quickstart/01_requirements.md)

```
openstack flavor list -c Name -c RAM -c Disk -c VCPUs -f value | \
          awk '$2>32768 && $3>100 && $4>12'
```

Currently ci-framework is running on CentOS stream 9. To find a Centos stream 9 image

```
openstack image list | grep -i centos
```

To find less congested network

```
openstack network list --external -c Name -f value | \
  xargs -n1 openstack ip availability show -f json | \
  jq -r '.id as $network_id | .subnet_ip_availability[] | select(.ip_version == 4) | "\(.total_ips - .used_ips) \($network_id)"' | \
  sort -nr | head -n1 |  awk ' {{print  $NF}}' | \
  xargs -n1 openstack network show  -c name -f value
```

Finally, create a vm with valued you picked for the flavor/image/network/key-pair

```
openstack server create --flavor ocp4-compute-large --image CentOS-Stream-9-latest \
          --key-name rhos-jenkins --network provider_net_cci_6 \
          --security-group default e2e-edpm-deployment
```


3. **Obtain the instance IP**

Wait until

```
openstack server show e2e-edpm-deployment -f value -c status
```
command returns "ACTIVE" and reveal the instance IP

```
openstack server show e2e-edpm-deployment -f value -c addresses
```

4. **ssh into the instance**

```
ssh cloud-user@<obtained IP> -i ~/.ssh/rhos-jenkins
```

5. **Install ci-framework dependencies**

```
sudo yum -y groupinstall "Development Tools"
sudo yum -y install  qemu-img qemu-kvm libguestfs libguestfs-tools-c wget pip
python3 -m pip install --user ansible jmespath
```

6. **Continue with Quickstart**

Continue with ci-framework deployment as described by the [Virtualized environment setup section](./99_nested_virt.md).
