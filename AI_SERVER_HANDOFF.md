# AI Server Handoff

Automatisch generierter Ein-Datei-Handoff fuer den aktuellen Homeserver-Stand.
Keine Secrets. Keine Passwoerter. Diese Datei ist dafuer gedacht, sie direkt an eine andere KI zu geben.

## Nutzung

- Primaerer Read-First fuer eine andere KI: diese Datei
- Wenn tieferer Repo-Kontext noetig ist: `INTRODUCTION_PROMPT.md`, `OPS_HOME.md`, `DOCS/Task_Archive/OPERATOR_TODO_QUEUE.md`
- Diese Datei neu erzeugen mit: `python scripts/generate_ai_server_handoff.py`

## Generierung

- Generated at: `2026-04-20 11:53:08`
- Workspace root: `/mnt/c/Users/Admin/Documents/Private_Networking`
- Git branch: `main`
- Pending git changes: `6`
- Managed hosts in inventory: `31`

## Source Freshness

- `AI_BOOTSTRAP_CONTEXT.md`: `2026-04-19 22:54:12`
- `OPS_HOME.md`: `2026-04-09 19:28:38`
- `DOCS/Task_Archive/OPERATOR_TODO_QUEUE.md`: `2026-04-19 22:54:54`
- `manifests/work_lanes/current_plan.json`: `2026-04-20 10:55:41`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.json`: `2026-04-20 11:18:26`
- `artifacts/public_ipv6_exposure_audit/latest_report.md`: `2026-04-09 19:28:46`
- `artifacts/estate_census/latest_report.json`: `2026-04-09 17:23:24`
  - stale_for_live_truth: `true` (estate census older than platform health by 8 day(s); estate census frontdoor host set ['100.99.206.128'] does not include current frontdoor 100.82.26.53)
- `artifacts/ucg_portal_pilot_preflight/latest_report.json`: `2026-04-13 12:15:49`
  - stale_for_live_truth: `true` (portal pilot preflight older than 1 day (6 day(s)); portal pilot frontdoor host 100.99.206.128 does not match current frontdoor 100.82.26.53)
- `artifacts/website_release_gate/20260330_161648/website_release_gate.md`: `2026-04-09 19:28:49`
- `artifacts/production_gate/20260328_072130/production_gate.md`: `2026-04-09 19:28:44`
- `manifests/control_surface/actions.json`: `2026-04-13 15:31:08`

## Estate Snapshot

- Organization: `FraWo GbR`
- Primary operator/admin: `Wolf`
- Primary business user rollout: `Franz`
- StudioPC local LAN gateway/router: `192.168.2.1` `easy_box` (legacy segment, still active for household devices)
- UCG primary gateway: `10.1.0.1` (UCG-Ultra, VLAN 101 – **aktives Primärnetz**)
- Proxmox host professional management path: `100.69.179.87` Tailscale, primary runtime `10.1.0.92`
- Core toolbox/control node: **`10.1.0.20`** (primary), Tailscale/frontdoor `100.82.26.53`
- Nextcloud VM: **`10.1.0.21`**
- Odoo VM: **`10.1.0.22`**
- Paperless VM: **`10.1.0.23`**
- Home Assistant OS VM: **`10.1.0.24`**
- PBS VM 240: `192.168.2.25`, status **`DEGRADED / INACTIVE`** – sauberes Neuaufsetzen geplant, sobald Kernstack stabil; aktuell kein valider Backup-Pfad
- Vaultwarden CT: `10.1.0.26:8080`, productive entry via `https://vault.hs27.internal`
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
- Transition note `2026-04-03`: `wolfstudiopc` currently reaches the core services professionally via `toolbox` Tailscale frontdoors on `100.82.26.53:*`; direct StudioPC access to the legacy guest `192.168.2.x` range is not the working path while the UCG migration bridge is active

## Core Service Map

