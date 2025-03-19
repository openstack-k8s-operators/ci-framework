#!/usr/bin/bash

BASE_DIR="${HOME}/ci-framework-data/tests/update/"
CI_INVENTORY="${HOME}/ci-framework-data/artifacts/zuul_inventory.yml"
OPERATOR_NAMESPACE="openstack-operators"
NAMESPACE="openstack"

function get_current_compute_state {
    local stage="${1:-}"
    file_pre="${BASE_DIR}${stage:+${stage}-}"

    if [ -e "${CI_INVENTORY}" ]; then
        echo "Collecting compute state ${stage:+for $stage }in ${BASE_DIR:-${PWD}}"

        # Collect all running containers an all compute nodes in ~/ci-framework-data/tests/update/ by default.
        ansible -i "${CI_INVENTORY}" -m shell -a \
                "sudo podman ps -q --filter 'status=running' | xargs -I {} sudo podman inspect --format {% raw %} '{{.Name}} {{.Config.Image}} {{.State.StartedAt}}' {% endraw %} {}|sort" computes | \
            awk -vfile_pre="${file_pre}" 'BEGIN {tp=strftime("%Y%m%d%H%M%S")} /^compute/ {if (s != "") {close(s)}; s = "containers-" $1 "_" tp ".txt"; next;}; s {print > file_pre s} '
        # Collect packages list an all compute nodes in ~/ci-framework-data/tests/update/ by default.
        ansible -i "${CI_INVENTORY}" -m shell -a \
                "sudo dnf list installed | sort" computes | \
            awk -vfile_pre="${file_pre}" 'BEGIN {tp=strftime("%Y%m%d%H%M%S")} /^compute/ {if (s != "") {close(s)}; s = "packages-" $1 "_" tp ".txt"; next;}; s {print > file_pre s} '
    fi
}

function get_current_pod_state {
    local stage="${1:-}"
    file_pre="${BASE_DIR}${stage:+${stage}-}"

    echo "Collecting pod state ${stage:+for $stage }in ${BASE_DIR:-${PWD}}"

    local openstack_state_file="${file_pre}pods_os_state_$(date +%Y%m%d_%H%M%S).tsv"
    local os_operator_state_file="${file_pre}pods_os_op_state_$(date +%Y%m%d_%H%M%S).tsv"
    oc get pods -n "${OPERATOR_NAMESPACE}" -o json | jq -r '.items[] | select(.status.phase == "Running") | . as $pod | .status.containerStatuses[] | [$pod.metadata.name, $pod.status.startTime, .image, .state.running.startedAt ] | @tsv' > $os_operator_state_file

    oc get pods -n "${NAMESPACE}" -o json | jq -r '.items[] | select(.status.phase == "Running") | . as $pod | .status.containerStatuses[] | [$pod.metadata.name, $pod.status.startTime, .image, .state.running.startedAt ] | @tsv' > $openstack_state_file
}

function get_current_state {
    local stage="${1:-}"
    get_current_compute_state "${stage}"
    get_current_pod_state "${stage}"
}

declare -A STAGES
STAGES=(
  [1]="001_before_operator_update"
  [2]="002_after_openstack_operator_update"
  [3]="03_after_ovn_controlplane_update"
  [4]="04_after_ovn_dataplane_update"
  [5]="05_after_controlplane_update"
  [6]="06_after_update"
)

print_stages() {
  echo "Available options:"
  for key in "${!STAGES[@]}"; do
    echo "$key) ${STAGES[$key]}"
  done
}

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <option>"
  echo "Try '$0 --list' to see available options."
  exit 1
fi

if [[ $1 == "--list" ]]; then
  print_stages
  exit 0
fi

# Determine the state based on the input argument
option="$1"
case $option in
  1|2|3|4|5|6)
    selected_state="${STAGES[$option]}"
    ;;
  "01_before_update"|"02_after_openstack_operator_update"|"03_after_ovn_controlplane_update"|"04_after_ovn_dataplane_update"|"05_after_controlplane_update"|"06_after_update")
    selected_state="$option"
    ;;
  *)
    echo "Invalid option: $option"
    echo "Try '$0 --list' to see available options."
    exit 1
    ;;
esac

mkdir -p "${BASE_DIR}"

# Execute the selected state logic
echo "Executing action for state: $selected_state"
get_current_state "$selected_state"
