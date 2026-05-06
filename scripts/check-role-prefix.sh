#!/bin/bash

# Validate that each commit in the PR has the correct role prefix
# based on the roles modified in that specific commit.

if [ -z "$GITHUB_BASE_REF" ]; then
    echo "Not running in GitHub Actions - skipping check"
    exit 0
fi

echo "Checking all commits in PR against base: origin/${GITHUB_BASE_REF}"
echo ""

# Get all commits in the PR
COMMITS=$(git rev-list origin/${GITHUB_BASE_REF}..HEAD)

if [ -z "$COMMITS" ]; then
    echo "No commits to check"
    exit 0
fi

FAILED=0

# Check each commit individually
while IFS= read -r COMMIT; do
    MSG=$(git log -1 --pretty=format:"%s" "$COMMIT")
    echo "Checking commit ${COMMIT:0:8}: $MSG"

    # Get roles changed in THIS commit only
    CHANGED_ROLES=$(git diff-tree --no-commit-id --name-only -r "$COMMIT" | grep '^roles/' | cut -d'/' -f2 | sort -u | xargs | sed 's/ /|/g')

    if [ -z "$CHANGED_ROLES" ]; then
        echo "  No roles modified - skipping"
        echo ""
        continue
    fi

    echo "  Changed roles: $CHANGED_ROLES"

    ROLE_COUNT=$(echo "$CHANGED_ROLES" | tr '|' '\n' | wc -l)

    if [ "$ROLE_COUNT" -eq 1 ]; then
        # shellcheck disable=SC2016
        ESCAPED_ROLE=$(printf '%s\n' "$CHANGED_ROLES" | sed 's/[]\.*^$()+?{|]/\\&/g')
        PATTERN="^[[(]${ESCAPED_ROLE}[])]"
    else
        PATTERN="^[[(](multiple)[])]"
    fi

    if ! grep -qE "$PATTERN" <<<"$MSG"; then
        echo ""
        echo "  **ERROR: Commit message must start with:**"
        if [ "$ROLE_COUNT" -eq 1 ]; then
            echo "    [$CHANGED_ROLES]"
        else
            echo "    (multiple)"
        fi
        echo ""
        FAILED=1
    else
        echo "  ✓ Valid prefix"
    fi
    echo ""
done <<< "$COMMITS"

if [ $FAILED -eq 1 ]; then
    echo "Example commit messages:"
    echo "  [reproducer] fix task something"
    echo "  (multiple) updated default value"
    exit 1
fi

echo "Each commit message prefix is valid."
