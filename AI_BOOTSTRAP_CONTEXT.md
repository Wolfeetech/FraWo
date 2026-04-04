# AI Bootstrap Context

## Purpose

- Read `INTRODUCTION_PROMPT.md` first.
- Then read this file.
- Then read `LIVE_CONTEXT.md`, `README.md`, `OPS_HOME.md`, and the relevant file in `OPERATIONS/`.
- This file exists so a future AI can understand the server, pages, users, and current direction in one pass.

## Estate In One Screen

- Organization: `FraWo`
- Primary operator/admin: `Wolf`
- Primary business user rollout: `Franz`
- StudioPC local LAN gateway/router: `192.168.2.1` `easy_box`
- UCG transition gateway for `proxmox-anker`: `10.1.0.1`
- Proxmox host professional management path: `100.69.179.87` Tailscale, runtime `10.1.0.92`, transition aliases `192.168.2.10` and temporary `192.168.2.1`
- Core toolbox/control node: internal `192.168.2.20`, additive UCG pilot alias `10.1.0.20`, Tailscale/frontdoor `100.99.206.128`
- Nextcloud VM: `192.168.2.21`
- Odoo VM: `192.168.2.22`
- Paperless VM: `192.168.2.23`
- Home Assistant OS VM: `192.168.2.24`
- PBS VM target: `192.168.2.25`, currently `degraded`
- Vaultwarden CT: `192.168.2.26:8080`, productive entry via `https://vault.hs27.internal`
- Radio node: `192.168.2.155` and Tailscale `100.64.23.77`
- Shared frontend node: `surface-go-frontend` on `192.168.2.154`
- Separate Stockenweiler legacy support LAN exists on `192.168.178.0/24`
- Internal DNS zone: `hs27.internal`
- Tailscale subnet router and internal reverse proxy live on `toolbox`
- Latest whole-estate census: `artifacts/estate_census/latest_report.md`
- Latest platform health audit: `artifacts/platform_health/latest_report.md`
- Latest storage optimization audit: `artifacts/storage_optimization/latest_report.md`
- Latest CI/CD delivery factory report: `artifacts/cicd_delivery_factory/latest_report.md`
- Latest CI/CD delivery factory preflight: `artifacts/cicd_delivery_factory/latest_preflight.md` with current hard limit `repo_side_factory_only`
- Transition note `2026-04-03`: `wolfstudiopc` currently reaches the core services professionally via `toolbox` Tailscale frontdoors on `100.99.206.128:*`; direct StudioPC access to the legacy guest `192.168.2.x` range is not the working path while the UCG migration bridge is active

## Service And Page Map

- Root control portal: `http://portal.hs27.internal`
- Franz start page: `http://portal.hs27.internal/franz/`
- Nextcloud: `http://cloud.hs27.internal` and direct `http://192.168.2.21`
- Paperless: `http://paperless.hs27.internal` and direct `http://192.168.2.23`
- Odoo: `http://odoo.hs27.internal` and direct `http://192.168.2.22:8069`
- Home Assistant: `http://ha.hs27.internal` and direct `http://192.168.2.24:8123`
- Vaultwarden: `https://vault.hs27.internal`
- Vaultwarden health/bootstrap path: `http://192.168.2.26:8080/alive`
- Vaultwarden admin path: `https://vault.hs27.internal/admin`
- Jellyfin browser path: `http://media.hs27.internal`
- Jellyfin TV-safe path: `http://192.168.2.20:8096`
- Jellyfin mobile Tailscale path: `http://100.99.206.128:8449`
- Radio UI: `http://radio.hs27.internal`
- Radio mobile Tailscale path: `http://100.99.206.128:8448`

## User And Device Model

- `Wolf` is the operator/admin path. His core tools are Nextcloud, Paperless, Odoo, Home Assistant, Radio Control, Vaultwarden, and the portal.
- `Wolf Arbeitssurface` is a separate trusted client from `Franz Surface Laptop`: default local work device, internal access on-demand via Tailscale, no permanent full-tunnel by default.
- `Franz` is the normal business user path. The current MVP scope is Surface Laptop, iPhone, Nextcloud, Paperless, Odoo, and Vaultwarden.
- Shared living-room usage is a separate path from admin usage.
- Google TV now connects to Jellyfin again, but the successful test used the `Wolf` account.
- The intended shared Jellyfin profile remains `TV Wohnzimmer`, but its password was not available during the last TV test.
- `surface-go-frontend` is a shared kiosk-style frontend node and remains inside the certification scope.
- `Stockenweiler` is the next external managed-support track after the website release track, not a second integrated site.

## Access And Secret Rules

