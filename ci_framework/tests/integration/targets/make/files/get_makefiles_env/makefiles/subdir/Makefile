# Pin to crc-2.19.0 due to https://issues.redhat.com/browse/OSP-25627
CRC_URL ?= 'https://developers.redhat.com/content-gateway/file/pub/openshift-v4/clients/crc/2.19.0/crc-linux-amd64.tar.xz'
KUBEADMIN_PWD ?= 12345678
CRC_DEFAULT_NETWORK_IP ?= 192.168.122.10
EDPM_COMPUTE_SUFFIX ?= 0
EDPM_TOTAL_NODES ?= 1
NETWORK_MTU	?= 1500

BMAAS_INSTANCE_NAME_PREFIX ?= crc-bmaas
BMAAS_INSTANCE_MEMORY ?= 4096
BMAAS_INSTANCE_VCPUS ?= 2
BMAAS_INSTANCE_DISK_SIZE ?= 20
BMAAS_INSTANCE_OS_VARIANT ?= centos-stream9
BMAAS_INSTANCE_VIRT_TYPE ?= kvm
BMAAS_INSTANCE_NET_MODEL ?= virtio
BMAAS_NETWORK_NAME ?= crc-bmaas
BMAAS_BRIDGE_IPADDRESS ?= 172.20.1.2
BMAAS_NETWORK_IPADDRESS ?= 172.20.1.1
BMAAS_NETWORK_NETMASK ?= 255.255.255.0
BMAAS_NODE_COUNT ?= 1
BMAAS_REDFISH_USERNAME ?= admin
BMAAS_REDFISH_PASSWORD ?= password
BMAAS_SUSHY_EMULATOR_NAMESPACE ?= sushy-emulator
BMAAS_LIBVIRT_USER ?= sushyemu

EDPM_REGISTRY_URL ?= quay.io/podified-antelope-centos9
EDPM_CONTAINER_TAG ?= current-podified
DATAPLANE_NTP_SERVER ?=pool.ntp.org
METADATA_SHARED_SECRET   ?= 1234567842
DATAPLANE_OVN_METADATA_AGENT_BIND_HOST ?=127.0.0.1
DATAPLANE_SSHD_ALLOWED_RANGES ?=['192.168.122.0/24']
DATAPLANE_DEPLOY_STRATEGY_DEPLOY ?= false

BM_PROVISIONING_INTERFACE  ?=enp6s0
BM_NETWORK_NAME            ?=default
BM_NETWORK_IPADDRESS       ?=192.168.122.1
BM_INSTANCE_NAME_PREFIX    ?=edpm-compute
BM_NODE_COUNT              ?=1

CLEANUP_DIR_CMD ?= rm -Rf

define vars
${1}: export CLEANUP_DIR_CMD=${CLEANUP_DIR_CMD}
endef

##@ General

# The help target prints out all targets with their descriptions organized
# beneath their categories. The categories are represented by '##@' and the
# target descriptions by '##'. The awk commands is responsible for reading the
# entire set of makefiles included in this invocation, looking for lines of the
# file as xyz: ## something, and then pretty-format the target and help. Then,
# if there's a line with ##@ something, that gets pretty-printed as a category.
# More info on the usage of ANSI control characters for terminal formatting:
# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
# More info on the awk command:
# http://linuxcommand.org/lc3_adv_awk.php

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Download required tools and versions
.PHONY: download_tools
download_tools: ## Runs an ansible playbook to install required tools with the versions to develop the service operators. The tools get installed in ~/bin and go in /usr/local/go (alternatives get used to set it as the system wide go version)
	ANSIBLE_FORCE_COLOR=true ansible-playbook \
	-v -i hosts \
	download_tools.yaml
