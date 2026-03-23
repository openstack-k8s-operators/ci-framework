#!/usr/bin/env python3
import yaml
import re
from pathlib import Path

README_PATH = Path("roles/test_operator/README.md")
DEFAULTS_PATH = Path("roles/test_operator/defaults/main.yml")
# GitHub URL for the defaults file
GITHUB_DEFAULTS_URL = "https://github.com/openstack-k8s-operators/ci-framework/blob/main/roles/test_operator/defaults/main.yml"
DEFAULTS_LINK = f"[main.yml]({GITHUB_DEFAULTS_URL})"
# Build regex that matches both old relative path and new GitHub URL
DEFAULTS_REGEX = (
    r"\[main\.yml\]\((defaults/main\.yml|" + re.escape(GITHUB_DEFAULTS_URL) + r")\)"
)

# Group rules
GROUP_MAP = {
    "TEMPEST_SPECIFIC_PARAMETERS": [
        "cifmw_test_operator_tempest_",
        "cifmw_tempest_",
    ],
    "TOBIKO_SPECIFIC_PARAMETERS": [
        "cifmw_test_operator_tobiko_",
    ],
    "HORIZONTEST_SPECIFIC_PARAMETERS": [
        "cifmw_test_operator_horizontest_",
    ],
    "ANSIBLETEST_SPECIFIC_PARAMETERS": [
        "cifmw_test_operator_ansibletest_",
    ],
}
GENERIC_GROUP = "GENERIC_PARAMETERS"


def detect_group(var):
    for group, prefixes in GROUP_MAP.items():
        for p in prefixes:
            if var.startswith(p):
                return group
    return GENERIC_GROUP


def get_defaults_link(var_name, line_numbers):
    """Generate GitHub URL with line anchor for a specific variable."""
    if var_name in line_numbers:
        start_line, end_line = line_numbers[var_name]
        if start_line == end_line:
            anchor = f"#L{start_line}"
        else:
            anchor = f"#L{start_line}-L{end_line}"
        return f"[main.yml]({GITHUB_DEFAULTS_URL}{anchor})"
    else:
        # Fallback to generic link if line number not found
        return DEFAULTS_LINK


def load_defaults():
    """Load defaults and track line numbers for each variable."""
    with open(DEFAULTS_PATH, "r") as f:
        content = f.read()
        defaults = yaml.safe_load(content) or {}

    # Track line numbers for each variable
    line_numbers = {}
    lines = content.splitlines()

    for i, line in enumerate(lines, start=1):
        # Match top-level variable definitions (no leading whitespace before variable name)
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:", line)
        if match:
            var_name = match.group(1)
            if var_name in defaults:
                start_line = i

                # Find end line by looking for the next top-level variable or end of file
                end_line = i
                for j in range(i, len(lines)):
                    # Check if next line is a new top-level variable or comment section
                    if j > i and re.match(
                        r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:|^#\s*Section", lines[j]
                    ):
                        end_line = j - 1
                        break
                    # If line has content (not just whitespace), update end_line
                    if lines[j].strip():
                        end_line = j + 1

                line_numbers[var_name] = (start_line, end_line)

    return defaults, line_numbers


def load_readme():
    return README_PATH.read_text()


def extract_section_blocks(readme):
    sections = {}
    for group in [GENERIC_GROUP] + list(GROUP_MAP.keys()):
        pattern = rf"(<!-- START {group} -->)(.*?)(<!-- END {group} -->)"
        m = re.search(pattern, readme, re.DOTALL)
        if not m:
            raise RuntimeError(f"Missing section markers for {group}")
        sections[group] = {
            "start": m.group(1),
            "content": m.group(2),
            "end": m.group(3),
        }
    return sections


def parse_existing_variable_blocks(section_content):
    """Extract full variable blocks (multi-line)."""
    vars = {}
    blocks = re.split(r"\n(?=\*\s*`)", section_content.strip())
    for block in blocks:
        m = re.match(r"\*\s*`([^`]+)`\s*:", block.strip())
        if m:
            vars[m.group(1)] = block.strip()
    return vars


def should_redirect(value):
    # Explicitly redirect only complex values
    if isinstance(value, (list, dict)):
        return True

    if isinstance(value, str) and "\n" in value:
        return True

    return False


def strip_multiline_default(block):
    """
    Remove any multiline default value YAML from README variable block.
    Keeps description but removes indented YAML.
    """
    lines = block.splitlines()
    cleaned = []
    skip = False

    for line in lines:
        if re.search(r"Default value:\s*$", line):
            cleaned.append(line)
            skip = True
            continue

        # Stop skipping when indentation ends
        if skip:
            if re.match(r"\s{2,}", line):
                continue
            skip = False

        cleaned.append(line)

    return "\n".join(cleaned)


