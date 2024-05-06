# Available containers

The project provides two types of containers:

- `Containerfile.ci`: builds a really basic container, mostly used in Prow, exposing needed tools
- `Containerfile.tests`: based upon the previous one, allows to run some tests locally, or run the framework

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
- `-v ~/custom_files:/home/prow/custom_files`: mounts the custom_files directory. This is useful for incorporating various files that cifmw requires, such as multiple inventory files, ci_token, and pull_secret.
- `--uidmap 1000:0:1 --uidmap 0:1:1000`: sets up user ID mappings for improved security.
- `--security-opt label=disable`: needed for SELinux environment.

### Inventory considerations

By default, the CI Framework runs against `localhost`. If you intend to run the framework against `localhost` from
within the container, you **must** provide a custom inventory in order to let ansible use the network connection
instead of the `local` default set in the provided inventory. For instance, you want an inventory like this:

~~~{code-block} YAML
:caption: custom/inventory.yml
:linenos:
all:
  hosts:
    localhost:
      ansible_ssh_common_args='-o StrictHostKeyChecking=no'
~~~

And then mount it in the container, as shown bellow.

### Home directory considerations

Since the container's primary goal was to run tests, without any interactive shell, the $HOME set to the used is the same as
in Prow environment: `/`. While the proposed commands exports the $HOME environment variables, some processes may not get it right.

In order to switch the user's home directory, we strongly advise running this as soon as you are in the container:
```Bash
[container]$ sudo usermod -d /home/prow prow
```

This should then ensure SSH, molecule and other things are consuming the right location.

### Commands

#### UNIX systems

Depending on your Linux version, you may or may not need to pass the `--security-opt`. This mostly depends
on your SELinux status.

##### On RHEL based systems (CentOS, RHEL, Fedora, ...):
```Bash
[laptop]$ podman run --rm -ti \
    -w /home/prow \
    -e HOME=/home/prow \
    -v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519 \
    -v $(pwd):/home/prow/ci-framework \
    -v ~/custom_files:/home/prow/custom_files \
    --security-opt label=disable \
    localhost/cifmw:latest bash
```

##### On non-SELinux systems (Debian, Ubuntu, Mint, MacOS, ...):
```Bash
[laptop]$ podman run --rm -ti \
    -w /home/prow \
    -e HOME=/home/prow \
    -v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519 \
    -v $(pwd):/home/prow/ci-framework \
    -v ~/custom_files:/home/prow/custom_files \
    --security-opt label=disable \
    localhost/cifmw:latest bash
```

##### On systems utilizing Podman Remote Machine (MacOS, Windows, ...):
~~~{warning}
It is required to have podman-machine configured with the home directory mounted.
Be aware that running this process will remove all existing images and containers,
including those that were preinstalled or already exist on your system.
~~~

```Bash
[macos]$ podman machine stop podman-machine-default
[macos]$ podman machine rm podman-machine-default
[macos]$ podman machine init -v $HOME:$HOME
[macos]$ podman machine start
```

```Bash
[macos]$ podman run --rm -ti \
    -w /home/prow \
    -e HOME=/home/prow \
    -v ~/.ssh/id_ed25519:/home/prow/.ssh/id_ed25519 \
    -v $(pwd):/home/prow/ci-framework \
    -v ~/custom_files:/home/prow/custom_files \
    --uidmap 1000:0:1 --uidmap 0:1:1000 \
    localhost/cifmw:latest bash
```
Note that you can replace `podman` command by `docker` with the same flags.
