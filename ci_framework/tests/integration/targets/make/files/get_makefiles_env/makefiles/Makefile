# general
SHELL       := /bin/bash
OCP_RELEASE := $(shell cut -d '.' -f 1,2 <<< $(shell oc version -o json | jq -r .openshiftVersion))
OPERATOR_NAMESPACE      ?= openstack-operators
NAMESPACE                ?= openstack
PASSWORD                 ?= 12345678
SECRET                   ?= osp-secret
OUT                      ?= ${PWD}/out
TIMEOUT                  ?= 300s
DBSERVICE           ?= galera
ifeq ($(DBSERVICE), galera)
DBSERVICE_CONTAINER = openstack-galera-0
else
DBSERVICE_CONTAINER = mariadb-openstack
endif
METADATA_SHARED_SECRET   ?= 1234567842
HEAT_AUTH_ENCRYPTION_KEY ?= 767c3ed056cbaa3b9dfedb8c6f825bf0

# Allows overriding the cleanup command used in *_cleanup targets.
# Useful in CI, to allow injectin kustomization in each operator CR directory
# before the resource gets deployed. If it's not possible to inject Kustomizations/CRs
# in the CR dir if a call to each deploy target cleans the CR dir.
CLEANUP_DIR_CMD					 ?= rm -Rf

METALLB_POOL			 ?=192.168.122.80-192.168.122.90
# are we deploying to microshift
MICROSHIFT ?= 0

# operators gets cloned here
OPERATOR_BASE_DIR   ?= ${OUT}/operator

# storage (used by some operators)
STORAGE_CLASS       ?= "local-storage"
CRC_STORAGE_RETRIES ?= 3

# network isolation
NETWORK_ISOLATION   ?= true
NETWORK_MTU         ?= 1500

# options to pass in all targets that use git clone
GIT_CLONE_OPTS      ?=

# set to 3 to use a 3-node galera sample
GALERA_REPLICAS         ?=

# OpenStack Operator
OPENSTACK_IMG                ?= quay.io/openstack-k8s-operators/openstack-operator-index:latest
OPENSTACK_REPO               ?= https://github.com/openstack-k8s-operators/openstack-operator.git
OPENSTACK_BRANCH             ?= main

ifeq ($(NETWORK_ISOLATION), true)
ifeq ($(DBSERVICE), galera)
OPENSTACK_CTLPLANE           ?= $(if $(findstring 3,$(GALERA_REPLICAS)),config/samples/core_v1beta1_openstackcontrolplane_galera_network_isolation_3replicas.yaml,config/samples/core_v1beta1_openstackcontrolplane_galera_network_isolation.yaml)
else
OPENSTACK_CTLPLANE           ?= config/samples/core_v1beta1_openstackcontrolplane_network_isolation.yaml
endif
else
ifeq ($(DBSERVICE), galera)
OPENSTACK_CTLPLANE           ?= $(if $(findstring 3,$(GALERA_REPLICAS)),config/samples/core_v1beta1_openstackcontrolplane_galera_3replicas.yaml,config/samples/core_v1beta1_openstackcontrolplane_galera.yaml)
else
OPENSTACK_CTLPLANE           ?= config/samples/core_v1beta1_openstackcontrolplane.yaml
endif
endif

OPENSTACK_CR                 ?= ${OPERATOR_BASE_DIR}/openstack-operator/${OPENSTACK_CTLPLANE}
OPENSTACK_BUNDLE_IMG         ?= quay.io/openstack-k8s-operators/openstack-operator-bundle:latest
OPENSTACK_STORAGE_BUNDLE_IMG ?= quay.io/openstack-k8s-operators/openstack-operator-storage-bundle:latest
OPENSTACK_CRDS_DIR           ?= openstack_crds
OPENSTACK_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/openstack-operator/kuttl-test.yaml
OPENSTACK_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/openstack-operator/tests/kuttl/tests
OPENSTACK_KUTTL_NAMESPACE ?= openstack-kuttl-tests

# Infra Operator
INFRA_IMG             ?= quay.io/openstack-k8s-operators/infra-operator-index:latest
INFRA_REPO            ?= https://github.com/openstack-k8s-operators/infra-operator.git
INFRA_BRANCH          ?= main
INFRA_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/infra-operator/kuttl-test.yaml
INFRA_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/infra-operator/tests/kuttl/tests
INFRA_KUTTL_NAMESPACE ?= infra-kuttl-tests