def add_default_if_missing(block, value, var_name, line_numbers):
    """Add 'Default value:' if it's completely missing (don't normalize existing variations)."""
    # Check if there's any default documentation (in any format)
    if re.search(
        r"Default value:|Defaults to|defaults to|Default:", block, re.IGNORECASE
    ):
        # Already has some form of default documentation, leave it as-is
        return block

    # No default documentation found, add "Default value:"
    if value is None:
        # Empty but valid default
        block = block.rstrip() + " Default value: ``"
    elif should_redirect(value):
        # Complex values should redirect to main.yml
        defaults_link = get_defaults_link(var_name, line_numbers)
        block = block.rstrip() + f" Default value: See defaults in {defaults_link}"
    else:
        # Simple values can be shown inline
        # Convert Python bool to lowercase for consistency with YAML
        if isinstance(value, bool):
            value_str = str(value).lower()
        elif value is None:
            value_str = "null"
        else:
            value_str = str(value)
        block = block.rstrip() + f" Default value: `{value_str}`"

    return block


def build_bullet(var, value, existing_block=None, line_numbers=None):
    """Build markdown bullet line for a variable while preserving descriptions."""
    if line_numbers is None:
        line_numbers = {}

    # CASE 1: Variable already exists in README
    if existing_block:
        # First, add "Default value:" if completely missing (don't normalize existing variations)
        existing_block = add_default_if_missing(
            existing_block, value, var, line_numbers
        )
        # 1. Redirect if value is complex
        if should_redirect(value):
            existing_block = strip_multiline_default(existing_block)
            defaults_link = get_defaults_link(var, line_numbers)

            if "See defaults in" not in existing_block:
                existing_block = re.sub(
                    r"Default value:.*",
                    f"Default value: See defaults in {defaults_link}",
                    existing_block,
                    flags=re.DOTALL,
                )
            else:
                # Update existing "See defaults in" link to use GitHub URL with line anchor
                existing_block = re.sub(
                    r"Default value:\s*See defaults in.*",
                    f"Default value: See defaults in {defaults_link}",
                    existing_block,
                    flags=re.DOTALL,
                )
            return existing_block

        # 2.RESTORE inline default if it was previously redirected
        if re.search(r"See defaults in", existing_block):
            existing_block = re.sub(
                r"Default value:\s*See defaults in.*",
                f"Default value: `{value}`",
                existing_block,
                flags=re.DOTALL,
            )
            return existing_block

        # 3. Update inline default value if it changed
        m = re.search(r"Default value:\s*`([^`]+)`", existing_block)
        if m:
            current_val = m.group(1).strip()
            # Convert Python bool to lowercase for consistency
            if isinstance(value, bool):
                value_str = str(value).lower()
            elif value is None:
                value_str = "null"
            else:
                value_str = str(value)
            if current_val != value_str:
                existing_block = re.sub(
                    r"Default value:\s*`[^`]+`",
                    f"Default value: `{value_str}`",
                    existing_block,
                    count=1,
                )

        return existing_block

    # CASE 2: New variable
    if should_redirect(value):
        defaults_link = get_defaults_link(var, line_numbers)
        return f"* `{var}`: Default value: See defaults in {defaults_link}"

    # Convert Python bool to lowercase for consistency
    if isinstance(value, bool):
        value_str = str(value).lower()
    elif value is None:
        value_str = "null"
    else:
        value_str = str(value)
    return f"* `{var}`: Default value: `{value_str}`"


def sync():
    defaults, line_numbers = load_defaults()
    readme = load_readme()
    sections = extract_section_blocks(readme)

    grouped_new = {g: {} for g in sections}
    existing_vars = {
        g: parse_existing_variable_blocks(sections[g]["content"]) for g in sections
    }

    # Merge defaults with existing variables
    for var in defaults:
        value = defaults[var]
        group = detect_group(var)
        grouped_new[group][var] = build_bullet(
            var, value, existing_vars[group].get(var), line_numbers
        )

    # Keep variables that exist only in README (but not if they just redirect to defaults)
    for group, existing in existing_vars.items():
        for var, block in existing.items():
            if var not in grouped_new[group]:
                # Skip removing variables that had redirect to defaults but no longer exist in defaults/main.yml
                if re.search(rf"See defaults in\s+{DEFAULTS_REGEX}", block):
                    # Skip keeping — this var was only referencing defaults, and now it's gone from defaults.yml
                    continue
                # If variable exists in defaults (even in different group), add default if missing
                if var in defaults:
                    value = defaults[var]
                    block = add_default_if_missing(block, value, var, line_numbers)
                    grouped_new[group][var] = block
                else:
                    # Otherwise keep it as-is (manual documentation, extra notes, etc.)
                    grouped_new[group][var] = block

    # Rebuild README
    for group in grouped_new:
        new_content = "\n".join(
            grouped_new[group][v] for v in sorted(grouped_new[group])
        )
        pattern = rf"(<!-- START {group} -->)(.*?)(<!-- END {group} -->)"
        readme = re.sub(pattern, rf"\1\n{new_content}\n\3", readme, flags=re.DOTALL)

    README_PATH.write_text(readme)


if __name__ == "__main__":
    sync()
