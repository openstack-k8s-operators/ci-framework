# Multi-Stage StackViz Example

## Scenario: Workflow with Multiple Tempest Test Stages

This example demonstrates how stackviz handles multiple test stages in a single workflow.

### Playbook Configuration

```yaml
---
- name: Run multi-stage Tempest tests
  hosts: localhost
  vars:
    cifmw_test_operator_generate_stackviz: true
    cifmw_test_operator_stackviz_create_index: true

    cifmw_test_operator_stages:
      - name: workflow-tests
        type: tempest
        workflow:
          - step_name: ironic-scenario-testing
            include_list: |
              tempest.api.baremetal.test_basic
              tempest.api.baremetal.test_nodes
          - step_name: multi-thread-testing
            include_list: |
              tempest.scenario.test_server_basic_ops
              tempest.scenario.test_network_basic_ops
  roles:
    - role: test_operator
```

## What Happens

### 1. Tests Execute

Two separate Tempest test stages run:
- **Step 0**: `ironic-scenario-testing` - Tests baremetal API
- **Step 1**: `multi-thread-testing` - Tests scenarios with parallel execution

Each stage creates its own `tempest_results.subunit.gz` file in separate directories.

### 2. Logs Are Collected

```
~/ci-framework-data/tests/test_operator/
├── tempest-tests-tempest-s00-ironic-scenario-testing/
│   ├── tempest_results.subunit.gz
│   ├── tempest.log
│   └── (other logs)
└── tempest-tests-tempest-s01-multi-thread-testing/
    ├── tempest_results.subunit.gz
    ├── tempest.log
    └── (other logs)
```

### 3. StackViz Processing

The integration automatically:

```
[1/2] Processing: ironic-scenario-testing
  ✓ Decompressing tempest_results.subunit.gz
  ✓ Generating tempest-viz.html
  ✓ Report created: .../tempest-tests-tempest-s00-ironic-scenario-testing/tempest-viz.html

[2/2] Processing: multi-thread-testing
  ✓ Decompressing tempest_results.subunit.gz
  ✓ Generating tempest-viz.html
  ✓ Report created: .../tempest-tests-tempest-s01-multi-thread-testing/tempest-viz.html

Creating summary index...
  ✓ Summary index created: .../stackviz/index.html
```

### 4. Final Directory Structure

```
~/ci-framework-data/tests/test_operator/
├── tempest-tests-tempest-s00-ironic-scenario-testing/
│   ├── tempest_results.subunit.gz    # Original compressed
│   ├── tempest_results.subunit        # Decompressed
│   └── tempest-viz.html               # ← Interactive report for Step 0
│
├── tempest-tests-tempest-s01-multi-thread-testing/
│   ├── tempest_results.subunit.gz    # Original compressed
│   ├── tempest_results.subunit        # Decompressed
│   └── tempest-viz.html               # ← Interactive report for Step 1
│
└── stackviz/
    └── index.html                     # ← Summary index linking both reports
```

## Viewing the Reports

### Option 1: View Summary Index (Recommended)

Open the summary index to see links to all reports:

```bash
# macOS
open ~/ci-framework-data/tests/test_operator/stackviz/index.html

# Linux
xdg-open ~/ci-framework-data/tests/test_operator/stackviz/index.html
```

The index page shows:
- Total number of reports generated
- Clickable links to each stage's report
- Full paths for easy reference

### Option 2: View Individual Reports

Each report can be opened independently:

```bash
# Step 0 - Ironic tests
open ~/ci-framework-data/tests/test_operator/tempest-tests-tempest-s00-ironic-scenario-testing/tempest-viz.html

# Step 1 - Multi-thread tests
open ~/ci-framework-data/tests/test_operator/tempest-tests-tempest-s01-multi-thread-testing/tempest-viz.html
```

## Benefits of Multi-Stage Support

### 1. **Isolated Analysis**
Each test stage has its own dedicated report, making it easy to:
- Analyze failures specific to one stage
- Compare test durations between stages
- Focus on a particular test suite without noise from others

### 2. **Easy Navigation**
The summary index provides:
- Quick overview of all test stages
- Direct links to each report
- No need to hunt through directories

### 3. **Efficient Processing**
- Dependency checking done once (not per file)
- All reports generated in a single pass
- Parallel-friendly design

### 4. **Flexible Viewing**
- View individual reports independently
- Use summary index for overview
- Share specific stage reports with team members

## Disabling Summary Index

If you prefer not to create the summary index:

```yaml
cifmw_test_operator_stackviz_create_index: false
```

Reports will still be generated in each stage directory, but no summary index will be created.

## Example Output

### Console Output During Generation

```
TASK [test_operator : Display found subunit.gz files]
ok: [localhost] => {
    "msg": "Found 2 subunit.gz file(s)"
}

TASK [test_operator : Display processing information]
ok: [localhost] => {
    "msg": "Processing [1/2]: tempest-tests-tempest-s00-ironic-scenario-testing"
}

TASK [test_operator : Display success for this report]
ok: [localhost] => {
    "msg": "✓ Generated report for tempest-tests-tempest-s00-ironic-scenario-testing: .../tempest-viz.html"
}

TASK [test_operator : Display processing information]
ok: [localhost] => {
    "msg": "Processing [2/2]: tempest-tests-tempest-s01-multi-thread-testing"
}

TASK [test_operator : Display success for this report]
ok: [localhost] => {
    "msg": "✓ Generated report for tempest-tests-tempest-s01-multi-thread-testing: .../tempest-viz.html"
}

TASK [test_operator : Display stackviz summary]
ok: [localhost] => {
    "msg": [
        "===================================================",
        "Stackviz Report Generation Complete!",
        "",
        "Total Reports Generated: 2",
        "",
        "- tempest-tests-tempest-s00-ironic-scenario-testing",
        "  ~/ci-framework-data/tests/test_operator/tempest-tests-tempest-s00-ironic-scenario-testing/tempest-viz.html",
        "- tempest-tests-tempest-s01-multi-thread-testing",
        "  ~/ci-framework-data/tests/test_operator/tempest-tests-tempest-s01-multi-thread-testing/tempest-viz.html",
        "",
        "Summary Index: ~/ci-framework-data/tests/test_operator/stackviz/index.html",
        "",
        "To view all reports:",
        "open ~/ci-framework-data/tests/test_operator/stackviz/index.html",
        "==================================================="
    ]
}
```

## Use Cases

### Development & Debugging
- Run specific test stages
- Quickly identify which stage is failing
- Drill down into stage-specific issues

### CI/CD Integration
- Archive individual reports for each stage
- Track metrics per stage over time
- Identify performance regressions in specific test suites

### Team Collaboration
- Share stage-specific reports with domain experts
- Ironic team reviews Step 0, Network team reviews Step 1
- Avoid overwhelming stakeholders with unrelated test results

## Summary

The multi-stage stackviz integration provides:
- ✅ Automatic detection of multiple test stages
- ✅ Individual reports per stage in their own directories
- ✅ Summary index for easy navigation
- ✅ Efficient single-pass processing
- ✅ No manual intervention required
- ✅ Fully configurable via Ansible variables
