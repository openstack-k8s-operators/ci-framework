#!/bin/bash
# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Poll for a detached command running in a shiftstackclient pod.
#
# Soft-transient oc exec errors (connection refused / i/o timeout) use a
# consecutive failure budget so brief API VIP blips do not fail the job, while
# a dead API does not burn the full poll window. Hard-transient patterns retry
# for the full max-retries window.
#
# Required environment:
#   CIFMW_SHIFTSTACK_POLL_NAMESPACE
#   CIFMW_SHIFTSTACK_POLL_POD
#   CIFMW_SHIFTSTACK_POLL_MAX_RETRIES
#   CIFMW_SHIFTSTACK_POLL_DELAY
#   CIFMW_SHIFTSTACK_POLL_SOFT_MAX
#   CIFMW_SHIFTSTACK_POLL_HARD_RE   (grep -E pattern, may be empty)
#   CIFMW_SHIFTSTACK_POLL_SOFT_RE   (grep -E pattern, may be empty)
#
# Exit codes:
#   0  - background command finished (stdout holds /tmp/cifmw_cmd_rc)
#   2  - background process gone without writing a marker
#   3  - soft-transient budget exhausted
#  10  - still running after max retries
# other - non-retryable oc exec failure
#
# On completion, prints CIFMW_SHIFTSTACK_POLL_ATTEMPTS=<n> on stderr.

set -euo pipefail

: "${CIFMW_SHIFTSTACK_POLL_NAMESPACE:?}"
: "${CIFMW_SHIFTSTACK_POLL_POD:?}"
: "${CIFMW_SHIFTSTACK_POLL_MAX_RETRIES:?}"
: "${CIFMW_SHIFTSTACK_POLL_DELAY:?}"
: "${CIFMW_SHIFTSTACK_POLL_SOFT_MAX:?}"
: "${CIFMW_SHIFTSTACK_POLL_HARD_RE?}"
: "${CIFMW_SHIFTSTACK_POLL_SOFT_RE?}"

soft=0
attempts=0
max_retries="${CIFMW_SHIFTSTACK_POLL_MAX_RETRIES}"
delay="${CIFMW_SHIFTSTACK_POLL_DELAY}"
soft_max="${CIFMW_SHIFTSTACK_POLL_SOFT_MAX}"
hard_re="${CIFMW_SHIFTSTACK_POLL_HARD_RE}"
soft_re="${CIFMW_SHIFTSTACK_POLL_SOFT_RE}"
ns="${CIFMW_SHIFTSTACK_POLL_NAMESPACE}"
pod="${CIFMW_SHIFTSTACK_POLL_POD}"
poll_cmd='if cat /tmp/cifmw_cmd_rc 2>/dev/null; then exit 0; elif [ -f /tmp/cifmw_cmd_pid ] && kill -0 $(cat /tmp/cifmw_cmd_pid) 2>/dev/null; then exit 10; else exit 2; fi'

emit_attempts() {
  echo "CIFMW_SHIFTSTACK_POLL_ATTEMPTS=${attempts}" >&2
}

while [ "${attempts}" -lt "${max_retries}" ]; do
  attempts=$((attempts + 1))
  stderr_file="$(mktemp)"
  set +e
  stdout="$(oc exec -n "${ns}" "${pod}" -- bash -c "${poll_cmd}" 2>"${stderr_file}")"
  rc=$?
  set -e
  stderr="$(cat "${stderr_file}" 2>/dev/null || true)"
  rm -f "${stderr_file}"

  if [ "${rc}" -eq 0 ] || [ "${rc}" -eq 2 ]; then
    printf '%s\n' "${stdout}"
    printf '%s\n' "${stderr}" >&2
    emit_attempts
    exit "${rc}"
  fi

  if [ "${rc}" -eq 10 ]; then
    soft=0
    sleep "${delay}"
    continue
  fi

  # oc exec itself failed (typically rc=1). Classify stderr.
  if [ -n "${hard_re}" ] && printf '%s\n' "${stderr}" | grep -Eiq -- "${hard_re}"; then
    soft=0
    sleep "${delay}"
    continue
  fi

  if [ -n "${soft_re}" ] && printf '%s\n' "${stderr}" | grep -Eiq -- "${soft_re}"; then
    soft=$((soft + 1))
    if [ "${soft}" -ge "${soft_max}" ]; then
      printf '%s\n' "${stderr}" >&2
      emit_attempts
      exit 3
    fi
    sleep "${delay}"
    continue
  fi

  printf '%s\n' "${stderr}" >&2
  emit_attempts
  exit "${rc}"
done

emit_attempts
exit 10
