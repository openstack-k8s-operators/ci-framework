# Quick Start: Update Packages in Containers

This is a quick reference guide for updating RPM packages in OpenStack containers.

## TL;DR - Just Run This

```bash
# Update OVN package (replicates original bash script)
./scripts/update_container_packages.sh \
  --package ovn24.03 \
  --repo http://rhos-qe-mirror.lab.eng.tlv2.redhat.com/rhel-9/nightly/updates/FDP/latest-FDP-9-RHEL-9/compose/Server/x86_64/os/
```

## Common Commands

### 1. Update OVN Package (Predefined Config)
```bash
./scripts/update_container_packages.sh -v ovn_update.yml
```

### 2. Update Neutron Package (Predefined Config)
```bash
./scripts/update_container_packages.sh -v neutron_update.yml
```

### 3. Update Custom Package
```bash
./scripts/update_container_packages.sh \
  -p your-package-name \
  -r http://your-repo-url.com/
```

### 4. Dry Run (See What Would Happen)
```bash
./scripts/update_container_packages.sh \
  -p ovn24.03 \
  -r http://example.com/repo/ \
  --dry-run
```

### 5. Direct Ansible Playbook
```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/
```

## What It Does

1. ✅ Authenticates with OpenShift registry
2. ✅ Gets all container images from OpenStackVersion CR
3. ✅ Checks each image for the target package
4. ✅ Builds new images with updated package
5. ✅ Pushes to OpenShift registry
6. ✅ Updates OpenStackVersion CR
7. ✅ Shows summary report

## Verify Results

```bash
# Check updated CR
oc get openstackversion controlplane -n openstack -o yaml | grep customContainerImages -A 10

# Watch pods restart
oc get pods -n openstack -w

# Verify package in container
oc exec -it <pod-name> -n openstack -- rpm -q ovn24.03
```

## Files Created

```
ci-framework/
├── playbooks/
│   ├── update_container_packages.yml        # Main playbook
│   ├── UPDATE_CONTAINER_PACKAGES.md         # Full documentation
│   └── vars/
│       ├── ovn_update.yml                   # OVN config
│       └── neutron_update.yml               # Neutron config
├── scripts/
│   └── update_container_packages.sh         # Helper script
└── roles/
    └── update_package_in_containers/        # The role
        ├── README.md                        # Role docs
        ├── USAGE.md                         # Usage guide
        ├── defaults/main.yml                # Default vars
        ├── tasks/                           # All tasks
        ├── templates/                       # Dockerfile & repo
        ├── molecule/                        # Tests
        └── examples/                        # Examples
```

## Help

```bash
# Script help
./scripts/update_container_packages.sh --help

# Full documentation
cat playbooks/UPDATE_CONTAINER_PACKAGES.md
cat roles/update_package_in_containers/README.md
```

## Prerequisites

- ✅ OpenShift CLI (`oc`) installed
- ✅ Podman installed
- ✅ Ansible 2.15+
- ✅ Permissions to manage OpenStack namespace

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "oc command not found" | Install OpenShift CLI |
| "Required variables missing" | Provide `-p` and `-r` flags |
| "Authentication failed" | Check `oc login` status |
| "No images found" | Verify OpenStackVersion CR exists |

---

**For detailed documentation, see:**
- [playbooks/UPDATE_CONTAINER_PACKAGES.md](playbooks/UPDATE_CONTAINER_PACKAGES.md)
- [roles/update_package_in_containers/README.md](roles/update_package_in_containers/README.md)
- [roles/update_package_in_containers/USAGE.md](roles/update_package_in_containers/USAGE.md)
