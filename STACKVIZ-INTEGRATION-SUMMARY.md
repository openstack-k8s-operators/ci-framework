# StackViz Integration Summary

## Overview

Successfully integrated StackViz report generation with test-operator for Tempest test visualization. The integration includes:
- Comprehensive dependency checking and optional auto-installation
- **Multi-stage support** - Generates separate reports for each test stage/workflow step
- Summary index page linking all generated reports
- Individual reports stored alongside their respective subunit files

## Key Features

### Multi-Stage Test Support

The integration handles multiple test stages intelligently:

**Scenario:** Multiple tempest test stages in a workflow
```
test_operator/
├── tempest-tests-tempest-s00-ironic-scenario-testing/
│   └── tempest-viz.html
├── tempest-tests-tempest-s01-multi-thread-testing/
│   └── tempest-viz.html
└── stackviz/
    └── index.html  (links to all reports)
```

**How it works:**
1. Finds all `tempest_results.subunit.gz` files recursively
2. Processes each file individually:
   - Decompresses in the same directory
   - Generates HTML report in the same directory
3. Creates a summary index with links to all reports
4. Each report is self-contained and can be viewed independently

## Files Added

1. **scripts/generate-stackviz-report.py**
   - Python script that processes .subunit files and generates interactive HTML reports
   - Creates timeline visualization, test statistics, and detailed test information

2. **roles/test_operator/tasks/generate-stackviz.yml**
   - Main orchestration for stackviz generation
   - Dependency checking (done once, not per file)
   - Loops through all found subunit files
   - Creates summary index page
   - Optional auto-installation of missing dependencies

3. **roles/test_operator/tasks/generate-stackviz-single.yml**
   - Processes individual subunit files
   - Handles decompression in the source directory
   - Generates HTML reports alongside subunit files
   - Tracks generated reports for summary index

4. **scripts/README-stackviz.md**
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
| `cifmw_test_operator_stackviz_create_index` | `true` | Create summary index when multiple reports exist |

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
Logs Collected (including all tempest_results.subunit.gz files)
         ↓
Find All Subunit Files Recursively
         ↓
Dependency Check (once for all files)
         ↓
   [Missing?] → Auto-install (if enabled) → Re-check
         ↓
   [OK] → For Each Subunit File:
         ├─ Decompress .gz in same directory
         ├─ Generate HTML in same directory
         └─ Add to reports list
         ↓
Create Summary Index (links to all reports)
         ↓
Reports Available:
  - Individual: <stage-dir>/tempest-viz.html
  - Summary: stackviz/index.html
```

### File Structure

**Single Stage:**
```
~/ci-framework-data/tests/test_operator/
└── tempest-tests-tempest/
    ├── tempest_results.subunit.gz   # Original
    ├── tempest_results.subunit      # Decompressed
    └── tempest-viz.html              # Report
```

**Multiple Stages (Workflow):**
```
~/ci-framework-data/tests/test_operator/
├── tempest-tests-tempest-s00-ironic-scenario-testing/
│   ├── tempest_results.subunit.gz
│   ├── tempest_results.subunit
│   └── tempest-viz.html              # Stage 0 report
├── tempest-tests-tempest-s01-multi-thread-testing/
│   ├── tempest_results.subunit.gz
│   ├── tempest_results.subunit
│   └── tempest-viz.html              # Stage 1 report
└── stackviz/
    └── index.html                    # Summary with links to all
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
2. **Multi-Stage Support**: Automatically handles workflows with multiple test stages
3. **Individual Reports**: Each stage gets its own report in its directory
4. **Summary Index**: Easy navigation between multiple reports via index page
5. **Robust Dependency Checking**: Clear errors with actionable solutions
6. **Optional Auto-Install**: Can automatically resolve missing dependencies
7. **Interactive Visualization**: Rich HTML report with timeline, filtering, and search
8. **Cross-Platform**: Works on macOS, Linux, and WSL
9. **Self-Contained**: Single HTML file with embedded JavaScript
10. **No External Dependencies**: Reports work offline without internet

## Next Steps

1. Test the integration with actual Tempest runs
2. Consider adding more visualization options
3. Potentially integrate with other test frameworks (tobiko, etc.)
4. Add report archiving capabilities
5. Consider adding report comparison features

## Troubleshooting

See `scripts/README-stackviz.md` for detailed troubleshooting information.
