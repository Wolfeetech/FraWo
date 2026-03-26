# PBS VM 240 Setup Plan

## Goal

Prepare a controlled Proxmox Backup Server rollout path without weakening the current backup posture or pretending that same-host same-disk backups are enough.

## Target Shape

- VM ID: `240`
- Planned hostname: `pbs`
- Planned IP: `192.168.2.25`
- Role: dedicated Proxmox Backup Server control plane
- CPU / RAM: `2 vCPU`, `4096 MB`
- System disk: `32 GB` on Proxmox `local-lvm`
- Datastore: only on a separately mounted backup filesystem exposed to the PBS guest workflow
- Exposure: internal only, never public

## Current Verified State - 2026-03-21

- The interim local backup path on Proxmox is live and healthy:
  - `homeserver2027-local-business-backup.timer` is enabled
  - `VM 200`, `VM 220` and `VM 230` have fresh local archives
- restore proof already succeeded for Odoo
- The PBS VM runner path is now prepared on Proxmox:
  - `ansible/playbooks/deploy_pbs_vm_runner.yml`
  - `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`
  - `make pbs-preflight`
  - `make pbs-stage-gate`
  - `make pbs-vm-check`
- The official PBS installer ISO is already staged and checksum-verified on Proxmox:
  - source file: `/var/lib/vz/template/iso/proxmox-backup-server_4.1-1.iso`
  - active alias: `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
  - checksum: `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
- Interim PBS USB mode is now live on Proxmox:
  - the `64GB` USB stick `HS27_PORTABLEBK` is mounted on `/srv/portable-backup-usb`
  - the same filesystem is bind-mounted to `/srv/pbs-datastore`
  - Proxmox storage `pbs-usb` exists and is active
  - `VM 240` now exists with:
    - `32 GB` system disk on `local-lvm`
    - `40 GB` USB-backed data disk on `pbs-usb`
    - `3072 MB` RAM as a constrained interim fit for the current host
  - the PBS guest is installed and reachable:
    - hostname `pbs`
    - IP `192.168.2.25`
    - SSH and web UI on `8007` are reachable
  - the USB-backed guest datastore is initialized:
    - filesystem label `PBS_DATA`
    - mountpoint `/mnt/datastore-interim`
    - datastore name `hs27-interim`
  - Proxmox storage `pbs-interim` is already registered and active against `hs27-interim`
  - daily backup job `hs27-pbs-interim-daily` exists for `200,210,220,230`
  - retention is intentionally constrained for the `64GB` stick:
  - schedule `02:40`
    - `keep-daily=2`
    - `keep-weekly=1`
    - `keep-monthly=1`
  - first green proof-backup run is now verified:
    - `VM 220`
    - datastore snapshot path `vm/220/2026-03-21T10:04:30Z`
    - Proxmox task `exitstatus: OK`

## Why PBS Is Not Fully Done Yet

The original blocker was lack of separate storage. That is now solved in an interim way with the attached `64GB` USB stick. The remaining blocker is now no longer installation, but proof quality:

- recurring restore drills on the PBS-v1 path still need to be repeated regularly after the first green proof
- this `64GB` USB mode remains intentionally small and temporary compared with the later final PBS target
- this `64GB` USB mode is useful and real, but intentionally smaller and less durable than the later final PBS target

## Controlled Build Path

1. Keep the staged official PBS installer ISO at `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`, or refresh it with `make pbs-iso-stage` when the version changes.
2. Keep the interim USB-backed datastore mount live on Proxmox at `/srv/pbs-datastore`.
3. Deploy or refresh the runner with `make pbs-runner-deploy`.
4. Build or refresh the VM only through `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`.
5. Keep the datastore `hs27-interim` on `/mnt/datastore-interim` mounted and healthy.
6. Keep Proxmox storage `pbs-interim` active.
7. Keep regular restore drills on the PBS-v1 path.
8. Replace this interim USB path later with larger dedicated PBS storage.
9. Re-check host RAM comfort before treating PBS-v1 as long-term steady state.

## Stage-Gate Rules

Do not treat `VM 240` as production-ready until all of these are true:

- `make proxmox-local-backup-check` is green
- `make backup-list` shows current archives for `VM 200`, `VM 220` and `VM 230`
- `make pbs-preflight` reports:
  - `pbs_4gb_fit=yes`
  - `pbs_system_disk_fit=yes`
  - `pbs_iso_present=yes`
  - `separate_backup_storage_ready=yes`
- the PBS guest install is complete
- the guest-side datastore is initialized and verified
- at least one proof-backup run to `pbs-interim` finishes cleanly

## Immediate Next Action

Keep the green proof-backup and restore path on `pbs-interim` repeatable, then keep the `64GB` USB attached until a larger final PBS target exists.

## Recurring Restore Drills (Betriebsstandard)

Ein verlässliches Backup ist nur so gut wie sein Restore-Test. Folgender Standard-Prozess wird monatlich empfohlen:

1. **Drill-Start**: `make pbs-restore-proof`
2. **Ausführung**:
   - Das Skript stellt eine ausgewählte VM (z.B. Odoo oder Nextcloud) unter einer neuen Test-ID (z.B. 920) in einen isolierten Zustand wieder her.
   - Proxmox holt die Daten vom PBS-Storage.
3. **Prüfung**:
   - Starte die Test-VM ohne Netzwerk / im isolierten Subnetz.
   - Prüfe via Proxmox-Konsole, ob Services wie Datenbank und Webserver erfolgreich booten.
4. **Clean-Up**:
   - Nach erfolgreichem Boot und Login den Test dokumentieren.
   - Die temporäre Test-VM (z.B. ID 920) sofort wieder löschen.
