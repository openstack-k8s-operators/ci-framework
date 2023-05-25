# Create a PSI instance

## Steps
1. **Download openrc.sh**

```
source openrc.sh
```

2. **Create VM**
Find a flavor satisfying preferred requirements

```
openstack flavor list -c Name -c RAM -c Disk -c VCPUs -f value | awk '$2>64 && $3>100 && $4>12'

```

Currently ci-framework is running on CentOS stream 9. To find a Centos stream 9 image

```
openstack image list | grep -i centos

```

To find less congested network

```
openstack network list -c ID -c Name -f value |   awk -F '|' '{match($0, /(provider_[^ ]+)/, arr); print arr[1]}' |  xargs -n1 openstack ip availability show -f json |  jq -r '(.subnet_ip_availability[0].total_ips-.subnet_ip_availability[0].used_ips),.id' |  sed 'N;s/\\n/ /' |  sort -nr | head -n1 |  awk ' {{print  $NF}}' |  xargs -n1 openstack network show  -c name -f value
```

Finally create a vm with valued you picked for the falvor/image/network/key-pair

```
openstack server create --flavor ocp4-compute-large --image CentOS-Stream-9-latest --key-name rhos-jenkins --network provider_net_cci_6 --security-group default e2e-edpm-deployment
```


3. **Obtain the instance IP**

Wait until

```
openstack server show e2e-edpm-deployment-1 -f value -c status
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
python3 -m pip install --user ansible jmespath beautifulsoup4

```

6. **Continue with Quickstart**

Continue with ci-framework deployment as described by the [Quickstart section](https://github.com/openstack-k8s-operators/ci-framework/wiki/Quickstart).
