# Stackviz Integration for Tempest Results

## Overview
This integration automatically generates HTML visualization reports from Tempest test results using Stackviz. The reports are generated automatically after each Tempest run when using the test_operator role.

## Files Modified/Created

### New Files
- `tasks/generate-stackviz.yml` - Main task file that handles stackviz HTML generation

### Modified Files
- `tasks/run-test-operator-job.yml` - Added include statement to call stackviz generation after log collection
- `defaults/main.yml` - Added `cifmw_test_operator_generate_stackviz` configuration variable

## How It Works

1. **After tempest completes**, logs are collected from the test-operator PVCs
2. **The script searches** for `tempest_results.subunit.gz` in the artifacts directory
3. **Decompresses** the gzipped subunit file
4. **Runs stackviz-export** to convert subunit data to interactive HTML
5. **Stores the HTML report** in `<artifacts_basedir>/stackviz/html/index.html`

## Configuration

### Enable/Disable Stackviz Generation
```yaml
# In your scenario file or playbook variables
cifmw_test_operator_generate_stackviz: true  # Default: true
```

Set to `false` to disable stackviz generation.

## Output Location

After a successful tempest run, the stackviz HTML report will be available at:
```
~/ci-framework-data/tests/test_operator/stackviz/html/index.html
```

You can open this file directly in a web browser:
```bash
firefox ~/ci-framework-data/tests/test_operator/stackviz/html/index.html
```

Or via file:// URL in your browser.

## Dependencies

The role will automatically install required dependencies:
- `python3-pip` (system package)
- `stackviz` (Python package via pip)

## Integration with CI/CD Artifacts

To publish the stackviz HTML to your CI/CD system, you can add a task after the test_operator role runs:

### Example: Publishing to Jenkins/Zuul Artifacts
```yaml
- name: Upload stackviz HTML to artifacts storage
  ansible.builtin.copy:
    src: "{{ cifmw_test_operator_artifacts_basedir }}/stackviz/"
    dest: "{{ zuul.executor.log_root }}/stackviz/"
    remote_src: true
  when: stackviz_html_path is defined
```

### Example: Publishing to S3/Swift
```yaml
- name: Upload stackviz to object storage
  amazon.aws.s3_sync:
    bucket: "{{ ci_artifacts_bucket }}"
    file_root: "{{ cifmw_test_operator_artifacts_basedir }}/stackviz/html"
    key_prefix: "tempest-results/{{ zuul.build }}/stackviz"
  when: stackviz_html_path is defined
```

## Troubleshooting

### Subunit file not found
If you see the warning "No tempest_results.subunit.gz file found", check:
1. Tempest actually ran and completed
2. Logs were successfully collected from the PVCs
3. The expected file path: `{{ cifmw_test_operator_artifacts_basedir }}/**/tempest_results.subunit.gz`

### Stackviz export failed
Check the ansible output for the error message. Common issues:
- Corrupted subunit file
- Incompatible stackviz version
- Insufficient disk space

### Installation failures
If stackviz installation fails:
```bash
# Manually install stackviz
sudo pip3 install stackviz

# Or use a specific version
sudo pip3 install stackviz==0.28
```

## Example Usage

```yaml
- name: Run tempest tests with stackviz
  hosts: controller
  vars:
    cifmw_test_operator_generate_stackviz: true
    cifmw_test_operator_artifacts_basedir: "/home/zuul/tempest-artifacts"
  roles:
    - test_operator
```

## Future Enhancements

Potential improvements for this integration:
1. Add support for comparing multiple test runs
2. Integration with ReportPortal for centralized test reporting
3. Automatic upload to centralized artifact storage
4. Email notifications with stackviz report links
5. Support for other test frameworks (tobiko, etc.)
