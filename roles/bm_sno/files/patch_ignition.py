#!/usr/bin/env python3
"""Patch an Ignition JSON file with a core user password and console autologin.

Applies three mechanisms for discovery-phase access on the agent live ISO:
1. passwd.users[].passwordHash  (standard ignition, may not work on live ISO)
2. set-core-password.service    (oneshot that forces the hash into /etc/shadow)
3. getty@tty{1,2} autologin     (console autologin drop-ins)
"""
import json
import sys

ign_file = sys.argv[1]
pw_hash = sys.argv[2]

with open(ign_file) as f:
    ign = json.load(f)

users = ign.setdefault("passwd", {}).setdefault("users", [])
core_user = next((u for u in users if u.get("name") == "core"), None)
if core_user is None:
    core_user = {"name": "core"}
    users.append(core_user)
core_user["passwordHash"] = pw_hash

units = ign.setdefault("systemd", {}).setdefault("units", [])

autologin_dropin = {
    "name": "autologin.conf",
    "contents": (
        "[Service]\nExecStart=\n"
        "ExecStart=-/sbin/agetty --autologin core --noclear %I $TERM\n"
    ),
}
for tty_svc in ["getty@tty1.service", "getty@tty2.service"]:
    units.append(
        {
            "name": tty_svc,
            "dropins": [autologin_dropin],
        }
    )

with open(ign_file, "w") as f:
    json.dump(ign, f)
