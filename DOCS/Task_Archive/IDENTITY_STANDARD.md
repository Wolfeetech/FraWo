# Identity Standard (FraWo GbR)

## Goal

Use personal identities for people, role identities for shared functions, and never use a shared mailbox as a personal admin login.

## Brand Identity Protocol (Finalized 07.04.2026)

**Concept:** High-End Hybrid (Altes Handwerkswissen trifft moderne Technik-Liebhaberei)

### 1. Markenname & Slogan
- **Offizieller Name:** FraWo GbR
- **Inhaber:** W. Prinz & F. Bienert
- **Subline/Claim:** Smart Media & Event
- **Tonalität:** Bodenständig, unzerstörbar, technisch präzise, lösungsorientiert.

### 2. Brand Kit (Visuals)
- **Primary Deep Forest:** `#064e3b` (Vertrauen & Handwerk)
- **Accent UV Power:** `#a855f7` (Technik, Innovation, Event-Licht)
- **Tech Mint Details:** `#4ade80` (Status-Anzeigen, Akzente)
- **Background Moss Light:** `#f0fdf4` (Lesbarkeit)
- **Typografie:** Poppins (Black für Überschriften, Medium für Sub, Regular für Text)

### 3. Logo-Architektur
- **Assets:** `brand_assets/1.png` (Primary), `brand_assets/2.png` (Accent-Wo)
- **Design:** Typographisch, "FRAWO" in Poppins Black, horizontale Trennlinie, "Smart Media & Event" mit hohem Letter-Spacing (300).

### 4. Tone of Voice
- **Direktheit:** Klartext, Probleme benennen, Lösungen liefern.
- **Expertise:** Verbindung von Zimmermanns-Präzision mit IT-Intelligenz ("Anpacker mit Köpfchen").
- **Ansprache:** Professionell auf Augenhöhe. Du-Form in der Branche, Sie-Form bei Neukunden/Industrie.

## Canonical Mailboxes

| Identity | Type | Purpose |
| --- | --- | --- |
| `wolf@frawo-tech.de` | personal | owner, admin, audit trail |
| `franz@frawo-tech.de` | personal | standard user, audit trail |
| `frontend@frawo-tech.de` | shared role | Surface Go, kiosk, shared frontend workflows |
| `agent@frawo-tech.de` | shared role | automation bot for Odoo and later workflow intake |
| `info@frawo-tech.de` | role | website/contact/inbound company mail |
| `noreply@frawo-tech.de` | role | system notifications |
| `admin@frawo-tech.de` | role | optional break-glass/admin alias |

## Mail And Secrets Default

- Real mailboxes are created first at `STRATO`.
- `Vaultwarden` on `CT120` is the target secret home.
- Shared business secrets live in the `FraWo` organization, not in isolated personal vaults.
- Markdown files may document state, but they are not the final password store.

## Rules

- `wolf@frawo-tech.de` and `franz@frawo-tech.de` are the primary human identities.
- `info@frawo-tech.de` is not a personal admin account.
- `frontend@frawo-tech.de` is the only shared device identity.
- `agent@frawo-tech.de` is an automation identity, not a human daily login.
- Every service should map back to a personal owner plus a documented role account where needed.

## Service Mapping

| Service | Wolf | Franz | Frontend | Notes |
| --- | --- | --- | --- | --- |
| Nextcloud | personal account | personal account | limited shared account | main file workflows |
| Paperless | personal account | personal account | limited shared search/upload account | access should follow filing rules |
| Odoo | named user | named user | no admin | business actions must stay attributable; `agent@...` only for bounded automation |
| Jellyfin | named profile | named profile | shared device profile | quick switching on TV/Surface |
| AzuraCast | named admin | optional editor later | no admin | avoid shared admin |
| Surface Go | local admin `frawo` | none | kiosk user `frontend` | kiosk is read-only by default |
| Stockenweiler | support owner | n/a | n/a | separate support and provider identities |

## FraWo Organization (GbR)

- Organization name: `FraWo GbR`
- Site contexts:
  - `Anker` for the base server and private core network
  - `Villa` for studio and radio operations
  - `Stockenweiler` for the external support location

## Order Of Work

1. Create final mailboxes at `STRATO`.
2. Finish internal `HTTPS` for `Vaultwarden`.
3. Create the `FraWo` organization and the six collections.
4. Update Odoo branding with the finalized Kit (07.04.2026).
5. Harden the Surface Go around the `frontend` role.