# DNS
# DNS_IMG     ?= (this is unused because this is part of infra operator)
DNSMASQ       ?= config/samples/network_v1beta1_dnsmasq.yaml
DNSDATA       ?= config/samples/network_v1beta1_dnsdata.yaml
DNSMASQ_CR    ?= ${OPERATOR_BASE_DIR}/infra-operator/${DNSMASQ}
DNSDATA_CR    ?= ${OPERATOR_BASE_DIR}/infra-operator/${DNSDATA}
DNS_DEPL_IMG  ?= unused

# NetConfig
NETCONFIG     ?= config/samples/network_v1beta1_netconfig.yaml
NETCONFIG_CR  ?= ${OPERATOR_BASE_DIR}/infra-operator/${NETCONFIG}
NETCONFIG_DEPL_IMG  ?= unused

# Memcached
# MEMCACHED_IMG     ?= (this is unused because this is part of infra operator)
MEMCACHED           ?= config/samples/memcached_v1beta1_memcached.yaml
MEMCACHED_CR        ?= ${OPERATOR_BASE_DIR}/infra-operator/${MEMCACHED}
MEMCACHED_DEPL_IMG  ?= unused

# Keystone
KEYSTONE_IMG             ?= quay.io/openstack-k8s-operators/keystone-operator-index:latest
KEYSTONE_REPO            ?= https://github.com/openstack-k8s-operators/keystone-operator.git
KEYSTONE_BRANCH          ?= main
KEYSTONEAPI              ?= config/samples/keystone_v1beta1_keystoneapi.yaml
KEYSTONEAPI_CR           ?= ${OPERATOR_BASE_DIR}/keystone-operator/${KEYSTONEAPI}
KEYSTONEAPI_DEPL_IMG     ?= unused
KEYSTONE_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/keystone-operator/kuttl-test.yaml
KEYSTONE_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/keystone-operator/tests/kuttl/tests
KEYSTONE_KUTTL_NAMESPACE ?= keystone-kuttl-tests

# Mariadb
MARIADB_IMG             ?= quay.io/openstack-k8s-operators/mariadb-operator-index:latest
MARIADB_REPO            ?= https://github.com/openstack-k8s-operators/mariadb-operator.git
MARIADB_BRANCH          ?= main
ifeq ($(DBSERVICE), galera)
MARIADB                 ?= config/samples/mariadb_v1beta1_galera.yaml
else
MARIADB                 ?= config/samples/mariadb_v1beta1_mariadb.yaml
endif
MARIADB_CR              ?= ${OPERATOR_BASE_DIR}/mariadb-operator/${MARIADB}
MARIADB_DEPL_IMG        ?= unused
MARIADB_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/mariadb-operator/kuttl-test.yaml
MARIADB_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/mariadb-operator/tests/kuttl/tests
MARIADB_KUTTL_NAMESPACE ?= mariadb-kuttl-tests

# Placement
PLACEMENT_IMG             ?= quay.io/openstack-k8s-operators/placement-operator-index:latest
PLACEMENT_REPO            ?= https://github.com/openstack-k8s-operators/placement-operator.git
PLACEMENT_BRANCH          ?= main
PLACEMENTAPI              ?= config/samples/placement_v1beta1_placementapi.yaml
PLACEMENTAPI_CR           ?= ${OPERATOR_BASE_DIR}/placement-operator/${PLACEMENTAPI}
PLACEMENTAPI_DEPL_IMG     ?= unused
PLACEMENT_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/placement-operator/kuttl-test.yaml
PLACEMENT_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/placement-operator/tests/kuttl/tests
PLACEMENT_KUTTL_NAMESPACE ?= placement-kuttl-tests

