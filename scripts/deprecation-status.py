#!/usr/bin/env python3
"""
Deprecation Status Dashboard
Tracks and reports on deprecation compliance across the CI Framework
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class DeprecatedComponent:
    name: str
    type: str  # playbook, role, task, etc.
    file_path: str
    deprecated_in: str
    removal_target: str
    alternative: Optional[str]
    has_migration_doc: bool
    has_runtime_warning: bool
    weeks_until_removal: int
    status: str  # active, deprecated, overdue, removed


class DeprecationTracker:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.current_release = self._get_current_release()
        self.deprecated_components: List[DeprecatedComponent] = []

    def _get_current_release(self):
        """Get current release version"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True, text=True, check=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except:
            # Fallback
            now = datetime.now()
            week = now.isocalendar()[1]
            return f"{now.year}.{week:02d}.0"

    def _calculate_weeks_until_removal(self, removal_release):
        """Calculate weeks until component removal"""
        try:
            # Parse releases (YYYY.WW.PATCH)
            current_match = re.match(r'(\d{4})\.(\d+)\.(\d+)', self.current_release)
            removal_match = re.match(r'(\d{4})\.(\d+)\.(\d+)', removal_release)

            if not current_match or not removal_match:
                return -1

            current_year = int(current_match.group(1))
            current_week = int(current_match.group(2))
            removal_year = int(removal_match.group(1))
            removal_week = int(removal_match.group(2))

            # Calculate weeks difference accounting for year rollover
            current_total_weeks = current_year * 52 + current_week
            removal_total_weeks = removal_year * 52 + removal_week

            return removal_total_weeks - current_total_weeks
        except:
            return -1

    def _check_migration_doc_exists(self, component_name):
        """Check if migration documentation exists"""
        doc_name = component_name.replace('/', '_')
        migration_paths = [
            self.repo_path / f"docs/migration/{doc_name}.md",
            self.repo_path / f"docs/deprecation/{doc_name}.md"
        ]
        return any(path.exists() for path in migration_paths)

    def _check_runtime_warning(self, file_path):
        """Check if file contains runtime deprecation warnings"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            warning_patterns = [
                r'deprecat.*warning',
                r'DEPRECATED',
                r'will be removed',
                r'migration.*required'
            ]

            return any(re.search(pattern, content, re.IGNORECASE) for pattern in warning_patterns)
        except:
            return False

    def scan_deprecated_components(self):
        """Scan repository for deprecated components"""
        file_patterns = ['**/*.yml', '**/*.yaml', '**/*.py']

        for pattern in file_patterns:
            for file_path in self.repo_path.glob(pattern):
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'test']):
                    continue

                self._scan_file_for_deprecations(file_path)

    def _scan_file_for_deprecations(self, file_path):
        """Scan individual file for deprecation notices"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Look for deprecation markers
            deprecation_pattern = r'#\s*DEPRECATED:?\s*(.+?)(?:\n|$)'
            removal_pattern = r'#\s*[Ww]ill be removed.*?(\d{4}\.S\d+\.\d+)'
            alternative_pattern = r'#\s*(?:Migration|Use):?\s*(.+?)(?:\n|$)'

            deprecation_matches = re.findall(deprecation_pattern, content, re.MULTILINE)
            removal_matches = re.findall(removal_pattern, content)
            alternative_matches = re.findall(alternative_pattern, content)

            if deprecation_matches:
                component_name = self._extract_component_name(file_path)
                component_type = self._determine_component_type(file_path)

                removal_target = removal_matches[0] if removal_matches else "TBD"
                alternative = alternative_matches[0].strip() if alternative_matches else None

                weeks_until = self._calculate_weeks_until_removal(removal_target)

                # Determine status
                if weeks_until < 0:
                    status = "overdue"
                elif weeks_until == 0:
                    status = "removal-due"
                elif weeks_until <= 4:  # 2 sprints
                    status = "removal-soon"
                else:
                    status = "deprecated"

                component = DeprecatedComponent(
                    name=component_name,
                    type=component_type,
                    file_path=str(file_path),
                    deprecated_in=self.current_release,
                    removal_target=removal_target,
                    alternative=alternative,
                    has_migration_doc=self._check_migration_doc_exists(component_name),
                    has_runtime_warning=self._check_runtime_warning(file_path),
                    weeks_until_removal=weeks_until,
                    status=status
                )

                self.deprecated_components.append(component)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def _extract_component_name(self, file_path):
        """Extract component name from file path"""
        # Remove repo path and file extension
        relative_path = file_path.relative_to(self.repo_path)
        return str(relative_path).replace('.yml', '').replace('.yaml', '').replace('.py', '')

    def _determine_component_type(self, file_path):
        """Determine component type from file path"""
        path_str = str(file_path)
        if '/playbooks/' in path_str:
            return 'playbook'
        elif '/roles/' in path_str:
            return 'role'
        elif '/tasks/' in path_str:
            return 'task'
        elif path_str.endswith('.py'):
            return 'module'
        else:
            return 'unknown'

    def generate_compliance_report(self):
        """Generate deprecation compliance report"""
        if not self.deprecated_components:
            return {
                "status": "✅ No deprecated components found",
                "summary": {"total": 0, "compliant": 0, "non_compliant": 0},
                "components": []
            }

        # Categorize components
        compliant = []
        non_compliant = []

        for component in self.deprecated_components:
            issues = []

            if not component.has_migration_doc:
                issues.append("Missing migration documentation")

            if not component.has_runtime_warning:
                issues.append("Missing runtime warnings")

            if component.removal_target == "TBD":
                issues.append("No removal target specified")

            if component.weeks_until_removal < 0:
                issues.append("Removal overdue")

            if issues:
                non_compliant.append((component, issues))
            else:
                compliant.append(component)

        # Generate report
        report = {
            "scan_date": datetime.now().isoformat(),
            "current_release": self.current_release,
            "summary": {
                "total": len(self.deprecated_components),
                "compliant": len(compliant),
                "non_compliant": len(non_compliant),
                "compliance_rate": f"{(len(compliant) / len(self.deprecated_components) * 100):.1f}%"
            },
            "status_breakdown": self._get_status_breakdown(),
            "compliant_components": [asdict(c) for c in compliant],
            "non_compliant_components": [
                {"component": asdict(comp), "issues": issues}
                for comp, issues in non_compliant
            ]
        }

        return report

    def _get_status_breakdown(self):
        """Get breakdown by status"""
        breakdown = defaultdict(int)
        for component in self.deprecated_components:
            breakdown[component.status] += 1
        return dict(breakdown)

    def print_dashboard(self):
        """Print human-readable dashboard"""
        report = self.generate_compliance_report()

        print("🗂️  CI Framework Deprecation Dashboard")
        print("=" * 50)
        print(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏷️  Current Release: {self.current_release}")
        print()

        summary = report["summary"]
        print("📊 Summary:")
        print(f"   Total deprecated components: {summary['total']}")
        print(f"   Compliant: {summary['compliant']} ✅")
        print(f"   Non-compliant: {summary['non_compliant']} ❌")
        print(f"   Compliance rate: {summary['compliance_rate']}")
        print()

        if report["status_breakdown"]:
            print("📈 Status Breakdown:")
            for status, count in report["status_breakdown"].items():
                emoji = {"deprecated": "⚠️", "removal-soon": "🚨", "overdue": "💥", "removal-due": "⏰"}.get(status, "❓")
                print(f"   {emoji} {status}: {count}")
            print()

        # Show non-compliant components
        if report["non_compliant_components"]:
            print("❌ Non-Compliant Components:")
            for item in report["non_compliant_components"]:
                comp = item["component"]
                issues = item["issues"]
                print(f"   📁 {comp['name']} ({comp['type']})")
                print(f"      📅 Removal: {comp['removal_target']} ({comp['weeks_until_removal']} weeks)")
                print(f"      🚨 Issues:")
                for issue in issues:
                    print(f"         - {issue}")
                print()

    def export_json_report(self, output_file):
        """Export report as JSON"""
        report = self.generate_compliance_report()
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report exported to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='CI Framework Deprecation Status Dashboard')
    parser.add_argument('--repo-path', default='.', help='Repository path to scan')
    parser.add_argument('--export', help='Export JSON report to file')
    parser.add_argument('--format', choices=['dashboard', 'json'], default='dashboard',
                       help='Output format')

    args = parser.parse_args()

    tracker = DeprecationTracker(args.repo_path)
    tracker.scan_deprecated_components()

    if args.format == 'json' or args.export:
        report = tracker.generate_compliance_report()
        if args.export:
            tracker.export_json_report(args.export)
        else:
            print(json.dumps(report, indent=2))
    else:
        tracker.print_dashboard()


if __name__ == '__main__':
    main()
