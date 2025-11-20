#!/bin/bash

MSG_FILE="$1"
MIN_BODY_LEN=10

# If no file provided, get latest commit message
if [ -z "$MSG_FILE" ]; then
    TMP_FILE=$(mktemp)
    git log -1 --pretty=format:"%B" >"$TMP_FILE"
    MSG_FILE="$TMP_FILE"
fi

# print commit message
echo -e "Processing commit message:\n"
cat "$MSG_FILE"
echo -e "\nEnd of commit message"

# 0 = pass, 1 = fail
FAIL_LENGTH=0
FAIL_SIGNED_OFF_BY=0

BODY=$(tail -n +3 "$MSG_FILE" | sed '/^\s*#/d' | sed '/^\s*$/d')
BODY_LEN=$(echo -n "$BODY" | sed '/Signed-off-by:/d' | wc -m)

if [ "$BODY_LEN" -lt "$MIN_BODY_LEN" ]; then
    echo -e "\n\n**WARNING: Commit message body is too short (has $BODY_LEN chars, minimum $MIN_BODY_LEN required).**\n" >&2
    echo "Please add a detailed explanation after the subject line." >&2
    FAIL_LENGTH=1
fi

if ! grep -qi '^Signed-off-by:' "$MSG_FILE"; then
    echo -e "\n\n**WARNING: Missing 'Signed-off-by:' line in commit message.**\n" >&2
    echo "Add: Signed-off-by: Your Name <you@example.com>" >&2
    FAIL_SIGNED_OFF_BY=1
fi

[ -n "$TMP_FILE" ] && rm -f "$TMP_FILE"

if [ "$FAIL_LENGTH" -eq 0 ] && [ "$FAIL_SIGNED_OFF_BY" -eq 0 ]; then
    echo "Commit message passes all checks."
    exit 0
else
    echo -e "\nSome checks failed. See warnings above.\n"
    exit 1
fi
