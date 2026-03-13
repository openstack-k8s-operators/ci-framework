#!/usr/bin/env python3
"""Create a redacted copy of an Ignition JSON file (strip pull-secret sources)."""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]

with open(src) as f:
    d = json.load(f)

for s in d.get("storage", {}).get("files", []):
    if "pull" in s.get("path", "").lower():
        s["contents"]["source"] = "data:,REDACTED"

with open(dst, "w") as f:
    json.dump(d, f, indent=2)
