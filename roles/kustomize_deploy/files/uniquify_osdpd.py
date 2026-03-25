#!/usr/bin/env python3
"""Append a run suffix to OpenStackDataPlaneDeployment resource names.

Usage: uniquify_osdpd.py <manifest_path> <suffix>

Reads the multi-document YAML file at <manifest_path>, appends <suffix>
to the metadata.name of every OpenStackDataPlaneDeployment resource that
does not already end with that suffix, and writes the result back in place.
Prints a "Renamed: <old> -> <new>" line for each renamed resource so that
the calling Ansible task can use changed_when on stdout.
"""
import sys
import yaml

path, suffix = sys.argv[1], sys.argv[2]

with open(path) as f:
    docs = [d for d in yaml.safe_load_all(f) if d is not None]

for doc in docs:
    if doc.get("kind") == "OpenStackDataPlaneDeployment":
        name = doc["metadata"]["name"]
        if not name.endswith("-" + suffix):
            doc["metadata"]["name"] = name + "-" + suffix
            print("Renamed: {} -> {}".format(name, doc["metadata"]["name"]))

with open(path, "w") as f:
    yaml.dump_all(docs, f, default_flow_style=False)
