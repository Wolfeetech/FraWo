# AI Server Handoff

Automatisch generierter Ein-Datei-Handoff fuer den aktuellen Homeserver-Stand.
Keine Secrets. Keine Passwoerter. Diese Datei ist dafuer gedacht, sie direkt an eine andere KI zu geben.

## Nutzung

- Primaerer Read-First fuer eine andere KI: diese Datei
- Wenn tieferer Repo-Kontext noetig ist: `INTRODUCTION_PROMPT.md`, `OPS_HOME.md`, `OPERATOR_TODO_QUEUE.md`
- Diese Datei neu erzeugen mit: `python scripts/generate_ai_server_handoff.py`

## Generierung

- Generated at: `2026-04-09 17:22:47`
- Workspace root: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace`
- Git branch: `main`
- Pending git changes: `66`
- Managed hosts in inventory: `30`

## Source Freshness

- `AI_BOOTSTRAP_CONTEXT.md`: `2026-04-04 02:03:02`
- `OPS_HOME.md`: `2026-03-31 06:53:07`
- `OPERATOR_TODO_QUEUE.md`: `2026-04-09 15:01:40`
- `manifests/work_lanes/current_plan.json`: `2026-04-04 02:03:02`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.json`: `2026-04-09 17:13:09`
- `artifacts/public_ipv6_exposure_audit/latest_report.md`: `2026-03-31 06:32:34`
- `artifacts/estate_census/latest_report.json`: `2026-04-03 23:27:25`
- `artifacts/ucg_portal_pilot_preflight/latest_report.json`: `2026-04-05 01:32:41`
- `artifacts\website_release_gate\20260330_161648\website_release_gate.md`: `2026-03-30 16:16:48`
- `artifacts\production_gate\20260328_072130\production_gate.md`: `2026-03-28 07:21:32`
- `manifests/control_surface/actions.json`: `2026-03-30 21:53:25`

## Estate Snapshot

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
- Vector Store Index: `homelab` (Pinecone Cloud, AWS us-east-1, dimension 1024)
- Transition note `2026-04-03`: `wolfstudiopc` currently reaches the core services professionally via `toolbox` Tailscale frontdoors on `100.99.206.128:*`; direct StudioPC access to the legacy guest `192.168.2.x` range is not the working path while the UCG migration bridge is active

## Core Service Map

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

## Current Release State

- Active delivery lane: `Lane A: MVP Closeout`
- Business MVP gate: `MVP_READY`
- Business MVP critical Codex checks: `passed=11` / `non-passed=0`
- Business MVP manual checks: `passed=8` / `pending_or_failed=0`
- Public website gate: `BLOCKED`
- Production certification gate: `BLOCKED`
- Public IPv6 exposure audit: `open_checks=0` / `total_checks=13`

## AI Operating Model

- Model: `professional_autopilot`
- Autonomy: `aggressive_autopilot`
- Primary end state: `internal_ops_first`
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

- Generated at: `2026-04-03 23:27:25`
- Tailscale peers: online `5` / offline `4` / routed `1`
- Running estate nodes: anker containers `3`, anker VMs `4`, stock containers `14`, stock VMs `2`
- Working toolbox frontdoors: `8` / `8`; Stockenweiler public legacy hosts green `0` / `4`
- Local active IPv4 interfaces: `vEthernet (WSL (Hyper-V firewall)): 172.24.176.1/20, Tailscale: 100.98.31.60/32, VPN: 10.0.0.2/32, Ethernet: 192.168.2.162/24`
- Current estate blockers:
  - StudioPC direct access to legacy guest 192.168.2.x is not the working path during the UCG transition because the same subnet exists on two different L2 domains.
  - StudioPC still has a legacy local WireGuard VPN interface active (`VPN` / `10.0.0.2`), which keeps old Stockenweiler assumptions alive and adds operator confusion.
  - Stockenweiler has inactive storage targets: anker-music.
  - Stockenweiler public legacy endpoints are still broken: https://home.prinz-stockenweiler.de, https://papierkram.prinz-stockenweiler.de/dashboard, https://cloud.prinz-stockenweiler.de/apps/dashboard/, https://pve.prinz-stockenweiler.de.
  - Some expected Tailscale peers are offline: pixel-8a.tail150400.ts.net, surface-go-frontend.tail150400.ts.net, wohnzimmertv.tail150400.ts.net, wolf-zenbook-ux325ea-ux325ea.tail150400.ts.net.
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

