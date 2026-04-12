# Ops Control Center

> **Zentraler Einstiegspunkt für den Solo-Operator.**
> Öffne diese Datei zuerst – egal ob du am Handy bist oder nicht weißt, wo du anfangen sollst.

---

## Was tun, wenn du nicht weißt, was zu tun ist?

1. **Prüfe, ob Tailscale verbunden ist.** Öffne die Tailscale App – ist `Connected` aktiv?
2. **Öffne den Portal-Link:** [`http://100.99.206.128:8447/`](http://100.99.206.128:8447/) → Wenn er lädt, ist dein Remote-Zugang in Ordnung.
3. **Schau in die Ampel unten** (Abschnitt [Status-Übersicht](#status-übersicht)) – dort siehst du, was grün oder rot ist.
4. **Nimm genau eine Aufgabe** aus [`OPERATOR_TODO_QUEUE.md`](OPERATOR_TODO_QUEUE.md) (Abschnitt **Next**) und mach nur diese.
5. **Wenn etwas kaputt ist:** Lies den entsprechenden Eintrag unter [Plattform-Kategorien](#plattform-kategorien) und folge dem Link zum Runbook.

**Goldene Regel:** Immer nur eine Sache auf einmal. Nie mehr als 3 Tasks gleichzeitig in "Doing".

---

## Status-Übersicht

Diese Sektion fasst die zuletzt generierten Artefakte zusammen.
Aktuelle Rohdaten: [`artifacts/estate_census/latest_report.md`](artifacts/estate_census/latest_report.md) · [`artifacts/platform_health/latest_report.md`](artifacts/platform_health/latest_report.md)

### Frontdoors (Stand: 2026-04-11)

| Service | Port | Status | URL |
|---------|------|--------|-----|
| **Vaultwarden** | 8442 | 🟢 ok (200) | `http://100.99.206.128:8442/alive` |
| **Home Assistant** | 8443 | 🟡 degraded (400) | `http://100.99.206.128:8443/` |
| **Odoo** | 8444 | 🟢 ok (200) | `http://100.99.206.128:8444/web/login` |
| **Nextcloud** | 8445 | 🟢 ok (302) | `http://100.99.206.128:8445/` |
| **Paperless** | 8446 | 🟢 ok (200) | `http://100.99.206.128:8446/accounts/login/` |
| **Portal** | 8447 | 🟢 ok (200) | `http://100.99.206.128:8447/` |
| **Radio** | 8448 | 🟡 degraded (502) | `http://100.99.206.128:8448/` |
| **Media** | 8449 | 🟢 ok (302) | `http://100.99.206.128:8449/` |

> **Hinweis:** Diese Tabelle wird manuell aktualisiert. Für den aktuellen Live-Stand immer
> [`artifacts/estate_census/latest_report.md`](artifacts/estate_census/latest_report.md) öffnen.

### Aktuelle Blocker (Stand: 2026-04-11)

- 🔴 **HTTPS / Public Edge** – `www.frawo-tech.de` HTTPS blockiert durch DS-Lite (EasyBox 805 kein IPv4-Portforward). Lösung: Cloudflare-Proxy oder ISP-Dual-Stack-Tarif.
- 🔴 **Stockenweiler SSL** – Zertifikat für `home.prinz-stockenweiler.de` seit April 2026 abgelaufen. Erneuerung via NPM LXC 103 oder Certbot CLI erforderlich.
- 🟡 **Home Assistant** Frontdoor gibt HTTP 400 zurück – Frontdoor-Konfiguration prüfen.
- 🟡 **Radio** gibt HTTP 502 zurück – AzuraCast/Pi-Node prüfen.
- 🟡 **PBS** (VM 240) – monatlicher Restore-Drill fällig.

Vollständige Blocker-Liste: [`artifacts/platform_health/latest_report.md`](artifacts/platform_health/latest_report.md)

---

## Plattform-Kategorien

### 🔐 Security & Recovery

**Was gehört hierher:** Vaultwarden (Passwort-Tresor), Vault-Ansible, Recovery Material, Secrets-Policy.

**Aktueller Stand:** Vaultwarden ist operativ. Recovery-Material (2 Offline-Kopien) verifiziert am 2026-04-09. ✅

**Wo nachschauen:**
- Runbook: [`OPERATIONS/BITWARDEN_OPERATIONS.md`](OPERATIONS/BITWARDEN_OPERATIONS.md)
- Sicherheits-Baseline: [`SECURITY_BASELINE.md`](SECURITY_BASELINE.md)
- Recovery Sheet: [`VAULTWARDEN_RECOVERY_SHEET.md`](VAULTWARDEN_RECOVERY_SHEET.md)
- Quick Link (Handy): `http://100.99.206.128:8442/alive`

---

### 💾 Backups & Restore

**Was gehört hierher:** Proxmox Backup Server (PBS), Restore-Drills, Portable USB Backup.

**Aktueller Stand:** PBS VM 240 gestoppt. Kein aktiver Backup-Job auf Anker. Monatlicher Restore-Drill offen.

**Wo nachschauen:**
- Runbook: [`OPERATIONS/PBS_OPERATIONS.md`](OPERATIONS/PBS_OPERATIONS.md)
- Setup-Plan: [`PBS_VM_240_SETUP_PLAN.md`](PBS_VM_240_SETUP_PLAN.md)
- Letzter Restore-Nachweis: [`BACKUP_RESTORE_PROOF.md`](BACKUP_RESTORE_PROOF.md)
- CLI: `make pbs-restore-proof`

---

### 🏢 Business Apps

**Was gehört hierher:** Odoo (CRM/ERP), Nextcloud (Dateien, Mail-Sync), Paperless (Dokumente/OCR).

**Aktueller Stand:** Alle drei grün und erreichbar.

**Wo nachschauen:**
- Odoo Runbook: [`OPERATIONS/ODOO_OPERATIONS.md`](OPERATIONS/ODOO_OPERATIONS.md)
- Nextcloud Runbook: [`OPERATIONS/NEXTCLOUD_OPERATIONS.md`](OPERATIONS/NEXTCLOUD_OPERATIONS.md)
- Paperless Runbook: [`OPERATIONS/PAPERLESS_OPERATIONS.md`](OPERATIONS/PAPERLESS_OPERATIONS.md)
- Quick Links (Handy):
  - Odoo: `http://100.99.206.128:8444/web/login`
  - Nextcloud: `http://100.99.206.128:8445/`
  - Paperless: `http://100.99.206.128:8446/accounts/login/`

---

### 🏠 Smart Home

**Was gehört hierher:** Home Assistant OS (HAOS, VM 210), Zigbee/USB-Geräte.

**Aktueller Stand:** HAOS läuft stabil auf `192.168.2.24`, aber Frontdoor gibt HTTP 400.

**Wo nachschauen:**
- Runbook: [`OPERATIONS/HAOS_OPERATIONS.md`](OPERATIONS/HAOS_OPERATIONS.md)
- Setup-Plan: [`HAOS_VM_210_SETUP_PLAN.md`](HAOS_VM_210_SETUP_PLAN.md)
- Quick Link (Handy): `http://100.99.206.128:8443/`

---

### 📻 Media / Radio

**Was gehört hierher:** AzuraCast (Radio-Engine, Raspberry Pi), Jellyfin (Medienserver, Toolbox).

**Aktueller Stand:** Radio-Frontdoor gibt HTTP 502 (Pi-Node offline?). Jellyfin läuft (8449 ok).

**Wo nachschauen:**
- AzuraCast Runbook: [`OPERATIONS/AZURACAST_OPERATIONS.md`](OPERATIONS/AZURACAST_OPERATIONS.md)
- Jellyfin Runbook: [`OPERATIONS/JELLYFIN_OPERATIONS.md`](OPERATIONS/JELLYFIN_OPERATIONS.md)
- Radio-Standard: [`RADIO_OPERATIONS_STANDARD.md`](RADIO_OPERATIONS_STANDARD.md)
- Quick Links (Handy):
  - Radio: `http://100.99.206.128:8448/`
  - Media (Jellyfin): `http://100.99.206.128:8449/`

---

### 🌐 Network & Access

**Was gehört hierher:** Tailscale VPN, Split-DNS (`hs27.internal`), AdGuard Home, UCG-Ultra.

**Aktueller Stand:** Tailscale läuft. Split-DNS (Tailnet Route-Freigabe) noch offen. AdGuard im Opt-in-Betrieb.

**Wo nachschauen:**
- Tailscale Phone-Zugang: [`TAILSCALE_PHONE_ACCESS.md`](TAILSCALE_PHONE_ACCESS.md)
- Split-DNS-Plan: [`TAILSCALE_SPLIT_DNS_PLAN.md`](TAILSCALE_SPLIT_DNS_PLAN.md)
- Netzwerk-Inventar: [`NETWORK_INVENTORY.md`](NETWORK_INVENTORY.md)
- UCG Zielarchitektur: [`UCG_NETWORK_ARCHITECTURE.md`](UCG_NETWORK_ARCHITECTURE.md)

---

### 🗄️ Storage & Capacity

**Was gehört hierher:** NVMe (Anker), HDD-Backup (Stockenweiler), Portable USB Backup, Capacity Review.

**Aktueller Stand:** Anker Rootfs bei 69 %, Stockenweiler HDD-Backup bei 84 % – kein neues Backup-Load. Stockenweiler Swap bei 79 % – Speicherdruck.

**Wo nachschauen:**
- Kapazitäts-Review: [`CAPACITY_REVIEW.md`](CAPACITY_REVIEW.md)
- Rightsizing-Plan: [`RIGHTSIZING_MAINTENANCE_PLAN.md`](RIGHTSIZING_MAINTENANCE_PLAN.md)
- Storage Runbook: [`OPERATIONS/STORAGE_NODE_OPERATIONS.md`](OPERATIONS/STORAGE_NODE_OPERATIONS.md)
- CLI: `make capacity-review`

---

## Einzige Nächste Operator-Aktion

> **Regel:** Wähle genau **eine** Aufgabe aus dem Abschnitt **🟡 Next** in [`OPERATOR_TODO_QUEUE.md`](OPERATOR_TODO_QUEUE.md),
> verschiebe sie nach **🟢 Doing** und erledige nur diese – bevor du eine neue startest.

**Aktuelle "Next"-Tasks (Stand 2026-04-11):**

| Task | Lane | Einstieg |
|------|------|---------|
| HTTPS für `www.frawo-tech.de` (Cloudflare oder ISP-Dual-Stack) | Lane B | `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` |
| Stockenweiler SSL erneuern (`home.prinz-stockenweiler.de`) | Lane D | NPM LXC 103 oder Certbot CLI |
| PBS-Restore-Drill monatlich wiederholen | Lane C | `make pbs-restore-proof` |

→ **Öffne [`OPERATOR_TODO_QUEUE.md`](OPERATOR_TODO_QUEUE.md) und wähle genau eine.**

---

## 📱 Phone Mode

**Wenn du nur ein Handy hast, gilt:**

- ✅ **Erlaubt:** Nur `http://100.99.206.128:<port>/...` (Tailscale IP + Port)
- ❌ **Nicht auf dem Handy:** `cloud.hs27.internal`, `odoo.hs27.internal`, `*.hs27.internal` – diese funktionieren nur im LAN mit Split-DNS
- ❌ **Nicht auf dem Handy:** Interne IPs wie `192.168.2.x` (kein direkter LAN-Zugriff von außen)

**Warum?** Interne Namen (`*.hs27.internal`) werden nur vom lokalen AdGuard/Split-DNS aufgelöst.
Das Handy benutzt euer internes DNS nicht automatisch – daher NXDOMAIN-Fehler.
Tailscale IP + Port umgeht das DNS vollständig und funktioniert immer, solange Tailscale verbunden ist.

**Checkliste vor dem Öffnen eines Links:**
1. Tailscale App → `Connected` ✓
2. URL beginnt mit `http://100.99.206.128:` ✓
3. Kein `https` (intern kein TLS) ✓

---

## Quick Links (Tailscale)

Alle Links über Tailscale-IP `100.99.206.128` (toolbox). Nur bei aktivem Tailscale erreichbar.

| Service | URL | Erwartete Antwort |
|---------|-----|-------------------|
| **Vaultwarden** (Passwörter) | [`http://100.99.206.128:8442/alive`](http://100.99.206.128:8442/alive) | `OK` ✅ |
| **Home Assistant** (Smart Home) | [`http://100.99.206.128:8443/`](http://100.99.206.128:8443/) | `302` oder Login (derzeit: 400) |
| **Odoo** (CRM/Business) | [`http://100.99.206.128:8444/web/login`](http://100.99.206.128:8444/web/login) | `200` Login-Seite ✅ |
| **Nextcloud** (Dateien) | [`http://100.99.206.128:8445/`](http://100.99.206.128:8445/) | `302` → Login ✅ |
| **Paperless** (Dokumente) | [`http://100.99.206.128:8446/accounts/login/`](http://100.99.206.128:8446/accounts/login/) | `200` Login-Seite ✅ |
| **Portal** (Übersicht) | [`http://100.99.206.128:8447/`](http://100.99.206.128:8447/) | `200` Portal ✅ |
| **Radio** (AzuraCast) | [`http://100.99.206.128:8448/`](http://100.99.206.128:8448/) | `200` (derzeit: 502) |
| **Media** (Jellyfin) | [`http://100.99.206.128:8449/`](http://100.99.206.128:8449/) | `302` → Login ✅ |

> **Tipp:** Portal (8447) ist dein "Alles-OK-Test". Wenn Portal lädt, ist Tailscale + Toolbox in Ordnung.

---

## Decision Gates

Bevor du einen Service als "produktionsbereit" betrachtest, muss er durch das **Produktions-Gate**:

**Zwei mögliche Ergebnisse:**
- `CERTIFIED` – alle harten Checks sind grün, manuelle Evidenz liegt vor
- `BLOCKED` – mindestens ein Kern-Check ist rot oder Evidenz fehlt

**Aktueller Gate-Status:** [`PLATFORM_STATUS.md`](PLATFORM_STATUS.md)

**Vollständige Gate-Definition:** [`OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`](OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md)

**Bedeutung für den Alltag:**
- `MVP_READY` = intern freigegeben, Business-MVP läuft – **das ist der aktuelle Stand** ✅ (Lane A abgeschlossen 2026-04-09)
- `CERTIFIED` = alle Checks grün, manuelle Evidenz vollständig, Runbooks vorhanden
- `BLOCKED` = offene Blocker verhindern den Betrieb – **PBS ist derzeit blocked**

Öffne [`OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`](OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md) für die vollständige Checkliste und Gate-Kriterien.

---

*Letzte manuelle Aktualisierung: 2026-04-11 | Artefakte: [`artifacts/estate_census/latest_report.md`](artifacts/estate_census/latest_report.md) (2026-04-09) · [`artifacts/platform_health/latest_report.md`](artifacts/platform_health/latest_report.md) (2026-04-11)*
