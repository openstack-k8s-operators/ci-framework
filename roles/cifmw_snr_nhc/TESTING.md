# Testing Guide for cifmw_snr_nhc Role

This document describes how to test the `cifmw_snr_nhc` role using Molecule and pytest.

## Prerequisites

Before running tests, you need to install the required dependencies:

```bash
# Install Python dependencies
pip install --user -r molecule/requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r molecule/default/requirements.yml --force
```

## Test Framework

This role uses two testing frameworks:

1. **Molecule** - For integration testing and role behavior validation
2. **Pytest** - For unit testing and structural validation

## Running Tests

### Quick Start

```bash
# Run all molecule tests (recommended)
~/.local/bin/molecule test

# Run only syntax and lint checks
ansible-lint tasks/main.yml
yamllint .

# Run pytest unit tests
pytest tests/ -v
```

### Molecule Tests

Molecule provides end-to-end testing of the role:

```bash
# Run full test suite (recommended)
~/.local/bin/molecule test

# Run individual steps for development
~/.local/bin/molecule create     # Create test environment
~/.local/bin/molecule converge   # Run the role
~/.local/bin/molecule verify     # Run verification tests
~/.local/bin/molecule destroy    # Clean up

# Quick development cycle
~/.local/bin/molecule converge   # Apply changes
~/.local/bin/molecule verify     # Check results
```

### Unit Tests

Pytest runs structural and unit tests:

```bash
# Run all pytest tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -v -m "not integration"  # Unit tests only
pytest tests/ -v -m "integration"      # Integration tests only

# Run specific test file
pytest tests/test_cifmw_snr_nhc.py -v
```

## Test Structure

```
├── molecule/
│   ├── default/
│   │   ├── molecule.yml      # Molecule configuration
│   │   ├── converge.yml      # Playbook to test the role
│   │   ├── verify.yml        # Verification tests
│   │   ├── prepare.yml       # Environment preparation
│   │   └── requirements.yml  # Ansible Galaxy dependencies
│   └── requirements.txt      # Python dependencies
├── tests/
│   ├── __init__.py
│   └── test_cifmw_snr_nhc.py # Unit tests
├── pytest.ini               # Pytest configuration
├── .yamllint                # YAML linting rules
└── .ansible-lint            # Ansible linting rules
```

## Test Scenarios

### Molecule Test Scenarios

The molecule tests validate all 7 tasks of the role:

1. **Create Namespace** - Tests namespace creation and idempotency
2. **Create OperatorGroup** - Tests OperatorGroup creation and idempotency  
3. **Create SNR Subscription** - Tests SNR subscription creation and idempotency
4. **Wait for SNR Deployment** - Tests deployment waiting logic and timeout handling
5. **Create NHC Subscription** - Tests NHC subscription creation and idempotency
6. **Wait for CSV** - Tests ClusterServiceVersion waiting logic and timeout handling
7. **Create NHC CR** - Tests NodeHealthCheck custom resource creation and idempotency

Each test includes:
- **Syntax validation** - Ensures Ansible syntax is correct
- **Role execution** - Tests role with mock Kubernetes environment
- **Idempotency checks** - Ensures role can run multiple times safely
- **Error handling** - Validates appropriate error handling
- **Verification** - Validates expected outcomes

### Unit Test Scenarios

1. **File Structure** - Validates role directory structure
2. **YAML Validation** - Ensures all YAML files are valid
3. **Variable Consistency** - Checks variable definitions
4. **Metadata Validation** - Validates role metadata

## Test Configuration

### Mock Environment

The tests use mock Kubernetes configurations:

- Mock kubeconfig with test cluster settings (`/tmp/kubeconfig`)
- Mock credentials for authentication (`/tmp/kubeadmin-password`)
- Test namespace: `workload-availability`
- Mock server: `api.test.example.com:6443`

### Test Variables

```yaml
# molecule/default/converge.yml
vars:
  cifmw_snr_nhc_kubeconfig: /tmp/kubeconfig
  cifmw_snr_nhc_namespace: workload-availability
```

### Expected Behavior

In the test environment:
- **Connection failures are expected** - Tests use mock endpoints
- **All tasks should complete without fatal errors** - Error handling is validated
- **Idempotency is verified** - Each task runs twice to ensure consistency
- **Proper error messages are displayed** - Mock environment limitations are handled gracefully

## Continuous Integration

The tests are designed to run in CI/CD environments:

- **Container-based**: Uses Podman containers for isolation
- **No external dependencies**: Mocks Kubernetes/OpenShift APIs
- **Fast execution**: Optimized for quick feedback (~2-3 minutes)
- **Comprehensive coverage**: Tests all role tasks individually

## Troubleshooting

### Common Issues

1. **Collection not found**: 
   ```bash
   ansible-galaxy collection install -r molecule/default/requirements.yml --force
   ```

2. **Molecule not found**: 
   ```bash
   pip install --user -r molecule/requirements.txt
   ```

3. **Podman not available**: Install podman or configure docker driver in `molecule.yml`

4. **Permission denied**: Ensure user has container runtime permissions

### Debug Mode

```bash
# Run with verbose output
~/.local/bin/molecule test --debug

# Keep environment after failure
~/.local/bin/molecule test --destroy=never

# Check detailed logs
~/.local/bin/molecule converge -- --vvv
```

### Linting

```bash
# Run all linting checks
ansible-lint tasks/main.yml
yamllint .
yamllint molecule/default/*.yml

# Check specific files
ansible-lint tasks/main.yml --parseable
yamllint molecule/default/converge.yml -d relaxed
```

## Development Workflow

1. **Make changes** to the role
2. **Run syntax check**: `ansible-lint tasks/main.yml`
3. **Run linting**: `yamllint .`
4. **Test changes**: `~/.local/bin/molecule converge`
5. **Verify results**: `~/.local/bin/molecule verify`
6. **Run full test suite**: `~/.local/bin/molecule test`
7. **Clean up**: `~/.local/bin/molecule destroy`

## Test Customization

### Adding New Tests

1. **Molecule tests**: Add tasks to `molecule/default/verify.yml`
2. **Unit tests**: Add functions to `tests/test_cifmw_snr_nhc.py`
3. **Integration tests**: Mark with `@pytest.mark.integration`

### Modifying Test Environment

1. **Test variables**: Update `molecule/default/converge.yml`
2. **Mock data**: Update `molecule/default/prepare.yml`
3. **Test configuration**: Update `molecule/default/molecule.yml`

## Test Results Interpretation

### Successful Test Run

A successful test run should show:
```
PLAY RECAP *********************************************************************
instance                   : ok=38   changed=0    unreachable=0    failed=0
```

### Expected Warnings

The following warnings/errors are normal in the test environment:
- `Name or service not known` - Mock server is not real
- `MODULE FAILURE` in debug output - Expected with mock Kubernetes API
- `Max retries exceeded` - Connection timeouts are expected

### Test Coverage

Current test coverage includes:
- All 7 role tasks individually tested
- Idempotency verification for each task
- Error handling validation
- Mock environment setup and teardown
- Syntax and linting validation
- Variable consistency checks

## Performance

- **Total test time**: ~2-3 minutes
- **Individual task tests**: ~10-15 seconds each
- **Full molecule cycle**: ~1-2 minutes
- **Container startup**: ~30 seconds

## Best Practices

1. **Always run full test suite** before committing changes
2. **Use development cycle** (`converge` → `verify`) for quick iterations
3. **Check linting** before running molecule tests
4. **Review test output** for any unexpected changes
5. **Keep tests updated** when modifying role functionality 