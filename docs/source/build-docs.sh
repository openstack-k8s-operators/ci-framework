#!/usr/bin/env bash

set -euxo pipefail
DOCS_DIR="./docs"
VENV_DIR=${DOCS_DIR}/_venv

python -m venv ${VENV_DIR} && source ${VENV_DIR}/bin/activate
cd ${DOCS_DIR}/source

make clean

pip install -r ../doc-requirements.txt
make html

deactivate
