#!/usr/bin/env bash
# Fail if playbooks/roles hardcode Cinder/Glance pod names that break when
# uniquePodNames is true. Prefer role discover_osp_pod (namespace + component/
# service labels from lib-common) or equivalent label selectors.
set -eu

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

PATTERN='cinder-api-0|cinder-backup-0|cinder-scheduler-0|glance-default-single-0|glance-default-external-api-0|glance-default-internal-api-0'

tmp="$(mktemp)"
filtered="$(mktemp)"
trap 'rm -f "${tmp}" "${filtered}"' EXIT

grep -RInE --binary-files=without-match \
  --include='*.yml' --include='*.yaml' --include='*.py' --include='*.sh' \
  -e "${PATTERN}" \
  roles hooks/playbooks playbooks plugins scripts 2>/dev/null >"${tmp}" || true

: >"${filtered}"
while IFS= read -r line || [ -n "${line}" ]; do
  [ -z "${line}" ] && continue
  case "${line}" in
    scripts/check_hardcoded_osp_pod_names.sh:* ) continue ;;
    tests/unit/plugins/filter/test_osp_pod_pick.py:* ) continue ;;
    plugins/filter/osp_pod_pick.py:* ) continue ;;
    roles/discover_osp_pod/* ) continue ;;
  esac
  printf '%s\n' "${line}" >>"${filtered}"
done <"${tmp}"

if [ -s "${filtered}" ]; then
  echo "Hardcoded OpenStack pod names found (break uniquePodNames: true):"
  sed 's/^/  /' "${filtered}"
  echo
  echo "Use ansible role discover_osp_pod (namespace + component=/service= labels)"
  echo "or kubernetes.core.k8s_info with the same selectors."
  exit 1
fi

echo "OK: no hardcoded Cinder/Glance pod names in automation paths."