- Root control portal: `http://portal.hs27.internal`
- Franz start page: `http://portal.hs27.internal/franz/`
- Nextcloud: `http://cloud.hs27.internal` and direct `http://10.1.0.21`
- Paperless: `http://paperless.hs27.internal` and direct `http://10.1.0.23`
- Odoo: `http://odoo.hs27.internal` and direct `http://10.1.0.22:8069`
- Home Assistant: `http://ha.hs27.internal` and direct `http://10.1.0.24:8123`
- Vaultwarden: `https://vault.hs27.internal`
- Vaultwarden health/bootstrap path: `http://10.1.0.26:8080/alive`
- Vaultwarden admin path: `https://vault.hs27.internal/admin`
- Jellyfin browser path: `http://media.hs27.internal`
- Jellyfin direct path: `http://10.1.0.20:8096`
- Jellyfin mobile Tailscale path: `http://100.82.26.53:8449`
- Radio UI: `http://radio.hs27.internal`
- Radio mobile Tailscale path: `http://100.82.26.53:8448`

## Current Release State

- Active delivery lane: `Lane B: Website/Public`
- Business MVP gate: `MVP_READY`
- Business MVP critical Codex checks: `passed=11` / `non-passed=0`
- Business MVP manual checks: `passed=8` / `pending_or_failed=0`
- Public website gate: `BLOCKED`
- Production certification gate: `BLOCKED`
- Public IPv6 exposure audit: `open_checks=0` / `total_checks=13`

## AI Operating Model

- Model: `professional_autopilot`
- Autonomy: `aggressive_autopilot`
- Primary end state: `internal_ops_stable_public_edge_next`
- Roles: `codex=lead` / `gemini=visible_verification_only` / `operator=decision_and_physical_actions_only`
- Execution loop: `read_only_truth, professional_check, change_classification, decision, post_verify, ssot_refresh`
- Mandatory stop categories:
  - `infra_public_changes`
  - `network_changes`
  - `data_migrations`
  - `storage_pbs_changes`
  - `router_changes`
  - `ha_pve_changes`
  - `security_boundary_changes`
  - `local_windows_admin_token_changes`
  - `irreversible_or_hard_to_rollback_changes`

## Control Plane Snapshot

- Workspace Pyrefly disabled: `true`
- Pyrefly process present: `false`
- Stale ssh helpers: `0`
- Stale mail powershell: `0`
- Tailscale backend: `Running` / stockenweiler route visible `True`
- ssh stock-pve: `unreachable`
- Local WireGuard VPN service running: `false`
- Important split: local StudioPC WireGuard is legacy/recovery only; it is not the same thing as a later professional site-to-site WireGuard between UCG and Stockenweiler.
- Primary Stockenweiler admin path is currently ssh stock-pve via toolbox-backed userspace WireGuard.
- Target professional bridge remains Tailscale subnet routing, not permanent dependence on the local stale Windows WireGuard tunnel.
- Workspace disables Pyrefly language services to avoid editor-side notify-file spam from a dead client.

## Estate Census Snapshot

- Generated at: `2026-04-09 17:23:24`
- Live-truth warning: this estate census is stale for current frontdoor/runtime truth.
- Use it only for topology/peer background; current mobile frontdoor truth is `100.82.26.53`.
  - estate census older than platform health by 8 day(s)
  - estate census frontdoor host set ['100.99.206.128'] does not include current frontdoor 100.82.26.53
- Tailscale peers: online `5` / offline `6` / routed `2`
- Running estate nodes: anker containers `3`, anker VMs `4`, stock containers `6`, stock VMs `1`
- Working toolbox frontdoors: `5` / `8`; Stockenweiler public legacy hosts green `0` / `4`
- Local active IPv4 interfaces: `vEthernet (WSL (Hyper-V firewall)): 172.24.176.1/20, Tailscale: 100.98.31.60/32, WLAN: 192.168.2.161/24, wg-studiopc: 10.0.0.2/32`
- Current estate blockers:
  - Home Assistant mobile/frontdoor is still degraded and returns HTTP 400 through toolbox.
  - StudioPC direct access to legacy guest 192.168.2.x is not the working path during the UCG transition because the same subnet exists on two different L2 domains.
  - Stockenweiler has inactive storage targets: anker-music.
  - Stockenweiler public legacy endpoints are still broken: https://home.prinz-stockenweiler.de, https://papierkram.prinz-stockenweiler.de/dashboard, https://cloud.prinz-stockenweiler.de/apps/dashboard/, https://pve.prinz-stockenweiler.de.
  - Some expected Tailscale peers are offline: iphone-15.tail150400.ts.net, pixel-8a.tail150400.ts.net, radio-node.tail150400.ts.net, surface-go-frontend.tail150400.ts.net, wohnzimmertv.tail150400.ts.net, wolf-zenbook-ux325ea-ux325ea.tail150400.ts.net.
