# StackViz Integration Summary

## Overview

Successfully integrated StackViz report generation with test-operator for Tempest test visualization. The integration includes comprehensive dependency checking and optional auto-installation of required Python packages.

## Files Added

1. **scripts/generate-stackviz-report.py**
   - Python script that processes .subunit files and generates interactive HTML reports
   - Creates timeline visualization, test statistics, and detailed test information

2. **roles/test_operator/tasks/generate-stackviz.yml**
   - Ansible tasks for automatic stackviz generation
   - Includes robust dependency checking
   - Handles decompression of .gz files
   - Optional auto-installation of missing dependencies

3. **scripts/README-stackviz.md**
   - Comprehensive documentation
   - Installation instructions
   - Usage examples
   - Troubleshooting guide

## Files Modified

1. **roles/test_operator/tasks/run-test-operator-job.yml**
   - Added call to generate-stackviz.yml after log collection
   - Only runs for tempest tests when enabled

2. **roles/test_operator/defaults/main.yml**
   - Added three new configuration variables (see below)

3. **test-stackviz-integration.yml**
   - Updated to match single-file output structure
   - Added browser auto-open capability

## New Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_test_operator_generate_stackviz` | `true` | Enable/disable automatic stackviz generation |
| `cifmw_test_operator_stackviz_debug` | `false` | Enable debug output during generation |
| `cifmw_test_operator_stackviz_auto_install_deps` | `false` | Automatically install missing Python packages |

## Dependency Checking Features

### 1. Individual Package Checks
The integration checks each required package separately:
- **python-subunit**: Required for parsing subunit streams
- **testtools**: Required for test result processing

### 2. Detailed Error Messages
If dependencies are missing, users receive:
- List of specific missing packages
- Installation commands for pip/pip3
- Distribution-specific installation commands (DNF, APT)
- Clear next steps

### 3. Optional Auto-Installation
When `cifmw_test_operator_stackviz_auto_install_deps: true`:
- Automatically attempts to install missing packages via pip3
- Re-checks installation success
- Only proceeds with report generation if successful
- Provides feedback on installation status

### 4. Smart Validation
The dependency check:
- Runs before attempting report generation
- Prevents cryptic Python import errors
- Fails fast with actionable error messages
- Can be bypassed by disabling stackviz generation

## Workflow

### Automatic Process

```
Tempest Tests Complete
         ↓
Logs Collected (including tempest_results.subunit.gz)
         ↓
Dependency Check
         ↓
   [Missing?] → Auto-install (if enabled) → Re-check
         ↓
   [OK] → Decompress .gz → Generate HTML
         ↓
Report Available: stackviz/tempest-viz.html
```

### File Structure

```
~/ci-framework-data/tests/test_operator/
└── stackviz/
    ├── tempest_results.subunit      # Decompressed input
    └── tempest-viz.html              # Interactive report
```

## Usage Examples

### Basic Usage (Auto-enabled)
```yaml
- name: Run Tempest tests
  hosts: localhost
  roles:
    - role: test_operator
```

### With Auto-Install Dependencies
```yaml
- name: Run Tempest tests with auto-install
  hosts: localhost
  vars:
    cifmw_test_operator_stackviz_auto_install_deps: true
  roles:
    - role: test_operator
```

### Disable StackViz
```yaml
- name: Run Tempest tests without stackviz
  hosts: localhost
  vars:
    cifmw_test_operator_generate_stackviz: false
  roles:
    - role: test_operator
```

### Manual Script Usage
```bash
# Install dependencies first
pip3 install python-subunit testtools

# Generate report
python3 scripts/generate-stackviz-report.py \
  /path/to/tempest_results.subunit \
  /path/to/output.html
```

## Error Handling

### Missing Dependencies (Example Output)
```
TASK [test_operator : Display installation instructions if packages are missing]
fatal: [localhost]: FAILED! => {
    "msg": |
      ERROR: Required Python packages are missing for stackviz report generation.

      Missing packages: python-subunit, testtools

      Please install the missing packages using one of the following methods:

      Using pip:
        pip install python-subunit testtools

      Using pip3:
        pip3 install python-subunit testtools

      Using system package manager (RHEL/CentOS/Fedora):
        sudo dnf install python3-subunit python3-testtools

      Using system package manager (Ubuntu/Debian):
        sudo apt-get install python3-subunit python3-testtools

      After installing the packages, re-run the playbook.
}
```

### No Subunit Files Found
```
TASK [test_operator : Display warning when no subunit files found]
ok: [localhost] => {
    "msg": "WARNING: No tempest_results.subunit.gz files found in
            ~/ci-framework-data/tests/test_operator.
            Stackviz report generation skipped."
}
```

## Testing

Use the provided test playbook:
```bash
ansible-playbook -i <inventory> test-stackviz-integration.yml
```

To test with auto-install:
```bash
ansible-playbook -i <inventory> test-stackviz-integration.yml \
  -e cifmw_test_operator_stackviz_auto_install_deps=true
```

## Opening Reports

### macOS
```bash
open ~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```

### Linux
```bash
xdg-open ~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```

### Windows (WSL)
```bash
explorer.exe ~/ci-framework-data/tests/test_operator/stackviz/tempest-viz.html
```

Or simply double-click the HTML file in your file browser.

## Benefits

1. **Automatic Integration**: No manual steps needed after test execution
2. **Robust Dependency Checking**: Clear errors with actionable solutions
3. **Optional Auto-Install**: Can automatically resolve missing dependencies
4. **Interactive Visualization**: Rich HTML report with timeline, filtering, and search
5. **Cross-Platform**: Works on macOS, Linux, and WSL
6. **Self-Contained**: Single HTML file with embedded JavaScript
7. **No External Dependencies**: Report works offline without internet

## Next Steps

1. Test the integration with actual Tempest runs
2. Consider adding more visualization options
3. Potentially integrate with other test frameworks (tobiko, etc.)
4. Add report archiving capabilities
5. Consider adding report comparison features

## Troubleshooting

See `scripts/README-stackviz.md` for detailed troubleshooting information.
