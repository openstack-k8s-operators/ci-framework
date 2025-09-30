#!/usr/bin/env python3
import yaml
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG — adjust paths for your repo structure
# ─────────────────────────────────────────────
defaults_file = Path("roles/test_operator/defaults/main.yml")
readme_file = Path("roles/test_operator/README.md")
defaults_link = "defaults/main.yml"  # link from README to defaults file
large_value_threshold = 200  # characters after YAML dump before we link out
# ─────────────────────────────────────────────

# Load defaults
with open(defaults_file) as f:
    defaults = yaml.safe_load(f)

# Function to classify variable into category
def categorize(var):
    if var.startswith("cifmw_test_operator_tempest_") or var.startswith("cifmw_tempest_"):
        return "Tempest Variables"
    elif var.startswith("cifmw_test_operator_tobiko_"):
        return "Tobiko Variables"
    elif var.startswith("cifmw_test_operator_ansibletest_"):
        return "AnsibleTest Variables"
    elif var.startswith("cifmw_test_operator_horizontest_"):
        return "HorizonTest Variables"
    else:
        return "Generic Variables"

# Split into categories
categories = {}
for var, val in defaults.items():
    cat = categorize(var)
    categories.setdefault(cat, {})[var] = val

# Build markdown content
md_lines = []
md_lines.append("<!-- BEGIN TEST OPERATOR PARAMS -->\n")
md_lines.append("## Test Operator Parameters\n")

for category, cat_vars in categories.items():
    md_lines.append(f"### {category}\n")
    md_lines.append("| Parameter | Default Value |")
    md_lines.append("|-----------|---------------|")
    for var, val in cat_vars.items():
        # decide if value is too big
        val_yaml = yaml.dump(val, default_flow_style=True, width=500, sort_keys=False).strip()
        if isinstance(val, (dict, list)) and len(val_yaml) > large_value_threshold:
            display_val = f"(see [defaults/main.yml]({defaults_link}))"
        else:
            display_val = val_yaml.replace("\n", " ")
        md_lines.append(f"| `{var}` | `{display_val}` |")
    md_lines.append("")  # blank line between categories

md_lines.append("<!-- END TEST OPERATOR PARAMS -->\n")

new_section = "\n".join(md_lines)

# Read README.md
readme_text = readme_file.read_text()

# Replace content between BEGIN and END markers or append if not present
import re
pattern = re.compile(r"<!-- BEGIN TEST OPERATOR PARAMS -->.*<!-- END TEST OPERATOR PARAMS -->", re.DOTALL)

if pattern.search(readme_text):
    updated = pattern.sub(new_section, readme_text)
else:
    updated = readme_text.strip() + "\n\n" + new_section

readme_file.write_text(updated)
print("✅ README.md updated successfully.")
