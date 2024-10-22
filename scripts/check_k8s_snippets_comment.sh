#!/bin/bash
set -o pipefail

exit_code=0

missing_comment=$(grep -rL '^# source: ' roles/ci_gen_kustomize_values/templates)
if [[ $missing_comment != '' ]]; then
    echo "!! Following templates are missing the needed '# source: path/to/template' comment."
    echo "   Path must be relative to 'templates'"
    echo
    echo "${missing_comment}"
    echo
    (( exit_code+=1 ))  # bashate: ignore=E043
fi

set_path=$(grep -r '^# source: ' roles/ci_gen_kustomize_values/templates | sed 's!roles/ci_gen_kustomize_values/templates/!!')
# shellcheck disable=SC2162
while read match; do
    tmpl=$(echo -n "${match}" | cut -d ':' -f 1)
    comment=$(echo -n "${match}" | cut -d ':' -f 3 | tr -d '[:space:]')
    if [[ "${tmpl}" != "${comment}" ]]; then
        (( exit_code+=1 ))  # bashate: ignore=E043
        echo "${tmpl} doesn't have correct 'source': ${comment}"
    fi
done <<< "${set_path}"
exit $exit_code
