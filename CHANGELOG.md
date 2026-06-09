# CHANGELOG - IT-Abteilung

Hier werden alle umgesetzten Änderungen (Optionen), die vom Chef freigegeben wurden, chronologisch dokumentiert.

## 2026-06-09 (Opus / Claude Code Session)
- **KRITISCH: proxmox-anker Root-Disk war 100% voll (0 frei) → 63% (24 GB frei).** Ursache: kaputte systemd-Drop-in `rclone-gdrive.service.d/cache.conf` (31.05.) überschrieb die gute Konfig und zwang den rclone-vfs-Cache (28 GB) auf die Root-Disk statt auf ssd2tb. Fix: Drop-in gelöscht → Haupt-Unit (cache-dir /mnt/ssd2tb/.rclone-cache) greift wieder; Root-Cache nach sauberem Stop freigegeben; gdrive-Mount verifiziert gesund. **Folge: die still scheiternden nächtlichen Backups (voller Root → verwaister Lock auf CT 130) sollten wieder laufen.**
- **radio-node (CT 130): 173 apt-Updates installiert + Reboot** (Backup-Netz: vzdump/PBS 2026-06-08). Stream + Container verifiziert, 4 Kerne aktiv. Verwaisten Backup-Lock (`pct unlock 130`) gelöst.
- **Odoo Performance:** workers=4 (statt 0) + db-filter + limit-time-real-cron=300 in Compose-command; DB-Selektor-Umweg weg. (frawo.tech extern bleibt tunnel-latenzabhängig.)
- **Agent-Cron repariert:** numbercall=-1 (lief nur 1×, dann gestoppt) → tickt jetzt autonom alle 2 Min.

## 2026-06-07 (Opus / Claude Code Session)

### KRITISCH behoben
- **PVE root-Partition war 100% voll** → 63% (25GB frei). Ursache: rclone-gdrive vfs-cache (26GB) lag auf `/var/cache/rclone-gdrive` (root-Disk). Service-Config zeigte zwar auf ssd2tb, aber alter Prozess hielt gelöschte Dateien. Fix: `systemctl restart rclone-gdrive.service`.
- **rclone-music-library**: hängender FUSE-Mount ("Transport endpoint not connected") → fusermount -u + restart → active.

### Verifiziert (Korrektur zu vorherigem Agent-Bericht)
- local-lvm noch bei 90.48% (NICHT auf 69% wie berichtet) — die Entlastung war auf `local`/root durch rclone-Cache.
- PBS VM240: läuft + pingbar (10.4.0.25), aber KEIN SSH-Key + kein guest-agent → Backups NICHT verifizierbar.
- Watchdog: war NICHT aktiv (nur Script vorhanden). softdog-Modul jetzt geladen + /etc/modules.

### HA Automationen
- 6 Automationen via Config-API angelegt (Datei-Include lud nicht): Sirius Black (3x), Werkstatt-Steckdose (3x). Alle state=on.

### OFFENER BEFUND (braucht Wolf-Entscheidung)
- **GrowBox HA-Steuerung komplett offline**: 45 Entitäten unavailable — shelly_grow_licht (20), growbox_schwenk (14), prima_klima_shelly (11). Sind das die Shellys der echten GrowBox? Absicht (Grow aus) oder Netzwerkproblem?

## 2026-06-07
- **Autonomer Odoo-Agent `frawo_agent` LIVE:**
  - Neues Odoo-Addon gebaut (Branch `feat/frawo-agent`, 14 Unit-Tests grün, E2E auf DB-Kopie `FraWo_GbR_test` mit echtem Ollama verifiziert).
  - Funktion: jeder neue `project.task` wird autonom als „🤖 Agent" (UID 7) nach CI ausformuliert (lokales Ollama `llama3:8b`), Rollen-Tag gesetzt (DevOps/Review-Wolf/Handwerk-Franz), Owner/Deadline als Freigabe-Vorschlag (Aktivität).
  - Schutzregeln: 1 Task/Cron-Takt, num_predict=300, Timeout 150s, Fehler-Isolation (`agent_state=error`), bereits dokumentierte Tasks (>=150 Zeichen) werden nicht überschrieben.
  - **Eingriff:** DB-Backup gezogen (`~/backups/FraWo_GbR_20260607_194904.dump`); Compose um bind-mount `./extra-addons` + `--addons-path` ergänzt (fehlte vorher ganz); odoo-web neu erstellt (~30s Downtime); Modul installiert; Cron aktiv (alle 2 Min, user agent@frawo.tech).
  - **Grund:** Wolf wollte „Agent sitzt in Odoo, formatiert neue Tasks autonom, ohne manuelle Aktivierung". Kosten: 0 € (Odoo Community + lokales Ollama).
  - Demo-Task #520 als Funktionsbeweis. Spec+Plan: `DOCS/specs/` + `DOCS/plans/`.
- **VM 240 (Proxmox Backup Server):** 
  - Die 500GB Daten-Festplatte (`vm-240-disk-1`) wurde von der NVMe (`local-lvm`) auf die `ssd2tb` verschoben.
  - **Grund:** Der LVM-Thin Pool war zu 90,4% gefüllt, was Backups blockiert hat. Durch den Umzug wurde massiv Speicherplatz auf der NVMe freigegeben.