# Sir Glancealot
GLANCE_IMG              ?= quay.io/openstack-k8s-operators/glance-operator-index:latest
GLANCE_REPO             ?= https://github.com/openstack-k8s-operators/glance-operator.git
GLANCE_BRANCH           ?= main
GLANCE                  ?= config/samples/glance_v1beta1_glance.yaml
GLANCE_CR               ?= ${OPERATOR_BASE_DIR}/glance-operator/${GLANCE}
GLANCEAPI_DEPL_IMG      ?= unused
GLANCE_KUTTL_CONF       ?= ${OPERATOR_BASE_DIR}/glance-operator/kuttl-test.yaml
GLANCE_KUTTL_DIR        ?= ${OPERATOR_BASE_DIR}/glance-operator/tests/kuttl/tests
GLANCE_KUTTL_NAMESPACE  ?= glance-kuttl-tests

# Ovn
OVN_IMG             ?= quay.io/openstack-k8s-operators/ovn-operator-index:latest
OVN_REPO            ?= https://github.com/openstack-k8s-operators/ovn-operator.git
OVN_BRANCH          ?= main
OVNDBS              ?= config/samples/ovn_v1beta1_ovndbcluster.yaml
OVNDBS_CR           ?= ${OPERATOR_BASE_DIR}/ovn-operator/${OVNDBS}
OVNNORTHD           ?= config/samples/ovn_v1beta1_ovnnorthd.yaml
OVNNORTHD_CR        ?= ${OPERATOR_BASE_DIR}/ovn-operator/${OVNNORTHD}
OVNCONTROLLER       ?= config/samples/ovn_v1beta1_ovncontroller.yaml
OVNCONTROLLER_CR    ?= ${OPERATOR_BASE_DIR}/ovn-operator/${OVNCONTROLLER}
# TODO: Image customizations for all OVN services
OVN_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/ovn-operator/kuttl-test.yaml
OVN_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/ovn-operator/tests/kuttl/tests
OVN_KUTTL_NAMESPACE ?= ovn-kuttl-tests

# Neutron
NEUTRON_IMG             ?= quay.io/openstack-k8s-operators/neutron-operator-index:latest
NEUTRON_REPO            ?= https://github.com/openstack-k8s-operators/neutron-operator.git
NEUTRON_BRANCH          ?= main
NEUTRONAPI              ?= config/samples/neutron_v1beta1_neutronapi.yaml
NEUTRONAPI_CR           ?= ${OPERATOR_BASE_DIR}/neutron-operator/${NEUTRONAPI}
NEUTRONAPI_DEPL_IMG     ?= unused
# TODO: Do we need interfaces to customize images for the other services ?
NEUTRON_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/neutron-operator/kuttl-test.yaml
NEUTRON_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/neutron-operator/test/kuttl/tests
NEUTRON_KUTTL_NAMESPACE ?= neutron-kuttl-tests

# Cinder
CINDER_IMG             ?= quay.io/openstack-k8s-operators/cinder-operator-index:latest
CINDER_REPO            ?= https://github.com/openstack-k8s-operators/cinder-operator.git
CINDER_BRANCH          ?= main
CINDER                 ?= config/samples/cinder_v1beta1_cinder.yaml
CINDER_CR              ?= ${OPERATOR_BASE_DIR}/cinder-operator/${CINDER}
# TODO: Image customizations for all Cinder services
CINDER_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/cinder-operator/kuttl-test.yaml
CINDER_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/cinder-operator/tests/kuttl/tests
CINDER_KUTTL_NAMESPACE ?= cinder-kuttl-tests

# RabbitMQ
RABBITMQ_IMG        ?= quay.io/openstack-k8s-operators/rabbitmq-cluster-operator-index:latest
RABBITMQ_REPO       ?= https://github.com/openstack-k8s-operators/rabbitmq-cluster-operator.git
RABBITMQ_BRANCH     ?= patches
RABBITMQ            ?= docs/examples/default-security-context/rabbitmq.yaml
RABBITMQ_CR         ?= ${OPERATOR_BASE_DIR}/rabbitmq-operator/${RABBITMQ}
RABBITMQ_DEPL_IMG   ?= unused

