# njmon

Install [njmon](https://nmon.sourceforge.io/pmwiki.php?n=Site.Njmon) from sources,
configure it and run it in the background.

## Privilege escalation
None

## Parameters
* `cifmw_njmon_basedir`: Base directory. Defaults to `{{ cifmw_basedir }}` which defaults to `~/ci-framework-data`.
* `cifmw_njmon_repository`: njmon repository. Defaults to `http://sourceforge.net/projects/nmon/files`.
* `cifmw_njmon_release`: njmon release. Defaults to `v83`.
* `cifmw_njmon_archive`: njmon archive name. Defaults to `njmon_linux_{{ cifmw_njmon_release }}.zip`.
* `cifmw_njmon_output_dir`: Output directory for njmon data. Defaults to `{{ cifmw_njmon_basedir }}/artifacts/njmon_stats`.
* `cifmw_njmon_options`: Additional njmon options. Defaults to `[]`.
* `cifmw_njmon_chart_release`: njmonchart release. Defaults to `v40`.
* `cifmw_njmon_chart_archive`: njmonchart archive name. Defaults to `njmonchart_{{ cifmw_njmon_chart_release }}.zip`.

### Default options
By default, we inject the following options via the `cifmw_njmon_default_opts` parameter:
```
-m {{ cifmw_njmon_output_dir }}
-K {{ cifmw_njmon_basedir }}/tmp/njmon.pid
-f
-s 10
-n
```
It is NOT recommended to change those default options.

## How to visualize data

### InfluxDB

In case you have a grafana infrastructure, you can inject the needed parameters to instruct
njmon to ship its data to the InfluxDB. Check `njmon -h` or the website for the correct options.

### njmonchart

You can fetch [njmonchart](https://nmon.sourceforge.io/pmwiki.php?n=Site.Njmon) from the website,
and run it against the dataset. It will generate not-so-beautiful, yet useful charts to visualize
the resources.

You can also import the `chart.yml` tasks to get the njmonchart binary (see examples).

## Examples

```yaml
- name: Deploy and stat njmon
  ansible.builtin.import_role:
    name: njmon

# do your other tasks, resources will be recorded

- name: Install njmonchart and generate HTML outputs
  ansible.builtin.import_role:
    name: njmon
    tasks_from: chart.yml

- name: Cleanup njmon
  ansible.builtin.import_role:
    name: njmon
    tasks_from: cleanup.yml
```
