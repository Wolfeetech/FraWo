# Storage Optimization Audit

- Generated at: `2026-04-04T02:04:25+02:00`
- Anker local dump: `23.31 GiB`
- Anker local usage: `69.1%` / local-lvm `61.2%`
- Stockenweiler hdd-backup usage: `84.0%`
- Stockenweiler music library: `1430.70 GiB`
- Stockenweiler yourparty library: `282.14 GiB`
- Stockenweiler music inbox: `68.48 GiB`

## Highest Pressure

- `stockenweiler` backup dataset is the first hard reclaim target: keep-last-2 on `VM 210` can free `223.80 GiB`
- keep-last-2 on `VM 360` can free `69.42 GiB`
- raw image archive review can free up to `131.00 GiB` if verified obsolete or exported first
- `music_hdd` is the second hard pressure point: `Library` `1430.70 GiB`, `yourparty_Libary` `282.14 GiB`, `Inbox` `68.48 GiB`

## Data Family Top Consumers

- `/mnt/data_family/Onenotes` -> `1.52 GiB`
- `/mnt/data_family/KEINE AHNUNG` -> `1.76 GiB`
- `/mnt/data_family/bis 24` -> `2.33 GiB`
- `/mnt/data_family/Programme` -> `10.61 GiB`
- `/mnt/data_family/backups` -> `86.51 GiB`
- `/mnt/data_family/Dokumente` -> `156.59 GiB`
- `/mnt/data_family/proxmox_backups` -> `521.82 GiB`
- `/mnt/data_family` -> `781.86 GiB`

## Library Top Consumers

- `/mnt/music_hdd/Library/Minimal Synth` -> `18.44 GiB`
- `/mnt/music_hdd/Library/Pop` -> `22.58 GiB`
- `/mnt/music_hdd/Library/Progressive House` -> `23.26 GiB`
- `/mnt/music_hdd/Library/Minimal` -> `26.26 GiB`
- `/mnt/music_hdd/Library/France` -> `30.67 GiB`
- `/mnt/music_hdd/Library/Synthpop` -> `31.40 GiB`
- `/mnt/music_hdd/Library/Italo Disco` -> `42.38 GiB`
- `/mnt/music_hdd/Library/Deep House` -> `47.46 GiB`
- `/mnt/music_hdd/Library/Trance` -> `91.33 GiB`
- `/mnt/music_hdd/Library/Electro` -> `91.64 GiB`
- `/mnt/music_hdd/Library/Dance` -> `111.42 GiB`
- `/mnt/music_hdd/Library/House` -> `113.02 GiB`
- `/mnt/music_hdd/Library/Techno` -> `122.48 GiB`
- `/mnt/music_hdd/Library/Electronic` -> `233.81 GiB`
- `/mnt/music_hdd/Library` -> `1430.70 GiB`

## Ordered Plan

- Freeze new backup load on `stockenweiler` until reclaim is complete.
- Keep only the last `2` verified dumps for `VM 210` and `VM 360`, but do not delete before the retained set is explicitly checked.
- Review `proxmox_backups/images/*` as cold archive payload, not as invisible permanent storage.
- Classify `music_hdd` into keep-local, migrate-to-Anker, or archive-offline; start with `Inbox` and `yourparty_Libary`, not the whole `Library` tree.
- Restore a green PBS path on `Anker` before moving or retargeting more backup load.
- Only after PBS is green: decide whether `Anker` local dump retention should be shortened or moved off root storage.

## Guardrails

- No blind deletes on `music_hdd`.
- No backup-pruning without an explicit kept-set check.
- No new Stockenweiler storage role before reclaim and PBS recovery.