- Generated at: `2026-04-04T00:06:27+02:00`
- Top priority issue: Stockenweiler host is under real memory pressure: swap used `6.3 GiB` / `8.0 GiB`.
- Frontdoors green: `8` / `8`; Odoo runtime green `true`
- Anker host: RAM `10.01 / 15.46 GiB`, rootfs `69.1%`, swap `0.0%`
- Stockenweiler host: RAM `11.1 / 15.5 GiB`, rootfs `25.7%`, swap `78.8%`
- Current blockers:
  - Stockenweiler host is under real memory pressure: swap used `6.3 GiB` / `8.0 GiB`.
  - Stockenweiler storage `hdd-backup` is at `84.0%` and should not receive new backup or migration load yet.
  - Anker PBS path `pbs-interim` is not active; backup consolidation is still not green.
  - Anker PBS path `pbs-usb` is not active; backup consolidation is still not green.
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

- Pilot: `portal`
- Ready for gated runtime change: `false`
- Recommendation: `fix_preflight_findings_before_any_runtime_portal_cutover`
- Runtime runbook: `UCG_PORTAL_PILOT_RUNBOOK.md`
- Portal status snapshot: platform_core `attention`, healthy `6` / `7`
  - `portal_frontdoor_http` -> `ok` / HTTP 200 via http://100.99.206.128:8447/
  - `portal_frontdoor_status_json` -> `fail` / HTTP 200, platform_core=attention, healthy=6/7
  - `portal_internal_hostname` -> `fail` / HTTP 0 via http://portal.hs27.internal/
  - `portal_internal_status_json` -> `fail` / HTTP 0 via http://portal.hs27.internal/status.json

## Current Lane Model

- `Lane A: MVP Closeout` -> `active`
  - goal: Close the internal business MVP with the remaining visible manual proofs.
- `Lane B: Website/Public Hold` -> `watch`
  - goal: Keep the public website truth path and blockers visible without pulling the track into active release work.
- `Lane C: Security/PBS/Infra` -> `watch`
  - goal: Keep hardening, reapply paths, and audits green without expanding the scope into a full infrastructure program.
- `Lane D: Stockenweiler` -> `watch`
  - goal: Keep the support concept, inventory baseline, remote-access model, and deferred phase-2 backlog visible without starting a live rollout or network marriage.
- `Lane E: Radio/Media` -> `hold`
  - goal: Keep radio and media operational without new feature work or UI expansion.

## Business MVP Blockers

- none

## Public Website Release State

- This track is separate from the internal business MVP.
- Latest website gate source: `artifacts\website_release_gate\20260330_161648\website_release_gate.md`
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

## Current Operator Queue

### `device_rollout_verified`

- `status`: `pending`
- `lane`: Lane A: MVP Closeout
- `change_class`: repo_only
- `goal`: Franz Surface Laptop and iPhone are visibly accepted as released MVP devices with the required direct entry paths.
- `done_when`: Franz Surface Laptop and Franz iPhone both have the required direct app entrypoints and the visible everyday path is confirmed.
- `blocked_by`: `visible_device_acceptance_missing`, `operator_smartphone_lost_2fa_block`
- `preflight_checks`: `python scripts/device_rollout_preflight.py returns ready_for_manual_device_acceptance`, `latest MVP gate still shows device_rollout_verified as pending before closure`
- `rollback_plan`: If the visible evidence is incomplete or inconsistent, keep the manual check pending and do not refresh the gate as passed.
- `verification_commands`: `python scripts/device_rollout_preflight.py`, `powershell -ExecutionPolicy Bypass -File .\scripts\prove_device_rollout.ps1`
- `last_verified_at`: 2026-04-03
- `next_operator_action`: Recover the missing 2FA path blocked by the lost operator smartphone, then walk the Franz Surface Laptop and iPhone through the real direct entrypoints and capture a fresh visible acceptance result.
- `next_codex_action`: Run scripts/device_rollout_preflight.py first. If it stays ready_for_manual_device_acceptance, use scripts/prove_device_rollout.ps1 with the fresh visible Surface Laptop and iPhone evidence so the MVP gate and AI handoff refresh automatically.

### `vaultwarden_recovery_material_verified`

