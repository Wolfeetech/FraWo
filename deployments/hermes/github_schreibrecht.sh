#!/usr/bin/env bash
# Hermes darf ins FraWo-Repo committen und pushen (AGENTS.md: Commit = Push). Wolf 07.10.2026, Odoo #1966.
# Eigener Schluessel nur fuer dieses eine Repo (GitHub "Deploy Key" mit Schreibrecht).
# Schritt 1 (Wolf, Browser): github.com/Wolfeetech/FraWo/settings/keys/new
#   Title: Hermes CT160 · Key: Inhalt von CT160 /home/hermes/.ssh/github_frawo.pub · Haken "Allow write access" · Add key
# Schritt 2 (Wolf am StudioPC):  ! bash C:/Users/StudioPC/FraWo/deployments/hermes/github_schreibrecht.sh
# Widerruf jederzeit: github.com/Wolfeetech/FraWo -> Settings -> Deploy keys -> Delete.
set -euo pipefail
ssh -o BatchMode=yes root@10.1.0.227 'pct exec 160 -- su - hermes -c "
  grep -q \"Host github.com\" ~/.ssh/config 2>/dev/null || printf \"Host github.com\n  IdentityFile ~/.ssh/github_frawo\n  IdentitiesOnly yes\n\" >> ~/.ssh/config
  chmod 600 ~/.ssh/config
  ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 | head -1
  cd ~/FraWo && git remote set-url origin git@github.com:Wolfeetech/FraWo.git
  git config user.name \"Hermes (FraWo)\"; git config user.email hermes@frawo.tech
  git push --dry-run origin main 2>&1 | tail -1; echo Hermes-Schreibrecht: fertig"'
