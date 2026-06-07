
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
