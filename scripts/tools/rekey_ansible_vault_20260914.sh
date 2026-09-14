#!/bin/bash
# Einmal-Skript (14.09.2026): rotiert das Ansible-Vault-Passwort, nachdem das
# alte in scripts/tools/vault_pass.sh im Klartext im public Repo lag (seit
# 30.03.2026, entfernt in Commit d318bed). Siehe Odoo-Aufgabe #1455.
#
# Laeuft auf dem ProDesk (stock-pve), weil ansible-vault unter Windows kaputt
# ist (os.get_blocking()-Bug). Kein Mensch tippt hier ein Passwort - das alte
# kommt automatisch aus der Git-Historie, das neue wird zufaellig erzeugt.
# Keiner der beiden Werte wird auf dem Bildschirm angezeigt.
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ ! -f ansible/inventory/group_vars/all/vault.yml ]; then
  echo "FEHLER: bitte aus dem FraWo-Repo-Hauptordner starten." >&2
  exit 1
fi

echo "1/4 Neues Vault-Passwort erzeugen (bleibt lokal, gitignored)..."
openssl rand -base64 32 > ansible/.vault_pass

echo "2/4 Altes Passwort aus Git-Historie holen (nicht angezeigt)..."
OLD_PW_FILE=$(mktemp)
git show d318bed~1:scripts/tools/vault_pass.sh | tail -1 | sed 's/^echo //' > "$OLD_PW_FILE"

TAG=$$
echo "3/4 Rekey auf stock-pve ausfuehren (dort funktioniert ansible-vault)..."
scp -q ansible/inventory/group_vars/all/vault.yml "stock-pve:/tmp/vault_rekey_${TAG}.yml"
scp -q "$OLD_PW_FILE" "stock-pve:/tmp/vault_old_${TAG}.txt"
scp -q ansible/.vault_pass "stock-pve:/tmp/vault_new_${TAG}.txt"

ssh stock-pve "ansible-vault rekey \
  --vault-password-file=/tmp/vault_old_${TAG}.txt \
  --new-vault-password-file=/tmp/vault_new_${TAG}.txt \
  /tmp/vault_rekey_${TAG}.yml"

scp -q "stock-pve:/tmp/vault_rekey_${TAG}.yml" ansible/inventory/group_vars/all/vault.yml
ssh stock-pve "shred -u /tmp/vault_rekey_${TAG}.yml /tmp/vault_old_${TAG}.txt /tmp/vault_new_${TAG}.txt 2>/dev/null || rm -f /tmp/vault_rekey_${TAG}.yml /tmp/vault_old_${TAG}.txt /tmp/vault_new_${TAG}.txt"
rm -f "$OLD_PW_FILE"

echo "4/4 Fertig. Pruefen und committen:"
echo "  git diff --stat ansible/inventory/group_vars/all/vault.yml"
echo "  git add ansible/inventory/group_vars/all/vault.yml"
echo "  git commit -m 'security: rekey ansible-vault mit neuem Passwort'"
echo "  git push"
echo ""
echo "Danach kann dieses Skript geloescht werden: git rm scripts/tools/rekey_ansible_vault_20260914.sh"
