#!/bin/sh
set -xe

PROJECT_DIR="$(dirname $(readlink -f $0))/../"

# Create a symlink for ansible_collections python package
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")

# Install the cifmw collection from source (removes the need for any symlink)
# Also install galaxy dependencies, required by ansible-doc-extractor
ansible-galaxy collection install -U .. -p "${SITE_PACKAGES}"

# Create links for roles' README.md in
# docs/source/roles
for i in ${PROJECT_DIR}/roles/*/README.md; do
    dir_name=$(dirname ${i})
    role_name=$(basename ${dir_name})
    test -L docs/source/roles/${role_name}.md || \
    ln -s ../../../roles/${role_name}/README.md \
        docs/source/roles/${role_name}.md
done