# Ironic
IRONIC_IMG             ?= quay.io/openstack-k8s-operators/ironic-operator-index:latest
IRONIC_REPO            ?= https://github.com/openstack-k8s-operators/ironic-operator.git
IRONIC_BRANCH          ?= main
IRONIC                 ?= config/samples/ironic_v1beta1_ironic.yaml
IRONIC_CR              ?= ${OPERATOR_BASE_DIR}/ironic-operator/${IRONIC}
IRONICAPI_DEPL_IMG     ?= unused
IRONICCON_DEPL_IMG     ?= unused
IRONICPXE_DEPL_IMG     ?= unused
IRONICINS_DEPL_IMG     ?= unused
IRONICNAG_DEPL_IMG     ?= unused
IRONIC_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/ironic-operator/kuttl-test.yaml
IRONIC_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/ironic-operator/tests/kuttl/tests
IRONIC_KUTTL_NAMESPACE ?= ironic-kuttl-tests

# Octavia
OCTAVIA_IMG             ?= quay.io/openstack-k8s-operators/octavia-operator-index:latest
OCTAVIA_REPO            ?= https://github.com/openstack-k8s-operators/octavia-operator.git
OCTAVIA_BRANCH          ?= main
OCTAVIA                 ?= config/samples/octavia_v1beta1_octavia.yaml
OCTAVIA_CR              ?= ${OPERATOR_BASE_DIR}/octavia-operator/${OCTAVIA}
# TODO: Image custom    izations for all Octavia services
OCTAVIA_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/octavia-operator/kuttl-test.yaml
OCTAVIA_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/octavia-operator/tests/kuttl/tests
OCTAVIA_KUTTL_NAMESPACE ?= octavia-kuttl-tests

# Designate
DESIGNATE_IMG             ?= quay.io/openstack-k8s-operators/designate-operator-index:latest
DESIGNATE_REPO            ?= https://github.com/openstack-k8s-operators/designate-operator.git
DESIGNATE_BRANCH          ?= main
DESIGNATE                 ?= config/samples/designate_v1beta1_designate.yaml
DESIGNATE_CR              ?= ${OPERATOR_BASE_DIR}/designate-operator/${DESIGNATE}
DESIGNATE_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/designate-operator/kuttl-test.yaml
DESIGNATE_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/designate-operator/tests/kuttl/tests
DESIGNATE_KUTTL_NAMESPACE ?= designate-kuttl-tests

# Nova
NOVA_IMG            ?= quay.io/openstack-k8s-operators/nova-operator-index:latest
NOVA_REPO           ?= https://github.com/openstack-k8s-operators/nova-operator.git
NOVA_BRANCH         ?= main
# NOTE(gibi): We intentionally not using the default nova sample here
# as that would require two RabbitMQCluster to be deployed which a) is not what
# the make rabbitmq_deploy target does ii) required extra resource in the dev
# environment.
NOVA                ?= config/samples/nova_v1beta1_nova_collapsed_cell.yaml
NOVA_CR             ?= ${OPERATOR_BASE_DIR}/nova-operator/${NOVA}
# TODO: Image customizations for all Nova services

# Horizon
HORIZON_IMG             ?= quay.io/openstack-k8s-operators/horizon-operator-index:latest
HORIZON_REPO            ?= https://github.com/openstack-k8s-operators/horizon-operator.git
HORIZON_BRANCH          ?= main
HORIZON                 ?= config/samples/horizon_v1beta1_horizon.yaml
HORIZON_CR              ?= ${OPERATOR_BASE_DIR}/horizon-operator/${HORIZON}
HORIZON_DEPL_IMG        ?= unused
HORIZON_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/horizon-operator/kuttl-test.yaml
HORIZON_KUTTL_NAMESPACE ?= horizon-kuttl-tests
HORIZON_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/horizon-operator/tests/kuttl/tests

# Heat
HEAT_IMG             ?= quay.io/openstack-k8s-operators/heat-operator-index:latest
HEAT_REPO            ?= https://github.com/openstack-k8s-operators/heat-operator.git
HEAT_BRANCH          ?= main
HEAT                 ?= config/samples/heat_v1beta1_heat.yaml
HEAT_CR              ?= ${OPERATOR_BASE_DIR}/heat-operator/${HEAT}
HEATAPI_DEPL_IMG     ?= unused
HEATCFNAPI_DEPL_IMG  ?= unused
HEATENGINE_DEPL_IMG  ?= unused
HEAT_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/heat-operator/kuttl-test.yaml
HEAT_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/heat-operator/tests/kuttl/tests
HEAT_KUTTL_NAMESPACE ?= heat-kuttl-tests

