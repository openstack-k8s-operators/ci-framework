# Minimum requirements

To run the ci-framework locally on your machine you will need:

* 32 GB RAM
* 120 GB free storage
* 6 CPU

# Needed packages
In order to be able to start consuming the Framework, the following packages
must be present on your system:

* git
* make
* python3-pip
* sudo

# Needed specific configurations
You must run the deployment as a **non root user**.

Your user must have full `sudo` access in order to:

* install packages
* push specific configurations linked to CRC

While we try to keep the footprint low on the system, packages are needed, and
some 3rd-party software requires access, such as CRC.

The best way to achieve that access is to add the following content to a
`/etc/sudoers.d/USERNAME` file using `visudo`:
```
USERNAME          ALL=(ALL)       NOPASSWD: ALL
```
Of course, replace `USERNAME` by your user's name.

## Specific access rights
Since we're using libvirt within the "system" namespace (thanks to CRC, mostly),
your user must be part of the "libvirt" user. While we manage this in one of
the roles, you may need to logout/login in order to refresh your groups.
