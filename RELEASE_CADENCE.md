# CI Framework Release Cadence & Deprecation Process

**Document Version:** 1.0
**Last Updated:** September 22, 2025
**Status:** Proposed
**Owner:** CI Framework Team

## Executive Summary

This document outlines the CI Framework's proposed release cadence and deprecation process, designed to provide stability for downstream consumers while maintaining development velocity. The solution implements a bi-weekly release cycle with structured deprecation timelines.

## Table of Contents

- [Background](#background)
- [Release Cadence Solution](#release-cadence-solution)
- [Deprecation Process](#deprecation-process)
- [Enforcement Strategy](#enforcement-strategy)
- [Implementation Plan](#implementation-plan)
- [Success Metrics](#success-metrics)
- [Risk Mitigation](#risk-mitigation)
- [Appendices](#appendices)

## Background

### Current Challenges

Based on the CI tooling team discussion on September 17, 2025, the current workflow presents several challenges:

#### Workflow and Stability Disruptions

• **Daily Sync Instability**: The main branch currently syncs daily changes to the stable CI framework branch. This process causes frequent disruption and instability for users. Users complain about constant changes that distrupt their current workflows.

• **Lack of Versioning**: A significant challenge is the lack of project versioning and the practice of pushing changes directly to the main branch. This makes it difficult for end users to easily understand changes or decide when to update their jobs.

• **Predictability Issues**: The lack of a defined release cadence means there is no advance versioning or defined release time between main and stable branches. Consequently, users face unpredictable breaking changes.

#### Deprecation and Development Problems

• **Issues with Deprecation**: The current process creates problems when trying to deprecate and remove playbooks from the CI framework. Confusion was expressed regarding how a new release cadence would even assist with playbook deprecation.

• **Long-Term Project Submission**: The existing structure causes issues when submitting Pull Requests (PRs) for long-term development changes.

• **Conflicting Goals ("Chicken and Egg Problem")**: There is a "chicken and egg problem" of wanting to release breaking changes while simultaneously keeping customers undisrupted. This is exacerbated by the difficulty downstream teams have with long-term planning because they cannot rely on stable component availability.

#### User Compliance and Implementation Concerns

• **Ensuring Updates**: A challenge lies in ensuring all downstream CI jobs update to the designated stable branch or new tags.

• **Communication Gaps**: Breaking changes surprise downstream consumers because of communication gaps and the lack of advance notice for deprecated components.

• **Overhead Concerns**: Concerns were raised regarding the potential overhead and complexity of implementing a new structured system, such as a tagging system.

The proposed solution to these issues involves adopting a stable branch and tags approach, with a predictable bi-weekly release cadence.

### Team Consensus

The team agreed on the following principles:
- **Stable branch + tagging approach** over complex branching strategies
- **2-week release cycle** for predictable cadence with CalVer versioning
- **6-release minimum deprecation timeline** (12 weeks notice)
- **Automation-first enforcement** to reduce manual overhead

## Release Cadence Solution

### Overview

```
Development Flow:
main branch (development) → stable branch (auto-promoted when criteria met) → tagged releases (scheduled)
```

### Current State
- **Stable branch automation**: Already exists - automatically updates when validation criteria are met
- **Missing component**: Scheduled tagging process for predictable releases
- **Goal**: Implement bi-weekly tagging of stable branch for consumption

### Release Schedule

- **Frequency**: Every 2 weeks (bi-weekly)
- **Release Cycle**: 2 weeks
- **Release Day**: Tuesday of even-numbered weeks
- **Emergency Releases**: Hot-fix tags as needed

### Versioning Scheme

**Format:** `YYYY.WW.PATCH` (CalVer - Calendar Versioning)

- **YYYY**: Year
- **WW**: ISO week number (01-53 annually)
- **PATCH**: Hot-fix increment

**Examples:**
- `2025.42.0` - Week 42, 2025 release
- `2025.42.1` - Hot-fix for Week 42 release
- `2025.44.0` - Next release (2 weeks later)

### Release Process

#### Week 1: Active Development
- All development on `main` branch
- Continuous integration testing
- Feature development and bug fixes
- Stable branch automatically updates when criteria are met

#### Week 2: Release Tagging
- **Monday-Wednesday**: Continue development, the stable branch continues its auto-updates
- **Monday**: Evaluate current stable branch commit for release tagging
- **Tuesday**: Create release tag from stable branch, send release communication

#### Stable Branch Automation (Ongoing)
- **Automatic promotion**: Main → stable when validation criteria are met
- **No manual intervention**: Process runs continuously based on CI results
- **Release readiness**: Stable branch is always in a releasable state

### Tagging Process (To Be Implemented)

#### Release Tag Creation
```bash
# Automated script for bi-weekly releases
./scripts/create-release-tag

# Dry run to see what would happen
./scripts/create-release-tag --dry-run

# Force tagging even if stable branch is stale
FORCE=true ./scripts/create-release-tag
```

#### Tag Selection Criteria
- **Source**: Current HEAD of stable branch (automatically promoted)
- **Timing**: Every Tuesday at 15:00 UTC via automation
- **Validation**:
  - Verify stable branch has recent commits (within last 2 weeks)
  - Ensure stable branch passed all promotion criteria
  - Ensure there are no duplicate tags
- **Naming**: Follow CalVer format `YYYY.WW.PATCH`

#### Hot-fix Tags
- **Trigger**: Critical issues in current release
- **Process**: Cherry-pick fix to stable, create patch release
- **Example**: `2025.42.1` for hot-fix of `2025.42.0`
- **Automation**: Patch increment handled by `create-release-tag` script

### Branch Strategy

| Branch | Purpose | Update Frequency | Consumer Usage |
|--------|---------|-----------------|----------------|
| `main` | Active development | Continuous | CI Framework developers only |
| `stable` | Tested, ready for consumption | Automatic (when criteria met) | Available for consumption |
| Tags | Fixed release points | Every 2 weeks (Tuesday) | Required for production jobs |

## Deprecation Process

### Timeline Overview

**Total Timeline**: A minimum of 6 releases (12 weeks)

| Phase | Release | Timeline | Actions Required |
|-------|---------|----------|------------------|
| **Initial Notice** | Release N | Week 0 | Deprecation announcement, runtime warnings |
| **Reinforcement** | Release N+2 | Week 4 | Second notice, migration support |
| **Final Warning** | Release N+4 | Week 8 | Mandatory acknowledgment, legacy tag info |
| **Removal** | Release N+6 | Week 12 | Component removed from main branch |

### Phase 1: Initial Deprecation Notice (Week 0)

**Actions:**
- Email notification to all stakeholders
- Add runtime deprecation warnings to component
- Create migration documentation
- Update release notes with deprecation notice

**Required Information:**
- Component name and location
- Deprecation reason
- Migration path and alternative
- Removal timeline (specific release)

### Phase 2: Deprecation Reinforcement (Week 4)

**Actions:**
- Second email reminder to stakeholders
- Enhanced warning messages in component logs
- Migration support office hours announced
- Jira tickets created for affected teams

### Phase 3: Final Warning (Week 8)

**Actions:**
- Final removal notice email
- List of tags that will retain deprecated features
- Emergency contact information provided
- Mandatory team acknowledgment required

### Phase 4: Removal (Week 12)

**Actions:**
- Remove component from main branch
- Update all documentation
- Create legacy support tag references
- Monitor for post-removal issues

### Deprecation Notice Format

```yaml
# DEPRECATED: component_name
# Will be removed in release 2025.48.0
# Reason: Replaced by more efficient implementation
# Migration: Use new_component_name instead
# See: docs/migration/component_name.md

- name: Show deprecation warning
  debug:
    msg: |
      ⚠️  DEPRECATION WARNING ⚠️

      Component: {{ component_name }}
      Status: Will be removed in {{ removal_release }}

      🔄 MIGRATION REQUIRED:
      Replace with: {{ alternative }}
      Guide: docs/migration/{{ component_name }}.md

      📅 Timeline:
      - Now: Deprecated, warnings shown
      - {{ removal_release }}: Component removed
      - Legacy access: Available in current and earlier tags

      👥 Need help? Contact @ci-framework-team
  when:
    - cifmw_deprecation_warnings | default(true) | bool
  tags:
    - always
    - deprecation-warning
```

### Communication Templates

#### Stakeholder Notification Email
```
Subject: [CI Framework] Deprecation Notice - [COMPONENT] removal in 12 weeks

Dear Teams,

We are deprecating [COMPONENT] in CI Framework release [REMOVAL_RELEASE]
(scheduled for [DATE]).

Affected Components:
- [LIST OF COMPONENTS]

Migration Required:
- Replace with: [ALTERNATIVE]
- Migration guide: [DOCUMENTATION_LINK]
- Example changes: [EXAMPLE_LINK]

Timeline:
- Deprecation Notice: Today
- Final Removal: [REMOVAL_RELEASE] release (12 weeks)
- Last Supporting Tag: [CURRENT_RELEASE]

Action Required:
1. Review your jobs using deprecated components
2. Plan migration during next 6 weeks
3. Test with new components
4. Contact us for migration assistance

Questions? Reply to this email or contact the CI Framework team.
```

#### Release Announcement Template
```
Subject: [CI Framework] Release 2025.42.0 Available

Bi-weekly Release: 2025.42.0 (Week 42, 2025)
Previous Release: 2025.40.0 (2 weeks ago)

Release Highlights:
- New features: X, Y
- Bug fixes: A, B, C
- Deprecation warnings: playbook XYZ (removal in 2025.48.0)

Breaking Changes: None this release
Migration Required: None this release

Next Release: 2025.44.0 (in 2 weeks)
Legacy Support: 2025.34.0 through 2025.40.0 still supported

Usage Instructions:
- Update your job tags to: 2025.42.0
- Emergency rollback tags: 2025.40.0, 2025.38.0
```

## Enforcement Strategy

### Technical Enforcement

#### 1. Commit Validation

**Mature Python-Based Tools from [conventionalcommits.org](https://www.conventionalcommits.org/en/about/#tooling-for-conventional-commits):**
- **Gitlint**: Python-based conventional commits linter
  - Install: `pip install -r test-requirements.txt` (includes gitlint==0.19.1)
  - Config: `.gitlint` configuration file included
  - Usage: Automatic via pre-commit hooks

- **Commitizen**: Python conventional commits workflow tool
  - Install: `pip install -r test-requirements.txt` (includes commitizen==3.29.0)
  - Usage: `cz commit` for interactive commit creation
  - Supports: Auto-changelog generation and version bumping

- **Pre-commit**: Essential for automated validation
  - Install: `pip install pre-commit && pre-commit install --hook-type commit-msg`
  - Benefits: Battle-tested, community maintained, comprehensive features

**CI Framework Integration:**
- **Conventional Commits**: Handled entirely by gitlint via pre-commit hooks
- **Deprecation Compliance**: `scripts/check-deprecation.py` (CI Framework specific rules only)
- **Pre-commit Config**: `.pre-commit-config.yaml` (clean separation: gitlint + CI Framework specific tools)

#### 2. CI/CD Pipeline Gates
- **GitHub Actions**: Perform deprecation compliance checks on PRs
- **Zuul Integration**: Automated validation for OpenStack CI
- **Failure Conditions**: Will fail if missing migration docs or the timeline is insufficient

#### 3. Developer Tools

##### Deprecation Helper CLI
```bash
# Interactive deprecation workflow
./scripts/cifmw-deprecate --interactive

# Non-interactive usage
./scripts/cifmw-deprecate --component "playbooks/old.yml" \
  --type playbook --reason "Performance issues" \
  --alternative "playbooks/new.yml"
```

##### Status Dashboard
```bash
# View current deprecation status
./scripts/deprecation-status.py

# Export JSON report
./scripts/deprecation-status.py --export report.json
```

##### Conventional Commits Validation (Recommended Tools)
```bash
# Using Pre-commit (Recommended)
pip install pre-commit
pre-commit install

# Using Gitlint
pip install -r test-requirements.txt  # Includes gitlint + commitizen
pre-commit install --hook-type commit-msg

# Validate commit messages
gitlint --msg-filename path/to/commit-message.txt
gitlint lint --commits HEAD~5..HEAD  # Validate commit range

# Interactive commit creation with Commitizen
cz commit
```

### Process Enforcement

#### 1. Pull Request Templates
- Mandatory checklists for breaking changes
- Deprecation compliance verification
- Migration documentation requirements

#### 2. Code Review Standards
- Minimum 2 reviewers for deprecations
- Team lead approval for major changes
- Mandatory migration guide review

#### 3. Automated Monitoring
- Weekly compliance reports
- Slack/Teams alerts for violations
- Compliance threshold enforcement (85% minimum)

### Developer Experience

#### 1. Developer Setup & VS Code Integration

**Setup (Python only, no npm required):**
```bash
# Install and setup pre-commit (uses existing .pre-commit-config.yaml)
pip install pre-commit
pre-commit install

# Test validation
git commit -m "feat: add user authentication"
```

**VS Code Integration:**
- **Conventional Commit Snippets**: `.vscode/conventional-commits.code-snippets`
  - `ccfeat` - Feature commits
  - `ccfix` - Bug fix commits
  - `ccdeprecate` - Deprecation commits
  - `ccremove` - Removal commits
  - `depwarn` - Deprecation warnings for YAML files
- **Auto-completion**: Migration guide paths, component references

#### 2. Commit Validation Rules & Examples

**Conventional Commits Standard:**
- **Format**: `<type>[optional scope]: <description>`
- **Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- **Breaking changes**: Use `!` or `BREAKING CHANGE:` footer
- **Length**: Subject ≤ 72 chars, body lines ≤ 100 chars

**CI Framework Extensions:**
- **Deprecation commits** must reference migration docs
- **Removal commits** should specify target version (CalVer format)
- **Ansible changes** should include component paths
- **Breaking changes** need detailed descriptions

**Examples:**
```bash
# ✅ Good conventional commits
feat: add user authentication
fix(roles): correct variable name in deploy_bmh
feat!: deprecate legacy playbook xyz

BREAKING CHANGE: legacy playbook xyz removed, use abc instead
See: docs/migration/playbook-xyz.md

# ❌ Bad commits (will be rejected)
add some stuff
WIP: testing things
Update files
```

**Troubleshooting:**
```bash
# Fix formatting issues
echo "your message" | npx commitlint

# Generate proper templates
./scripts/cifmw-deprecate --interactive

# Skip validation (emergency only)
git commit --no-verify -m "hotfix: critical security patch"
```

#### 3. Documentation Templates
- Migration guide generators
- Deprecation notice formats
- Communication templates

## Implementation Plan

### Phase 1: Foundation Setup (Weeks 1-2)

**Week 1:**
- [ ] Deploy technical enforcement tools
  - `scripts/check-deprecation.py`
  - Pre-commit hooks configuration
  - CI/CD pipeline integration
- [ ] Create pull request templates
- [ ] Design automated tagging process

**Week 2:**
- [ ] Deploy developer CLI tools
  - `scripts/cifmw-deprecate`
  - VS Code snippets and templates
  - Documentation templates
- [ ] Implement automated tagging workflow
- [ ] Test tag creation and release process

### Phase 2: Process Integration (Weeks 3-4)

**Week 1:**
- [ ] Launch deprecation status dashboard
- [ ] Setup automated compliance monitoring

**Week 2:**
- [ ] Integrate with Jira for tracking
- [ ] Establish team review standards
- [ ] Test complete enforcement pipeline

### Phase 3: Team Adoption (Weeks 5-6)

**Week 1:**
- [ ] Establish compliance metrics (85% threshold)
- [ ] Launch peer review requirements

**Week 2:**
- [ ] Deploy notification integrations
- [ ] Create knowledge base documentation
- [ ] Conduct first compliance audit

### Phase 4: First Production Release (Weeks 7-8)

**Week 1:**
- [ ] Migrate consuming teams to tagged releases
- [ ] Validate job compatibility
- [ ] Monitor migration success

**Week 2:**
- [ ] Execute first official 2-week release
- [ ] Send stakeholder communications
- [ ] Monitor and gather feedback

### Phase 5: Optimization (Ongoing)

- [ ] Monitor compliance metrics
- [ ] Refine tools based on feedback
- [ ] Quarterly process reviews

## Success Metrics

### Release Cadence Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| On-time releases | 99% | Every Tuesday bi-weekly release |
| Release window | <2 hours | Monday validation to Tuesday tag |
| Zero surprise breakages | 100% | All breaking changes have 12-week notice |
| Quick adoption | 90% | Teams update to new tags within 2 weeks |

### Deprecation Process Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Advance notice compliance | 100% | All deprecations provide 12+ week notice |
| Migration guide coverage | 100% | Every deprecated item has replacement docs |
| Support escalations | <3 per deprecation | Teams can self-migrate with guides |
| Emergency rollbacks | 0 | No surprise removals requiring urgent fixes |

### Enforcement Effectiveness

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compliance rate | >85% | Automated deprecation process compliance |
| Tool usage | >90% | Deprecations using `cifmw-deprecate` helper |
| False positive rate | <5% | Incorrect automated compliance flags |

### Developer Experience

| Metric | Target | Measurement |
|--------|--------|-------------|
| Review efficiency | <2 days | Average deprecation PR review time |
| Tool satisfaction | >85% | Developer satisfaction with enforcement tools |
| Support tickets | <3 per deprecation | Migration assistance requests |

## Risk Mitigation

### High-Frequency Release Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Quality degradation due to speed | High | Automated quality gates, mandatory Monday validation |
| Team fatigue from bi-weekly releases | Medium | Full automation, minimal manual intervention |
| Insufficient testing time | High | Continuous testing on main, Monday gate validation |
| Communication overload | Medium | Automated announcements, digest format, opt-in notifications |

### Deprecation Process Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| 12 weeks too short for complex migrations | High | Extend to 18 weeks for major architectural changes |
| Teams miss notices in bi-weekly flow | Medium | Multi-channel notifications, mandatory acknowledgment |
| Tool maintenance overhead | Medium | Simple technologies, extensive test coverage |
| Process drift over time | Medium | Quarterly reviews, continuous monitoring |

### Enforcement Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Developer resistance to process | Medium | Excellent tooling, automation over manual work |
| Over-reliance on automation | Medium | Human review for major changes, regular audits |
| False security from tools | Low | Community feedback, effectiveness reviews |

## Appendices

### Appendix A: Tool Documentation

#### check-deprecation.py
- **Purpose**: Pre-commit validation of deprecation compliance
- **Usage**: Integrated with git hooks and CI pipelines
- **Validations**: Conventional commits, timeline compliance, documentation

#### cifmw-deprecate
- **Purpose**: Interactive deprecation workflow helper
- **Usage**: `./scripts/cifmw-deprecate --interactive`
- **Features**: Template generation, timeline calculation, documentation creation

#### deprecation-status.py
- **Purpose**: Compliance monitoring and reporting dashboard
- **Usage**: `./scripts/deprecation-status.py --export report.json`
- **Features**: Status tracking, compliance metrics, automated alerts

#### create-release-tag
- **Purpose**: Automated bi-weekly release tagging from stable branch
- **Usage**: `./scripts/create-release-tag [--dry-run] [--force]`
- **Features**: CalVer tagging, activity validation, release announcements

#### check-deprecation.py
- **Purpose**: CI Framework specific deprecation compliance validation
- **Usage**: `./scripts/check-deprecation.py --commit-msg "message"` or `--files file1 file2`
- **Features**: CalVer format validation, deprecation timeline checks, migration documentation validation
- **Note**: Conventional commits validation handled separately by gitlint

#### Mature Tools from Conventional Commits Ecosystem
- **Gitlint**: `pip install -r test-requirements.txt` (Python-based conventional commits linter)
- **Commitizen**: `pip install -r test-requirements.txt` (Interactive commit tool with auto-changelog)
- **Pre-commit**: `pip install pre-commit && pre-commit install --hook-type commit-msg` (Hook framework)

### Appendix B: Integration Examples

#### Current Pre-commit Configuration
```yaml
# .pre-commit-config.yaml (CI Framework setup with conventional commits)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
      - id: check-executables-have-shebangs
      - id: check-merge-conflict

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck

  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 24.8.0
    hooks:
      - id: black

  - repo: https://github.com/ansible/ansible-lint
    rev: v6.22.2
    hooks:
      - id: ansible-lint

  # Conventional commits validation using gitlint (mature Python solution)
  - repo: https://github.com/jorisroovers/gitlint
    rev: v0.19.1
    hooks:
      - id: gitlint
        stages: [commit-msg]
```


#### GitHub Actions Workflow
```yaml
# .github/workflows/commit-compliance.yml
name: Commit & Deprecation Compliance Check
on:
  pull_request:
    branches: [main, stable]
jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need full history for commit validation

      - name: Validate Conventional Commits
        run: |
          # Install and validate using commitlint (standard tool)
          npm install -g @commitlint/cli @commitlint/config-conventional
          npx commitlint --from origin/main --to HEAD --verbose

      - name: Check Deprecation Compliance
        run: |
          # Check changed files for deprecation compliance
          CHANGED_FILES=$(git diff --name-only origin/main..HEAD)
          if [ -n "$CHANGED_FILES" ]; then
            python scripts/check-deprecation.py --files $CHANGED_FILES
          fi

      - name: Generate Compliance Report
        if: failure()
        run: |
          echo "## Compliance Check Failed" >> $GITHUB_STEP_SUMMARY
          echo "Please ensure your commits follow conventional commit format" >> $GITHUB_STEP_SUMMARY
          echo "and deprecations include proper documentation." >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### Quick Fixes:" >> $GITHUB_STEP_SUMMARY
          echo "- Setup validation: \`pip install pre-commit && pre-commit install\`" >> $GITHUB_STEP_SUMMARY
          echo "- Setup guide: See Developer Experience section in this document" >> $GITHUB_STEP_SUMMARY
          echo "- Deprecation helper: \`./scripts/cifmw-deprecate --interactive\`" >> $GITHUB_STEP_SUMMARY
```

### Appendix C: Training Materials

#### Training Modules

1. **Understanding Deprecation Impact**
   - Why proper deprecation matters for CI stability
   - Cost of breaking changes to downstream consumers
   - CI Framework's commitment to predictable releases

2. **Technical Implementation**
   - How to use the `cifmw-deprecate` helper tool
   - Writing proper conventional commits
   - Creating migration documentation

3. **Process Compliance**
   - 6-release minimum timeline
   - Communication requirements
   - Code review standards

### Appendix D: Communication Standards

#### Team Standards
```yaml
deprecation_standards:
  mandatory_practices:
    - conventional_commits: "All breaking changes use conventional commit format"
    - migration_docs: "Every deprecation includes migration guide"
    - runtime_warnings: "Components show deprecation warnings during execution"
    - stakeholder_notification: "Email notifications sent to all affected teams"
    - minimum_timeline: "6 releases minimum between deprecation and removal"

  recommended_practices:
    - advance_communication: "Discuss major deprecations in team meetings"
    - user_support: "Offer migration assistance during deprecation period"
    - gradual_removal: "Phase out complex components over multiple releases"
    - testing_support: "Provide test environments for migration validation"

  forbidden_practices:
    - silent_removal: "Never remove components without proper deprecation"
    - immediate_breaking: "No same-release breaking changes"
    - insufficient_notice: "Less than 6 releases deprecation period"
    - missing_alternatives: "Deprecating without providing migration path"
```

---

**Document Status**: This plan requires team approval and stakeholder sign-off before implementation.

**Next Steps**:
1. Team review and feedback collection
2. Stakeholder notification and approval
3. Implementation timeline finalization
4. Tool deployment and testing

**Contact**: CI Framework Team for questions or feedback on this plan.