- `status`: `pending`
- `lane`: Lane A: MVP Closeout
- `change_class`: repo_only
- `goal`: Vaultwarden recovery material exists offline in two separate physical copies.
- `done_when`: Two separate offline copies exist and a fresh visible proof is recorded instead of relying on assumption.
- `blocked_by`: `fresh_offline_proof_missing`
- `preflight_checks`: `Fresh visible proof exists for two separate offline recovery copies`, `latest MVP gate still shows vaultwarden_recovery_material_verified as pending before closure`
- `rollback_plan`: If the proof is stale or not visibly separate, keep the manual check pending and do not refresh the gate as passed.
- `verification_commands`: `python scripts/release_mvp_gate.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Create or verify two separate offline copies of the Vaultwarden recovery material and provide a fresh proof.
- `next_codex_action`: Update the manual MVP check, rerun release_mvp_gate.py, and regenerate AI_SERVER_HANDOFF.md.

## Visible Side Strands

### `website_public_hold`

- `status`: `watch`
- `lane`: Lane B: Website/Public Hold
- `change_class`: read_only
- `goal`: Public website work stays visible as a paused truth path, not as an active release lane.
- `done_when`: Lane A is closed and public edge work is intentionally reactivated.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Review latest website gate`, `Review latest public IPv6 exposure audit`, `Confirm Lane A is still the active delivery lane`
- `rollback_plan`: No runtime mutation; only truth-path refreshes and blocker updates.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: No action unless a new public regression must be documented.
- `next_codex_action`: Keep the website gate, blockers, and security notes current; do not resume public release implementation.

### `platform_agnostic_delivery_factory`

- `status`: `watch`
- `lane`: Lane B: Website/Public Hold
- `change_class`: repo_only
- `goal`: Keep one platform-agnostic CI/CD and DMZ delivery model visible so future public deployment work stops mixing build, registry, runtime, and HA concepts.
- `done_when`: The repo has one canonical delivery-factory plan, one machine-readable manifest, one app catalog, one preflight, one report, and one thin CI validation workflow that define dev, prod, promotion, DMZ nodes, controller boundaries, and current non-ready prerequisites.
- `blocked_by`: `lane_a_mvp_closeout_active`, `public_edge_still_watch_only`
- `preflight_checks`: `UCG VLAN target model is already canonical and does not need redesign`, `Public Edge remains a watch lane, not an active rollout lane`, `No runtime DMZ, DNS, router, or Coolify deployment change is attempted in this step`, `python scripts/cicd_delivery_factory_preflight.py confirms repo_side_factory_only`, `GHCR contract and env examples exist for the first stateless reference app`, `scripts/coolify_management_host_audit.py can prove a real Anker management-node candidate`, `Secret distribution model stays repo-only and does not activate live runtime secrets yet`
- `rollback_plan`: Repo-side step only; revert the factory plan, manifest, app catalog, workflow, and reports if the target architecture or first-wave app choice changes.
- `verification_commands`: `python scripts/cicd_delivery_factory_preflight.py`, `python scripts/cicd_delivery_factory_report.py`, `python scripts/generate_ai_server_handoff.py`, `python scripts/coolify_management_host_audit.py`
- `last_verified_at`: 2026-04-04
- `next_operator_action`: Later decide which OCI registry and which internal host should run Coolify management once Lane B is intentionally activated.
- `next_codex_action`: Use the Anker host audit to carry the next gated decision: create a dedicated internal management node first, then wire GHCR and Coolify live paths on top of it.

