#!/usr/bin/env bash

set -euxo pipefail
DOCS_DIR="./docs"
VENV_DIR="${DOCS_DIR}/_venv"
BUILD_TYPE="${BUILD_TYPE:=static}"

# Create a virtual environment and activate it
python -m venv ${VENV_DIR} && source ${VENV_DIR}/bin/activate
pip3 install -r ${DOCS_DIR}/doc-requirements.txt

cd ${DOCS_DIR}/source

# Fake the ansible_collections path for python imports
SITE_PACKAGES=$(python -c 'import site; print(site.getsitepackages()[0])')
# install the cifmw collection from source without dependencies (removes the
# need for any symlink)
ansible-galaxy collection install -U ../.. -p "${SITE_PACKAGES}"

make clean

# Build the documentation based on the specified build type
if [[ $BUILD_TYPE == "static" ]]; then
    make html
elif [[ $BUILD_TYPE == "live" ]]; then
    sphinx-autobuild --pre-build "make autobuild_pre" \
        --watch ../../plugins \
        --re-ignore '(plugins|module_utils|roles)/.*.rst' \
        . ../_build
fi

# Deactivate the virtual environment
deactivate
