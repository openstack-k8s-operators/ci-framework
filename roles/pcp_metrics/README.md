PCP Metrics
===========

This role manages Performance Co-Pilot (PCP) toolkit [^1] on the target host
for monitoring and analyzing the historical details of system performance [^2].

**Note**: The PCP toolkit is not to be confused with GitHub Copilot [^3],
which is an AI coding assistant – and not a concern of this role here.


Usage
-----

Please check the hooks provided in this repository for real-world examples:
- [pcp-metrics-pre.yml](/hooks/playbooks/pcp-metrics-pre.yml)
- [pcp-metrics-post.yml](/hooks/playbooks/pcp-metrics-post.yml)

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


Collected metrics
-----------------

The set of metrics exported to CSV (and plotted) is defined in
[pmrep-metricspec.conf](/roles/pcp_metrics/files/pmrep-metricspec.conf) and
covers CPU, memory, disk and network usage. The CPU accounting includes
`steal`, `iowait` and `idle` alongside `cpu` and `sys`. `steal` is the share
of time a CPU was runnable but the hypervisor was busy running another guest,
so it is a direct measure of noisy-neighbour contention on shared hosts -- it
is what lets us tell apart a node that is slow because it is starved of CPU
cycles from one that is merely idle or waiting on I/O. When these columns are
present, `plot.py` renders an extra "Steal + IOwait" panel; older CSVs without
them are still plotted (the panel is simply omitted).


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
