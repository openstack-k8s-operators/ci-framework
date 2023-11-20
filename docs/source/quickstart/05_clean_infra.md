# Clean deployed infrastructure

We propose two kind of cleanup.

## Quick cleanup
The recommended one, allowing a faster re-deploy, especially for the
Validated Architecture.

```Bash
$ ansible-playbook -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor-1 \
    reproducer-clean.yml
```

~~~{tip}
If you deployed on your laptop/desktop, you don't need to pass the inventory nor
the `cifmw_target_host` extra variable.
~~~

## Deep scrub
In case you need to re-deploy the full OCP cluster for your next deploy,
or if you just want to see everything burning.

```Bash
$ ansible-playbook -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor-1 \
    reproducer-clean.yml \
    --tags deepscrub
```
