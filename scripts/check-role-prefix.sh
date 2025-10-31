#!/bin/bash

# Get the latest commit message file
TMP_MSG_FILE=$(mktemp)
git log -1 --pretty=format:"%s%n%n%b" >"$TMP_MSG_FILE"

echo "Checking latest commit message:"
cat "$TMP_MSG_FILE"

if [ -n "$GITHUB_BASE_REF" ]; then
    CHANGED_ROLES=$(git diff "origin/${GITHUB_BASE_REF}" --name-only || true)
else
    CHANGED_ROLES=$(git diff --cached --name-only || true)
fi

CHANGED_ROLES=$(echo "$CHANGED_ROLES" | grep '^roles/' | cut -d'/' -f2 | sort -u | xargs | sed 's/ /|/g')
if [ -z "$CHANGED_ROLES" ]; then
    echo "No roles modified - skipping check..."
    exit 0
fi

echo -e "\n\nDetected changed roles: $CHANGED_ROLES"
MSG=$(head -n 1 "$TMP_MSG_FILE")
if ! grep -qE "^\[($CHANGED_ROLES)\]" <<<"$MSG"; then
    echo -e "\nERROR: Commit message must start with one of: [$CHANGED_ROLES]\n"
    echo "Example: [reproducer] fix task or [cifmw_helpers] improve code"
    exit 1
fi

echo "Commit message prefix is valid."
