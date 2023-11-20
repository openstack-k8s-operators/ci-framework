#!/bin/sh
set -xe
# Create links for roles' README.md in
# docs/source/roles
PROJECT_DIR="$(dirname $(readlink -f $0))/../"
for i in ${PROJECT_DIR}/ci_framework/roles/*/README.md; do
    dir_name=$(dirname ${i})
    role_name=$(basename ${dir_name})
    test -L docs/source/roles/${role_name}.md || \
    ln -s ../../../ci_framework/roles/${role_name}/README.md \
        docs/source/roles/${role_name}.md
done
