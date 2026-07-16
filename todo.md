# TODO

Aktive Aufgaben und offene Punkte für Wolf.
_Stand-Abgleich 2026-07-16 (Werkstatt-Inventur): erledigte/überholte Ideen markiert, damit keine losen Enden bleiben._

## Infrastruktur

- [ ] Beets ersten Test-Import auf ProDesk (`--pretend`)
- [ ] Discogs API Token holen und in .env eintragen
- [ ] music_hdd/Inbox säubern (HEIC, .crdownload entfernen)
- [ ] Beets + Navidrome Stack auf ProDesk deployen
- [ ] AzuraCast Mediabibliothek mit Radio_Master verbinden
- [x] ~~Anthropic API Credits aufladen~~ — **überholt:** RAG läuft seit OpenClaw-Relaunch lokal/kostenlos (kein OpenAI/Anthropic-Budget nötig)

## Netzwerk

- [ ] frawo-docker-1 wieder online bringen (WireGuard-Gateway für hs27 LAN) — _bekannt: Egress-Drossel über netcup-VPS, siehe NOW.md_
- [x] ~~LAN-Hosts erreichbar machen: toolbox, nextcloud, odoo, paperless~~ — **erledigt 15.07.:** Anker-LAN-Fix (accept-routes + sshd). Odoo (10.1.0.112) erreichbar. Offen nur: sollen toolbox/nextcloud auf Anker überhaupt laufen? (Wolf-Frage)
- [ ] Thomson TV (IoT) für Radio-Monitoring/Kiosk konfigurieren

## Radio / Musik

- [ ] Erste Kuration via Navidrome Web UI testen
- [ ] AzuraCast Playlist aus kuratierter Radio_Master-Library erstellen
