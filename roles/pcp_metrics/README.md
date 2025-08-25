PCP Metrics
===========

This role manages Performance Co-Pilot (PCP) toolkit [^1] on the target host
for monitoring and analyzing the historical details of system performance [^2].

**Note**: The PCP toolkit is not to be confused with GitHub Copilot [^3],
which is an AI coding assistant – and not a concern of this role here.


Usage
-----

To setup and enable PCP on the target host, include the role with setup tasks:

```
- name: Setup PCP
  include_role:
    name: pcp_metrics
    tasks_from: setup
```

To collect current metrics from the host, include the role with gather tasks:

```
- name: Gather metrics
  include_role:
    name: pcp_metrics
    tasks_from: gather
```

Alternatively, `pcp_metrics_setup` and `pcp_metrics_gather` boolean variables
can be used to control which actions to perform when including the role with
just main tasks file (the default one). For example:

```
- name: Setup PCP
  include_role:
    name: pcp_metrics
  vars:
    pcp_metrics_setup: true
```


Impact
------

According to my brief checks, enabling PCP causes negligible difference
in the system load. The metrics in default configuration took about 5 MB
of disk space per hour (although it can be reduced by over 90% with `xz`,
IMVHO it is not worth the additional CPU usage).


References
----------

[^1]: https://pcp.io

[^2]: https://pcp.readthedocs.io/

[^3]: https://github.com/features/copilot
