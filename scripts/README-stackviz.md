# StackViz Integration with Test Operator

This document describes the StackViz integration for visualizing Tempest test results in the CI Framework.

## Overview

The `generate-stackviz-report.py` script processes Tempest test results from `.subunit` files and generates an interactive HTML visualization report. This integration is automatically triggered when running Tempest tests via the test_operator role.

## Requirements

### Python Dependencies

The script requires the following Python packages:
- **python-subunit**: For parsing subunit test result streams
- **testtools**: For test result processing

#### Dependency Checking

The integration automatically checks for required dependencies before generating reports. If dependencies are missing, you'll see a detailed error message with installation instructions.

#### Installation Methods

**Using pip:**
```bash
pip install python-subunit testtools
# or
pip3 install python-subunit testtools
```

**Using system package manager (RHEL/CentOS/Fedora):**
```bash
sudo dnf install python3-subunit python3-testtools
```

**Using system package manager (Ubuntu/Debian):**
```bash
sudo apt-get install python3-subunit python3-testtools
```

#### Auto-Install Dependencies (Optional)

You can enable automatic installation of missing dependencies by setting:

```yaml
cifmw_test_operator_stackviz_auto_install_deps: true
```

This will attempt to install missing packages using pip3 before generating the report. By default, this is disabled and you must install dependencies manually.

## How It Works

### Automatic Integration

When you run Tempest tests using the test_operator role:

1. **Test Execution**: Tempest tests run in test-operator pods
2. **Log Collection**: Test logs including `tempest_results.subunit.gz` are collected from PVCs
3. **Decompression**: The `.gz` file is automatically decompressed to `tempest_results.subunit`
4. **Report Generation**: The Python script generates `tempest-viz.html` with an interactive visualization
5. **Access**: The HTML file can be opened directly in any web browser

### File Locations

All artifacts are stored under the test_operator artifacts directory:

```
~/ci-framework-data/tests/test_operator/
└── stackviz/
    ├── tempest_results.subunit      # Decompressed subunit file
    └── tempest-viz.html              # Interactive HTML report
```

## Configuration Variables

### In `roles/test_operator/defaults/main.yml`:

- **`cifmw_test_operator_generate_stackviz`**: Enable/disable stackviz generation (default: `true`)
- **`cifmw_test_operator_stackviz_debug`**: Enable debug output during stackviz generation (default: `false`)
- **`cifmw_test_operator_stackviz_auto_install_deps`**: Automatically install missing Python dependencies using pip3 (default: `false`)
- **`cifmw_test_operator_artifacts_basedir`**: Base directory for test artifacts (default: `~/ci-framework-data/tests/test_operator`)

## Usage

### Using the Test Playbook

A test playbook is provided at `test-stackviz-integration.yml`:

```bash
ansible-playbook -i <inventory> test-stackviz-integration.yml
```

This will:
- Run a minimal Tempest smoke test
- Generate the stackviz report
- Display the report location and instructions to open it

### Manual Script Execution

You can also run the script manually on any `.subunit` file:

```bash
# Basic usage (output defaults to tempest-viz.html)
python3 scripts/generate-stackviz-report.py /path/to/tempest_results.subunit

# Specify custom output file
python3 scripts/generate-stackviz-report.py /path/to/input.subunit /path/to/output.html
```

### Opening the Report

#### On macOS:
```bash
open ~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```

#### On Linux:
```bash
xdg-open ~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```

#### Or manually:
Simply double-click the HTML file or open it in your preferred web browser.

## Report Features

The generated HTML report includes:

- **Summary Statistics**: Total, passed, failed, and skipped tests
- **Interactive Timeline**: Visualize test execution across workers with zoom/scroll capabilities
- **Searchable Test List**: Filter and search through all test results
- **Detailed Test Information**: Click on any test to view duration, status, and error details
- **Worker Visualization**: See parallel test execution across different workers

## Disabling StackViz Generation

To disable automatic stackviz generation, set the variable in your playbook or inventory:

```yaml
cifmw_test_operator_generate_stackviz: false
```

## Troubleshooting

### Missing Python Packages

If stackviz generation fails with a dependency error, you have two options:

**Option 1: Install manually (recommended)**
```bash
pip3 install python-subunit testtools
```

**Option 2: Enable auto-install**
Set in your playbook or inventory:
```yaml
cifmw_test_operator_stackviz_auto_install_deps: true
```

The error message will show exactly which packages are missing and provide specific installation commands for your system.

### No Subunit Files Found

If no `tempest_results.subunit.gz` files are found:
- Check that Tempest tests actually ran
- Verify log collection completed successfully
- Check the artifacts directory: `~/ci-framework-data/tests/test_operator/`

### Script Not Found

Ensure the script exists at:
```
<ci-framework-repo>/scripts/generate-stackviz-report.py
```

## Integration Details

The integration is implemented in the following files:

- **`scripts/generate-stackviz-report.py`**: The main stackviz generation script
- **`roles/test_operator/tasks/generate-stackviz.yml`**: Ansible tasks for automatic generation
- **`roles/test_operator/tasks/run-test-operator-job.yml`**: Integration point (includes generate-stackviz.yml)
- **`roles/test_operator/defaults/main.yml`**: Configuration variables
- **`test-stackviz-integration.yml`**: Example test playbook

## Example Workflow

```yaml
- name: Run Tempest tests with StackViz
  hosts: localhost
  vars:
    cifmw_test_operator_generate_stackviz: true
    cifmw_test_operator_stages:
      - name: smoke-tests
        type: tempest
    cifmw_test_operator_tempest_include_list: |
      tempest.api.identity.*
  roles:
    - role: test_operator
```

After execution, find your report at:
```
~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```
