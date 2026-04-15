# PBS VM 240 Setup Plan

Stand: `2026-03-27`

## Goal

Rebuild `VM 240` as a clean, controlled PBS path without writing to the wrong removable device and without pretending that the current hardware state is already ready.

## Current Verified State

- `CT100 toolbox` is repaired and no longer consuming Proxmox root through the obsolete local bootstrap media sync.
- Proxmox root is healthy again with real working headroom.
- The official PBS installer ISO is staged and checksum-verified on Proxmox:
  - `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
  - SHA256 `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
- `VM 240` still exists, but its current config is drifted:
  - `scsi0` points to `pbs-usb`
  - `scsi1` points to `pbs-usb`
  - this is not the intended runner contract
- The intended runner contract remains:
  - system disk `32G` on `local-lvm`
  - data disk `40G` on Proxmox storage `pbs-usb`
- The latest PBS storage audit is blocked:
  - report: `artifacts/pbs_storage_audit/20260327_081910/report.md`
  - no clean 64GB-class rebuild USB is currently visible
  - the visible boot-stick candidate reports `No medium found`
  - the visible `1.8T` USB SSD is data-bearing and must not be reformatted blindly

## Non-Negotiable Safety Rules

- Never wipe a USB or SSD by path alone.
- Every destructive PBS device step must be gated by:
  - a visible serial number
  - explicit approval in `manifests/pbs_rebuild/device_contract.json`
  - a fresh contract check report
- Boot USB and datastore device must be separate roles.
- The PBS datastore device must not be reused from the portable backup shuttle path.
- The current data-bearing `1.8T` USB SSD stays untouched until it is explicitly approved for reformat.

## Guarded Rebuild Workflow

1. Run `make pbs-rebuild-storage-audit`.
2. Run `make pbs-device-inventory` to capture the currently visible serials and device facts.
3. Fill `manifests/pbs_rebuild/device_contract.json` with:
   - approved boot USB serial
   - approved datastore device serial
   - explicit destructive approval flags
   - operator approval metadata
   - optional helper:
   - `make pbs-contract-prefill BOOT_SERIAL=... DATASTORE_SERIAL=... APPROVED_BY=...`
4. Attach only the intended PBS boot USB and the intended datastore device.
5. Run `make pbs-rebuild-contract-check`.
6. Only if the contract check says `ready_for_guarded_pbs_datastore_prepare`, run:
   - `make pbs-datastore-prepare DEV=/dev/sdX`
7. Re-deploy the PBS runner with `make pbs-runner-deploy`.
8. Dry-run the guarded VM worker with:
   - `make pbs-vm240-reconcile`
   - or the combined guarded pipeline:
   - `make pbs-guarded-rebuild`
9. Reconcile or rebuild `VM 240` so it matches the runner contract:
   - `scsi0` on `local-lvm`
   - `scsi1` on `pbs-usb`
   - real execution is only allowed with `PBS_VM240_EXECUTE=yes` and `PBS_VM240_ALLOW_DESTROY=yes`
10. Continue with guest install, datastore initialization, proof backup and restore drill.

## What Is Already Automated

- `make pbs-iso-stage`
  - stages and verifies the official PBS ISO
- `make pbs-rebuild-storage-audit`
  - checks live hardware visibility and obvious unsafe conditions
- `make pbs-device-inventory`
  - produces a non-destructive report of visible block devices, serials and obvious hazards on Proxmox
- `make pbs-rebuild-contract-check`
  - verifies approved serials, approval metadata and current device visibility
- `make pbs-contract-prefill`
  - writes approved serials into the contract while keeping destructive approvals explicitly false
- `make pbs-datastore-prepare DEV=/dev/sdX`
  - guarded destructive prepare for the approved PBS datastore device
- `make pbs-vm240-reconcile`
  - dry-runs the VM240 drift/rebuild decision and only executes behind explicit environment flags
- `make pbs-guarded-rebuild`
  - runs audit, contract check, runner deploy, preflight and the guarded VM path in one controlled entrypoint
- `make pbs-preflight`
  - checks memory, system-disk fit, ISO presence and datastore mount state
- `make pbs-stage-gate`
  - checks whether the overall PBS path is really green

## Current Blocker

The rebuild is blocked by hardware, not by missing automation:

- the current boot-stick candidate is visible only as `USB Disk 3.0 / FC2604224284249D`
- it currently reports `No medium found`
- the visible `1.8T` USB SSD is not a safe automatic target because it contains existing data

## Next Admin Action

Provide:

1. a real, readable PBS boot USB stick
2. a dedicated datastore device or datastore partition that is explicitly approved for reformat

After that, the guarded workflow above is the only approved rebuild path.