- Current working order:
  - Treat Tailscale as the only professional operator path; stop depending on direct StudioPC-to-legacy 192.168.2.x reachability during migration.
  - Freeze the current working transition state: Proxmox on 10.1.0.92, toolbox frontdoors 8/8 green, guests still isolated behind the transition router.
  - Use the existing published UCG VLAN schema as the target network model; do not reopen subnet design unless the SSOT itself changes.
- Canonical Anker transition sequence:
  - Freeze the current working control plane and keep Tailscale/frontdoor access as the canonical operator path.
  - Use `UCG_NETWORK_ARCHITECTURE.md` as the binding target VLAN/subnet model and focus only on service-to-VLAN adoption plus runtime cutover order.
  - Keep DNS and browser entrypoints target-agnostic; users should prefer toolbox frontdoors and hs27.internal names instead of direct guest IPs.
  - Run one low-risk pilot move first, preferably a non-business-critical endpoint such as portal, media, or radio pathing.
  - After the pilot is green, migrate the core business services in order: Odoo, Nextcloud, Paperless.

## Platform Health Snapshot

- Generated at: `2026-04-18T11:25:05+02:00`
- Top priority issue: Stockenweiler host is under real memory pressure: swap used `5.64 GiB` / `8.0 GiB`.
- Frontdoors green: `0` / `8`; Odoo runtime green `false`
- Anker host: RAM `11.82 / 15.46 GiB`, rootfs `30.0%`, swap `62.6%`
- Stockenweiler host: RAM `9.64 / 15.5 GiB`, rootfs `30.4%`, swap `70.6%`
- Current blockers:
  - Stockenweiler host is under real memory pressure: swap used `5.64 GiB` / `8.0 GiB`.
  - Stockenweiler storage `hdd-backup` is at `85.6%` and should not receive new backup or migration load yet.
  - VM 240 PBS is still stopped, so there is no current green dedicated PBS runtime on Anker.
  - Odoo frontdoor is not green from StudioPC: HTTP `000`.
- Recommended next order:
  - Keep Anker stable; do not start broad migrations while PBS and Stockenweiler pressure remain open.
  - Define the Odoo production profile and customer portal scope before calling it production-ready.
  - Capture the essential yourparty payload from Stockenweiler into Rothkreuz before deleting or thinning radio/web components.
  - Only after payload capture: retire duplicated Stockenweiler radio/web/api roles stepwise.

## CI/CD Snapshot

- Delivery factory status: `defined_not_deployed`
- Safe scope now: `repo_side_factory_only`
- Verified start state: workflows `3`, Dockerfiles `1`, ready apps `1`
- Open factory prerequisites: `4`
- CD controller role: `Coolify as delivery-only layer`
- Registry contract: `GHCR v1` for `ghcr.io/wolfeetech/frawo/radio-player-frontend`
- Env/secret contract: `dev/prod env examples plus future Coolify webhook secret names`
- Coolify host contract: `dedicated internal Anker management node preferred; toolbox only temporary fallback`
- First deploy bundle: `deployment/factory/apps/radio-player-frontend/compose.yaml`
- Management-node recommendation: `dedicated_internal_anker_management_node`
- Storage pressure snapshot: `artifacts/storage_optimization/latest_report.md`
- Dev/Prod model: `develop -> dev`, `main/tag -> prod`
- Backup/Restore rule: `stateless public = redeploy`, `stateful internal = PBS/VM restore plus app-native data restore`
- Factory report: `artifacts/cicd_delivery_factory/latest_report.md`

## UCG Pilot Snapshot

