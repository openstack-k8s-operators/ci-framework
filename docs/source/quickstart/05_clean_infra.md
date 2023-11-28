# Clean deployed infrastructure

We propose two kind of cleanup.

## Quick cleanup
The recommended one, allowing a faster re-deploy.

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
In case you want to remove everything, with the base images.

```Bash
$ ansible-playbook -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor-1 \
    reproducer-clean.yml \
    --tags deepscrub
```
