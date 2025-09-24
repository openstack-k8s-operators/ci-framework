#!/usr/bin/env python3
import yaml
import re
from pathlib import Path
import json

# Paths
defaults_file = Path("roles/test_operator/defaults/main.yml")
readme_file = Path("roles/test_operator/README.md")

# Keys that should always point to defaults file
TOO_BIG_KEYS = {
    "cifmw_test_operator_tempest_config",
    "cifmw_test_operator_tobiko_config",
    "cifmw_test_operator_ansibletest_config",
    "cifmw_test_operator_horizontest_config",
    "cifmw_test_operator_log_pod_definition",
}

# Categories (prefix -> category)
CATEGORIES = {
    "cifmw_test_operator_tempest_": "Tempest",
    "cifmw_test_operator_tobiko_": "Tobiko",
    "cifmw_test_operator_horizontest_": "Horizontest",
    "cifmw_test_operator_ansibletest_": "Ansible Test",
}

# Max length for inline YAML representation
MAX_INLINE_LENGTH = 60

def load_defaults():
    with open(defaults_file, "r") as f:
        return yaml.safe_load(f)

def categorize_var(key: str) -> str:
    """Determine the category of a variable based on prefix or keyword."""
    # Check prefix match first
    for prefix, cat in CATEGORIES.items():
        if key.startswith(prefix):
            return cat
    # Check keyword in variable name
    lowered = key.lower()
    for keyword, cat in [("tempest", "Tempest"),
                         ("tobiko", "Tobiko"),
                         ("horizontest", "Horizontest"),
                         ("ansibletest", "Ansible Test")]:
        if keyword in lowered:
            return cat
    return "Generic"

def format_value(key, value):
    """Format a default value for README markdown table."""

    # Always point to defaults for huge/complex keys
    if key in TOO_BIG_KEYS:
        return f"See [`defaults/main.yml`](./defaults/main.yml)"

    # Scalars (int, float, bool, None)
    if isinstance(value, (int, float, bool)) or value is None:
        return f"`{value}`"

    # Strings
    if isinstance(value, str):
        # Escape pipe for table rendering
        escaped = value.replace("|", r"\|")
        # Keep full Jinja templates intact
        if "{{" in value and "}}" in value:
            return f"`{escaped}`"
        # If string is too long, point to defaults
        if len(value) > MAX_INLINE_LENGTH:
            return f"See [`defaults/main.yml`](./defaults/main.yml)"
        return f"`{escaped}`"

    # Lists or dicts
    if isinstance(value, (list, dict)):
        try:
            inline = json.dumps(value)
            if len(inline) <= MAX_INLINE_LENGTH:
                return f"`{inline}`"
            else:
                return f"See [`defaults/main.yml`](./defaults/main.yml)"
        except Exception:
            return f"See [`defaults/main.yml`](./defaults/main.yml)"

    # Fallback
    return f"See [`defaults/main.yml`](./defaults/main.yml)"

def build_tables(defaults):
    """Build per-category markdown tables"""
    categorized = {cat: [] for cat in list(CATEGORIES.values()) + ["Generic"]}

    for key, val in defaults.items():
        cat = categorize_var(key)
        categorized[cat].append((key, val))

    md_sections = []
    for cat, items in categorized.items():
        if not items:
            continue
        md_sections.append(f"### {cat} Variables\n")
        md_sections.append("| Variable | Default |")
        md_sections.append("|----------|---------|")
        for key, val in sorted(items):
            md_sections.append(f"| `{key}` | {format_value(key, val)} |")
        md_sections.append("")  # blank line for spacing
    return "\n".join(md_sections)

def update_readme(defaults):
    readme = readme_file.read_text()

    start_marker = "<!-- START DEFAULTS -->"
    end_marker = "<!-- END DEFAULTS -->"

    if start_marker not in readme or end_marker not in readme:
        raise RuntimeError("README.md missing START/END DEFAULTS markers")

    new_content = build_tables(defaults)

    updated_readme = re.sub(
        f"{start_marker}.*?{end_marker}",
        f"{start_marker}\n{new_content}\n{end_marker}",
        readme,
        flags=re.DOTALL,
    )

    readme_file.write_text(updated_readme)
    print(f"README.md updated with categorized and readable defaults")

if __name__ == "__main__":
    defaults = load_defaults()
    update_readme(defaults)