- Live-truth warning: this portal pilot preflight is stale for current frontdoor/runtime truth.
  - portal pilot preflight older than 1 day (6 day(s))
  - portal pilot frontdoor host 100.99.206.128 does not match current frontdoor 100.82.26.53
- Pilot: `portal`
- Ready for gated runtime change: `false`
- Recommendation: `fix_preflight_findings_before_any_runtime_portal_cutover`
- Runtime runbook: `UCG_PORTAL_PILOT_RUNBOOK.md`
- Portal status snapshot: platform_core `attention`, healthy `2` / `7`

## Current Lane Model

- `Lane A: MVP Closeout` -> `done`
  - goal: Keep the internal business MVP closed and documented as the completed first delivery lane.
- `Lane B: Website/Public` -> `active`
  - goal: Finish a small, controlled public release for www.frawo-tech.de without exposing internal admin surfaces.
- `Lane C: Security/PBS/Infra` -> `active`
  - goal: Hold the recovered platform on a professional baseline while finishing DNS, admin-path, and infrastructure follow-through.
- `Lane D: Stockenweiler` -> `watch`
  - goal: Keep the support rollout prepared without starting live cutover work too early.
- `Lane E: Radio/Media` -> `watch`
  - goal: Keep media stable and recover the radio backend without turning the lane into a feature-expansion track.

## Business MVP Blockers

- none

## Public Website Release State

- This track is separate from the internal business MVP.
- Latest website gate source: `artifacts/website_release_gate/20260330_161648/website_release_gate.md`
- Current blocked reasons:
  - public-http-redirect-check=failed
  - public-dualstack-edge-check=failed
  - public-https-check=failed
  - public-mail-dns-check=failed
  - public_browser_acceptance_verified=failed
  - public_mail_model_verified=pending

## Security Posture Snapshot

- Latest public IPv6 re-audit timestamp: `20260331_063204`
- Public IPv6 direct exposure findings open: `0`
- Verified closed in the current audit: direct public IPv6 checks for `nextcloud`, `odoo`, `paperless`, `vaultwarden`, `storage-node`, `homeassistant`.
- Important limitation: this is risk reduction, not a promise of zero risk.
- Public edge and TLS are still not in a final green release state.

## Stockenweiler Snapshot

- Lane state remains `watch`; no live rollout, no site marriage, no site-to-site VPN.
- Primary remote access model: `tailscale` / fallback `anydesk`
- Stockenweiler endpoints currently modeled: `8`
- Current Stockenweiler blockers: `13`
- Current direction:
  - parents' scan folders stay local first
  - later document automation should use a separate Stockenweiler Paperless DB
  - radio is later hosted on the most stable hardware, not by ideology of site
  - Stockenweiler PVE HDDs are only a future PBS/storage complement candidate
- Public truth / DynDNS split: dyn-dns-like `2`
  - home.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 and returns HTTPS 200.
  - cloud.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 but currently fails TLS/SNI.
  - papierkram.prinz-stockenweiler.de resolves directly to 80.134.168.100 and currently times out on HTTPS.
- Remote path truth: tailscale `Running`, route_all `True`, stockenweiler route visible `False`
  - ssh `stock-pve` is `reachable`; AnyDesk candidates `7`
  - Tailscale backend is `Running` on StudioPC.
  - Visible Tailscale primary routes are currently limited to: 192.168.2.0/24 via toolbox.tail150400.ts.net.
- Management bridge: state `route_approval_pending`, target `Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24`
  - fallback `StudioPC -> toolbox -> userspace WireGuard wgstkw -> 192.168.178.25` / direct local WG reachable `False`
  - architecture note: current admin bridge is Tailscale-first, but the later permanent site bridge may become native WireGuard between UCG and Stockenweiler after read-only inventory of the existing Stockenweiler WG topology
  - next operator action: Approve the advertised subnet route 192.168.178.0/24 for stockenweiler-pve in Tailscale admin so the route becomes visible on StudioPC.
- Existing WireGuard truth: reachable `true`, server `10.0.0.1/24` on port `51820`, client profiles `4`
  - CT 106 is a running dedicated WireGuard server in Stockenweiler.
  - The server currently listens on port 51820 and serves the VPN subnet 10.0.0.1/24.