### `control_plane_clean`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: reversible_runtime
- `goal`: Keep one clean control plane per target, reduce stale helper paths and local noise, and make the primary admin paths explicit.
- `done_when`: Stale local helper processes are reduced, workspace Pyrefly noise is suppressed, and the canonical admin path for Anker and Stockenweiler is verifiably documented.
- `blocked_by`: `local_windows_admin_token_needed_for_full_wireguard_cleanup`, `stockenweiler_tailscale_subnet_route_approval_pending`
- `preflight_checks`: `Collect current process, service and route truth with scripts/control_plane_audit.py`, `Confirm stock-pve remains reachable before cleaning stale local helper paths`, `Do not perform Windows admin-token actions without an explicit gated stop`
- `rollback_plan`: If cleanup removes a useful path, restore the canonical admin path only: direct Anker aliases plus ssh stock-pve via toolbox-backed WireGuard. Do not reactivate old parallel paths blindly.
- `verification_commands`: `python scripts/control_plane_audit.py`, `powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_stale_control_plane_processes.ps1`, `python scripts/control_plane_audit.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only intervene if an elevated Windows token is needed for full WireGuard cleanup or if the advertised subnet route 192.168.178.0/24 for stockenweiler-pve must be approved in Tailscale admin.
- `next_codex_action`: Run the control-plane audit, keep the workspace-level Pyrefly suppression in place, remove only clearly stale helper processes, and keep Tailscale-first with ssh stock-pve as the current Stockenweiler admin path until the bridge is approved.

### `anker_ucg_transition_sequence`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: repo_only
- `goal`: Keep one canonical Anker transition sequence visible so the UCG migration stops jumping between unrelated subproblems.
- `done_when`: The next runtime step is always taken from the same published service order instead of ad hoc troubleshooting.
- `blocked_by`: `ucg_vlan_schema_exists_but_runtime_adoption_not_started`
- `preflight_checks`: `Estate census is current and shows all Anker toolbox frontdoors green`, `Proxmox transition router state is documented in VM_AUDIT.md and NETWORK_INVENTORY.md`, `No runtime renumbering or UCG firewall change is attempted in this step`
- `rollback_plan`: Documentation-only step; revert SSOT changes if the runtime truth changes.
- `verification_commands`: `python scripts/portal_ucg_pilot_preflight.py`, `python scripts/estate_census_audit.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-04-03
- `next_operator_action`: Confirm that the published VLAN target in UCG_NETWORK_ARCHITECTURE.md remains the binding target model for the runtime migration.
- `next_codex_action`: Keep the canonical order visible in the estate census, VM_AUDIT.md, LIVE_CONTEXT.md, and AI_SERVER_HANDOFF.md; do not reopen subnet design, focus only on service-to-VLAN adoption and runtime cutover order.

### `anker_ucg_portal_pilot_preflight`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: repo_only
- `goal`: Keep the first low-risk UCG portal pilot live and verified so the transition now has one proven runtime success before core business services move.
- `done_when`: Toolbox carries the additive `10.1.0.20/24` pilot alias, the portal vhost answers on the target IP, and toolbox frontdoors remain green.
- `blocked_by`: `next_low_risk_pilot_not_yet_selected`
- `preflight_checks`: `Estate census is current and shows all Anker toolbox frontdoors green`, `Portal frontdoor 8447 remains green from wolfstudiopc`, `No runtime firewall, DNS, router, or VLAN mutation is attempted in this step`
- `rollback_plan`: Documentation-only preflight step; revert the pilot checklist if the runtime target or order changes.
- `verification_commands`: `python scripts/estate_census_audit.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-04-03
- `next_operator_action`: Confirm whether `media` should become the second low-risk pilot before the first core business move.
- `next_codex_action`: Keep the live portal pilot verified in scripts/portal_ucg_pilot_preflight.py and SSOT, then prepare the next low-risk pilot without touching core business services yet.

### `security_pbs_infra_watch`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: read_only
- `goal`: Hardening, PBS status, and infrastructure guardrails remain visible without becoming the active delivery lane.
- `done_when`: Lane A is closed and a dedicated certification or PBS rebuild block is intentionally resumed.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Review latest hardening audits`, `Review latest PBS/runtime blockers`, `Confirm no new regression has appeared`
- `rollback_plan`: No broad infra mutation in watch mode; only regression response and audit refresh.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only escalate if a new regression appears.
- `next_codex_action`: Maintain the existing audit-green state and the reapply paths; avoid broad new infra work.

### `wolf_arbeitssurface_access_model`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: repo_only
- `goal`: Keep Wolfs Arbeitssurface as a separate trusted client with split access: normal local work by default, internal full access only on demand.
- `done_when`: The device is documented and treated separately from Franz Surface Laptop, with no permanent full-tunnel and no blind RouteAll requirement.
- `blocked_by`: `surface_laptop_identity_needs_live_revalidation`
- `preflight_checks`: `Confirm Surface_Laptop remains modeled separately from Franz Surface Laptop`, `Confirm no full-tunnel or blind RouteAll requirement has been introduced`
- `rollback_plan`: Revert documentation-only drift if the live identity is disproven; do not push runtime VPN policy without a gated decision.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Confirm that the active WLAN device Surface_Laptop on 192.168.2.118 is Wolfs current Arbeitssurface and whether Tailscale is already installed there.
- `next_codex_action`: Keep the split-access model canonical in NETWORK_INVENTORY.md, OPERATIONS/USER_ONBOARDING_OPERATIONS.md, and AI_BOOTSTRAP_CONTEXT.md; do not fold the device into the Franz or kiosk paths.

