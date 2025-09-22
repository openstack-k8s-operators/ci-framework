#!/usr/bin/env python3
"""
CI Framework Deprecation Configuration Rule for Gitlint
Enforces deprecation compliance rules integrated with gitlint workflow
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

from gitlint.options import IntOption
from gitlint.rules import ConfigurationRule, CommitRule, RuleViolation


class DeprecationConfigurationRule(ConfigurationRule):
    """
    Configuration rule that enforces CI Framework deprecation compliance.
    Applied before other gitlint rules to validate deprecation practices.
    """

    name = "ci-framework-deprecation-config"
    id = "CIFMW-CR1"  # CI Framework Configuration Rule 1

    options_spec = [
        IntOption("min-deprecation-weeks", 12, "Minimum weeks between deprecation notice and removal")
    ]

    def apply(self, config, commit):
        """Apply deprecation configuration rules to the commit"""
        self.log.debug("Checking CI Framework deprecation compliance")

        # Get current release for timeline validation
        current_release = self._get_current_release()

        # Check commit message for deprecation-related content
        commit_msg = commit.message.full

        if self._is_deprecation_commit(commit_msg):
            self.log.debug("Found deprecation-related commit")

            # Validate migration documentation references
            if not self._has_migration_reference(commit_msg):
                # Add custom property to trigger specific rule later
                commit.deprecation_missing_migration = True
                self.log.debug("Deprecation commit missing migration reference")

            # For deprecation commits, be more lenient on line length
            # since they might need longer explanations
            config.set_rule_option("body-max-line-length", "line-length", 120)

        # Check staged files for proper deprecation format
        staged_files = self._get_staged_files()
        for file_path in staged_files:
            if file_path.endswith(('.yml', '.yaml')):
                issues = self._check_file_deprecation_format(file_path, current_release)
                # Store issues on commit for later rule processing
                if not hasattr(commit, 'deprecation_file_issues'):
                    commit.deprecation_file_issues = []
                commit.deprecation_file_issues.extend(issues)

    def _get_current_release(self) -> str:
        """Get current release from git tags or generate from date"""
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except:
            # Fallback: generate CalVer based on current date
            now = datetime.now()
            week = now.isocalendar()[1]
            return f"{now.year}.{week:02d}.0"

    def _is_deprecation_commit(self, commit_msg: str) -> bool:
        """Check if commit is deprecation-related"""
        # Be more specific to avoid false positives
        deprecation_keywords = ['deprecat', 'obsolete', 'sunset']
        removal_keywords = ['remove.*deprecated', 'delete.*deprecated', 'drop.*deprecated']
        
        msg_lower = commit_msg.lower()
        
        # Check explicit deprecation keywords
        if any(keyword in msg_lower for keyword in deprecation_keywords):
            return True
            
        # Check removal of deprecated items (more specific)  
        return any(re.search(pattern, msg_lower) for pattern in removal_keywords)

    def _has_migration_reference(self, commit_msg: str) -> bool:
        """Check if commit references migration documentation"""
        migration_patterns = [
            r'docs/migration/',
            r'migration.*guide',
            r'see.*docs',
            r'alternative.*component',
            r'replaced.*by',
            r'use.*instead'
        ]
        return any(
            re.search(pattern, commit_msg, re.IGNORECASE)
            for pattern in migration_patterns
        )

    def _get_staged_files(self) -> List[str]:
        """Get list of staged files from git"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []

    def _check_file_deprecation_format(self, file_path: str, current_release: str) -> List[dict]:
        """Check file for proper deprecation format"""
        issues = []

        if not os.path.exists(file_path):
            return issues

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'deprecat' in line.lower():
                    # Check for proper CalVer format
                    pattern = r'# DEPRECATED.*?(\d{4}\.\d{2}\.\d+)'
                    match = re.search(pattern, line, re.IGNORECASE)

                    if not match:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'type': 'improper_format',
                            'message': f"Deprecation notice should follow CalVer format: '# DEPRECATED: Will be removed in release YYYY.WW.PATCH'"
                        })
                    else:
                        # Validate timeline if removal version is specified
                        removal_version = match.group(1)
                        timeline_issue = self._validate_deprecation_timeline(
                            current_release, removal_version
                        )
                        if timeline_issue:
                            timeline_issue['file'] = file_path
                            timeline_issue['line'] = i
                            issues.append(timeline_issue)

        except Exception as e:
            issues.append({
                'file': file_path,
                'line': 0,
                'type': 'read_error',
                'message': f"Could not read file: {e}"
            })

        return issues

    def _validate_deprecation_timeline(self, current_release: str, removal_release: str) -> dict:
        """Validate deprecation timeline meets minimum requirements"""
        try:
            # Parse CalVer format YYYY.WW.PATCH
            current_match = re.match(r'(\d{4})\.(\d{2})\.(\d+)', current_release)
            removal_match = re.match(r'(\d{4})\.(\d{2})\.(\d+)', removal_release)

            if not current_match or not removal_match:
                return {
                    'type': 'invalid_format',
                    'message': "Release versions should follow CalVer YYYY.WW.PATCH format"
                }

            current_year = int(current_match.group(1))
            current_week = int(current_match.group(2))
            removal_year = int(removal_match.group(1))
            removal_week = int(removal_match.group(2))

            # Calculate weeks difference
            current_total_weeks = current_year * 52 + current_week
            removal_total_weeks = removal_year * 52 + removal_week
            weeks_difference = removal_total_weeks - current_total_weeks

            min_weeks = self.options["min-deprecation-weeks"].value

            if weeks_difference < min_weeks:
                return {
                    'type': 'insufficient_timeline',
                    'message': f"Deprecation period too short: {weeks_difference} weeks. Minimum {min_weeks} weeks required."
                }

        except Exception as e:
            return {
                'type': 'timeline_error',
                'message': f"Could not validate timeline: {e}"
            }

        return None


class DeprecationCommitRule(CommitRule):
    """
    Commit rule that validates deprecation compliance based on
    data gathered by DeprecationConfigurationRule
    """

    name = "ci-framework-deprecation-violations"
    id = "CIFMW-C1"  # CI Framework Commit rule 1

    def validate(self, commit):
        """Validate commit for deprecation compliance violations"""
        violations = []

        # Check for missing migration reference in deprecation commits
        if hasattr(commit, 'deprecation_missing_migration') and commit.deprecation_missing_migration:
            violations.append(RuleViolation(
                self.id,
                "Deprecation commit should reference migration documentation or alternative component",
                line_nr=1
            ))

        # Report file-level deprecation format issues
        if hasattr(commit, 'deprecation_file_issues'):
            for issue in commit.deprecation_file_issues:
                violations.append(RuleViolation(
                    self.id,
                    f"{issue['file']}:{issue['line']} - {issue['message']}",
                    line_nr=1
                ))

        return violations
