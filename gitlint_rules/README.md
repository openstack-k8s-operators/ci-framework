# CI Framework Custom Gitlint Rules

This directory contains custom gitlint rules for enforcing CI Framework specific deprecation compliance.

## Overview

Deprecation validation is integrated directly into gitlint using [Configuration Rules](https://jorisroovers.com/gitlint/latest/rules/user_defined_rules/configuration_rules/). This provides:

- **Integrated workflow**: Part of existing gitlint validation in pre-commit
- **Dynamic behavior**: Rules can modify gitlint behavior based on commit content
- **Better error reporting**: Leverages gitlint's violation system
- **Cleaner architecture**: No separate tool to maintain

## Rules

### DeprecationConfigurationRule (CIFMW-CR1)
- **Type**: Configuration Rule (runs before other rules)
- **Purpose**: Detects deprecation-related commits and configures validation behavior
- **Features**:
  - Detects commits with deprecation keywords (`deprecate`, `remove`, `delete`, etc.)
  - Validates migration documentation references in commit messages
  - Checks staged files for proper deprecation format (CalVer)
  - Validates deprecation timeline (minimum 12 weeks by default)
  - Adjusts body line length to 120 chars for deprecation commits

### DeprecationCommitRule (CIFMW-C1)
- **Type**: Commit Rule (validates based on configuration rule findings)
- **Purpose**: Reports specific deprecation compliance violations
- **Violations**:
  - Missing migration documentation references
  - Improper deprecation format in files
  - Insufficient deprecation timeline

## Configuration

The rules support configuration options in `.gitlint`:

```ini
[CIFMW-CR1]
# Minimum weeks between deprecation notice and removal (default: 12)
min-deprecation-weeks=12
```

## Expected Deprecation Format

### Commit Messages
Deprecation commits should reference migration documentation:
```
refactor: deprecate old authentication module

This removes the deprecated auth module. See docs/migration/auth-migration.md
for alternative components.

Signed-off-by: Developer <dev@example.com>
```

### File Format (YAML/Ansible)
```yaml
# DEPRECATED: Will be removed in release 2025.52.0
# Migration: Use new_auth_module instead, see docs/migration/auth-migration.md
- name: Old auth task
```

## Testing

Test the rules with various commit messages:

```bash
# Valid deprecation commit
echo "refactor: deprecate auth module

See docs/migration/auth.md for alternatives.

Signed-off-by: Dev <dev@example.com>" | gitlint --msg-filename /dev/stdin

# Invalid (missing migration reference)
echo "refactor: remove old module

No migration info provided." | gitlint --msg-filename /dev/stdin
```
