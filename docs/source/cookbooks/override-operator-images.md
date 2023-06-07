# Override operator images

## Full deploy override
In order to override images during an actual deploy, you have to:

* clone [openstack-k8s-operators/openstack-operator](https://github.com/openstack-k8s-operators/openstack-operator/)
* edit [custom-bundle.Dockerfile](https://github.com/openstack-k8s-operators/openstack-operator/blob/main/custom-bundle.Dockerfile) in order to point to the wanted images
* run `go mod edit` in the [project root](https://github.com/openstack-k8s-operators/openstack-operator/blob/main/go.mod) and update references
* run `go mod edit` in the [apis directory](https://github.com/openstack-k8s-operators/openstack-operator/blob/main/apis/go.mod#L11) and update references

Then, you'll have to pass down the repository path to the ci-framework, rebuild it, and deploy:
```YAML
cifmw_operator_build_meta_src: /path/to/openstack-operator
cifmw_operator_build_meta_build: true
cifmw_operator_build_push_registry: "default-route-openshift-image-registry.apps-crc.testing"
cifmw_operator_build_push_org: "openstack-operators"
```

### Example
You want to update the keystone operator, and point to a specific version.

* You edit the [custom-bundle.Dockerfile on line 3](https://github.com/openstack-k8s-operators/openstack-operator/blob/015b6a5293b76cbb2e1e14553168e501477314ef/custom-bundle.Dockerfile#L3)
* You `go mod edit` [line 16](https://github.com/openstack-k8s-operators/openstack-operator/blob/015b6a5293b76cbb2e1e14553168e501477314ef/go.mod#L16)
* You `go mod edit` [line 12](https://github.com/openstack-k8s-operators/openstack-operator/blob/015b6a5293b76cbb2e1e14553168e501477314ef/apis/go.mod#L12)
* You commit locally

And you pass down the previously listed parameters.
