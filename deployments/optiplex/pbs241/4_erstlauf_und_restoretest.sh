#!/bin/bash
# 🤖 [Claude] 24.09.2026 — Laeuft auf dem OPTIPLEX, Odoo #1462
# Erste Sicherung eines kleinen Gastes + echte Wiederherstellung als Beweis.
# Der Testgast wird NICHT gestartet (er traegt die feste IP des Originals) und danach entfernt.
set -euo pipefail
vzdump 102 --storage pbs --mode snapshot
SNAP=$(pvesm list pbs --vmid 102 | awk 'NR>1{print $1}' | tail -1)
echo "Sicherung: $SNAP"
pct restore 9102 "$SNAP" --storage local-lvm --unique 1
pct mount 9102 >/dev/null
test -s /var/lib/lxc/9102/rootfs/etc/hostname && echo "RESTORE-TEST OK: $(cat /var/lib/lxc/9102/rootfs/etc/hostname), $(du -sh /var/lib/lxc/9102/rootfs 2>/dev/null | cut -f1)"
pct unmount 9102
pct destroy 9102 --purge 1
echo "Testgast 9102 entfernt"
