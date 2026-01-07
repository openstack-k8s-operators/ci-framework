#!/usr/bin/env python3
import yaml
import re
from pathlib import Path

README_PATH = Path("roles/test_operator/README.md")
DEFAULTS_PATH = Path("roles/test_operator/defaults/main.yml")
DEFAULTS_REL = DEFAULTS_PATH.relative_to("roles/test_operator")
DEFAULTS_LINK = f"[{DEFAULTS_REL.name}]({DEFAULTS_REL})"
# Build dynamic regex for removal
DEFAULTS_REGEX = re.escape(f"[{DEFAULTS_REL.name}]({DEFAULTS_REL})")

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

MAX_INLINE_LENGTH = 200
MAX_INLINE_LINES = 3


def detect_group(var):
    for group, prefixes in GROUP_MAP.items():
        for p in prefixes:
            if var.startswith(p):
                return group
    return GENERIC_GROUP


def load_defaults():
    with open(DEFAULTS_PATH, "r") as f:
        return yaml.safe_load(f) or {}


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
    """
    Decide whether a variable's default value should be referenced
    to defaults/main.yml instead of being inlined in README.
    """

    if value is None:
        return False

    # Lists / dicts → redirect
    if isinstance(value, (list, dict)):
        return True

    value_str = str(value).strip()

    # Multiline → redirect
    if "\n" in value_str:
        return True

    # Very long lines (heuristic, adjust if needed)
    if len(value_str) > 120:
        return True

    # Everything else is safe to inline
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


def build_bullet(var, value, existing_block=None):
    """Build markdown bullet line for a variable while preserving descriptions."""

    # CASE 1: Variable already exists in README
    if existing_block:

        # Redirect if complex AND present in defaults/main.yml
        if should_redirect(value):
            # Remove any inlined YAML
            existing_block = strip_multiline_default(existing_block)

            # Replace default value with redirect
            if "See defaults in" not in existing_block:
                existing_block = re.sub(
                    r"Default value:.*",
                    f"Default value: See defaults in {DEFAULTS_LINK}",
                    existing_block,
                    flags=re.DOTALL,
                )

            return existing_block

        # ---- Inline value update logic (unchanged) ----
        m = re.search(r"Default value:\s*`([^`]+)`", existing_block)
        if m:
            current_val = m.group(1).strip()
            if str(current_val) != str(value):
                existing_block = re.sub(
                    r"Default value:\s*`[^`]+`",
                    f"Default value: `{value}`",
                    existing_block,
                    count=1,
                )
        return existing_block

    # CASE 2: New variable
    if should_redirect(value):
        return f"* `{var}`: Default value: See defaults in {DEFAULTS_LINK}"

    return f"* `{var}`: `{value}`"


def sync():
    defaults = load_defaults()
    readme = load_readme()
    sections = extract_section_blocks(readme)

    grouped_new = {g: {} for g in sections}
    existing_vars = {g: parse_existing_variable_blocks(sections[g]["content"]) for g in sections}

    # Merge defaults with existing variables
    for var, value in defaults.items():
        group = detect_group(var)
        grouped_new[group][var] = build_bullet(var, value, existing_vars[group].get(var))

    # Keep variables that exist only in README (but not if they just redirect to defaults)
    for group, existing in existing_vars.items():
        for var, block in existing.items():
            if var not in grouped_new[group]:
                # Skip removing variables that had redirect to defaults but no longer exist in defaults/main.yml
                if re.search(rf"See defaults in\s+{DEFAULTS_REGEX}", block):
                    # Skip keeping — this var was only referencing defaults, and now it’s gone from defaults.yml
                    print(f"Removing obsolete variable from README: {var}")
                    continue
                # Otherwise keep it (manual documentation, extra notes, etc.)
                grouped_new[group][var] = block

    # Rebuild README
    for group in grouped_new:
        new_content = "\n".join(grouped_new[group][v] for v in sorted(grouped_new[group]))
        pattern = rf"(<!-- START {group} -->)(.*?)(<!-- END {group} -->)"
        readme = re.sub(pattern, rf"\1\n{new_content}\n\3", readme, flags=re.DOTALL)

    README_PATH.write_text(readme)
    print("README successfully synchronized with inline YAML support.")


if __name__ == "__main__":
    sync()
