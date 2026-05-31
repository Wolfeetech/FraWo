# Security Incident — Credentials in Git History

**Datum:** 2026-05-31  
**Status:** Teilweise behoben — **Manuelle Rotation erforderlich**

---

## Was ist passiert

Im Repository wurden über längere Zeit echte Zugangsdaten committed:

| Datei | Inhalt | Status |
|-------|--------|--------|
| `vaultwarden_import.csv` | Passwörter für Proxmox, Cloudflare, Odoo | Aus Tracking entfernt ✅ |
| `crack_vault.py` | Liste möglicher Vault-Passwörter (`Hs27Storage2026!` etc.) | Aus Tracking entfernt ✅ |
| `scratch/*.py` | `Wolf2024!Frawo` als Odoo/SMTP-Passwort in ~30 Dateien | Aus Tracking entfernt ✅ |
| `apps/radio-backend/docker-compose.yml` | `POSTGRES_PASSWORD: radio`, `GF_SECURITY_ADMIN_PASSWORD=admin` | Auf Env-Vars umgestellt ✅ |
| `apps/yourparty/apps/api/main.py` | Debug-print von JWT-Secret-Prefix | Entfernt ✅ |

---

## Was JETZT manuell zu tun ist

### 🔴 1. Alle exponierten Passwörter sofort rotieren

Die folgenden Credentials lagen in der Git-History und müssen als **kompromittiert** betrachtet werden:

- **`Wolf2024!Frawo`** — Odoo-Passwort für wolf@frawo-tech.de + SMTP-Passwort bei Strato
- **`Wolf2024!Frawo`** — Proxmox root-Passwort (pve-anker)
- **`Wolf2024!Frawo`** — Cloudflare Login
- Alle Passwörter aus `vaultwarden_import.csv`
- Alle Passwörter aus der `PASSWORDS`-Liste in `crack_vault.py` (auch wenn sie vielleicht nicht stimmen)

### 🔴 2. Git-History bereinigen

Die Dateien sind aus dem aktuellen Branch entfernt, aber **noch in der Git-History** vorhanden. Jeder mit Zugriff auf das Repo kann sie weiterhin sehen via `git log`.

```bash
# Option A: BFG Repo Cleaner (einfacher)
# https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files "vaultwarden_import.csv" .
java -jar bfg.jar --delete-files "crack_vault.py" .
java -jar bfg.jar --delete-folder "scratch" .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# Option B: git filter-repo
pip install git-filter-repo
git filter-repo --path vaultwarden_import.csv --invert-paths
git filter-repo --path crack_vault.py --invert-paths
git filter-repo --path scratch/ --invert-paths
```

> ⚠️ Beide Optionen erfordern einen `force push` und müssen mit allen Repo-Nutzern koordiniert werden.

### 🟡 3. Wenn das Repo mal öffentlich war

Falls das Repo zu irgendeinem Zeitpunkt public war oder Zugriff nach außen hatte:
- GitHub unterstützt das vollständige Löschen von Daten aus der History via Support-Ticket: https://support.github.com/contact
- Alternativ: Neues Repo anlegen, nur saubere Commits übertragen

---

## Was bereits gefixt ist (dieser Commit)

- `scratch/` aus Git-Tracking entfernt und in `.gitignore` aufgenommen
- `vaultwarden_import.csv`, `crack_vault.py`, `odoo_output*.json`, `repo.zip`, `rendered_index.html` aus Tracking entfernt
- `.gitignore` bereinigt (war teilweise UTF-16LE-kodiert, Einträge wirkten nicht)
- Debug-print in `apps/yourparty/apps/api/main.py` entfernt (hat JWT-Key-Prefix geloggt)
- `docker-compose.yml` nutzt jetzt `${POSTGRES_PASSWORD}` statt hardcoded `radio`
- `.env.example` um `POSTGRES_PASSWORD`, `POSTGRES_USER`, `GRAFANA_ADMIN_PASSWORD` ergänzt

---

## Präventionsregeln

1. **Kein Scratch-Code im Repo** — lokale Scripts gehören nicht in die Source Control
2. **Kein `git add .`** ohne `git diff --cached` gelesen zu haben
3. **Pre-commit Hook** oder `git-secrets` / `gitleaks` einsetzen
4. **Ansible Vault** für alle Secrets — nie im Klartext in Scripts