- Shared passwords and shared app credentials belong in the `FraWo` organization in Vaultwarden.
- No plaintext credentials in markdown, ad hoc notes, or repo-tracked local files.
- `wolf@frawo-tech.de` is the operator identity, but the technical base mailbox for app SMTP is `webmaster@frawo-tech.de`.
- `franz@frawo-tech.de` is a real mailbox and was technically verified against STRATO IMAP/SMTP.
- App SMTP authenticates with `webmaster@frawo-tech.de`.
- The visible app sender is `noreply@frawo-tech.de`.
- Vaultwarden is invite-only for productive use.

## Current Verified Live Facts

- The root portal UI at `portal.hs27.internal` was rebuilt and is live.
- The root portal and the Franz page are now intentionally reduced to the current business MVP: Portal, Vault, Nextcloud, Paperless, and Odoo.
- Vaultwarden SMTP is live, invitations are enabled, and the admin token is no longer stored as plaintext in the live container config.
- The Vaultwarden invitation mail to `franz@frawo-tech.de` arrived successfully.
- The `FraWo` invite for `franz@frawo-tech.de` was accepted.
- UCG transition segment is active: `proxmox-anker` now reports `vmbr0` on `10.1.0.92/24` (GW `10.1.0.1`) plus transition aliases `192.168.2.10/24` and `192.168.2.1/24`.
- `wolfstudiopc` currently reaches `Home Assistant`, `Odoo`, `Nextcloud`, `Paperless`, `Portal`, `Vault`, `Radio`, and `Media` professionally through the `toolbox` Tailscale frontdoors on `100.99.206.128`.
- Platform health snapshot `2026-04-04`: Anker is operational and not capacity-critical; the hottest runtime pressure is Stockenweiler host swap plus `hdd-backup` pressure, while `Odoo` itself is runtime-green.
- Stockenweiler still carries a fragmented legacy `yourparty` payload across `VM 210 azuracast-vm`, `CT 207 radio-wordpress-prod`, `CT 208 mariadb-server`, and `CT 211 radio-api`; capture this payload before thinning the site.
- First UCG service pilot is live on `toolbox`: additive alias `10.1.0.20/24` is active and persistent, and the `portal` vhost answers on the target IP while the existing frontdoors remain green.
- Jellyfin now publishes the direct LAN address for clients, which fixed the TV connection path for devices without working `hs27.internal` DNS.
- Franz mailbox authentication was verified.
- `Nextcloud`, `Paperless`, and `Odoo` are SMTP-configured against the shared mail baseline.
- `AzuraCast` remains the only app-SMTP holdout because the current blocker is SSH access to `raspberry_pi_radio`.
- The next real end-to-end user test is the visible MVP walkthrough for Wolf and Franz across Vault, Nextcloud, Paperless, and Odoo.
- Strategic default for the next product phase: keep `Odoo` as CRM/portal/business shell and keep `AzuraCast` as the media engine instead of trying to make listener accounts the master identity path.
- Stockenweiler local legacy facts were recovered from old StudioPC workspaces and a local router export:
  - router `FRITZ!Box 5690 Pro` on `192.168.178.1`
  - Proxmox host `192.168.178.25`
  - Home Assistant `192.168.178.67`
  - Brother printer `192.168.178.153`
  - MagentaTV `192.168.178.120`
  - canonical external target name now `online-prinz.de`

## Certification Reality

- The estate is not yet allowed to claim a professional production seal.
- `artifacts/release_mvp_gate/<latest>/release_mvp_gate.md` is the business-MVP decision source.
- `artifacts/production_gate/<latest>/production_gate.md` is the only valid certification decision source.
- `MVP_READY` means the current business core can be released internally.
- `MVP_READY` does not mean `CERTIFIED`.
- `PBS` remains the main technical blocker until `VM 240`, datastore, backup proof, and restore proof are green again.
- Manual evidence for user rollout, shared devices, and frontend acceptance is still required.
- Future AI must not call the platform "production-ready" unless the latest production gate says `CERTIFIED`.

## Working Rule For Future AI

1. Read `INTRODUCTION_PROMPT.md` first.
2. Read `AI_BOOTSTRAP_CONTEXT.md`.
3. Read `LIVE_CONTEXT.md` for the latest generated handoff state.
4. Read `README.md` for the canonical read order and source-of-truth map.
5. Open the relevant service runbook in `OPERATIONS/`.
6. Use the latest stress test, release-MVP gate, and production gate artifacts as the deciding runtime evidence.
7. If a task is blocked by hardware, browser login, physical device access, or provider account action, state it with `AKTION VON DIR ERFORDERLICH:`.

## Immediate Do-Not-Regress Rules

- Do not switch Jellyfin TV clients back to `http://media.hs27.internal`; TVs should use `http://192.168.2.20:8096`.
- Do not recreate any plaintext access register inside the workspace; keep shared passwords out of markdown files.
- Do not bloat the portal UI with Media, Radio, Home Assistant, or shared frontend controls before the current business MVP is visibly stable.
- Do not mark PBS healthy until the guarded rebuild path is actually completed and proven.
- Do not claim the shared frontend is certified just because the portal exists; it remains an explicit acceptance item.
