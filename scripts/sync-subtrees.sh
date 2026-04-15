#!/bin/bash
# FraWo Git Subtree Sync Automation
# This script pulls updates from the consolidated repositories.

set -e

echo "Starting Subtree Sync..."

# App: yourparty
echo "--- Syncing yourparty ---"
git subtree pull --prefix=apps/yourparty https://github.com/wolfeetech/yourparty-tech main --squash

# App: fayanet
echo "--- Syncing fayanet ---"
git subtree pull --prefix=apps/fayanet https://github.com/wolfeetech/FaYa-Net main --squash

echo "--- Sync Complete ---"
