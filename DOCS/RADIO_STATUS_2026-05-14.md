# Radio / AzuraCast Status - 2026-05-14

**Update:** Diagnostik durch Claude (Radio-Init)
**Ziel:** funk.frawo-tech.de für AzuraCast einrichten

---

## 🎯 AKTUELLER STATUS: 🔴 OFFLINE — Raspberry Pi physisch nicht erreichbar

### Infrastruktur

| Component | IP | Status | Notizen |
|-----------|-----|--------|---------|
| **Raspberry Pi 4 (radio-node)** | 192.168.2.155 | ❌ OFFLINE | "Destination host unreachable" von StudioPC |
| **Raspberry Pi Tailscale** | 100.64.23.77 | ❌ OFFLINE | Nicht in `tailscale status` gelistet, Auth abgelaufen? |
| **Raspberry Pi VLAN 103** | 10.3.0.9 | ❌ OFFLINE | Legacy-IP, VLAN existiert nicht mehr (10.4.0.x jetzt aktiv) |
| **Proxmox Anker** | 100.69.179.87 | ✅ ONLINE | Host OK, kein Radio-Container vorhanden |
| **Proxmox Stockenweiler** | 100.91.20.116 | ❌ OFFLINE | 4+ Tage offline |
| **Storage Node (CT 110)** | 10.1.0.30 / 10.4.0.30 | ✅ ONLINE | Erreichbar von Proxmox (10.4.0.30) |

### Was geprüft wurde

1. ✅ SSH zu Proxmox Anker (100.69.179.87) — erfolgreich
2. ✅ `pct list` — kein Radio-Container vorhanden (Container: toolbox, adguard-slave, storage-node, vaultwarden)
3. ✅ `qm list` — kein Radio-VM vorhanden (VMs: nextcloud, haos, odoo, paperless, PBS)
4. ✅ Ping-Sweep 10.4.0.1-30 von Anker — Pi nicht im Netz
5. ✅ ARP-Scan von StudioPC (192.168.2.x) — Pi MAC nicht gefunden
6. ✅ Tailscale Status — Pi nicht im Tailnet gelistet
7. ✅ Ping 192.168.2.155 — "Destination host unreachable"
8. ✅ Ping 100.64.23.77 — Timeout
9. ✅ Ping 10.3.0.9 von Anker — 100% packet loss

### Music Library auf Anker (verfügbar!)

| Pfad | Größe | Inhalt |
|------|-------|--------|
| `/mnt/music_ssd/yourparty.radio/` | 67 GB | Legacy yourparty Library |
| `/mnt/music_ssd/FraWo_Musikarchiv/` | 5 GB | Kuratiertes Archiv |
| `/mnt/music_ssd/` (gesamt) | ~72 GB | Auf 983 GB SSD |

---

## 🚨 BLOCKER

### Der Raspberry Pi muss physisch geprüft werden

**Das ist der einzige Blocker.** Alles andere (Domain, AzuraCast-Config, Player) kann erst danach passieren.

**Mögliche Ursachen:**
1. **Stromkabel ab** — einfachster Fall
2. **SD-Karte korrupt** — Pi bootet nicht (häufig bei Pi 4)
3. **Netzwerkkabel ab / DHCP-Lease abgelaufen** — Pi hat keine IP mehr
4. **Pi an anderem Switch/VLAN** — seit Netzwerk-Migration auf 10.4.0.x

**Was zu tun ist (physisch, durch Wolf):**
1. Prüfen ob der Pi eingeschaltet ist (grüne LED blinkt?)
2. Prüfen ob Ethernet-Kabel steckt
3. Monitor anschließen um Boot-Status zu sehen
4. Falls kein Boot: SD-Karte in PC prüfen, ggf. neu flashen
5. Nach Boot: IP prüfen (`ip addr show`)

---

## 🔄 ALTERNATIVE STRATEGIE: AzuraCast auf Proxmox Anker

Falls der Pi defekt/verschollen ist, kann AzuraCast auch als **LXC Container auf Proxmox Anker** laufen:

### Vorteile
- Sofort verfügbar (kein physischer Eingriff)
- Musik-SSD bereits angeschlossen (983 GB)
- Mehr RAM/CPU als Pi 4
- Backup über PBS möglich

### Ressourcen auf Anker
- **CPU**: 6 Kerne (3 genutzt durch VMs)
- **RAM**: 9.2 GB frei
- **Storage**: 34 GB root + 879 GB music_ssd + 1.7 TB ssd2tb
- **Template**: Ubuntu 26.04 LTS verfügbar

### Quick-Setup (wenn User zustimmt)
```bash
# 1. Template downloaden
pveam download local ubuntu-26.04-standard_26.04-1_amd64.tar.zst

# 2. LXC erstellen (CT 130)
pct create 130 local:vztmpl/ubuntu-26.04-standard_26.04-1_amd64.tar.zst \
  --hostname radio-node \
  --memory 2048 \
  --cores 2 \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1,keyctl=1 \
  --unprivileged 0 \
  --start 1

# 3. Music SSD mounten
pct set 130 -mp0 /mnt/music_ssd,mp=/mnt/music

# 4. Docker + AzuraCast installieren
pct exec 130 -- bash -c "
  apt update && apt install -y curl
  curl -fsSL https://raw.githubusercontent.com/AzuraCast/AzuraCast/main/docker.sh | bash
"
```

---

## 📋 ENTSCHEIDUNG FÜR WOLF

| Option | Aufwand | Risiko | Empfehlung |
|--------|---------|--------|------------|
| **A: Pi reparieren** | 10-30 Min physisch | SD-Karte defekt? | ✅ Wenn Pi da & erreichbar |
| **B: LXC auf Anker** | 15 Min remote | LVM-thin bei 89.8%! | ⚠️ Besser auf ssd2tb |
| **C: Warten** | 0 Min | Radio bleibt offline | ❌ Nicht empfohlen |

> **Empfehlung:** Option A versuchen. Falls Pi defekt → Option B (LXC auf Anker, rootfs auf ssd2tb statt local-lvm).

---

## 📝 NÄCHSTE SCHRITTE (nach Pi online / LXC erstellt)

1. AzuraCast Docker starten
2. Station "FraWo Funk" konfigurieren
3. Music Library mounten (67 GB yourparty + 5 GB FraWo_Musikarchiv)
4. Erste Playlist erstellen + AutoDJ
5. funk.frawo-tech.de DNS (Cloudflare)
6. NPM Proxy Host einrichten
7. Web-Player für frawo-tech.de
8. SSL/HTTPS

---

**Status:** 🔴 BLOCKED — Raspberry Pi physisch offline
**Blocker:** Hardware-Check durch Wolf erforderlich
**Verantwortlich:** Wolf (physischer Zugriff nötig)