# AnsibleEE
ANSIBLEEE_IMG        ?= quay.io/openstack-k8s-operators/openstack-ansibleee-operator-index:latest
ANSIBLEEE_REPO       ?= https://github.com/openstack-k8s-operators/openstack-ansibleee-operator
ANSIBLEEE_BRANCH          ?= main
ANSIBLEEE                 ?= config/samples/_v1alpha1_ansibleee.yaml
ANSIBLEEE_CR              ?= ${OPERATOR_BASE_DIR}/openstack-ansibleee-operator/${ANSIBLEEE}
ANSIBLEEE_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/openstack-ansibleee-operator/kuttl-test.yaml
ANSIBLEEE_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/openstack-ansibleee-operator/tests/kuttl/tests
ANSIBLEEE_KUTTL_NAMESPACE ?= ansibleee-kuttl-tests


# Baremetal Operator
BAREMETAL_IMG       ?= quay.io/openstack-k8s-operators/openstack-baremetal-operator-index:latest
BAREMETAL_REPO      ?= https://github.com/openstack-k8s-operators/openstack-baremetal-operator.git
BAREMETAL_BRANCH    ?= main
BMH_NAMESPACE       ?= ${NAMESPACE}

# Dataplane Operator
DATAPLANE_IMG                                    ?= quay.io/openstack-k8s-operators/dataplane-operator-index:latest
DATAPLANE_REPO                                   ?= https://github.com/openstack-k8s-operators/dataplane-operator.git
DATAPLANE_BRANCH                                 ?= main
OPENSTACK_DATAPLANENODESET                       ?= config/samples/dataplane_v1beta1_openstackdataplanenodeset.yaml
OPENSTACK_DATAPLANENODESET_BAREMETAL             ?= config/samples/dataplane_v1beta1_openstackdataplanenodeset_baremetal_with_ipam.yaml
DATAPLANE_NODESET_CR                             ?= ${OPERATOR_BASE_DIR}/dataplane-operator/${OPENSTACK_DATAPLANENODESET}
DATAPLANE_NODESET_BAREMETAL_CR                   ?= ${OPERATOR_BASE_DIR}/dataplane-operator/${OPENSTACK_DATAPLANENODESET_BAREMETAL}
DATAPLANE_ANSIBLE_SECRET                         ?=dataplane-ansible-ssh-private-key-secret
DATAPLANE_ANSIBLE_USER                           ?=
DATAPLANE_COMPUTE_IP                             ?=192.168.122.100
DATAPLANE_COMPUTE_1_IP                           ?=192.168.122.101
DATAPLANE_TOTAL_NODES                            ?=2
DATAPLANE_RUNNER_IMG                             ?=quay.io/openstack-k8s-operators/openstack-ansibleee-runner:latest
DATAPLANE_NETWORK_INTERFACE_NAME                 ?=eth0
DATAPLANE_SSHD_ALLOWED_RANGES                    ?=['192.168.122.0/24']
DATAPLANE_NTP_SERVER                      ?=pool.ntp.org
DATAPLANE_REGISTRY_URL                           ?=quay.io/podified-antelope-centos9
DATAPLANE_CONTAINER_TAG                          ?=current-podified
DATAPLANE_OVN_METADATA_AGENT_BIND_HOST           ?=127.0.0.1
DATAPLANE_SINGLE_NODE                            ?=true
DATAPLANE_KUTTL_CONF      ?= ${OPERATOR_BASE_DIR}/dataplane-operator/kuttl-test.yaml
DATAPLANE_KUTTL_DIR       ?= ${OPERATOR_BASE_DIR}/dataplane-operator/tests/kuttl/tests
DATAPLANE_KUTTL_NAMESPACE ?= dataplane-kuttl-tests
DATAPLANE_DEFAULT_GW      ?= 192.168.122.1

# Manila
MANILA_IMG            ?= quay.io/openstack-k8s-operators/manila-operator-index:latest
MANILA_REPO           ?= https://github.com/openstack-k8s-operators/manila-operator.git
MANILA_BRANCH         ?= main
MANILA                ?= config/samples/manila_v1beta1_manila.yaml
MANILA_CR             ?= ${OPERATOR_BASE_DIR}/manila-operator/${MANILA}
# TODO: Image customizations for all Manila services
MANILA_KUTTL_CONF     ?= ${OPERATOR_BASE_DIR}/manila-operator/kuttl-test.yaml
MANILA_KUTTL_DIR      ?= ${OPERATOR_BASE_DIR}/manila-operator/tests/kuttl/tests
MANILA_KUTTL_TIMEOUT  ?= 180

