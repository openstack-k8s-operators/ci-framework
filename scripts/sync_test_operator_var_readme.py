import yaml
import re
import os

DEFAULT_FILE = "roles/test_operator/defaults/main.yml"
README_FILE = "roles/test_operator/README.md"
MAX_VALUE_LEN = 60  # threshold to redirect long default values


def parse_yaml():
    """Load variables from defaults/main.yml."""
    with open(DEFAULT_FILE) as f:
        return yaml.safe_load(f)


def parse_existing_descriptions(readme_text):
    """
    Parse README and extract existing variable descriptions.
    Works with formats like:
    * `var_name`: (String) Description here. Default value: `xyz`
    """
    descs = {}
    # Capture variable name and text before "Default value:"
    matches = re.findall(
        r"\* [`](.*?)`:\s*\((?:String|Integer|List|Dict|Bool|Boolean|Object)?.*?\)\s*(.*?)(?:Default value:|Default:)",
        readme_text,
        re.IGNORECASE | re.DOTALL,
    )
    for var, desc in matches:
        descs[var.strip()] = desc.strip().rstrip(". ")
    return descs


def format_var(var, value, description=""):
    """Return formatted bullet line for a variable."""
    # Redirect to defaults/main.yml if too long or multiline
    if isinstance(value, (dict, list)) or len(str(value)) > MAX_VALUE_LEN or "\n" in str(value):
        default_str = f"[Refer to `{DEFAULT_FILE}`]"
    else:
        default_str = f"`{value}`"

    desc_part = f" — {description}" if description else ""
    return f"* `{var}`: (Default: {default_str}){desc_part}"


def build_section(title, yaml_data, descs, keys):
    """Build a README section for a given group of variables."""
    section = [f"### {title}\n"]
    for key in keys:
        if key in yaml_data:
            val = yaml_data[key]
            desc = descs.get(key, "")
            section.append(format_var(key, val, desc))
    return "\n".join(section)


def extract_sections(data):
    """Identify variables belonging to different categories."""
    sections = {
        "Generic Params": [],
        "Tempest": [],
        "Tobiko": [],
        "AnsibleTest": [],
        "HorizonTest": [],
    }

    for key in data:
        key_lower = key.lower()
        if "tempest" in key_lower:
            sections["Tempest"].append(key)
        elif "tobiko" in key_lower:
            sections["Tobiko"].append(key)
        elif "ansibletest" in key_lower:
            sections["AnsibleTest"].append(key)
        elif "horizontest" in key_lower:
            sections["HorizonTest"].append(key)
        else:
            sections["Generic Params"].append(key)

    return sections


def update_readme():
    with open(README_FILE) as f:
        readme_text = f.read()

    yaml_data = parse_yaml()
    descs = parse_existing_descriptions(readme_text)
    sections = extract_sections(yaml_data)

    new_sections = []
    for title, keys in sections.items():
        new_sections.append(build_section(title, yaml_data, descs, keys))

    # Replace the full README content between markers
    pattern = re.compile(r"<!-- START VARIABLES -->.*<!-- END VARIABLES -->", re.DOTALL)
    new_content = (
        "<!-- START VARIABLES -->\n"
        + "\n\n".join(new_sections)
        + "\n<!-- END VARIABLES -->"
    )

    if pattern.search(readme_text):
        updated = pattern.sub(new_content, readme_text)
    else:
        # Append if no markers exist
        updated = readme_text.strip() + "\n\n" + new_content

    with open(README_FILE, "w") as f:
        f.write(updated)

    print("✅ README.md updated successfully.")


if __name__ == "__main__":
    if not os.path.exists(DEFAULT_FILE):
        print(f"❌ Cannot find {DEFAULT_FILE}")
    elif not os.path.exists(README_FILE):
        print(f"❌ Cannot find {README_FILE}")
    else:
        update_readme()