- Visible legacy host check: reachable `1` / broken `3`
  - Home Assistant is the only legacy host that still presents a frontend at HTTPS level.
  - Paperless currently times out on port 443.
  - Nextcloud currently fails with ERR_SSL_UNRECOGNIZED_NAME_ALERT, which points to a reverse-proxy or certificate SNI mismatch.
- Latest Stockenweiler PVE read-only probe: `reachable` on target `stock-pve`

## Surface Control V1

- Ready actions: `7`
- Ready groups: `Dokumente, Odoo, Radio`
- `Nextcloud Eingang` -> `http://cloud.hs27.internal/apps/files/files?dir=/Paperless/Eingang`
- `Paperless` -> `http://paperless.hs27.internal/dashboard`
- `Odoo Aufgaben` -> `http://odoo.hs27.internal/web#action=118&active_id=8&model=project.task&view_type=kanban&menu_id=352`
- `Odoo Projekte` -> `http://odoo.hs27.internal/web#action=252&model=project.project&view_type=kanban&menu_id=141`
- `Odoo Kalender` -> `http://odoo.hs27.internal/web#action=517&model=project.task&view_type=calendar&menu_id=357`
- `Radio hoeren` -> `http://radio.hs27.internal/public/frawo-funk`
- `Radio Control` -> `http://radio.hs27.internal/login`
- Backlog-only actions remain hidden:
  - `Dokument scannen` (`Dokumente`)
  - `TV / Magenta Hilfe` (`Stockenweiler`)
  - `Fernhilfe` (`Stockenweiler`)
  - `Vater Home Assistant` (`Stockenweiler`)

## Access And Secret Rules

- Shared passwords and shared app credentials belong in the `FraWo` organization in Vaultwarden.
- No plaintext credentials in markdown, ad hoc notes, or repo-tracked local files.
- `wolf@frawo-tech.de` is the operator identity, but the technical base mailbox for app SMTP is `webmaster@frawo-tech.de`.
- `franz@frawo-tech.de` is a real mailbox and was technically verified against STRATO IMAP/SMTP.
- App SMTP authenticates with `webmaster@frawo-tech.de`.
- The visible app sender is `noreply@frawo-tech.de`.
- Vaultwarden is invite-only for productive use.
- The `FraWo GbR` organization is the master identity for all business collections.

## Current Operator Queue

### `split_dns_finalization`

- `status`: `blocked`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: gated_infra
- `goal`: hs27.internal resolves cleanly for remote Tailscale clients through the recovered toolbox DNS path.
- `done_when`: The restricted nameserver for hs27.internal points to 100.82.26.53 and remote clients resolve internal names without local hacks.
- `blocked_by`: `operator_tailscale_admin_action_missing`
- `preflight_checks`: `scripts/tailscale_split_dns_readiness_check.sh returns split_dns_prereqs_ready=yes`, `scripts/adguard_pilot_readiness_check.sh returns adguard_pilot_ready=yes`, `toolbox DNS answers hs27.internal correctly on 100.82.26.53:53`
- `rollback_plan`: If restricted DNS causes client breakage, remove the restricted nameserver entry or revert the local NRPT helper and fall back to direct Tailscale frontdoor access.
- `verification_commands`: `wsl bash scripts/tailscale_split_dns_readiness_check.sh`, `nslookup odoo.hs27.internal 100.82.26.53`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Set the restricted nameserver for hs27.internal to 100.82.26.53 in Tailscale Admin or run the elevated local NRPT helper.
- `next_codex_action`: Keep the split-DNS checks and SSOT pointed at 100.82.26.53 and re-verify after the operator-side DNS action.

### `public_edge_https_release`

