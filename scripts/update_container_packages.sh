#!/bin/bash
# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Helper script to run the update_container_packages playbook
# This provides an easy interface for updating packages in containers

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CI_FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
PLAYBOOK="${CI_FRAMEWORK_DIR}/playbooks/update_container_packages.yml"
VARS_FILE=""
TARGET_PACKAGE=""
REPO_URL=""
NAMESPACE="openstack"
CR_NAME="controlplane"
IMAGE_PREFIX="updated"
DRY_RUN=false
VERBOSE=""

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Update RPM packages in OpenStack container images.

OPTIONS:
    -p, --package PACKAGE       Target package name (required)
    -r, --repo URL              Repository base URL (required)
    -v, --vars FILE             Use variables from file (overrides -p and -r)
    -n, --namespace NAMESPACE   OpenShift namespace (default: openstack)
    -c, --cr-name NAME          OpenStackVersion CR name (default: controlplane)
    -i, --image-prefix PREFIX   Image name prefix (default: updated)
    -d, --dry-run               Show what would be done without doing it
    -V, --verbose               Verbose output
    -h, --help                  Show this help message

EXAMPLES:
    # Update OVN package using command line arguments
    $0 -p ovn24.03 -r http://example.com/repo/

    # Update using a variables file
    $0 -v playbooks/vars/ovn_update.yml

    # Dry run to see what would happen
    $0 -p ovn24.03 -r http://example.com/repo/ --dry-run

    # Update with custom namespace and image prefix
    $0 -p openstack-neutron -r http://example.com/repo/ \\
       -n openstack-prod -i neutron-hotfix

PREDEFINED CONFIGURATIONS:
    The following vars files are available in playbooks/vars/:
    - ovn_update.yml      : Update OVN 24.03 package
    - neutron_update.yml  : Update Neutron package

EOF
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--package)
            TARGET_PACKAGE="$2"
            shift 2
            ;;
        -r|--repo)
            REPO_URL="$2"
            shift 2
            ;;
        -v|--vars)
            VARS_FILE="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -c|--cr-name)
            CR_NAME="$2"
            shift 2
            ;;
        -i|--image-prefix)
            IMAGE_PREFIX="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -V|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Validation
if [[ -z "$VARS_FILE" ]]; then
    if [[ -z "$TARGET_PACKAGE" ]] || [[ -z "$REPO_URL" ]]; then
        echo -e "${RED}Error: Either --vars or both --package and --repo are required${NC}"
        usage
    fi
fi

# Check if ansible-playbook is available
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}Error: ansible-playbook command not found${NC}"
    exit 1
fi

# Build ansible-playbook command
ANSIBLE_CMD="ansible-playbook $PLAYBOOK"

if [[ -n "$VARS_FILE" ]]; then
    # Using vars file
    if [[ ! -f "$VARS_FILE" ]]; then
        # Try to find it in playbooks/vars/
        if [[ -f "${CI_FRAMEWORK_DIR}/playbooks/vars/$VARS_FILE" ]]; then
            VARS_FILE="${CI_FRAMEWORK_DIR}/playbooks/vars/$VARS_FILE"
        else
            echo -e "${RED}Error: Variables file not found: $VARS_FILE${NC}"
            exit 1
        fi
    fi
    ANSIBLE_CMD="$ANSIBLE_CMD -e @$VARS_FILE"
    echo -e "${GREEN}Using variables from: $VARS_FILE${NC}"
else
    # Using command line arguments
    ANSIBLE_CMD="$ANSIBLE_CMD -e cifmw_upic_target_package=$TARGET_PACKAGE"
    ANSIBLE_CMD="$ANSIBLE_CMD -e cifmw_upic_repo_baseurl=$REPO_URL"
    ANSIBLE_CMD="$ANSIBLE_CMD -e cifmw_upic_namespace=$NAMESPACE"
    ANSIBLE_CMD="$ANSIBLE_CMD -e cifmw_upic_openstack_cr_name=$CR_NAME"
    ANSIBLE_CMD="$ANSIBLE_CMD -e cifmw_upic_image_name_prefix=$IMAGE_PREFIX"
fi

if [[ "$DRY_RUN" == "true" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD --check"
    echo -e "${YELLOW}Running in DRY-RUN mode (no actual changes will be made)${NC}"
fi

if [[ -n "$VERBOSE" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD $VERBOSE"
fi

# Display configuration
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Container Package Update${NC}"
echo -e "${GREEN}================================${NC}"
if [[ -z "$VARS_FILE" ]]; then
    echo -e "Package:     ${YELLOW}$TARGET_PACKAGE${NC}"
    echo -e "Repository:  ${YELLOW}$REPO_URL${NC}"
    echo -e "Namespace:   ${YELLOW}$NAMESPACE${NC}"
    echo -e "CR Name:     ${YELLOW}$CR_NAME${NC}"
    echo -e "Image Prefix: ${YELLOW}$IMAGE_PREFIX${NC}"
fi
echo -e "Playbook:    ${YELLOW}$PLAYBOOK${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Confirm before proceeding (unless dry-run)
if [[ "$DRY_RUN" == "false" ]]; then
    read -p "Do you want to proceed? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Aborted by user${NC}"
        exit 0
    fi
fi

# Run the playbook
echo -e "${GREEN}Running playbook...${NC}"
echo -e "${YELLOW}Command: $ANSIBLE_CMD${NC}"
echo ""

eval "$ANSIBLE_CMD"

# Check exit status
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Update completed successfully!${NC}"
    echo -e "${GREEN}================================${NC}"
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}Update failed!${NC}"
    echo -e "${RED}================================${NC}"
    exit 1
fi
