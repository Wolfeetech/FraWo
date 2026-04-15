# Portable Backup USB Plan

## Purpose

This is the interim path for a `64GB` USB stick that will be plugged into Proxmox and filled with the most valuable local `vzdump` archives.

Current live note:
- the originally prepared stick has now been repurposed into the interim PBS USB path
- it is no longer just an off-host shuttle, but an always-attached temporary PBS storage component

It is explicitly **not** the same thing as the planned PBS datastore:

- PBS target remains `/srv/pbs-datastore`
- PBS stage gate still expects materially larger separate storage
- the `64GB` stick is a practical off-host shuttle and extra copy, not the final backup architecture

## Target

- Label: `HS27_PORTABLEBK`
- Mount path on Proxmox: `/srv/portable-backup-usb`
- Content path: `/srv/portable-backup-usb/archives`
- Manifest path: `/srv/portable-backup-usb/manifests/selection.txt`

## Fill Policy

The stick should be filled as usefully as possible, not randomly:

1. Always include the newest local archive for each protected business VM:
   - `200`
   - `210`
   - `220`
   - `230`
2. Then add additional older archives by recency while staying within the USB budget.
3. Keep safety slack:
   - reserve about `4 GiB`
   - do not exceed about `94%` of total capacity

## Commands

Prepare after the stick is physically attached to Proxmox:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
./scripts/proxmox_portable_backup_usb_prepare.sh /dev/sdX
```

Or use the safer auto-detect helper when only the intended 64GB backup stick is attached:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
./scripts/proxmox_portable_backup_usb_autoprepare.sh
```

Fill it with the best-fit archive set:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
./scripts/proxmox_portable_backup_usb_fill.sh
```

Check status:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
./scripts/proxmox_portable_backup_usb_check.sh
```

One-command operator path once the stick is attached to Proxmox:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
./scripts/proxmox_portable_backup_usb_run.sh
```

## Operator Notes

- The prepare step is destructive for the target USB device.
- Use this only for the dedicated backup stick, not the install sticks.
- Once the fill is complete, the stick can be unplugged and kept off-host as an interim durability improvement.
- Auto-detect only succeeds if exactly one unprepared 64GB-class USB disk is attached to Proxmox.
