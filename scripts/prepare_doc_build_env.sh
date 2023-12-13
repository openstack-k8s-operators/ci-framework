#!/bin/sh
set -xe

PROJECT_DIR="$(dirname $(readlink -f $0))/../"

# Create a symlink for ansible_collections python package
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
mkdir -p "${SITE_PACKAGES}/ansible_collections/cifmw"
ln -nsfr ${PROJECT_DIR}/ci_framework ${SITE_PACKAGES}/ansible_collections/cifmw/general

# Create links for roles' README.md in
# docs/source/roles
for i in ${PROJECT_DIR}/ci_framework/roles/*/README.md; do
    dir_name=$(dirname ${i})
    role_name=$(basename ${dir_name})
    test -L docs/source/roles/${role_name}.md || \
    ln -s ../../../ci_framework/roles/${role_name}/README.md \
        docs/source/roles/${role_name}.md
done