- `status`: `blocked`
- `lane`: Lane B: Website/Public
- `change_class`: gated_infra
- `goal`: Finish the smallest safe public HTTPS path for www.frawo-tech.de.
- `done_when`: www.frawo-tech.de serves the intended website over HTTPS with rollback notes and no public admin exposure.
- `blocked_by`: `public_ipv4_edge_path_missing`, `acme_connection_refused_on_ipv4`
- `preflight_checks`: `VM220 website origin answers internally on 10.1.0.22`, `Public DNS still points at the intended target`, `No internal admin UI is included in the public scope`
- `rollback_plan`: If the public cutover fails, keep DNS and proxy on the last known-good HTTP-only state and do not publish a broken HTTPS path as released.
- `verification_commands`: `python scripts/website_release_gate.py`, `python scripts/public_dualstack_edge_check.py`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Choose and provide the final public edge path, currently Cloudflare proxy or equivalent public IPv4 routing.
- `next_codex_action`: Keep Lane B focused on the narrow website release and do not mix it with unrelated infra or media work.

### `radio_node_recovery`

- `status`: `blocked`
- `lane`: Lane E: Radio/Media
- `change_class`: gated_infra
- `goal`: Restore the physical radio backend so the existing frontdoor can go green again.
- `done_when`: radio-node responds on LAN or Tailnet and the frontdoor on 100.82.26.53:8448 no longer returns 502.
- `blocked_by`: `operator_on_site_recovery_missing`
- `preflight_checks`: `Confirm radio-node is still unreachable on 192.168.2.155`, `Confirm radio-node is still unreachable on 100.64.23.77`, `Confirm toolbox frontdoor returns 502 on 100.82.26.53:8448`
- `rollback_plan`: No rollback in absent-hardware state; once the Pi is back, keep the existing reverse-proxy path and only restore known-good runtime pieces.
- `verification_commands`: `bash ./scripts/rpi_radio_integration_check.sh`, `make radio-ops-check`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Check power, LEDs, boot, and LAN-link on the Pi, then bring back either the LAN or Tailscale path.
- `next_codex_action`: Hold the diagnosis honest, then resume radio integration checks as soon as the Pi is reachable again.

### `wolfstudiopc_admin_path`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: gated_infra
- `goal`: Restore one explicit and supportable admin path to wolfstudiopc.
- `done_when`: OpenSSH or an equivalent documented admin path is available and reflected in SSOT.
- `blocked_by`: `operator_windows_admin_action_missing`
- `preflight_checks`: `Confirm wolfstudiopc remains the primary admin device in SSOT`, `Confirm the intended admin path does not require blind full-tunnel changes`
- `rollback_plan`: If a new admin path creates unnecessary exposure, disable it and fall back to the current manual-local admin model.
- `verification_commands`: `ssh wolfstudiopc "echo ok"`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Enable the chosen admin path on wolfstudiopc, preferably OpenSSH with the existing access model.
- `next_codex_action`: Keep docs and checks ready, but avoid Windows admin-token drift until the operator chooses the exact path.

### `stockenweiler_preparation`

- `status`: `watch`
- `lane`: Lane D: Stockenweiler
- `change_class`: repo_only
- `goal`: Keep Stockenweiler prepared as the next external support track without starting live cutover work prematurely.
- `done_when`: The support model, certificate state, and access path are ready for intentional activation.
- `blocked_by`: `lane_b_website_public_active`
- `preflight_checks`: `Support rollout remains intentionally deferred behind current active work`, `Current cert and remote-access facts are collected before rollout decisions`
- `rollback_plan`: Planning-only watch state; no live site changes are made from this task.
- `verification_commands`: `python scripts/stockenweiler_public_truth_check.py`, `python scripts/stockenweiler_remote_path_probe.py`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Provide current facts for the expired certificate and the intended support rollout timing.
- `next_codex_action`: Maintain the support planning truth and keep the rollout explicitly deferred.

### `haos_usb_path`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: gated_infra
- `goal`: Prepare a clean HAOS USB path without touching it prematurely.
- `done_when`: The correct Zigbee/Z-Wave hardware is attached, identified, and documented for passthrough.
- `blocked_by`: `usb_hardware_not_yet_connected`
- `preflight_checks`: `USB dongles are physically available`, `Vendor and product IDs are audited before passthrough`
- `rollback_plan`: If passthrough destabilizes HAOS or host USB visibility, remove the passthrough and return to the current VM state.
- `verification_commands`: `lsusb`, `qm config 210`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Attach the intended Zigbee/Z-Wave hardware so the passthrough path can be audited.
- `next_codex_action`: Keep the guardrail documentation current and wait for real hardware before attempting runtime changes.

