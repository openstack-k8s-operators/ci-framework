#!/usr/bin/env python3
"""Helpers for osp-secret keys in kustomize-built manifests."""

import base64
import json
import sys

import yaml

OSP_SECRET_NAME = "osp-secret"


def load_docs(path):
    with open(path) as handle:
        return [doc for doc in yaml.safe_load_all(handle) if doc is not None]


def find_osp_secret(docs):
    for doc in docs:
        if doc.get("kind") != "Secret":
            continue
        if doc.get("metadata", {}).get("name") != OSP_SECRET_NAME:
            continue
        return doc
    return None


def get_secret_namespace(docs):
    secret = find_osp_secret(docs)
    if secret is None:
        return None
    return secret.get("metadata", {}).get("namespace")


def get_secret_key(docs, key):
    secret = find_osp_secret(docs)
    if secret is None:
        return None
    data = secret.get("data", {})
    if key not in data or not data[key]:
        return None
    return base64.b64decode(data[key]).decode()


def apply_secret_keys(docs, keys):
    secret = find_osp_secret(docs)
    if secret is None:
        return False, []
    data = secret.setdefault("data", {})
    changed_keys = []
    for key, value in keys.items():
        if not value:
            continue
        encoded = base64.b64encode(value.encode()).decode()
        if data.get(key) != encoded:
            data[key] = encoded
            changed_keys.append(key)
    return bool(changed_keys), changed_keys


def cmd_has(path):
    secret = find_osp_secret(load_docs(path))
    sys.exit(0 if secret else 1)


def cmd_get(path, key):
    value = get_secret_key(load_docs(path), key)
    if value is None:
        sys.exit(2)
    sys.stdout.write(value)


def cmd_get_namespace(path):
    namespace = get_secret_namespace(load_docs(path))
    if not namespace:
        sys.exit(2)
    sys.stdout.write(namespace)


def cmd_set(path, keys_json):
    docs = load_docs(path)
    keys = json.loads(keys_json)
    changed, changed_keys = apply_secret_keys(docs, keys)
    if changed:
        with open(path, "w") as handle:
            yaml.dump_all(docs, handle, default_flow_style=False)
    for key in changed_keys:
        print("Set: {}".format(key))


def main():
    if len(sys.argv) < 3:
        sys.exit(
            "usage: osp_secret_manifest.py <has|get|get-namespace|set> <path> [args]"
        )
    command = sys.argv[1]
    path = sys.argv[2]
    if command == "has":
        cmd_has(path)
    elif command == "get":
        if len(sys.argv) != 4:
            sys.exit("usage: osp_secret_manifest.py get <path> <key>")
        cmd_get(path, sys.argv[3])
    elif command == "get-namespace":
        cmd_get_namespace(path)
    elif command == "set":
        if len(sys.argv) != 4:
            sys.exit("usage: osp_secret_manifest.py set <path> <json>")
        cmd_set(path, sys.argv[3])
    else:
        sys.exit("unknown command: {}".format(command))


if __name__ == "__main__":
    main()
