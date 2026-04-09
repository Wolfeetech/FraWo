# Surface Go Frontend Setup Plan

## Purpose

This document is the canonical rebuild and post-install runbook for the shared Surface Go frontend node in Homeserver 2027.

## Current State

- Device: `surface-go-frontend`
- Current IP: `192.168.2.154`
- Intended role: shared touch frontend for Wolf and Franz
- Confirmed local admin user: `frawo`
- Current state after rebuild:
  - Ubuntu Desktop 24.04.4 LTS is installed
  - SSH baseline is active
  - password-based SSH for the local admin path is currently usable again
  - local portal and kiosk baseline are applied
  - `nginx` is absent and `HTTP/80` / `HTTPS/443` are closed
  - the node is reachable again over Tailnet on `100.106.67.127`
  - GNOME idle is `0` and both AC and battery sleep policy are now `nothing`
  - root-level sleep target masking is complete
  - a remote reboot came back cleanly over SSH
- the local portal is now served via `http://127.0.0.1:17827`
- the current working launcher is `FRAWO Control`
- the browser fallback is currently `epiphany-browser`
- visual acceptance has been reached in the live `frawo` desktop session
- `Surface Control V1` is now installed live as the local action console
- the kiosk desktop now exposes only `FRAWO Control` and `Bildschirmtastatur`
- the admin desktop now exposes only `FRAWO Control`, `Bildschirmtastatur`, `Radio Control`, `AnyDesk` and `StudioPC Remote`
- local user `frontend` is operational again with an explicitly set local password path
- live browser verification from `StudioPC` is now also reproducible:
  - SSH alias `hs27-surface-portal`
  - local forward `127.0.0.1:27827 -> 127.0.0.1:17827`
  - helper `scripts/open_surface_portal_tunnel.ps1 -Verify`
- current load-path hardening is now also applied:
  - `Kabelgebundene Verbindung 1` on `192.168.1.x` no longer provides default route or DNS
  - `Frawo-Direkt` on `192.168.2.x` is now the primary default route with metric `100`
  - this removed the mixed uplink/DNS condition that caused intermittent slow loading on the Surface

## Target Standard

- Operating system: `Ubuntu Desktop 24.04 LTS`
- Kernel policy:
  - use the stock Ubuntu kernel first
  - only add `linux-surface` if touch, suspend, camera, Type Cover or pen support is materially broken
- Intended operating mode: `hybrid`
  - local admin user `frawo`
  - separate kiosk user `frontend`
  - automatic login into the kiosk session
  - no local server role

## Rebuild Sequence

1. Save any data that still matters on the current device.
2. Prepare an Ubuntu Desktop 24.04 LTS installation medium.
3. Reinstall the device cleanly.
4. During install:
   - keep the system lean
   - create or retain admin user `frawo`
   - do not install Ubuntu Studio extras
5. After first boot:
   - connect to LAN
   - confirm the correct hostname target `surface-go-frontend`
   - confirm package updates work
6. Enable the management baseline:
   - `OpenSSH Server`
   - `Tailscale`
   - automatic security updates
7. Create kiosk user `frontend` without sudo.
8. Apply the post-install baseline playbook:
   - `ansible/playbooks/bootstrap_surface_go_frontend.yml`
9. Validate kiosk and admin paths:
   - autologin into `frontend`
   - browser starts in kiosk mode
   - local portal page opens
   - `frawo` still works as the local admin account

## Why not full zero-touch desktop preseed by default

The Pi path can be heavily preseeded before first boot.

The Surface path intentionally stays one step more conservative:

- a shared desktop appliance needs a real local admin account
- a fully unattended desktop install would require pre-baking local admin credentials
- touch hardware, storage selection and post-install ergonomics are riskier than a headless Pi bootstrap

Therefore the professional default is:

1. clean Ubuntu Desktop install
2. first networked boot
3. Codex/Gemini takes over the real configuration remotely through the prepared playbook

## Post-Install Baseline

