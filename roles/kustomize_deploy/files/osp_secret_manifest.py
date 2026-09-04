#!/usr/bin/env python3
"""Helpers for osp-secret keys in kustomize-built manifests."""

import base64
import json
import secrets
import string
import sys

import yaml

OSP_SECRET_NAME = "osp-secret"


def load_docs(path):
    with open(path) as handle:
        return [doc for doc in yaml.safe_load_all(handle) if doc is not None]


def find_osp_secret(docs):
    # Each kustomize output is expected to contain at most one osp-secret.
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


def generate_random_password(length=20):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_hex_key(byte_length):
    return secrets.token_hex(byte_length)


def randomize_secret_keys(docs, config):
    """Replace osp-secret data values with random ones.

    ``config`` is a dict with optional keys:
      cluster_values  - dict of key->plaintext from the live cluster
      skip_keys       - list of keys to leave untouched
      special_keys    - dict of key->{type, length} for non-password formats
    """
    secret = find_osp_secret(docs)
    if secret is None:
        return False, []

    data = secret.setdefault("data", {})
    cluster_values = config.get("cluster_values", {})
    skip_keys = set(config.get("skip_keys", []))
    special_keys = config.get("special_keys", {})

    changed_keys = []
    for key in list(data.keys()):
        if key in skip_keys:
            continue

        if key in cluster_values and cluster_values[key]:
            new_value = cluster_values[key]
        elif key in special_keys:
            spec = special_keys[key]
            if spec.get("type") == "hex":
                new_value = generate_hex_key(spec.get("length", 16))
            elif spec.get("type") == "base64":
                raw = generate_random_password(spec.get("length", 32))
                new_value = base64.b64encode(raw.encode()).decode()
            else:
                new_value = generate_random_password()
        else:
            new_value = generate_random_password()

        encoded = base64.b64encode(new_value.encode()).decode()
        if data.get(key) != encoded:
            data[key] = encoded
            changed_keys.append(key)

    return bool(changed_keys), changed_keys


def cmd_has(path):
    # Exit codes: 0 = osp-secret found, 1 = not found, 2 = error while
    # reading/parsing the manifest. Callers must not treat 2 the same as 1:
    # a parse failure should never be silently mistaken for "nothing to do".
    try:
        docs = load_docs(path)
    except Exception as exc:
        sys.stderr.write("error: failed to load manifest {}: {}\n".format(path, exc))
        sys.exit(2)
    secret = find_osp_secret(docs)
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


def load_keys(keys_path):
    with open(keys_path) as handle:
        return json.load(handle)


def cmd_set(path, keys_path):
    docs = load_docs(path)
    keys = load_keys(keys_path)
    changed, changed_keys = apply_secret_keys(docs, keys)
    if changed:
        with open(path, "w") as handle:
            yaml.dump_all(docs, handle, default_flow_style=False)
    for key in changed_keys:
        print("Set: {}".format(key))


def cmd_randomize(path, config_path):
    docs = load_docs(path)
    config = load_keys(config_path)
    changed, changed_keys = randomize_secret_keys(docs, config)
    if changed:
        with open(path, "w") as handle:
            yaml.dump_all(docs, handle, default_flow_style=False)
    for key in changed_keys:
        print("Randomized: {}".format(key))


def main():
    if len(sys.argv) < 3:
        sys.exit(
            "usage: osp_secret_manifest.py"
            " <has|get|get-namespace|set|randomize> <path> [args]"
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
            sys.exit("usage: osp_secret_manifest.py set <path> <keys-json-file>")
        cmd_set(path, sys.argv[3])
    elif command == "randomize":
        if len(sys.argv) != 4:
            sys.exit(
                "usage: osp_secret_manifest.py randomize <path> <config-json-file>"
            )
        cmd_randomize(path, sys.argv[3])
    else:
        sys.exit("unknown command: {}".format(command))


if __name__ == "__main__":
    main()
