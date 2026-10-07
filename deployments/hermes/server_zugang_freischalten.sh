#!/usr/bin/env bash
# Hermes (CT160) darf auf OptiPlex, Anker und ProDesk als root arbeiten (Wolf 07.10.2026: "Arbeitsblockade fuer Hermes
# entfernen ... im System schreibt nur KI"). Odoo #1966.
# Schluessel nur von 10.1.0.160 aus gueltig (from=), Sicherung der authorized_keys je Host.
# Von Wolf am StudioPC:  ! bash C:/Users/StudioPC/FraWo/deployments/hermes/server_zugang_freischalten.sh
set -uo pipefail
K='from="10.1.0.160" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE5IGI84dagjuXYgqOeiUDDkjJkd+7Gbho15EGCnpkAM hermes@ct160-frawo'
for h in 10.1.0.227 10.1.0.92 10.1.0.128; do
  ssh -o BatchMode=yes root@$h "cp -p /root/.ssh/authorized_keys /root/.ssh/authorized_keys.bak-20261007-hermes; grep -q hermes@ct160-frawo /root/.ssh/authorized_keys || echo '$K' >> /root/.ssh/authorized_keys; echo \$(hostname): Hermes-Schluessel eingetragen" 2>&1 | grep -v Authorized
done
# Hermes kennt die Hosts (known_hosts) und testet den Zugang
ssh -o BatchMode=yes root@10.1.0.227 "pct exec 160 -- su - hermes -c 'for h in 10.1.0.227 10.1.0.92 10.1.0.128; do ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@\$h hostname; done'"
