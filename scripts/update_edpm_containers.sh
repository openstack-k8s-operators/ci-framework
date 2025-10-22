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

# Script to deploy updated containers to EDPM nodes
#
# Usage:
#   ./scripts/update_edpm_containers.sh --nodeset openstack-edpm --services ovn,neutron-metadata

set -euo pipefail

# Default values
NODESET_NAME="openstack-edpm"
NAMESPACE="openstack"
SERVICES=""
DEPLOYMENT_NAME=""
DRY_RUN=false
WAIT=true
TIMEOUT=3600

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help message
show_help() {
    cat << EOF
Update EDPM Container Images Deployment Script

This script creates an OpenStackDataPlaneDeployment to update containers on EDPM nodes.

Usage:
  $(basename "$0") [OPTIONS]

Options:
  -n, --nodeset NAME          NodeSet name (default: openstack-edpm)
  -s, --services SERVICES     Comma-separated list of services to update
                              Example: ovn,neutron-metadata,nova-custom-ovsdpdksriov
  -d, --deployment NAME       Deployment name (auto-generated if not specified)
  -N, --namespace NAMESPACE   OpenShift namespace (default: openstack)
  -w, --no-wait               Don't wait for deployment to complete
  -t, --timeout SECONDS       Timeout for deployment (default: 3600)
  -D, --dry-run               Show what would be done without applying
  -h, --help                  Show this help message

Examples:
  # Update OVN and Neutron Metadata on all nodes in openstack-edpm nodeset
  $(basename "$0") --nodeset openstack-edpm --services ovn,neutron-metadata

  # Update all services (full redeploy)
  $(basename "$0") --nodeset openstack-edpm

  # Dry run to see what would be deployed
  $(basename "$0") --nodeset openstack-edpm --services ovn --dry-run

  # Update specific services without waiting
  $(basename "$0") --nodeset openstack-edpm --services nova-custom-ovsdpdksriov --no-wait

Common Services:
  - bootstrap
  - download-cache
  - configure-ovs-dpdk
  - configure-network
  - install-os
  - configure-os
  - ovn
  - neutron-metadata
  - neutron-sriov
  - libvirt
  - nova-custom-ovsdpdksriov
  - telemetry

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--nodeset)
                NODESET_NAME="$2"
                shift 2
                ;;
            -s|--services)
                SERVICES="$2"
                shift 2
                ;;
            -d|--deployment)
                DEPLOYMENT_NAME="$2"
                shift 2
                ;;
            -N|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -w|--no-wait)
                WAIT=false
                shift
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -D|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prereqs() {
    print_info "Validating prerequisites..."

    # Check oc command
    if ! command -v oc &> /dev/null; then
        print_error "oc command not found. Please install OpenShift CLI."
        exit 1
    fi

    # Check if logged in to OpenShift
    if ! oc whoami &> /dev/null; then
        print_error "Not logged in to OpenShift. Please run 'oc login' first."
        exit 1
    fi

    # Check if namespace exists
    if ! oc get namespace "$NAMESPACE" &> /dev/null; then
        print_error "Namespace '$NAMESPACE' does not exist."
        exit 1
    fi

    # Check if nodeset exists
    if ! oc get openstackdataplanenodeset "$NODESET_NAME" -n "$NAMESPACE" &> /dev/null; then
        print_error "OpenStackDataPlaneNodeSet '$NODESET_NAME' not found in namespace '$NAMESPACE'."
        exit 1
    fi

    print_success "Prerequisites validated"
}

# Generate deployment name
generate_deployment_name() {
    if [[ -z "$DEPLOYMENT_NAME" ]]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        if [[ -n "$SERVICES" ]]; then
            # Use first service name in deployment name
            local first_service=$(echo "$SERVICES" | cut -d',' -f1)
            DEPLOYMENT_NAME="edpm-update-${first_service}-${timestamp}"
        else
            DEPLOYMENT_NAME="edpm-update-all-${timestamp}"
        fi
    fi
}

# Create deployment YAML
create_deployment_yaml() {
    print_info "Creating deployment manifest..."

    local yaml_content
    yaml_content=$(cat <<EOF
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneDeployment
metadata:
  name: ${DEPLOYMENT_NAME}
  namespace: ${NAMESPACE}
spec:
  nodeSets:
    - ${NODESET_NAME}
EOF
)

    # Add services override if specified
    if [[ -n "$SERVICES" ]]; then
        yaml_content+=$(cat <<EOF

  servicesOverride:
EOF
)
        # Convert comma-separated services to YAML list
        IFS=',' read -ra SERVICE_ARRAY <<< "$SERVICES"
        for service in "${SERVICE_ARRAY[@]}"; do
            service=$(echo "$service" | xargs) # Trim whitespace
            yaml_content+=$(cat <<EOF

    - ${service}
EOF
)
        done
    fi

    echo "$yaml_content"
}

# Apply deployment
apply_deployment() {
    local yaml_content
    yaml_content=$(create_deployment_yaml)

    print_info "Deployment manifest:"
    echo "---"
    echo "$yaml_content"
    echo "---"

    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "Dry run mode - deployment not applied"
        return 0
    fi

    print_info "Applying deployment..."
    echo "$yaml_content" | oc apply -f -

    print_success "Deployment '${DEPLOYMENT_NAME}' created in namespace '${NAMESPACE}'"
}

# Wait for deployment
wait_for_deployment() {
    if [[ "$WAIT" == "false" ]] || [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    print_info "Waiting for deployment to complete (timeout: ${TIMEOUT}s)..."

    local elapsed=0
    local interval=10

    while [[ $elapsed -lt $TIMEOUT ]]; do
        local status
        status=$(oc get openstackdataplanedeployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")

        local message
        message=$(oc get openstackdataplanedeployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].message}' 2>/dev/null || echo "")

        case "$status" in
            "True")
                print_success "Deployment completed successfully!"
                return 0
                ;;
            "False")
                if [[ "$message" == *"failed"* ]] || [[ "$message" == *"error"* ]]; then
                    print_error "Deployment failed: $message"
                    print_info "Check logs with: oc logs -n ${NAMESPACE} -l app=openstackansibleee --tail=100"
                    return 1
                fi
                ;;
        esac

        echo -ne "\r${BLUE}[INFO]${NC} Waiting... ${elapsed}s / ${TIMEOUT}s (Status: ${status})"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo "" # New line after progress
    print_error "Deployment timed out after ${TIMEOUT}s"
    return 1
}

# Show deployment status
show_deployment_status() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    print_info "Deployment status:"
    oc get openstackdataplanedeployment "$DEPLOYMENT_NAME" -n "$NAMESPACE"

    print_info "To monitor progress, use:"
    echo "  oc get openstackdataplanedeployment ${DEPLOYMENT_NAME} -n ${NAMESPACE} -w"
    echo "  oc logs -n ${NAMESPACE} -l app=openstackansibleee --tail=100 -f"

    print_info "To check deployment details:"
    echo "  oc describe openstackdataplanedeployment ${DEPLOYMENT_NAME} -n ${NAMESPACE}"
}

# Main function
main() {
    parse_args "$@"

    print_info "EDPM Container Update Deployment"
    print_info "================================="
    print_info "NodeSet: ${NODESET_NAME}"
    print_info "Namespace: ${NAMESPACE}"
    print_info "Services: ${SERVICES:-All services}"
    echo ""

    validate_prereqs
    generate_deployment_name

    print_info "Deployment name: ${DEPLOYMENT_NAME}"
    echo ""

    apply_deployment
    wait_for_deployment
    show_deployment_status
}

# Run main function
main "$@"
