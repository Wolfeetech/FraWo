# Technischer Stack – Status und nächste Umsetzung

**Stand:** 10.10.2026, 20:25 CEST  
**Prüfung:** read-only, keine Neustarts, keine Konfigurations- oder Netzwerkänderungen.

## Ergebnis in einem Satz

Der FraWo-Kernstack läuft aktuell auf allen drei Proxmox-Knoten quorate und die öffentlichen Kernwege antworten; der größte offene Betriebsblock ist nicht ein fehlender Dienst, sondern die noch nicht bestandene Stabilitäts-/Backup-Abnahme und die daraus folgende Netz-/Ausfallsicherheitskette.

## Live-Landkarte

| Bereich | Live-Stand | Nachweis |
|---|---|---|
| Proxmox-Verbund | 3/3 Knoten online, Quorum vorhanden | `pvesh /cluster/status` auf Anker und ProDesk |
| Anker 10.1.0.92 | uptime 5 Tage 6:35 h, Load 0,64/0,79/0,83 | `uptime`, `qm/pct list` |
| ProDesk 10.1.0.128 | uptime 5 Tage 6:41 h, Load 0,80/1,36/1,38 | `uptime`, `qm/pct list` |
| OptiPlex 10.1.0.227 | uptime 5 Tage 6:59 h, Load 0,21/0,24/0,29 | `uptime`, `qm/pct list` |
| Odoo/Website CT140 | Odoo-Prozesse, Nginx, Cloudflare-Tunnel und Datenbankprozesse vorhanden | Prozessliste + öffentliche GETs |
| Monitoring CT155 | Prometheus, Alertmanager, Grafana, Blackbox- und Node-Exporter aktiv | `systemctl`, Ports 9090/9093/3000/9115, lokale Readiness-GETs HTTP 200 |
| Radio VM220 | VM läuft auf ProDesk | `qm list`; öffentliche Now-Playing-API HTTP 200 |
| Fileserver CT120 | Container läuft auf ProDesk | `pct list` |
| Nextcloud VM300 | VM läuft auf OptiPlex | `qm list` |
| Paperless/n8n CT110 | Container läuft auf OptiPlex | `pct list` |
| Hermes CT160 | Container läuft auf OptiPlex | `pct list` |
| Home Assistant VM210 | VM läuft auf Anker; `home.frawo.tech` HTTP 200 | `qm list`, öffentlicher GET |
| Backup/PBS VM241 | VM läuft auf OptiPlex | `qm list` |

## Öffentliche Nutzerwege

- `https://frawo.tech/` → HTTP 200
- `https://frawo.tech/verleih` → HTTP 200
- `https://frawo.tech/kontakt` → HTTP 200
- `https://funk.frawo.tech/api/nowplaying/1` → HTTP 200
- `https://home.frawo.tech` → HTTP 200
- Der öffentliche AzuraCast-Status-Endpunkt antwortete bei diesem direkten Probeaufruf mit HTTP 403; die Now-Playing-API und die vorherige Streamprüfung sind davon getrennt. Das ist als Auth-/WAF-Prüfpunkt offen, nicht als Radioausfall gewertet.

## Odoo-Konsolidierung

### Aktive Umsetzung – zwei Zeilen

1. **#1929 Radio-/Cloud-Musik** – laufender rclone-Transfer; Prozess `proc_3d0b5e872c08` ist weiterhin aktiv. Professionelle Musikabnahme bleibt nachgelagert und offen.
2. **#1644 Website-Kundenreview** – konkrete Live-Korrekturen, zuletzt Kundenportal-Wortlaut ehrlich gemacht; Commit `9c8d187`.

### Stabiler Betrieb – eine saubere Elternkette

- **#1510 Cluster stabilisieren** – Elternaufgabe, 9 Schritte abgeschlossen bzw. in der Kette.
- **#1519 Sieben Tage Stabilität** – aktuell `Als Nächstes`, Codex-Sperre entfernt; Gate ist nach dem Read-only-Prüfstand vom 10.10. nicht bestanden.
- **#1520 Ausfallsicherheit entscheiden** – Backlog, sinnvoll erst nach dem Stabilitäts-Gate.

### Netzbetrieb – eigene Folgezeile

- **#1523 Netz professionell betreibbar machen** – `Als Nächstes`.
- M1, M2 und M7 sind blockiert; M4–M6 liegen im Backlog. Keine neue Netzänderung ohne klare Abhängigkeit, Backup und Review.

### Zurücksortiert

Meta-/Dachvorhaben und nicht laufende Vorbereitungen stehen nicht mehr fälschlich in `In Arbeit`: #1090, #1263, #1927, #1930, #1966 sowie #1519 stehen in `Als Nächstes`.

## Was wirklich noch umgesetzt werden muss

### 1. Stabilitäts-Gate #1519 abschließen

- 7-Tage-Fenster ohne ungeklärte Verbundverluste nachweisen.
- Backup-TÜV vollständig und aktuell belegen; aktueller Prüfstand hatte alte Gäste-Sicherungen und `gaeste_cloud` wegen Rate-Limit offen.
- Danach erst die Freigabe für Netz-/Ausfallsicherheitsarbeiten erteilen.

### 2. Netzvorhaben #1523 in der richtigen Reihenfolge

- M1: verbindlicher Adressplan gegen Live-Zustand.
- M2: zweiter Alarmweg ohne Hausinternet.
- M4: kontrollierter Neustarttest.
- M5: Messung nach jeder Änderung.
- M6: Dokumentation auf Wirklichkeit bringen.
- M7: verständliche Alarmtexte.

### 3. Sicherheitsbefund aus der Read-only-Prüfung

In der laufenden Odoo-Prozessliste war ein Datenbank-Zugangswert als Kommandozeilenargument sichtbar. Der Wert wurde nicht übernommen oder dokumentiert. Das ist ein konkreter Kandidat für #1523/M1 bzw. einen separaten Security-Fix: künftig keine Secrets in Prozessargumenten, sondern sichere Environment-/Secret-Datei mit passender Berechtigung. **Nicht in diesem Audit geändert.**

### 4. Dokumentationsabgleich

`INFRA.md` beschreibt die wesentlichen Live-Komponenten noch brauchbar, ist aber an mehreren Stellen zeitbezogen (Stand 14.09.) und muss nach dem Stabilitäts-Gate mit den aktuellen Host-/Gastrollen, Monitoringpfaden und Radio-/Cloud-Zuständen einmal gegen die Live-Ausgabe aktualisiert werden. Dafür keine zweite Landkarte anlegen: diese Datei bleibt die Quelle.

## Priorität für den nächsten großen sichtbaren Schritt

Nicht noch eine weitere Website-Kleinigkeit, sondern die technische Kette als überprüfbares Paket: **#1519 stabilitätsfest machen → danach #1523 mit M1/M2/M4–M7 als sauberer Teilaufgabenfolge abarbeiten.** Der Cloud-Musiklauf bleibt parallel unangetastet aktiv.
