# Backup and Restore Proof

## Latest Verified Run

- Verification date: `2026-03-21`
- Verified backup paths:
  - `local` on Proxmox
  - `pbs-interim` on `VM 240 pbs`
- Restore target storage: `local-lvm`
- Scope of protected business VMs in this proof:
  - `VM 200` Nextcloud
  - `VM 210` HAOS
  - `VM 220` Odoo
  - `VM 230` Paperless

## Backup Results

| VM | Service | Archive | Size | Result |
| --- | --- | --- | --- | --- |
| `200` | Nextcloud | `vzdump-qemu-200-2026_03_18-00_18_22.vma.zst` | `1.8G` | success |
| `220` | Odoo | `vzdump-qemu-220-2026_03_18-00_18_59.vma.zst` | `1.7G` | success |
| `230` | Paperless | `vzdump-qemu-230-2026_03_18-00_19_33.vma.zst` | `2.8G` | success |

## Restore Proof

- Source VM: `VM 220` Odoo
- Restored test VM: `VM 920`
- Temporary proof IP: `192.168.2.240`
- Verification endpoint: `http://192.168.2.240:8069/web/login`
- Guest-Agent status after boot: `qga_ok`
- HTTP verification result: `200 OK`
- Cleanup result:
  - `VM 920` was stopped and destroyed again after the proof
  - the Proxmox config for `VM 920` no longer exists

## PBS Interim V1 Proof - 2026-03-21

- PBS target:
  - guest `VM 240 pbs`
  - address `192.168.2.25`
  - datastore `hs27-interim`
  - Proxmox storage `pbs-interim`
- Proof-backup result:
  - source VM `220`
  - snapshot `vm/220/2026-03-21T10:04:30Z`
  - Proxmox task status `exitstatus: OK`
- Proof-restore result:
  - restored test VM `920`
  - temporary proof IP `192.168.2.240`
  - verification endpoint `http://192.168.2.240:8069/web/login`
  - guest-agent status after boot `qga_ok`
  - HTTP verification result `200 OK`
  - cleanup result:
    - `VM 920` was stopped and destroyed again after the proof
    - the Proxmox config for `VM 920` no longer exists

## Operational Notes

- The local proof path is valid as an interim safeguard until PBS is live.
- PBS-v1 is now also practically proven on the interim USB-backed path:
  - backup target `pbs-interim`
  - datastore `hs27-interim`
  - first backup proof and first restore proof are both green for `VM 220`
  - current interim retention:
    - `02:40,14:40`
    - `keep-daily=2`
    - `keep-weekly=1`
    - `keep-monthly=1`
- Interim local night operation is now also live on Proxmox:
  - systemd timer `homeserver2027-local-business-backup.timer`
  - next scheduled run: daily at `02:40`
  - runner script on host: `/usr/local/sbin/homeserver2027-local-business-backup.sh`
  - deployed from `ansible/playbooks/deploy_proxmox_local_backup_ops.yml`
- Verified timer-backed run on `2026-03-18`:
  - `VM 200` -> `vzdump-qemu-200-2026_03_18-06_02_33.vma.zst`
  - `VM 220` -> `vzdump-qemu-220-2026_03_18-06_03_12.vma.zst`
  - `VM 230` -> `vzdump-qemu-230-2026_03_18-06_03_47.vma.zst`
  - run finished with `status=0/SUCCESS`
  - resulting retention after the run: `2` local archives per business VM
- Verified rerun after HAOS integration on `2026-03-18`:
  - `VM 200` -> `vzdump-qemu-200-2026_03_18-20_44_45.vma.zst`
  - `VM 210` -> `vzdump-qemu-210-2026_03_18-20_45_24.vma.zst`
  - `VM 220` -> `vzdump-qemu-220-2026_03_18-20_46_06.vma.zst`
  - `VM 230` -> `vzdump-qemu-230-2026_03_18-20_46_42.vma.zst`
  - rerun finished with `status=0/SUCCESS`
  - resulting retention after the rerun: `2` local archives per secured VM
- Current post-run storage state on Proxmox:
  - `local` usage is about `24%`
  - `local-lvm` usage is about `13%`
- The proof was executed with `./scripts/proxmox_business_backup_proof.sh`.
- Local retention until PBS is live:
  - keep the latest `2` local qemu backup archives per secured VM
  - inspect with `make backup-list`
  - dry-run cleanup with `make backup-prune-dry-run`
  - apply cleanup with `make backup-prune`
  - verify timer and host archives with `make proxmox-local-backup-check`

## Next Step

1. Keep the scheduled local backup timer as a second local safety net while PBS-v1 is stabilized.
2. Keep the scheduled PBS regime active on `pbs-interim`.
3. Repeat restore tests on a rotating basis, for example monthly on `VM 200`, `VM 210` or `VM 230`.
4. Migrate later from the `64GB` interim USB target to larger dedicated PBS storage.