- Canonical playbook:
  - `ansible/playbooks/bootstrap_surface_go_frontend.yml`
- Canonical host vars:
  - `ansible/inventory/host_vars/surface_go_frontend.yml`
- Baseline behaviors:
  - local `nginx` removed
  - `OpenSSH` enabled
  - root SSH login disabled
  - `epiphany-browser` is available as the current local launcher path via `FRAWO Control`
  - `Tailscale` installed from the official Ubuntu package feed
  - the local portal is rendered into `/home/frontend/homeserver2027-portal`
  - a loopback-only local HTTP service serves that portal on `127.0.0.1:17827`
  - `gdm3` autologin is configured for `frontend`
  - GNOME defaults are tuned for touch use:
    - on-screen keyboard enabled
    - accessibility toolkit enabled
    - text scaling set to `1.25`
    - suspend on AC disabled for kiosk-style stationary use

## Local Portal Contract

The local portal is now a compact internal action console instead of a mixed dashboard.

Why:
- the original `file://` browser path was fragile on the rebuilt Surface
- a tiny loopback-only HTTP service avoids the browser sandbox edge cases
- the kiosk still keeps a controlled local landing page without a LAN-exposed webserver

Portal source of truth:
- `manifests/control_surface/actions.json`
- only `ready` actions render
- `verify` and `backlog` stay hidden until they are browser-proven

## Current Reality

- Infrastructure status is green:
  - SSH works
  - Tailscale admin works
  - root sleep hardening is complete
  - local portal service on `127.0.0.1:17827` is live
  - the local portal service is currently verified as `active`
- Remaining Surface work is now mostly UX polish:
  - browser launch behavior should stay on the local loopback portal path
  - touch keyboard behavior still needs pragmatic local refinement
  - current working hypothesis: the touch keyboard may be opening behind the browser window instead of in the visible foreground
  - treat these as frontend sidequests, not as blockers for the core server platform
- Surface Control V1 now aims at exactly three visible groups:
  - `Dokumente`
  - `Odoo`
  - `Radio`
- the current browser-proven visible action set is now reduced to:
  - `Nextcloud Eingang`
  - `Paperless`
  - `Odoo Aufgaben`
  - `Odoo Projekte`
  - `Odoo Kalender`
  - `Radio hoeren`
  - `Radio Control`
- touch acceptance is now green for the current seven-action layout:
  - `Nextcloud Eingang` is now promoted via the canonical `files/files?dir=/Paperless/Eingang` route
  - `Odoo Kalender` is now promoted via the verified `action=517` calendar route
  - no persona cards
  - no old dashboard residue
  - no visible `Stockenweiler` area
  - the live file on the Surface matches the current rendered portal content
- no persona cards
- no full service wall
- no fake `Scannen` button until a real ingest path exists
- `Stockenweiler` actions remain backlog-only and are not rendered in V1
- launcher cleanup is now part of the operational baseline:
  - kiosk desktop stays minimal
  - admin desktop stays on the five verified launchers above

## Acceptance Criteria

- The device responds on `SSH/22` after the rebuild.
- The local hostname is `surface-go-frontend`.
- `Tailscale` is installed and reaches `Running`.
- `nginx` is absent and `HTTP/80` is no longer exposed by default.
- Kiosk autologin works without manual intervention.
- The local portal is reachable on `http://127.0.0.1:17827`.
- `FRAWO Control` launches the portal in the local desktop session.
- `frontend` has no sudo privileges.
- `frawo` remains available for local admin tasks.
- Touch usage is acceptable with the stock Ubuntu kernel, or a documented `linux-surface` follow-up exists.

## Deferred Follow-Ups

- add the final DHCP reservation on the active gateway
- evaluate `linux-surface` only if stock-kernel hardware support is insufficient
- keep `Stockenweiler` support actions out of the visible kiosk until the remote paths are verified
- keep the public website in hold mode; do not mix public website work into the Surface V1 action console