# Ceph
CEPH_IMG            ?= quay.io/ceph/demo:latest

# NNCP
NNCP_INTERFACE      ?= enp6s0
NNCP_TIMEOUT		?= 240s
NNCP_CLEANUP_TIMEOUT	?= 120s

# Telemetry
TELEMETRY_IMG                    ?= quay.io/openstack-k8s-operators/telemetry-operator-index:latest
TELEMETRY_REPO                   ?= https://github.com/openstack-k8s-operators/telemetry-operator.git
TELEMETRY_BRANCH                 ?= main
TELEMETRY                        ?= config/samples/telemetry_v1beta1_telemetry.yaml
TELEMETRY_CR                     ?= ${OPERATOR_BASE_DIR}/telemetry-operator/${TELEMETRY}
CEILOMETER_CENTRAL_DEPL_IMG      ?= unused
CEILOMETER_NOTIFICATION_DEPL_IMG ?= unused
SG_CORE_DEPL_IMG                 ?= unused

# BMO
BMO_REPO                         ?= https://github.com/metal3-io/baremetal-operator
BMO_BRANCH                       ?= main
BMO_PROVISIONING_INTERFACE       ?= enp6s0
BMO_IRONIC_HOST                  ?= 192.168.122.10

# Swift
SWIFT_IMG        ?= quay.io/openstack-k8s-operators/swift-operator-index:latest
SWIFT_REPO       ?= https://github.com/openstack-k8s-operators/swift-operator.git
SWIFT_BRANCH     ?= main
SWIFT            ?= config/samples/swift_v1beta1_swift.yaml
SWIFT_CR         ?= ${OPERATOR_BASE_DIR}/swift-operator/${SWIFT}
SWIFT_KUTTL_CONF   ?= ${OPERATOR_BASE_DIR}/swift-operator/kuttl-test.yaml
SWIFT_KUTTL_DIR    ?= ${OPERATOR_BASE_DIR}/swift-operator/tests/kuttl/tests
SWIFT_KUTTL_NAMESPACE ?= swift-kuttl-tests

# CertManager
CERTMANAGER_TIMEOUT                  ?= 300s

# target vars for generic operator install info 1: target name , 2: operator name
define vars
${1}: export OCP_RELEASE=$(OCP_RELEASE)
${1}: export NAMESPACE=${NAMESPACE}
${1}: export OPERATOR_NAMESPACE=${OPERATOR_NAMESPACE}
${1}: export SECRET=${SECRET}
${1}: export PASSWORD=${PASSWORD}
${1}: export METADATA_SHARED_SECRET=${METADATA_SHARED_SECRET}
${1}: export HEAT_AUTH_ENCRYPTION_KEY=${HEAT_AUTH_ENCRYPTION_KEY}
${1}: export STORAGE_CLASS=${STORAGE_CLASS}
${1}: export OUT=${OUT}
${1}: export CLEANUP_DIR_CMD=${CLEANUP_DIR_CMD}
${1}: export OPERATOR_NAME=${2}
${1}: export OPERATOR_DIR=${OUT}/${OPERATOR_NAMESPACE}/${2}/op
${1}: export DEPLOY_DIR=${OUT}/${NAMESPACE}/${2}/cr
endef

BMO_CRDS=$(shell oc get crds | grep metal3.io)
ifeq (,$(findstring baremetalhosts.metal3.io, ${BMO_CRDS}))
	BMO_SETUP ?= true
endif

.PHONY: openstack_prep
openstack_prep: export IMAGE=${OPENSTACK_IMG}
openstack_prep: $(if $(findstring true,$(NETWORK_ISOLATION)), nmstate nncp netattach metallb metallb_config)
openstack_prep: $(if $(findstring true,$(BMO_SETUP)), crc_bmo_setup) ## creates the files to install the operator using olm
	$(eval $(call vars,$@,openstack))
	bash scripts/gen-olm.sh
