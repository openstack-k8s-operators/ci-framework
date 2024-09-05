# build_push_container

`build_push_container` aims to be a generic role that can build multi-arch containers and push them to remote registry.

## Privilege escalation

- Installing packages
- Installing qemu-user-static

### Tagging

A single image or manifest can have multiple tags moving independently. By default each push can have a tag, each PR and branch can have a latest tag.
Care should be taken with the latest tag, when running in a Zuul job, the latest tag should only be moved by a [Supercedent Pipeline](https://zuul-ci.org/docs/zuul/latest/config/pipeline.html#value-pipeline.manager.supercedent) which runs after check and gate jobs have passed.

### Multi-arch Builds

Multi-arch builds are made possible by using QEMU emulation via `qemu-user-static`.
When the non native arch is build a `binfmt_misc` rule is triggered instructing the process to be emulated transparently.

The `binfmt_misc` rules live in `/proc/sys/fs/binfmt_misc/` and can be queried like so:

```shell
cat /proc/sys/fs/binfmt_misc/qemu-arm64
enabled
interpreter /usr/bin/qemu-arm64-static
flags: F
offset 0
magic 7f454c460201010000000000000000000200b700
mask ffffffffffffff00fffffffffffffffffeffffff
```

When a multi-arch build is requested, a manifest is first created to hold the container images. This manifest is allows clients to call the same image reference and get a different base architecture image.

For example:

```shell
# On ARM based MacBook
$ podman run -t --rm quay.rdoproject.org/openstack-k8s-operators/cifmw-client:latest uname -m
aarch64

# On X86 based server
$ podman run -t --rm quay.rdoproject.org/openstack-k8s-operators/cifmw-client:latest uname -m
x86_64
```

## Testing

Molecule tests are ran to build single and multi-arch images, these are pushed to a local registry deployed via our `registry_deploy` role.

## Parameters

*`cifmw_build_push_container_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which  defaults to `~/ci-framework`.
*`cifmw_build_push_container_artifacts`: (String) Role artifacts directory. Defaults to `{{ cifmw_build_push_container_basedir }}/artifacts/build_push_container`
*`cifmw_build_push_container_name`: (String) Name of container to be build and/or pushed, this is mandatory. Defaults to `Null`
*`cifmw_build_push_container_build_context_path`: (String) Directory that will be used for the container build context. Defaults to Zuul project src_dir.
*`cifmw_build_push_container_containerfile_name`: (String) Filename of Containerfile. Defaults to `Containerfile`
*`cifmw_build_push_container_containerfile_path`: (String) Path to Containerfile. Defaults to {{ zuul.project.src_dir }}/Containerfile
*`cifmw_build_push_container_local_build_tag`: (String) Local tag used when building container. Defaults to `"{{ (cifmw_build_push_container_name,'latest') | join(':') }}"`
*`cifmw_build_push_container_supported_platform`: (List) List of architectures to build, supported architectures can be found [here](https://github.com/multiarch/qemu-user-static) Defaults to `[linux/amd64]`
*`cifmw_build_push_container_qemu_user_static_image`: (String) Container to pull when QEMU is required. Defaults to `quay.rdoproject.org/ci-framework/qemu-user-static:latest`
*`cifmw_build_push_container_git_sha`: (String) Git SHA that can be provided to tag container image on registry. Defaults to `"{{ zuul.commit_id }}"`
*`cifmw_build_push_container_patch_number`: (Int) Patch number that can be provided to tag container image on registry. Defaults to `"{{ zuul.change }}"`
*`cifmw_build_push_container_tag_override`: (List) Variable to add additional tags for container on registry. Defaults to `[]`
*`cifmw_build_push_container_push`: (Boolean) Enables pushing to remote registry. Defaults to `false`
*`cifmw_build_push_container_registry_name`: (String) Name of remote registry like `<domain>/<org>/<container_name>`. Defaults to `Null`
*`cifmw_build_push_container_registry_username`: (String) Username to authenticate to registry. Defaults to `Null`
*`cifmw_build_push_container_registry_password`: (String) Password to authenticate to registry. Defaults to `Null`
*`cifmw_build_push_container_registry_tls_verify`: (Boolean) Defaults to `true`

## Examples

Build container locally:

```yaml
---
- name: Build container
  hosts: localhost
  tasks:
    - name: Call build_push_container role
      vars:
        cifmw_build_push_container_name: test_container
        cifmw_build_push_container_build_context_path: /home/user/cool_project
        cifmw_build_push_container_tag_override: [super, cool, tags]
      ansible.builtin.include_role
        name: build_push_container
```

Build container locally and push to remote registry with multi-arch build:

```yaml
---
- name: Build container
  hosts: localhost
  tasks:
    - name: Call build_push_container role
      vars:
        cifmw_build_push_container_name: Test container
        cifmw_build_push_container_build_context_path: /home/user/cool_project
        cifmw_build_push_container_tag_override: [super, cool, tags]
        cifmw_build_push_container_supported_platform: [linux/amd64, linux/arm64]
        cifmw_build_push_container_push: true
        cifmw_build_push_container_registry_name: quay.rdoproject.org/cool_project/test_container
        cifmw_build_push_container_registry_username: username
        cifmw_build_push_container_registry_password: Passw0rd
      ansible.builtin.include_role
        name: build_push_container
```

Building a container from a Zuul job:

```yaml
- job:
    name: build-push-container-cifmw-client
    description: |
      Build and push cifmw-client container to
        quay.rdoproject.com registry.
      vars:
        cifmw_build_push_container_push - Used by build_push_container role to trigger pushing to registry.
        cifmw_build_push_container_name - Name of container being build and pushed.
        cifmw_build_push_container_containerfile_path - Path to containerfile.
        cifmw_build_push_container_registry_name - Registry built containers will be pushed too.
      Runtime: ~30mins.
    parent: build-push-container-build
    vars:
      ansible_user_dir: "{{ lookup('env', 'HOME') }}"
      cifmw_ci_framework_src: >-
        {{
          (ansible_user_dir,
          zuul.project.src_dir) | ansible.builtin.path_join
        }}
      cifmw_build_push_container_push: true
      cifmw_build_push_container_name: cifmw-client
      cifmw_build_push_container_containerfile_path: >-
        {{
          (cifmw_ci_framework_src,
          'containerfiles',
          'Containerfile.client') | ansible.builtin.path_join
        }}
      cifmw_build_push_container_registry_name: >-
        quay.rdoproject.org/openstack-k8s-operators/cifmw-client
      cifmw_build_push_container_supported_platform: [linux/arm64, linux/amd64]
    timeout: 5400
```
