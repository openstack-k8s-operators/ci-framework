#!/usr/bin/env python3
"""Helpers for Secret keys in kustomize-built manifests.

Originally written for ``osp-secret`` (the default target of every
function/command below), the same helpers also operate on other
single-Secret manifests such as ``libvirt-secret`` by passing an explicit
``secret_name``.
"""

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


def find_secret(docs, secret_name=OSP_SECRET_NAME):
    # Each kustomize output is expected to contain at most one Secret
    # with a given name (e.g. osp-secret, libvirt-secret).
    for doc in docs:
        if doc.get("kind") != "Secret":
            continue
        if doc.get("metadata", {}).get("name") != secret_name:
            continue
        return doc
    return None


def find_osp_secret(docs):
    return find_secret(docs, OSP_SECRET_NAME)


def get_secret_namespace(docs, secret_name=OSP_SECRET_NAME):
    secret = find_secret(docs, secret_name)
    if secret is None:
        return None
    return secret.get("metadata", {}).get("namespace")


def get_secret_key(docs, key, secret_name=OSP_SECRET_NAME):
    secret = find_secret(docs, secret_name)
    if secret is None:
        return None
    data = secret.get("data", {})
    if key not in data or not data[key]:
        return None
    return base64.b64decode(data[key]).decode()


def apply_secret_keys(docs, keys, secret_name=OSP_SECRET_NAME):
    secret = find_secret(docs, secret_name)
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


def randomize_secret_keys(docs, config, secret_name=OSP_SECRET_NAME):
    """Replace a Secret's data values with random ones.

    ``config`` is a dict with optional keys:
      cluster_values  - dict of key->plaintext from the live cluster
      skip_keys       - list of keys to leave untouched
      special_keys    - dict of key->{type, length} for non-password formats
    """
    secret = find_secret(docs, secret_name)
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


def cmd_has(path, secret_name=OSP_SECRET_NAME):
    # Exit codes: 0 = secret found, 1 = not found, 2 = error while
    # reading/parsing the manifest. Callers must not treat 2 the same as 1:
    # a parse failure should never be silently mistaken for "nothing to do".
    try:
        docs = load_docs(path)
    except Exception as exc:
        sys.stderr.write("error: failed to load manifest {}: {}\n".format(path, exc))
        sys.exit(2)
    secret = find_secret(docs, secret_name)
    sys.exit(0 if secret else 1)


def cmd_get(path, key, secret_name=OSP_SECRET_NAME):
    value = get_secret_key(load_docs(path), key, secret_name)
    if value is None:
        sys.exit(2)
    sys.stdout.write(value)


def cmd_get_namespace(path, secret_name=OSP_SECRET_NAME):
    namespace = get_secret_namespace(load_docs(path), secret_name)
    if not namespace:
        sys.exit(2)
    sys.stdout.write(namespace)


def load_keys(keys_path):
    with open(keys_path) as handle:
        return json.load(handle)


def cmd_set(path, keys_path, secret_name=OSP_SECRET_NAME):
    docs = load_docs(path)
    keys = load_keys(keys_path)
    changed, changed_keys = apply_secret_keys(docs, keys, secret_name)
    if changed:
        with open(path, "w") as handle:
            yaml.dump_all(docs, handle, default_flow_style=False)
    for key in changed_keys:
        print("Set: {}".format(key))


def cmd_randomize(path, config_path, secret_name=OSP_SECRET_NAME):
    docs = load_docs(path)
    config = load_keys(config_path)
    changed, changed_keys = randomize_secret_keys(docs, config, secret_name)
    if changed:
        with open(path, "w") as handle:
            yaml.dump_all(docs, handle, default_flow_style=False)
    for key in changed_keys:
        print("Randomized: {}".format(key))


def main():
    if len(sys.argv) < 3:
        sys.exit(
            "usage: osp_secret_manifest.py"
            " <has|get|get-namespace|set|randomize> <path> [args] [secret-name]"
        )
    command = sys.argv[1]
    path = sys.argv[2]
    if command == "has":
        secret_name = sys.argv[3] if len(sys.argv) > 3 else OSP_SECRET_NAME
        cmd_has(path, secret_name)
    elif command == "get":
        if len(sys.argv) not in (4, 5):
            sys.exit("usage: osp_secret_manifest.py get <path> <key> [secret-name]")
        secret_name = sys.argv[4] if len(sys.argv) == 5 else OSP_SECRET_NAME
        cmd_get(path, sys.argv[3], secret_name)
    elif command == "get-namespace":
        secret_name = sys.argv[3] if len(sys.argv) > 3 else OSP_SECRET_NAME
        cmd_get_namespace(path, secret_name)
    elif command == "set":
        if len(sys.argv) not in (4, 5):
            sys.exit(
                "usage: osp_secret_manifest.py"
                " set <path> <keys-json-file> [secret-name]"
            )
        secret_name = sys.argv[4] if len(sys.argv) == 5 else OSP_SECRET_NAME
        cmd_set(path, sys.argv[3], secret_name)
    elif command == "randomize":
        if len(sys.argv) not in (4, 5):
            sys.exit(
                "usage: osp_secret_manifest.py"
                " randomize <path> <config-json-file> [secret-name]"
            )
        secret_name = sys.argv[4] if len(sys.argv) == 5 else OSP_SECRET_NAME
        cmd_randomize(path, sys.argv[3], secret_name)
    else:
        sys.exit("unknown command: {}".format(command))


if __name__ == "__main__":
    main()
