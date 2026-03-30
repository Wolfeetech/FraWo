# Stockenweiler Inventory Report

Inventory source: `manifests/stockenweiler/site_inventory.json`

## Canonical Domain

- canonical: `online-prinz.de`
- legacy: `prinz-stockenweiler.de`

## Access Model

- primary remote access: `tailscale`
- fallback remote access: `anydesk`
- WAN admin exposure allowed: `False`
- site-to-site VPN allowed: `False`

## Current Known Facts

- `router`: `FRITZ!Box 5690 Pro` @ `192.168.178.1`
- `proxmox`: `proxmox Host` @ `192.168.178.25`
- `home_assistant`: `homeassistant` @ `192.168.178.67`
- `printer_scanner`: `Brother - Drucker` @ `192.168.178.153`
- `magenta_tv`: `MagentaTV` @ `192.168.178.120`

## Endpoint Status Counts

- `legacy_fact_needs_revalidation`: `5`
- `pending_inventory`: `2`

## Issues

- none

## Legacy Conflicts To Revalidate

- `proxmox_host_ip`: best guess `192.168.178.25`, conflicting legacy `192.168.178.172`
- `home_assistant_ip`: best guess `192.168.178.67`, conflicting legacy `192.168.178.68`
