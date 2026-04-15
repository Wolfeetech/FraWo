# 2-TB SSD Assessment

## Live Facts

- Host device: `/dev/sda`
- Connection: `USB`
- Size: `1.8 TiB`
- Partition table: `GPT`
- Main data partition: `/dev/sda2`
- Filesystem: `NTFS`
- Volume label: `Wolf.EE`
- Used: `602 GB`
- Free: `1.3 TB`
- Current production role: interim cold archive for local Proxmox dump relief, not mounted persistently

## Current Content Snapshot

| Path | Size | Relevance |
| --- | ---: | --- |
| `Plugins` | `176.5 GB` | high - Studio/Audio assets |
| `von HDD` | `156.4 GB` | medium - mixed legacy import source |
| `SteamLibrary` | `119.5 GB` | low - not server relevant |
| `$RECYCLE.BIN` | `84.6 GB` | medium - old recoverable data |
| `StudioOne` | `31.3 GB` | high - production data |
| `Nicotine` | `17.1 GB` | high - music source pool |
| `MUSIK` | `6.4 GB` | high - music source pool |
| `Sets` | `3.7 GB` | medium - radio/DJ candidate material |
| `The_TraXx` | `2.7 GB` | medium - radio candidate material |
| `Job Jobse` | `0.4 GB` | medium - music source pool |

## Assessment

- Yes, this is real additional storage.
- No, it is not yet server-grade storage in its current form.
- The limiting factors are `USB` transport, `NTFS`, and the fact that private, legacy, and production data still share one partition.
- It is suitable for media archive, ingest, staging, and cold/warm storage.
- It is not the right place for VM disks, databases, or anything latency-critical.

## Current Verdict

- **The acute storage crisis is solved.**
- **The long-term storage architecture is not fully solved yet.**

Reason:

- `local-lvm` is no longer in emergency saturation.
- `local` was relieved.
- The `2-TB` SSD currently works as controlled archive spillover.
- But the disk is still `USB + NTFS` and therefore not the final server-grade tier.

## Recommended Use

### Short term

- Do not delete or repartition anything yet.
- Keep using the SSD only for low-risk archive spillover, not for active VM storage.
- The first live use is now an interim archive folder:
  - `hs27_local_dump_archive/2026-03-26_root_relief`
- Do not treat this NTFS volume as Proxmox storage.

### Medium term

- Run `chkdsk` on the disk from Windows.
- Shrink the NTFS partition from Windows, not from Proxmox Linux.
- Create a second Linux partition in the freed space.
- Format the new server partition as `ext4`.
- Mount it on the Proxmox host and expose it deliberately to the right workload.

### Target layout

- Keep `NTFS` for Wolf's legacy/private desktop data.
- Add a new Linux partition for one server purpose only:
  - `media-archive`
  - or `studio-assets`
  - or `backup-ingest`

## Explicit Recommendation

Recommended next design:

1. Leave the existing NTFS partition intact.
2. After the current media migration is complete, shrink NTFS in Windows.
3. Create a new `ext4` partition of roughly `500 GB` to `1 TB`.
4. Use that new Linux partition for server-side archive or staging.
5. Do not use this USB SSD for Proxmox VM disks or databases.

## Operational Answer

If the question is "have we solved storage cleanly?", the professional answer is:

- **operationally yes**
- **architecturally not fully yet**

That means:

- the platform can run and survive a controlled internal stress test
- but the final durable storage layout still needs one deliberate next step

## Current Interim Use

- On `2026-03-26`, local Proxmox dump archives were moved from `/var/lib/vz/dump` to:
  - `Wolf.EE/hs27_local_dump_archive/2026-03-26_root_relief`
- This relieved the host root filesystem from `100%` to about `78%`.
- This is an emergency relief measure, not the final storage architecture.
