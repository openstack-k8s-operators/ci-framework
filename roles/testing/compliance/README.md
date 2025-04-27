# Compliance Role

Execute compliance scans on the control plane via the [compliance-operator](https://github.com/openshift/compliance-operator)
as well as OpenSCAP [scans](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/security_hardening/scanning-the-system-for-configuration-compliance-and-vulnerabilities_security-hardening#configuration-compliance-tools-in-rhel_scanning-the-system-for-configuration-compliance-and-vulnerabilities) against the compute nodes.  Retrieve compliance results and generate reports.

The parameter `cifmw_compliance_suites` is used to specify the compliance suites to be scanned.  Each suite is related to specific
compliance profiles through the `cifmw_compliance_scan_settings` parameter.

When a suite is included, a scansettingbinding is created for each profile (`<suite>-<profile>-binding`).  This triggers
various compliance scans associated with each profile.  The results are aggregated and are used to generate reports.  The results and
reports are stored in `cifmw_compliance_artifacts_basedir/<suite>`.

Note that while it is possible to associate more than one profile with a scansettingbinding, this can lead to errors with resource
contention if too many scans are running at once.  Therefore, we only associate one profile per scansettingbinding - and we wait
until the compliance scans complete or error out before moving on to the next profile.

## Parameters

* `cifmw_compliance_artifacts_basedir`: (String) Directory where we will have all test-operator related files. Default value: `{{ cifmw_basedir }}/tests/compliance` which defaults to `~/ci-framework-data/tests/compliance`
* `cifmw_compliance_cleanup`: (Boolean) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_compliance_compute_artifacts_basedir`: (String) Directory for the results of compute node scans.  Default value: `~/compliance-scans`
* `cifmw_compliance_compute_profiles: (List of Strings) Profiles to use when scanning compute nodes. Default value:
```
  - pci-dss
  - e8
  - stig
```
* `cifmw_compliance_dry_run`: (Boolean) Whether the compliance-operator should and OpenSCAP scans should run or not.  Default value: `false`
* `cifmw_compliance_namespace`: (String) Namespace inside which all the resources are created. Default value: `openshift-compliance`
* `cifmw_compliance_plugin_image`: (String) Image to use to extract the oc compliance plugin. Default value: `registry.redhat.io/compliance/oc-compliance-rhel8:stable`
* `cifmw_compliance_podman_password`: (String) password to log into registry to retrieve image for oc compliance plugin
* `cifmw_compliance_podman_registry`: (String) registry to get image for oc compliance plugin.  Default value: registry.redhat.io
* `cifmw_compliance_podman_username`: (String) user to log into registry to retrieve image for oc compliance plugin
* `cifmw_compliance_scan_settings`: (Dictionary) Dictionary that maps compliance suites to compliance profiles.  Default value:
```
  cis:
    - ocp4-cis
        #- ocp4-cis-node
  e8:
    - ocp4-e8
    - rhcos4-e8
  high:
    - ocp4-high
    - ocp4-high-node
    - rhcos4-high
  moderate:
    - ocp4-moderate
    - ocp4-moderate-node
    - rhcos4-moderate
  nerc-cip:
    - ocp4-nerc-cip
    - ocp4-nerc-cip-node
    - rhcos4-nerc-cip
  pci-dss:
    - ocp4-pci-dss
    - ocp4-pci-dss-node
  stig:
    - ocp4-stig
    - ocp4-stig-node
    - rhcos4-stig
```
* `cifmw_compliance_scap_content_file`: (String) File to get scap profile content in compute scans. Default value: `/usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml`
* `cifmw_compliance_suites`: (List of Strings) Scan settings to execute.  Default value:
```
  - cis
  - e8
  - high
  - moderate
  - nerc-cip
  - pci-dss
  - stig
```
