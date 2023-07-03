# Speed up daily use
In order to speed up your daily tasks, you may now consume ansible tags. They
will allow to not run through the package installation tasks as well as skip
some of the main bootstrap steps.

In order to leverage this, you may first run this:
```Bash
$ ansible-playbook deploy-edpm.yml \
    -e @scenarios/centos-9/local-env.yml \
    --tags packages,cifmw_boostrap
```
This first step will create the necessary directories and install all the
packages needed by the "local-env.yml" environment file. Of course, if you have
some other scenarios to use, pass them to ansible directly.

Once things are ready, you may want to ensure you're in the `libvirt` group:
```Bash
$ groups
[...] libvirt [...]
```

If you aren't, please logout and login again. This should refresh your group
list, allowing you to talk to the correct libvirt namespace (system).

From now on, you may run only the actual deploy tasks:
```Bash
$ ansible-playbook deploy-edpm.yml \
    -e @scenarios/centos-9/local-env.yml \
    --skip-tags packages,cifmw_bootstrap
```
This second command will run everything that isn't related to packages or
bootstrap - making a (small) gain of time, since many tasks won't have to run.
