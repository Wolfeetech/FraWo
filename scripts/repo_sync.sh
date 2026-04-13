#!/bin/bash
# Professional Repository Sync Script for FraWo Master SSOT

WORKSPACE_DIR="/c/Users/Admin/Documents/Private_Networking"
UPSTREAM="origin"
BRANCH="main"

echo "--- Repository Sync Protocol: FraWo Master SSOT ---"
echo "Target: $UPSTREAM/$BRANCH"

# 1. Fetch latest from upstream
git fetch $UPSTREAM $BRANCH

# 2. Check for local changes
if [[ -n $(git status -s) ]]; then
    echo "WARNING: Local workspace has uncommitted changes."
    echo "Please commit or stash your work before syncing."
    exit 1
fi

# 3. Check for divergence
BEHIND=$(git rev-list HEAD..$UPSTREAM/$BRANCH --count)
AHEAD=$(git rev-list $UPSTREAM/$BRANCH..HEAD --count)

if [ $BEHIND -gt 0 ]; then
    echo "Status: Workspace is BEHIND upstream by $BEHIND commits."
    echo "Performing FF-only pull..."
    git pull --ff-only $UPSTREAM $BRANCH
elif [ $AHEAD -gt 0 ]; then
    echo "Status: Workspace is AHEAD of upstream by $AHEAD commits."
    echo "Pushing professional state to GitHub..."
    git push $UPSTREAM $BRANCH
else
    echo "Status: Workspace is UP TO DATE."
fi

echo "--- Sync Complete ---"
