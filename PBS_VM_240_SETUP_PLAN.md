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

## Current Verified State - 2026-03-18

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
- The stage gate intentionally remains red until one real prerequisite exists:
  - a separately mounted backup-storage path exists on Proxmox at `/srv/pbs-datastore`

## Why PBS Is Not Live Yet

The current host only exposes the internal NVMe-backed `local` and `local-lvm` storages. That is good enough for the interim local `vzdump` safety net, but not good enough to call PBS a real durability layer. A same-host same-disk PBS datastore would improve workflow convenience, but it would not materially protect against host-storage failure. Installer media is no longer the blocker; storage separation is.

## Controlled Build Path

1. Mount separate backup storage on Proxmox at `/srv/pbs-datastore`.
2. Keep the staged official PBS installer ISO at `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`, or refresh it with `make pbs-iso-stage` when the version changes.
3. Run `make pbs-stage-gate` and wait for `pbs_stage_gate_ready=yes`.
4. Deploy or refresh the runner with `make pbs-runner-deploy`.
5. Create the VM only through `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`.
6. Install PBS in the guest.
7. Add PBS as a storage target in Proxmox only after guest health, datastore mount and SSH/admin access are verified.
8. Migrate business backup jobs from the local stopgap to PBS-backed jobs.
9. Keep regular restore drills.

## Stage-Gate Rules

Do not create `VM 240` until all of these are true:

- `make proxmox-local-backup-check` is green
- `make backup-list` shows current archives for `VM 200`, `VM 220` and `VM 230`
- `make pbs-preflight` reports:
  - `pbs_4gb_fit=yes`
  - `pbs_system_disk_fit=yes`
  - `pbs_iso_present=yes`
  - `separate_backup_storage_ready=yes`
- `make pbs-stage-gate` reports `pbs_stage_gate_ready=yes`

## Immediate Next Action

Keep the current local backup timer as the active protection layer, mount separate backup storage on Proxmox, and only then lift the PBS gate from prepared to build-ready.
