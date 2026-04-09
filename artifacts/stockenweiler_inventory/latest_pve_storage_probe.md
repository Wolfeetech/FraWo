# Stockenweiler PVE Storage Probe

- generated_at: `2026-03-31 13:03:34`
- target: `stock-pve`
- probe_status: `reachable`

## Summary

- host: `pve`
- pveversion: `pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)`
- read-only truth captured for host identity, block devices, mounted filesystems, and `pvesm status`

## SSH Error

```text
Warning: Permanently added '192.168.178.25' (ED25519) to the list of known hosts.
PVE Host - Authorized Access Only
```

## Host

```text
pve
```

## PVE Version

```text
pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)
```

## Block Devices

```text
major minor  #blocks  name

   7        0   33554432 loop0
   7        1   20971520 loop1
   7        2   15728640 loop2
 259        0  250059096 nvme0n1
 259        1       1007 nvme0n1p1
 259        2    1048576 nvme0n1p2
 259        3  249009479 nvme0n1p3
 252        0    8388608 dm-0
 252        1   72736768 dm-1
 252        2    1507328 dm-2
 252        3  164864000 dm-3
 252        4  164864000 dm-4
 252        5  164864000 dm-5
   8        0 1953481728 sda
   8        1      16367 sda1
   8        2 1953464320 sda2
   8       16  976729088 sdb
   8       17  976727040 sdb1
 252        7    8388608 dm-7
 252        8   10485760 dm-8
 252        9    5242880 dm-9
 252       10   10485760 dm-10
 252       11   20971520 dm-11
 252       12   33554432 dm-12
 252       13   16777216 dm-13
 252       17       4096 dm-17
 252       19   20971520 dm-19
 252       20   44040192 dm-20
 252       21       4096 dm-21
 252       23   10485760 dm-23
 252       16   15728640 dm-16
 252        6    8388608 dm-6
 252       14    4194304 dm-14
```

## Filesystem Usage

```text
Filesystem           Type      Size  Used Avail Use% Mounted on
udev                 devtmpfs  7.8G     0  7.8G   0% /dev
tmpfs                tmpfs     1.6G  182M  1.4G  12% /run
/dev/mapper/pve-root ext4       68G   18G   47G  28% /
tmpfs                tmpfs     7.8G   31M  7.8G   1% /dev/shm
efivarfs             efivarfs  150K   73K   73K  50% /sys/firmware/efi/efivars
tmpfs                tmpfs     5.0M     0  5.0M   0% /run/lock
tmpfs                tmpfs     1.0M     0  1.0M   0% /run/credentials/systemd-journald.service
/dev/nvme0n1p2       vfat     1022M  8.8M 1014M   1% /boot/efi
tmpfs                tmpfs     7.8G     0  7.8G   0% /tmp
/dev/fuse            fuse      128M   44K  128M   1% /etc/pve
tmpfs                tmpfs     1.0M     0  1.0M   0% /run/credentials/getty@tty1.service
tmpfs                tmpfs     1.6G  8.0K  1.6G   1% /run/user/0
/dev/sdb1            fuseblk   932G  932G     0 100% /mnt/data_family
/dev/sda2            fuseblk   1.9T  1.9T   13G 100% /mnt/music_hdd
tmpfs                tmpfs     1.0M     0  1.0M   0% /run/credentials/telegraf.service
```

## PVE Storage

```text
Name              Type     Status     Total (KiB)      Used (KiB) Available (KiB)        %
hdd-backup         dir     active       976727036       976727036               0  100.00%
local              dir     active        71017632        18229560        49134852   25.67%
local-lvm      lvmthin     active       164864000       106502144        58361856   64.60%
```