### `storage_optimization_watch`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: read_only
- `goal`: Keep one factual storage-pressure and reclaim plan visible so backup, media, and PBS decisions stop mixing together.
- `done_when`: A dedicated storage optimization block is intentionally activated and the kept-set plus reclaim sequence are explicitly approved.
- `blocked_by`: `storage_pbs_changes`, `lane_a_mvp_closeout_active`
- `preflight_checks`: `Review latest platform health audit`, `Review latest stockenweiler storage probe`, `Confirm no storage delete or PBS mutation is attempted in this step`
- `rollback_plan`: Audit-and-plan step only; no runtime storage mutation in watch mode.
- `verification_commands`: `python scripts/storage_optimization_audit.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-04-04
- `next_operator_action`: Approve the kept-set policy for stockenweiler backup pruning and the classification rule for music_hdd payload before any deletes happen.
- `next_codex_action`: Keep the storage audit current and do not delete or retarget storage until the kept-set and PBS direction are explicitly chosen.

### `stockenweiler_watch`

- `status`: `watch`
- `lane`: Lane D: Stockenweiler
- `change_class`: read_only
- `goal`: Stockenweiler stays visible as a prepared support track with inventory, remote-access concept, and a deferred management-first phase-2 backlog only.
- `done_when`: Lane A is closed and Stockenweiler is explicitly promoted into an active rollout.
- `blocked_by`: `lane_a_mvp_closeout_active`, `ucg_2fa_unavailable`
- `preflight_checks`: `Verify stock-pve access path still works`, `Review latest Stockenweiler public truth, remote path and storage probe artifacts`, `Confirm Lane A remains active so no live rollout starts`
- `rollback_plan`: Stay in truth-collection mode only; no site marriage, no migration, no router/public changes.
- `verification_commands`: `python scripts/stockenweiler_public_truth_check.py`, `python scripts/stockenweiler_remote_path_probe.py`, `python scripts/stockenweiler_wireguard_inventory.py`, `python scripts/stockenweiler_pve_storage_probe.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: No live rollout or cutover yet; share real gateway, FRITZ, UCG, Tailscale, or existing Stockenweiler WireGuard facts if available.
- `next_codex_action`: Keep inventory and planning current; stay read-only, but explicitly inventory the existing Stockenweiler WireGuard setup so a later professional UCG<->Stockenweiler site-to-site decision can be made without guesswork.

### `radio_media_hold`

- `status`: `hold`
- `lane`: Lane E: Radio/Media
- `change_class`: read_only
- `goal`: Radio and media remain operational, but expansion work stays out of the active queue.
- `done_when`: Lane A is closed and there is an explicit decision to expand radio/media again.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Check only for breakage that affects current radio/media operation`
- `rollback_plan`: No expansion in hold mode; only restore known-good operation if breakage appears.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only report breakage that impacts current operation.
- `next_codex_action`: Hold the current operating state; no new features, no new public surface.

## Recommended Next Planning Order

- First close `device_rollout_verified` in `Lane A: MVP Closeout`.
- First close `vaultwarden_recovery_material_verified` in `Lane A: MVP Closeout`.
- Keep `website_public_hold` visible in `Lane B: Website/Public Hold` without promoting it into active delivery.
- Keep `platform_agnostic_delivery_factory` visible in `Lane B: Website/Public Hold` without promoting it into active delivery.
- Keep `control_plane_clean` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `anker_ucg_transition_sequence` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `anker_ucg_portal_pilot_preflight` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `security_pbs_infra_watch` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `wolf_arbeitssurface_access_model` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `storage_optimization_watch` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `stockenweiler_watch` visible in `Lane D: Stockenweiler` without promoting it into active delivery.
- Keep `radio_media_hold` visible in `Lane E: Radio/Media` without promoting it into active delivery.

## Canonical Files To Read Next

- `AI_OPERATING_MODEL.md`
- `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`
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
