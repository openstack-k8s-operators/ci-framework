#!/bin/bash

# Get the latest commit message file
TMP_MSG_FILE="$1"

if [ -z "$TMP_MSG_FILE" ]; then
    TMP_MSG_FILE=$(mktemp)
    git log -1 --pretty=format:"%B" | head -n1
fi

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

echo -e "\n\nDetected changes in roles: **$CHANGED_ROLES**"
MSG=$(head -n 1 "$TMP_MSG_FILE")
ROLE_COUNT=$(echo "$CHANGED_ROLES" | tr '|' '\n' | wc -l)

if [ "$ROLE_COUNT" -eq 1 ]; then
    # shellcheck disable=SC2016
    ESCAPED_ROLE=$(printf '%s\n' "$CHANGED_ROLES" | sed 's/[]\.*^$()+?{|]/\\&/g')
    PATTERN="^[[(]${ESCAPED_ROLE}[])]"
else
    PATTERN="^[[(](multiple)[])]"
fi

if ! grep -qE "$PATTERN" <<<"$MSG"; then
    echo -e "\n**ERROR: Commit message must start with:**\n"
    if [ "$ROLE_COUNT" -eq 1 ]; then echo -e "\t[$CHANGED_ROLES]\n"; fi
    if [ "$ROLE_COUNT" -gt 1 ]; then echo -e "\t(multiple)\n\n"; fi
    echo -e "Example commit header:\n"
    echo -e "\t-[reproducer] fix task something\n"
    echo -e "\t-(cifmw_helpers) improve code\n"
    echo -e "\t-[multiple] updated default value"
    exit 1
fi

echo "Commit message prefix is valid."
