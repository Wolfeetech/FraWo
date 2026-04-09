# PBS Storage Audit

Recommendation: `blocked_wait_for_clean_hardware`

## Core Facts

- Proxmox root free: `0.0 GiB`
- `/var/lib/vz` free: `0.0 GiB`
- `pbs-usb` active: `false`
- `pbs-interim` active: `false`
- `VM 240` points to `pbs-usb`: `true`

## Findings

- Proxmox root has only 0.0 GiB free.
- No clean 64GB-class USB rebuild stick is currently visible.
- The visible USB SSD carries an existing data-bearing filesystem and must not be reformatted blindly.
- No dedicated ext4/xfs backup partition suitable for PBS storage is visible.
- VM 240 still points to disabled pbs-usb storage.

## Raw 64GB USB Candidates

- none

## Data-Bearing USB SSD Candidates

- `/dev/sda` `1863.02 GiB` fstype=`unknown` label=`none` model=`Tech` serial=`DD56419883961`

## Dedicated Backup Partitions

- none