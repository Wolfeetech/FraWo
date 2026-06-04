# proxmox-anker Stabilitätsproblem — Analyse 2026-06-04

## Crash-Pattern
- 4 Abstürze in ~24 Stunden (03-04.06.2026)
- Uptime jeweils 8-12 Stunden vor dem Absturz
- PBS Backup-Job läuft tägl. 02:00 → könnte Auslöser sein (I/O-Last)

## Sofort-Maßnahmen (Wolf im BIOS/PVE)

### 1. BIOS — Lenovo Thin Centre
- Power Management → **Performance Mode**
- C-States: **deaktivieren** (C1, C3, C6, C7 aus)
- Thermal: Fan auf **immer aktiv** stellen
- Wake on LAN: aktivieren (für Remote-Restart)

### 2. PVE Einstellungen
```bash
# ACPI-Events ignorieren (verhindert versehentlichen Sleep)
echo 'HandlePowerKey=ignore' >> /etc/systemd/logind.conf
echo 'HandleSuspendKey=ignore' >> /etc/systemd/logind.conf
systemctl restart systemd-logind

# Watchdog aktivieren (automatischer Neustart bei Kernel-Panic)
echo 'kernel.panic = 30' >> /etc/sysctl.conf
echo 'kernel.panic_on_oops = 1' >> /etc/sysctl.conf
sysctl -p

# Nach Absturz: Logs prüfen
journalctl -xb -1 | tail -50
dmesg | grep -iE 'error|kill|oom|panic|hang' | tail -20
```

### 3. PBS Backup-Job entlasten
```bash
# Backup von 02:00 auf 03:00 verschieben (nach fstrim um 04:00)
pvesh set /cluster/backup/daily-all-pbs --schedule "03:00"
pvesh set /cluster/backup/6b5de9469e7bf882b520ee027801a2985b159202:1 --schedule "03:30"
```

## Langfristige Lösung
HP ProDesk (stockenweiler-pve) als 2. PVE-Knoten → Proxmox Cluster mit HA
→ Wenn Lenovo crasht: VMs migrieren automatisch auf HP ProDesk
