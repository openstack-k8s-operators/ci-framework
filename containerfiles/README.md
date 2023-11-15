# Available containers

The project provides two types of containers:

- Containerfile.ci: builds a really basic container, mostly used in Prow, exposing needed tools
- Containerfile.tests: based upon the previous one, allows to run some tests locally, or run the framework

## Build containers

Leveraging make, you can build the container on your own:
```Bash
$ make ci_ctx
```

## Using the container

In the examples bellow, the options will do:

- `-w /home/prow`: change the working directory to /home/prow
- `-e HOME=/home/prow`: switch *prow* user home directory location.
- `-v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519`: exposes your private SSH key.
- `-v .:/home/prow/ci-framework`: exposes the project content in /home/prow/ci-framework in the container.
- `-v ~/inventory.yml:/home/prow/ci-framework/inventory.yml`: an example of how you can override the inventory.yml.
- `--security-opt label=disable`: needed for SELinux environment.

### Inventory considerations

By default, the CI Framework runs against `localhost`. If you intend to run the framework against `localhost` from
within the container, you **must** provide a custom inventory in order to let ansible use the network connection
instead of the `local` default set in the provided inventory. For instance, you want an inventory like this:

```YAML
all:
  hosts:
    localhost:
      ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

And then mount it in the container, as shown bellow.

### Commands

#### UNIX systems

Depending on your Linux version, you may or may not need to pass the `--security-opt`. This mostly depends
on your SELinux status.

##### On RHEL based systems (CentOS, RHEL, Fedora, ...):
```Bash
podman run --rm -ti \
    -w /home/prow \
    -e HOME=/home/prow \
    -v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519 \
    -v .:/home/prow/ci-framework \
    -v ~/inventory.yml:/home/prow/ci-framework/inventory.yml \
    --security-opt label=disable \
    localhost/cifmw:latest bash
```

##### On non-SELinux systems (Debian, Ubuntu, Mint, MacOS, ...):
```Bash
podman run --rm -ti \
    -w /home/prow \
    -e HOME=/home/prow \
    -v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519 \
    -v .:/home/prow/ci-framework \
    -v ~/inventory.yml:/home/prow/ci-framework/inventory.yml \
    --security-opt label=disable \
    localhost/cifmw:latest bash
```

Note that you can replace `podman` command by `docker` with the same flags.
