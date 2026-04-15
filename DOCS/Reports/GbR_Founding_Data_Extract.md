# GbR Founding Data Extract - WolfStudioPC

**Timestamp:** 2026-04-15 23:02
**Source:** `FraWo/DOCS/Task_Archive/`

## 📧 Canonical Email Addresses
All emails are managed via Strato.

| Email | Type | Role / Purpose |
| :--- | :--- | :--- |
| `wolf@frawo-tech.de` | Personal | Owner, Admin (often alias of `webmaster@`) |
| `franz@frawo-tech.de` | Personal | Co-Owner, Standard User |
| `info@frawo-tech.de` | Role | General Inbound / Contact |
| `agent@frawo-tech.de` | Role | Automation Bot (Odoo intake) |
| `frontend@frawo-tech.de`| Role | Kiosk / Surface Go Frontend |
| `noreply@frawo-tech.de` | Role | System Notifications |
| `webmaster@frawo-tech.de`| Tech | Technical Base Mailbox |

---

## 🏢 GbR Founding Information
- **Official Name:** FraWo GbR
- **Owners:** Wolfgang Prinz & Franz Bienert
- **Concept:** "High-End Hybrid" (Craftsmanship meets High-Tech)
- **Claim:** Smart Media & Event
- **Brand Kit (Finalized 07.04.2026):**
  - **Deep Forest:** `#064e3b` (Trust & Craft)
  - **Accent UV Power:** `#a855f7` (Technic & Event Light)
  - **Tech Mint:** `#4ade80` (Accents)
  - **Typography:** Poppins (Black/Medium/Regular)

---

## 🚀 Active Projects (Lanes)
The architecture is divided into operational "Lanes":

- **Lane A (Business-MVP):** Core apps (Nextcloud, Odoo, Paperless) - **Status: DONE**
- **Lane B (Website/Public):** Public Edge via Cloudflare/Caddy - **Status: ACTIVE**
- **Lane C (Security/PBS):** Backup Infrastructure & Hardening - **Status: WATCH**
- **Lane D (Stockenweiler):** Remote Support Node - **Status: OK**
- **Lane E (Radio/Media):** AzuraCast & Jellyfin - **Status: BLOCKED** (Pi 4 hardware issue)

---

## 📝 Critical TODOs & Open Tasks
Extracted from `OPERATOR_TODO_QUEUE.md` and `IDENTITY_STANDARD.md`:

### Immediate Actions
- [x] **Release-Gate:** Set `release-mvp-gate.md` to GREEN (`RELEASE_APPROVED`).
- [ ] **Odoo-SSOT:** Monitor `agent@` intake and board governance.
- [x] **Email-Test:** `send_odoo_test_mail.py` created and ready for execution.
- [x] **Jellyfin:** Instructions for `TV Wohnzimmer` password updated.

### Blocked Tasks
- **Vaultwarden Recovery:** Physical offline copies needed (**Target: 2026-05-01**).
- **Radio Pi:** Hardware power cycle required at physical location.

### Infrastructure
- **DS-Lite / HTTPS:** Resolve IPv4 reaching for `www.frawo-tech.de`.
- **PBS Drill:** Repeat monthly restore exercise.
- **Stockenweiler SSL:** Renew certificate for `home.prinz-stockenweiler.de`.

---

## 🗺️ Service URLs (Internal)
- **Portal:** `http://portal.hs27.internal`
- **Nextcloud:** `http://cloud.hs27.internal`
- **Odoo:** `http://odoo.hs27.internal`
- **Vaultwarden:** `https://vault.hs27.internal`
- **Radio:** `http://radio.hs27.internal`
