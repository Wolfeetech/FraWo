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
  - local portal and kiosk baseline are applied
  - `nginx` is absent and `HTTP/80` / `HTTPS/443` are closed
  - the node later went offline again with a sleep/off-network pattern and is currently not under active remote control
  - remaining technical steps are: verify the Tailscale join, hard-disable sleep targets and finish the reboot/kiosk acceptance

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
  - Firefox installed for kiosk mode
  - `Tailscale` installed from the official Ubuntu package feed
  - kiosk autostart points to a local portal file under `/opt/homeserver2027/frontend-portal/index.html`
  - `gdm3` autologin is configured for `frontend`
  - GNOME defaults are tuned for touch use:
    - on-screen keyboard enabled
    - accessibility toolkit enabled
    - text scaling set to `1.25`
    - suspend on AC disabled for kiosk-style stationary use

## Local Portal Contract

The local portal page is intentionally static and file-based.

Why:
- no local webserver is needed
- the kiosk still has a controlled landing page
- internal service links stay easy to update

Default portal links:
- `Home Assistant` -> `http://ha.hs27.internal`
- `Nextcloud` -> `http://cloud.hs27.internal`
- `Radio` -> `http://radio.hs27.internal`
- `Paperless` -> `http://paperless.hs27.internal`
- `Odoo` -> `http://odoo.hs27.internal/web/login`

## Acceptance Criteria

- The device responds on `SSH/22` after the rebuild.
- The local hostname is `surface-go-frontend`.
- `Tailscale` is installed and reaches `Running`.
- `nginx` is absent and `HTTP/80` is no longer exposed by default.
- Kiosk autologin works without manual intervention.
- Firefox launches in kiosk mode to the local portal page.
- `frontend` has no sudo privileges.
- `frawo` remains available for local admin tasks.
- Touch usage is acceptable with the stock Ubuntu kernel, or a documented `linux-surface` follow-up exists.

## Deferred Follow-Ups

- add the final DHCP reservation on the active gateway
- switch the kiosk landing page from the local portal file to `portal.hs27.internal` once the shared internal portal exists
- evaluate `linux-surface` only if stock-kernel hardware support is insufficient