### `pbs_guarded_rebuild`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: gated_infra
- `goal`: Keep the PBS rebuild path ready without risking the wrong hardware or a premature datastore action.
- `done_when`: The guarded rebuild is executed on approved hardware and followed by a real proof backup and restore drill.
- `blocked_by`: `approved_pbs_hardware_missing`
- `preflight_checks`: `Dedicated boot USB and datastore device are identified`, `Device contract is approved before datastore preparation`, `PBS remains out of current business-MVP scope`
- `rollback_plan`: If hardware or datastore identity is uncertain, do nothing and keep PBS in staged-not-live status.
- `verification_commands`: `python scripts/pbs_device_inventory.py`, `python scripts/pbs_rebuild_stage_gate.py`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Provide the approved hardware set and device serial confirmation for the guarded rebuild.
- `next_codex_action`: Keep PBS staged and documented, but do not cross the safety gate before hardware approval.

### `windows_gui_updates_closeout`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: reversible_runtime
- `goal`: Finish the remaining GUI-gated workstation updates without reintroducing hanging update runs.
- `done_when`: The remaining blocked-by-process and timed-out packages are cleanly resolved or explicitly deferred with a fresh audit.
- `blocked_by`: `interactive_processes_still_running`
- `preflight_checks`: `Interactive apps that blocked winget are closed`, `The controlled workstation update runner remains the only allowed update path`
- `rollback_plan`: If an update blocks or requests elevation unexpectedly, stop the run and leave the remaining packages pending rather than forcing them.
- `verification_commands`: `powershell -ExecutionPolicy Bypass -File .\scripts\update_windows_operator_workstation.ps1 -WingetTimeoutSeconds 10`
- `last_verified_at`: 2026-04-19
- `next_operator_action`: Close the remaining GUI apps and rerun the controlled update path when convenient.
- `next_codex_action`: Keep the hardened update runner and audit path as the only accepted workstation update method.

## Visible Side Strands

- none

## Recommended Next Planning Order

- First close `split_dns_finalization` in `Lane C: Security/PBS/Infra`.
- First close `public_edge_https_release` in `Lane B: Website/Public`.
- First close `radio_node_recovery` in `Lane E: Radio/Media`.
- First close `wolfstudiopc_admin_path` in `Lane C: Security/PBS/Infra`.
- First close `stockenweiler_preparation` in `Lane D: Stockenweiler`.
- First close `haos_usb_path` in `Lane C: Security/PBS/Infra`.
- First close `pbs_guarded_rebuild` in `Lane C: Security/PBS/Infra`.
- First close `windows_gui_updates_closeout` in `Lane C: Security/PBS/Infra`.

## Canonical Files To Read Next

- `INTRODUCTION_PROMPT.md`
- `BUSINESS_MVP_PROMPT.md` oder `WEBSITE_RELEASE_PROMPT.md` oder `FULL_CERTIFICATION_PROMPT.md` je nach Arbeitsmodus
- `GEMINI_BROWSER_MVP_ACCEPTANCE_PROMPT.md` fuer die offenen Browser-Abnahmen im MVP
- `AI_BOOTSTRAP_CONTEXT.md`
- `AI_SERVER_HANDOFF.md`
- `OPERATOR_TODO_QUEUE.md`
- Release-MVP-Gate: `artifacts/release_mvp_gate/latest_release_mvp_gate.md`
- Produktions-Gate: `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
- Dokument-Ownership: `OPERATIONS/DOCUMENT_OWNERSHIP_OPERATIONS.md`
- Benutzer-Onboarding: `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- Operator-Routinen: `OPERATIONS/OPERATOR_ROUTINES.md`
- Vaultwarden Start: `VAULTWARDEN_SELFHOST_START.md`

## Generator Notes

- This file is generated from current source-of-truth docs and latest gate/audit artifacts.
- If a source file is older than the newest hardening change, prefer the fresher artifact listed in `Source Freshness`.
- For runtime operations, do not invent credentials or provider-side state that is not visible in the cited sources.
