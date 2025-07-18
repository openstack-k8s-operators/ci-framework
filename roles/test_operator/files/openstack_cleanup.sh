#!/bin/bash
set -euo pipefail

log() {
  echo "[+] $1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || { echo "Required command '$1' not found. Install it and retry."; exit 1; }
}

# require_command jq

# Cleanup flavors
flavors=$(openstack flavor list -c ID -f value)
if [[ -n "$flavors" ]]; then
  log "Deleting flavors..."
  echo "$flavors" | tee /tmp/flavors_deleted.txt | xargs openstack flavor delete
fi

# Cleanup servers
servers=$(openstack server list --all-projects -c ID -f value)
if [[ -n "$servers" ]]; then
  log "Deleting servers..."
  echo "$servers" | tee /tmp/servers_deleted.txt | xargs openstack server delete
fi

# Cleanup images
: << 'END_COMMENT'
images=$(openstack image list -c ID -f value)
if [[ -n "$images" ]]; then
  log "Deleting images..."
  echo "$images" | tee /tmp/images_deleted.txt | xargs openstack image delete
fi
END_COMMENT

# Cleanup volumes
volumes=$(openstack volume list --all-projects -c ID -f value)
if [[ -n "$volumes" ]]; then
  log "Deleting volumes..."
  echo "$volumes" | tee /tmp/volumes_deleted.txt | xargs openstack volume delete
fi

# Cleanup floating IPs
fips=$(openstack floating ip list -c ID -f value)
if [[ -n "$fips" ]]; then
  log "Deleting floating IPs..."
  echo "$fips" | tee /tmp/fips_deleted.txt | xargs openstack floating ip delete
fi

# Cleanup network trunks
trunks=$(openstack network trunk list -c ID -f value)
if [[ -n "$trunks" ]]; then
  log "Deleting network trunks..."
  echo "$trunks" | tee /tmp/trunks_deleted.txt | xargs openstack network trunk delete
fi

# Cleanup routers and interfaces
routers=$(openstack router list -f value -c ID)
if [[ -n "$routers" ]]; then
  log "Removing subnets from routers and deleting routers..."
  for router in $routers; do
    subnets=$(openstack subnet list -c ID -f value)
    for subnet in $subnets; do
      if openstack router show "$router" -f yaml | grep -A 10 interfaces_info | grep -q "$subnet"; then
        openstack router remove subnet "$router" "$subnet" && echo "$router <- $subnet" >> /tmp/router_subnets_removed.txt
      else
        echo "$router does not have subnet $subnet attached — skipping" >> /tmp/router_subnets_skipped.txt
      fi
    done
    openstack router delete "$router" && echo "$router" >> /tmp/routers_deleted.txt
  done
fi

# Cleanup ports
ports=$(openstack port list -c ID -f value)
if [[ -n "$ports" ]]; then
  log "Deleting ports..."
  echo "$ports" | tee /tmp/ports_deleted.txt | xargs openstack port delete
fi

# Cleanup networks
networks=$(openstack network list -c ID -f value)
if [[ -n "$networks" ]]; then
  log "Deleting networks..."
  echo "$networks" | tee /tmp/networks_deleted.txt | xargs openstack network delete
fi

# Cleanup security groups
sec_groups=$(openstack security group list -c ID -f value)
if [[ -n "$sec_groups" ]]; then
  log "Deleting security groups..."
  echo "$sec_groups" | tee /tmp/secgroups_deleted.txt | xargs openstack security group delete
fi

# Cleanup keypair
if openstack keypair show test_keypair &>/dev/null; then
  log "Deleting keypair 'test_keypair'..."
  openstack keypair delete test_keypair && echo "test_keypair" >> /tmp/keypair_deleted.txt
fi

# Cleanup role
if openstack role show heat_stack_owner &>/dev/null; then
  log "Deleting role 'heat_stack_owner'..."
  openstack role delete heat_stack_owner && echo "heat_stack_owner" >> /tmp/roles_deleted.txt
fi

# Cleanup aggregates
aggregates=$(openstack aggregate list -f value -c ID)
for a in $aggregates; do
  hosts=$(openstack aggregate show "$a" -c hosts -f value | tr -d "[]'" | tr ',' '\n')
  for h in $hosts; do
    openstack aggregate remove host "$a" "$h" && echo "$a - $h removed" >> /tmp/aggregate_hosts_removed.txt
  done
  openstack aggregate delete "$a" && echo "$a" >> /tmp/aggregates_deleted.txt
done

# Cleanup baremetal nodes, including failed state recovery
nodes=$(openstack baremetal node list -c UUID -f value)
if [[ -n "$nodes" ]]; then
  log "Deleting baremetal nodes..."
  for node in $nodes; do
    echo "Attempting to delete baremetal node: $node"
    if openstack baremetal node delete "$node" &>/dev/null; then
      echo "$node" >> /tmp/baremetal_nodes_deleted.txt
    else
      log "Direct delete failed for $node. Setting maintenance mode and retrying..."
      openstack baremetal node maintenance set "$node"
      openstack baremetal node delete "$node" && echo "$node (via maintenance)" >> /tmp/baremetal_nodes_deleted.txt
    fi
  done
fi

log "OpenStack resource cleanup complete. Logs are in /tmp/*_deleted.txt"