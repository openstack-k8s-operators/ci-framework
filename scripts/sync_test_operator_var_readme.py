#!/usr/bin/env python3
import yaml
import re
from pathlib import Path
from textwrap import indent

# ---- FILE LOCATIONS ----
defaults_file = Path("roles/test_operator/defaults/main.yml")
readme_file = Path("roles/test_operator/README.md")

# ---- LOAD DEFAULTS ----
with defaults_file.open() as f:
    defaults = yaml.safe_load(f)

# ---- DEFINE CATEGORIES ----
categories = {
    "Generic Parameters": {},
    "Tempest Parameters": {},
    "Tobiko Parameters": {},
    "AnsibleTest Parameters": {},
    "HorizonTest Parameters": {}
}

# ---- CLASSIFY VARIABLES ----
for key, value in defaults.items():
    k = key.lower()
    if k.startswith("cifmw_test_operator_tempest_") or k.startswith("cifmw_tempest_"):
        categories["Tempest Parameters"][key] = value
    elif k.startswith("cifmw_test_operator_tobiko_"):
        categories["Tobiko Parameters"][key] = value
    elif k.startswith("cifmw_test_operator_ansibletest_"):
        categories["AnsibleTest Parameters"][key] = value
    elif k.startswith("cifmw_test_operator_horizontest_"):
        categories["HorizonTest Parameters"][key] = value
    else:
        categories["Generic Parameters"][key] = value

# ---- BUILD MARKDOWN ----
md_lines = []
md_lines.append("<!-- START VARIABLES -->\n")
md_lines.append("_This section is automatically generated from `defaults/main.yml`. Do not edit manually._\n")

for cat_name, cat_vars in categories.items():
    if not cat_vars:
        continue
    md_lines.append(f"\n## {cat_name}\n")
    for var, val in cat_vars.items():
        # For very large values → just point to defaults file
        if isinstance(val, (dict, list)) and len(str(val)) > 200:
            md_lines.append(f"- **{var}**: (see defaults/main.yml)")
        else:
            formatted = yaml.dump(val, default_flow_style=False, sort_keys=False).rstrip()
            md_lines.append(f"- **{var}**:\n")
            md_lines.append(indent(f"```yaml\n{formatted}\n```", "  "))
    md_lines.append("")  # blank line

md_lines.append("\n<!-- END VARIABLES -->")
new_variables_md = "\n".join(md_lines)

# ---- UPDATE README ----
readme_text = readme_file.read_text()

start_marker = "<!-- START VARIABLES -->"
end_marker = "<!-- END VARIABLES -->"

pattern = re.compile(
    f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}",
    re.DOTALL,
)

if pattern.search(readme_text):
    updated_readme = pattern.sub(new_variables_md, readme_text)
else:
    # markers not found: append section at the end
    updated_readme = readme_text.rstrip() + "\n\n" + new_variables_md

readme_file.write_text(updated_readme)

print("README updated with latest defaults.")
