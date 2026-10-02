# FraWo prüft Infrastruktur und macht Risiken sichtbar


## FraWo: Grundprüfung deckt konkrete Betriebsrisiken auf

Unabhängiger Review vom 02.10.2026 für Wolf, Odoo-Aufgabe #1863. Die Infrastruktur läuft überwiegend, doch grüne Erreichbarkeitsprüfungen verdecken erhebliche Berechtigungs- und Automatikfehler. Öffentlich erreichbare Abrechnungs- und Radio-Routen haben unzureichende Rechteprüfungen. Die aktive Aufgabenqueue prüft keine Agenten-Sperren; die Belegverarbeitung kann einen falschen Zahler bestimmen. Daneben sind ein Hostbackup und ein Monitoringzugang nachweislich defekt.

Live belegt: drei Online-PVE-Knoten, elf LXC und sechs VMs; 16 Gäste laufen, VM990 ist gestoppt. Der Basisgraph enthält 489 Knoten und 634 Beziehungen, darunter 18 physische Datenträger und 42 Dienstknoten. Die 359 HA-Registerzeilen, 46 physisch benannten Odoo-Wartungseinträge und 32 positiven internen Lagerzeilen sind getrennte Quellen. Sie dürfen nicht zu einer Hardware-Stückzahl addiert werden.

Dieser Bericht prüft Bestand, ausgewählte produktive Quellpfade, Konfigurationsgrenzen, Endpunkte, Sicherungsbelege und frühere Abnahmen. Er bescheinigt keine Vollsicherheit und keine Prüfung jeder einzelnen Einstellung. Das Organisationsdiagramm zeigt alle 17 Gäste; vollständige Hardware-/HA-Register bleiben im PDF-Anhang und im bearbeitbaren HTML erhalten.

Es wurden keine produktiven Code-, Netzwerk-, Finanz- oder Geräteänderungen durchgeführt. Schreibende Exploits, Schalter, Neustarts und Wiederherstellung am Produktivziel wurden nicht ausgeführt. Shelly 10.4.0.11 bleibt ausdrücklich unberührt. Die Korrektur der zu breiten Aufgabenabnahme #1555 durch den Koordinator wird separat dokumentiert.

Evidenz: Recherchedateien code_configs.md, live_inventory.md und odoo_governance.md im gleichnamigen Audit-Quellenverzeichnis; Zielbelege und Quellpfade sind in den folgenden Abschnitten angegeben.

| Ergebnis | Nachgewiesen | Grenze |
| --- | --- | --- |
| Betrieb | 18/18 Blackbox-Probes; 25/26 Scrapes | Erreichbarkeit ist keine Rechte- oder Funktionsabnahme |
| Bestand | 17 Gäste; 359 HA-Zeilen; 46 Wartungszeilen | Überlappungen und Sets bleiben unbereinigt |
| Sicherung | 12/12 TÜV-Prüfungen grün; Odoo-Restoremarker | Kein neuer Restore; Hostbackup defekt |
| Werkzeuge | 369 exponierte Toolnamen; 148 Odoo-Module | Exponiert/installiert bedeutet nicht angemeldet/getestet |


## Die Priorität ergibt sich aus Zugriff und Schaden

P1 bezeichnet vorrangig zu begrenzende Risiken mit direktem Eingriff in Geschäftsdaten oder Sendebetrieb. P2 bezeichnet belastbare Funktions-, Sicherungs- oder Organisationsprobleme. Gemischte Priorität hängt von realer Automatik- und Expositionsreichweite ab. Die folgenden Befunde sind überprüfbar; Abhilfen sind Empfehlungen für separate, gesicherte und gegengeprüfte Umsetzung.

Zuerst F01/F02 technisch eingrenzen, anschließend F03/F04 und den Nachweis von Backup/Monitoring behandeln. Eine pauschale Deaktivierung oder Finanzbereinigung wurde nicht vorgenommen. Cron32 ist ein bestehendes, bereits im Juni vorgesehenes System; die Freigabehistorie ist ungeklärt. Belegt sind fehlende Gates und Konflikte mit dem späteren Protokoll, nicht der unerlaubte Neubau eines Bots.


### F01 | P1 | Öffentliche Verbrauchsabrechnung

Auslöser/Evidenz: Internet-GET ohne Sitzung liefert private Berichtsfassade (200). auth=public, csrf=False; POST mark_billed markiert per sudo alle offenen Verbräuche abgerechnet.
Risiko und Grenze: Forderungen können unberechtigt als erledigt gelten. Schreibender Angriff wurde nicht ausgeführt.
Nächster Nachweis: Interne Gruppe, CSRF, eindeutige Datensatzauswahl; negative Anonym-/Portaltests.
Quelle: addons/frawo_agent/controllers/main.py:504


### F02 | P1 | Radio-Verwaltung ohne Rollenprüfung

Auslöser/Evidenz: /api/radio/playlists anonym 200; skip erlaubt GET+POST auth=none, nutzt serverseitigen AzuraCast-Key. Update/Restart/Preset ebenfalls ohne Rollen-/Token-Gate.
Risiko und Grenze: Fremde können Sendebetrieb und Playlistkonfiguration beeinflussen; Livecode identisch, Mutationen nicht getestet.
Nächster Nachweis: Alle Verwaltungsrouten auf interne Rolle begrenzen; GET-Mutationen entfernen.
Quelle: addons/frawo_agent/controllers/main.py:3466,3556,3837,3874


### F03 | P1/P2 | Cron32 umgeht Organisationsgrenzen

Auslöser/Evidenz: Aktiv alle zwei Minuten, user7, sechs queued Aufgaben; Selektion prüft weder Projekt noch Sperr-Tag. Beschreibungen unter 150 Zeichen werden aus Titel allein ersetzt.
Risiko und Grenze: Faktenverlust und Fremd-/gesperrte Bearbeitung möglich. Kein aktueller Lock-Übergriff nachgewiesen; agent_state=done ist nicht Aufgabenstufe Erledigt.
Nächster Nachweis: Eigentümer-, Projekt- und Lock-Gates; Fakten erhalten; Altgenehmigung mit Jarvis klären.
Quelle: addons/frawo_agent/models/project_task.py:45,56,104


### F04 | P1/P2 | Auslage-Zahler falsch erkannt

Auslöser/Evidenz: Offline-Reproduktion aus echter Funktion: Rechnung an GbR, Ansprechpartner Wolf, bezahlt durch Franz, Karte => Zahler Wolf. Nachgelagert Buchung und Zahlung im AUSW.
Risiko und Grenze: Falsche Gesellschafterverbindlichkeit möglich. Kein produktiver Buchungsversuch und kein pauschales Urteil zu #1585.
Nächster Nachweis: Private Zahlungsquelle belastbar zuordnen; mehrdeutige Belege zur Prüfung.
Quelle: deployments/paperless/paperless_smart_router.py:475,918


### F05 | P2 | OptiPlex-Hostbackup scheitert

Auslöser/Evidenz: Täglicher Dienst 04:35 schlägt fehl: alte PBS-Credentialdatei fehlt nach Migration.
Risiko und Grenze: Hostkonfiguration ist durch diesen Dienst aktuell nicht gesichert.
Nächster Nachweis: Aktuelles Ziel und Secretreferenz prüfen; Sicherung zurücklesen, Fehleralarm belegen.
Quelle: optiplex_health.txt; pbs_live.txt


### F06 | P2 | PVE-Scrape down ohne aktiven Alarm

Auslöser/Evidenz: pve_prodesk HTTP500; Exporterjournal 401 Unauthorized. 25/26 Scrapes up, aktive Alarme leer.
Risiko und Grenze: Ein Überwachungszugang fehlt trotz grüner Rules. Überlappende Anker-Clusterdaten verhindern Aussage vollständigen Metrikausfalls.
Nächster Nachweis: Tokenrechte/Nodezuordnung korrigieren; up/absent-Alarm gezielt auslösen und Rückkehr belegen.
Quelle: prom_targets.json; pve_exporter_error.txt; prom_alerts.json


### F07 | P2 | IoT-Freigabe überdeckt Ollama-Grenze

Auslöser/Evidenz: Frühes ACCEPT für 10.4.0.0/24 und Tailnet 100.64/10; Liveiptables IoT RETURN vor Port11434-Allowlist. Firewalldienst zusätzlich failed.
Risiko und Grenze: PVE-Regeln allein begrenzen IoT-Zugriff nicht wie die spätere Port-Allowlist. UCG-Abfangwirkung ungeprüft.
Nächster Nachweis: Ende-zu-Ende-Pfad prüfen; engere Regelreihenfolge mit Sicherung und Peerreview.
Quelle: network_anker.txt; ollama_firewall_evidence.txt


### F08 | P2 | Tagesbericht rechnet Sommerzeit fest

Auslöser/Evidenz: Fester UTC+2-Offset und naive UTC-Tagesfilter. 02.11.08:00UTC wird 10:00 statt Berlin09:00; 01.11.23:30UTC gehört zum nächsten Berliner Tag.
Risiko und Grenze: Ab Winterzeit 25.10.2026 falsche Dienstplanzeiten und Tageszuordnung. Keine Fristumschreibung durch diese Funktion.
Nächster Nachweis: Europe/Berlin korrekt konvertieren und lokale Tagesgrenzen nach UTC abbilden.
Quelle: scripts/odoo_tagesbericht.py:52-63; Liveaktion828


### F09 | P2 | Portalnutzer erhalten interne Rechte

Auslöser/Evidenz: Summary/Kiosk akzeptieren jeden nichtöffentlichen Nutzer; Taskantwort sudo auf beliebige Task-ID im Namen Wolf.
Risiko und Grenze: Portalaccount könnte interne Daten sehen/ändern. Kein echter Portal-Login getestet.
Nächster Nachweis: Interne Gruppe/Objektrechte je Route; eigene Kioskidentität.
Quelle: addons/frawo_agent/controllers/main.py:759,4015; addons/frawo_agent/controllers/anker_tracker.py:91


### F10 | P2/P3 | Private Peers können Wolf-Login umgehen

Auslöser/Evidenz: is_private akzeptiert gesamtes privates Netz; touch/login setzt session.uid Wolf. ProxyFix/live Nginx geprüft; öffentliche Telemetrie auch mit gefälschten Headers403.
Risiko und Grenze: LAN/VPN-Geräte erhalten potenziell Wolf-Sitzung. Internet-Bypass nicht bewiesen; Login nicht aufgerufen.
Nächster Nachweis: Konkrete Kiosk-Allowlist und eingeschränkter Kiosk-User.
Quelle: addons/frawo_agent/controllers/main.py:44,2229


### F11 | P2 | Belegidentität und Fristen vermischt

Auslöser/Evidenz: Task-Match nur Lieferant/offen/Paperless-Import; Deadline immer ersetzt. Invoice-Dedupe nur Lieferantenpräfix, Datum, Betrag.
Risiko und Grenze: Unterschiedliche gleichteure Rechnungen verschwinden; späterer Beleg überdeckt frühere Frist.
Nächster Nachweis: Dokument-/Rechnungs-ID und Hash verwenden; Mehrdeutigkeit anzeigen; Frist nur begründet ändern.
Quelle: paperless_smart_router.py:676,835


### F12 | P2 | Metadaten und Ingest verlieren Kontinuität

Auslöser/Evidenz: Tag-PATCH ersetzt vorhandene Tags. Scanquelle wird nach staging verschoben, fehlgeschlagener Push später nicht wieder aufgenommen. GDrive move löscht Cloudquelle vor Importverifikation.
Risiko und Grenze: Prüf-/Workflowtags gehen verloren; gestrandete Datei bleibt liegen. Scanproduktion über Stock-Alias nicht verifiziert.
Nächster Nachweis: Tags vereinigen; staging erneut abarbeiten; atomare Übergabe und Zielnachweis.
Quelle: paperless_smart_router.py:207,529,608; frawo-scan-ingest.sh:51; frawo-gdrive-inbox-pull.sh:45


### F13 | P2 | Alarmgruppen und Ollama-ACK unzuverlässig

Auslöser/Evidenz: Dedupe-Key für ganze Gruppe: A und A+B werden neu verarbeitet. Alertregister nach sieben Tagen gelöscht. Ollama wird erst nach ACK in Daemonthread verarbeitet, ohne persistente Queue.
Risiko und Grenze: Doppelverarbeitung und Verlust bei Neustart/Fehler möglich; keine vollständige Rückmeldung.
Nächster Nachweis: Einzelvorfall-Dedupe; Ollama vor ACK dauerhaft speichern; klarer Fehlerabschluss.
Quelle: infra/openclaw/odoo_webhook_handler.py:167,302,572,641,815


### F14 | P2 | Inventar und Sicherungsmarker widersprechen sich

Auslöser/Evidenz: Dokumentation nennt alte Hosts/IDs; Odoo Monitoring CT150 statt live155. Musik/PBS-Cloudmarker 19./20.09. alt, TÜV grün.
Risiko und Grenze: Notfallbedienung/Backupvertrauen kann auf falschem Ziel beruhen. Kein bestätigter Verlust aller Cloudkopien.
Nächster Nachweis: SSOT-Abgleich und Herkunft/Alter der Marker klären; unabhängiges Offsite-Ziel zurücklesen.
Quelle: odoo_catalog.json; backup_prometheus.json; INFRA.md


## Grüne Laufzeitwerte decken nur einen Teil der Funktion ab

frawo-cluster ist online und quorate. Alle elf Container sind unprivilegiert und haben nesting=1; CT110/130/140 zusätzlich keyctl=1. Alle laufenden Gäste starten mit onboot=1. DHCP ist bei den Containern außer CT102 eingerichtet; CT102 hat statisch 10.1.0.53. VM210/241 haben net0 firewall=1; bei den übrigen gelesenen VMs fehlt dieses Flag. Das Flag allein bewertet nicht die gesamten Firewallpfade.

Hostsysteme Anker und ProDesk haben keine failed units; OptiPlex zwei. CT130 hat run-rpc_pipefs.mount failed, CT103 und CT120 sys-kernel-config.mount failed. Eine unprivilegierte Containergrenze als Ursache ist plausibel, wurde aber nicht bewiesen. Die relevanten App-Ports bleiben aktiv. AzuraCast VM220 und PBS VM241 haben keine failed units.

Dockerzustände: Vaultwarden1.37.3, Paperless und Radio-Backend/Postgres/Redis healthy; n8n1.123.76, Tika/Gotenberg/Redis up. CT140 betreibt Nginx, Odoo19, Drawio, Postgres15 und Cloudflared; CT150 OpenClaw. Auf OptiPlex sind OpenWebUI healthy und SearXNG up. AzuraCast/Updater sind healthy. Up ohne Healthcheck beweist nur Laufzeit.

Die 18 bestehenden Blackbox-Probes melden Erfolg. Nicht in deren DNS-Liste enthalten ist CT102/.53; kein direktes OptiPlex-PVE-Blackboxziel gefunden. 65 Prometheusregeln sind auswertbar, 26 Scrapes existieren, 25 sind up. Das bestätigt keine Alarmzustellung. VM210 zeigt 199 unavailable/77 unknown States, VM360 116/47; darunter Integrations- und Altlasten. Daraus folgt keine Zahl defekter physischer Geräte.

Evidenz: cluster_resources.json, cluster_health.txt, anker_guests.txt, prodesk_guests.txt, optiplex_health.txt, radio_live.txt, pbs_live.txt, prom_targets.json, prom_rules.json, probe_success.json, ha210_states_summary.json, ha360_states_summary.json

| Gast / Host | Adresse / Ressourcen | Funktion und Prüfgrenze |
| --- | --- | --- |
| 101 adguard-slave; Anker Lenovo ThinkCentre M720q | 10.1.0.27; 6 vCPU / 0.5GiB RAM / 3.86GiB Root/System | AdGuard DNS53/Web3000; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 102 adguard-optiplex; Dell OptiPlex 7050 | 10.1.0.53; 1 vCPU / 0.5GiB RAM / 3.86GiB Root/System | AdGuard DNS53; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 103 adguard; HP ProDesk 600 G3 DM | 10.1.0.52; 1 vCPU / 0.5GiB RAM / 7.78GiB Root/System | AdGuard DNS53/Web300; AdGuard sync8080; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 106 wireguard; Anker Lenovo ThinkCentre M720q | 10.1.0.239; 1 vCPU / 0.25GiB RAM / 4.84GiB Root/System | WireGuard wg1 UDP44633; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 108 vaultwarden; Anker Lenovo ThinkCentre M720q | 10.1.0.95; 1 vCPU / 0.5GiB RAM / 9.75GiB Root/System | Vaultwarden80/3012; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 110 n8n; Anker Lenovo ThinkCentre M720q | 10.1.0.100; 2 vCPU / 2.0GiB RAM / 29.36GiB Root/System | n8n5678; Paperless8000; Tika9998 internal; Gotenberg3000 internal; Redis6379 internal; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 120 fileserver; HP ProDesk 600 G3 DM | 10.1.0.94; 4 vCPU / 2.0GiB RAM / 31.2GiB Root/System | Samba445/139; Navidrome4533; Musikredaktion8338; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 130 radio-node; Anker Lenovo ThinkCentre M720q | 10.1.0.200; 4 vCPU / 2.0GiB RAM / 62.44GiB Root/System | Radio backend9500/9590; Postgres5432 loopback; Redis6379 loopback; Samba445/139; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 140 frawotech-web; Anker Lenovo ThinkCentre M720q | 10.1.0.112; 4 vCPU / 4.0GiB RAM / 23.46GiB Root/System | Nginx80/8069; Odoo19 internal8069/8072; Drawio8080 internal; Postgres15 internal5432; Cloudflared; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 150 openclaw; Anker Lenovo ThinkCentre M720q | 10.1.0.31; 4 vCPU / 2.0GiB RAM / 15.58GiB Root/System | OpenClaw19000; Odoo webhook19001; Tailnet HTTPS443; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 155 monitoring-stack; Anker Lenovo ThinkCentre M720q | 10.1.0.35; 2 vCPU / 2.0GiB RAM / 9.75GiB Root/System | Prometheus9090; Alertmanager9093/9094; Grafana3000; Blackbox9115; PVE exporter127.0.0.1:9221; Node exporter9100; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 210 haos; Anker Lenovo ThinkCentre M720q | 10.1.0.40; 2 vCPU / 2.0GiB RAM / 32.0GiB Root/System | Home Assistant8123; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 220 azuracast-vm; HP ProDesk 600 G3 DM | 10.1.0.38; 4 vCPU / 3.0GiB RAM / 64.0GiB Root/System | AzuraCast80/443/8000; Listener frontend; Admin frontend; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 241 PBS-FraWo-OptiPlex; Dell OptiPlex 7050 | 10.1.0.8; 4 vCPU / 4.0GiB RAM / 32.0GiB Root/System | PBS8007; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 300 nextcloud; Anker Lenovo ThinkCentre M720q | 10.1.0.21; 2 vCPU / 1.5GiB RAM / 32.0GiB Root/System | Nextcloud80/443; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 360 homeassistant-eltern; HP ProDesk 600 G3 DM | 10.1.0.248; 2 vCPU / 2.0GiB RAM / 42.0GiB Root/System | Home Assistant8123; Config und Laufzeit gelesen; keine vollständige App-Abnahme |
| 990 surface-test; Dell OptiPlex 7050 | ; 2 vCPU / 6.0GiB RAM / 32.0GiB Root/System | ; gestoppt; keine Laufzeitprüfung |


## Sicherung braucht ein unabhängiges Ziel und Wiederherstellungsbelege

Der Nachtjob pbs-alle-nachts sichert um 01:00 alle produktiven Gäste auf PBS und schließt VM241/PBS selbst sowie VM990/Test aus. CT102/103/120 sind enthalten. Cloudgruppen: Montag VM300/CT150/155/101/106, Mittwoch CT130/VM210/CT108, Freitag CT140/110, jeweils04:00. ProDesk lokal sichert Sonntag03:00 VM360/220 nach hdd-backup, Cloudupload über separaten Dienst. Eine eigene Cloud-Gastgruppe für CT102/103/120 ist nicht belegt.

PBS läuft als VM241 auf OptiPlex, 10.1.0.8, Web8007. Die 32GB-System- und 750GB-Datenplatte liegen trotz virtueller Trennung auf derselben Crucial2TB-NVMe. Ein physischer Ausfall trifft beide. Root ist17% und Datastore15% belegt; etwa597GiB frei. Datastorefrawo GC06:30; Contentliste wurde zurückgelesen. Der Audit führte keinen Restore-in-place aus.

Anker-backup ist ZFS ONLINE mit zwei WD2TB-USB-Platten im Mirror; READ/WRITE/CKSUM0 und Scrub01.10. ohne Fehler. Ein lokales Mirror schützt vor Einzelplattenausfall, belegt aber kein räumlich unabhängiges Offsiteziel. Der Cluster enthält keine HA-Ressourcen: Quorum ist kein automatisches Dienstfailover. Ein Anker-Ausfall trifft Odoo, Vault, OpenClaw, Monitoring und HA-Rothkreuz zusammen.

Zwölf Backup-TÜV-Prüfungen sind grün, letzte Läufe02.10.08:03:22/08:00:37CEST. Odoo-Offsite ist erfolgreich mit186.893.283Bytes, letzter Erfolg02.10.07:40:33CEST. Odoo-Restore-Testmarker vom27.09.09:03:33CEST ist grün; das ist ein vorhandener Automatikbeleg, kein neu durchgeführter Audit-Restore.

Dem stehen das konkret defekte OptiPlex-Hostbackup sowie alte Einzelmarker gegenüber: Musik-Cloud19.09.03:35:48CEST mit bytes0, PBS-Konfig20.09.03:45:45CEST trotz ok1. Herkunft und Bezug zu alten Skripten oder früherem PBS müssen geklärt werden. Der Widerspruch ist eine Diagnoseaufgabe, kein Beweis, dass sämtliche Cloudkopien verloren sind.

Evidenz: cluster_health.txt, pbs_live.txt, pbs_snapshots.txt, backup_prometheus.json; C:/Users/StudioPC/FraWo/NOW.md


## Endpunkte haben unterschiedliche Schutzgrenzen

Anonyme Internet-GETs wurden ohne Sitzung und ohne Mutation geprüft. Der angepasste Audit-User-Agent erhielt bei Settlement200HTML und Playlists200JSON. Zusammenfassung401, Telemetrie403; Cockpit303 und Radio/Admin/Status303 leiteten zur Anmeldung, Draw/Templates302 ebenfalls. Das ursprüngliche200 bei Cockpit/Status entstand durch automatisches Folgen des Redirects und wurde korrigiert. Cloudflare403 für den Standard-Python-User-Agent ist keine belastbare Rechteprüfung.

Positiv: Draw.io prüft über auth_request einen internen Odoo-Nutzer; Upload/Curate verlangen intern plus Origin/Referer-Prüfung, Delete JSON. Radio-Redaktionsurteil prüft group_radio_redaktion; Export verlangt konfigurierten Summarytoken. Beim Webhook fehlen Pflichtwerte nicht stillschweigend: Start scheitert geschlossen. Agent/Chatter werden vor ACK in SQLite WAL/FULL persistiert, Fehler liefert503; ausgelieferte Message-IDs bleiben dauerhaft registriert. Diese Garantien gelten nicht gleichwertig für den Ollama-Zweig.

Paperless erzeugt bei vollständigem LLM-Ausfall weder Aufgabe noch Rechnung und markiert Nacharbeit. Auslagenzahlung liest nach jeder Stufe Status erneut; JournalAUSW statt BNK1 entspricht der vorgesehenen Gesellschafterlogik. Die Zahlererkennung und Tagbehandlung bleiben dennoch fehlerhaft. 14 bestehende Radio-Unittests bestanden offline mit gemockten externen Schreibvorgängen; synthetische Queue- und Zahlertests reproduzierten die Befunde ohne Produktivschreiben.

Evidenz: code_configs.md; C:/Users/StudioPC/FraWo/addons/frawo_agent/controllers/main.py; radio_votes.py; infra/openclaw/odoo_webhook_handler.py; deployments/paperless/paperless_smart_router.py

| Endpunkt/Gruppe | Ergebnis | Nicht geprüft |
| --- | --- | --- |
| /anker/report/settlement | anonym200; auth=public; csrf=False | mark_billed POST nicht ausgeführt |
| /api/radio/playlists; skip/update/restart/preset | Lesen anonym200; Mutatoren im identischen Livecode ohne Rollengate | Keine Radio-Mutation |
| Summary / Telemetrie | anonym401 / 403; Header-Spoof Telemetrie403 | Echte Portal- und private Peer-Sitzung |
| Cockpit / Radioadmin / Drawtemplates | 303/303/302 zur Anmeldung | Vollständiger angemeldeter Workflow |
| Kiosk / Taskantwort / Touchlogin | Quellcode-Rollengrenzen unzureichend | Kein Passwortloslogin, keine Aufgabe beantwortet |
| 42 Dienstknoten im Organisationsdiagramm | Ports/Rollen inventarisiert | Nicht jede API-Methode oder jede App-Einstellung |


## Odoo-Abnahme und Regeln müssen dem tatsächlichen Umfang folgen

Odoo19 enthält148 installierte Module,47 Crons davon28 aktiv und21 Automationsregeln davon12 aktiv. Kein aktiver Cron hat failure_count>0. Installed/active/failure0 sind Katalog- und Laufzeitangaben; sie bestätigen weder externe Anmeldung noch korrektes Ergebnis. Der MCP-Katalog erlaubt49 Modelle; write/create sind breit, unlink für Aufgaben/Projekte erlaubt, für Finanzen/Produkte nicht. ir.cron ist dort nicht freigegeben; SQL wurde ausschließlich gelesen.

Die1173 aktiven Aufgaben wurden aggregiert geprüft, keine Generalabnahme jeder Aufgabe durchgeführt. FraWo-WIP11 überschreitet die dokumentierte Grenze6. Die MCP-Seite ist trotz hoher Limitangabe auf100 begrenzt; die358 offenen Gesamttreffer wurden nicht mit einer100er-Partialliste verwechselt. SQL belegt keine offenen Mehrfach-Agentenlocks, keine unzugeordneten Projektstufen aktiver projektgebundener Aufgaben und keine aktuell queued Aufgabe mit Lock. Sechs stufenlose Willkommensaufgaben sind ohne Projekt, kein bewiesener verlorener Geschäftsvorgang.

#1555: Off-Timernachbesserung mit80s-Test und wiederhergestellten Einstellungen technisch belegt. Der vollständige Auftrag verlangt zusätzlich beide Heizungsbuttons und ARD/ZDF von den Eltern bedienbar. Dafür fehlt eine Eltern-UI-Probe. Die frühere Elternabschlussmeldung war zu weitgehend; der Koordinator hat die Aufgabe mit Nachricht22452 wieder auf InArbeit/Stufe3 gesetzt. Off bedeutet fünf Wohnthermostate12-15°C/Eco und Hausgangsummeroff. Die Aufgabe erlaubt Absenkung/Off; allein daraus folgt kein Funktionalverstoß.

#1557: Technische Freigabe durch Jarvis21664 umfasst Rollbackfehlfall, Sicherung, Live=Repo und Cron44. Automatik4 ist false; es gibt0 aktive Blocker-prüfen-Aktivitäten. Die54 historischen inaktiven/nullaktiven Zeilen sind keine54 offenen Meldungen. Die technische Abnahme bleibt gültig; der gesonderte Zeitfehler F08 wird dadurch nicht entkräftet.

#1585: Der negative Review21663 liegt vor der späteren Betreiberentscheidung21684 vom30.09.17:11UTC. Dort ist Wolfs Freigabe zur Bereinigung und ausdrückliches Beibehalten_05/_06 berichtet. Deshalb werden diese Vorgänge nicht pauschal als ungenehmigt bezeichnet und nichts finanziell geändert. Die Belegqualität des0,95Euro-PIN-Briefs bleibt ein eigener fachlicher Restpunkt;_05/_06 sind posted/paid residual0. _01 ist inzwischen ebenfalls paid/residual0 gegenüber früherem Teilbetrag; Ursache des späteren Ausgleichs nicht geprüft.

Die fünf geprüften Benutzer sind aktiv und haben im abgefragten Feld kein TOTP-Secret; vorgelagerte MFA wurde nicht bewertet. OAuth, Stripe/IAP, Mailversand und Kalender-Ende-zu-Ende wurden nicht ausgelöst. Offene fremdgesperrte Übergaben wurden gelesen und nicht übernommen.

Evidenz: odoo_governance.md; odoo_catalog.json; modelcatalog.json; Odoo #1555/#1557/#1585; AGENTS.md


## Die Coverage-Matrix zeigt geprüfte und offene Einstellungen

Geprüft bedeutet hier die konkret genannte Methode, nicht umfassende Abnahme des ganzen Produkts. Alle benannten Gäste sind vollständig in der Ressourcen-/Hostliste enthalten; die Tiefe der Applikationsprüfung variiert. Das Wort alle bezieht sich auf die erhobenen Register und Kataloge. Unbekannte, nicht dokumentierte oder ausgeschaltete Hardware kann diese Fernprüfung nicht beweisen.

Die Repositorybasis main wurde vor der Arbeit aktualisiert. Kernpfade wurden gegen produktive SHA256-Werte verglichen. Eine zwischenzeitliche extern verursachte lokale Nginxänderung wurde erhalten; später war main wieder sauber (10:13:52CEST). Daraus wird kein Deployment der fremden Änderung abgeleitet. Eine separate Zeitkontrolle um10:12-10:13CEST zeigt keinen materiellen Minutenversatz; PostgreSQL ist Etc/UTC. Die feste Sommerzeit im Berichtscode ist ein davon unabhängiger Fehler.

Evidenz: code_configs.md; live_inventory.md; odoo_governance.md; timestamp_check.md

| Bereich | Erhobener Umfang | Offen / nicht getestet |
| --- | --- | --- |
| 3 PVE / Cluster | live Config, Quorum, Ressourcen, Units, Speicher | Hostupdates/CVE, Hardwarebelastung, Failovertest |
| 11 LXC / 6 VMs | alle Ressourcen/configs gelesen; 16 Laufzeiten | Nicht jede Gast-App-Einstellung; VM990 gestoppt |
| Netz / WireGuard | Interfaces, Routen, Bridge-VLANs, PVE-Regeln; wg1 aktiv | UCG/AP-Firmware, DHCP-Pools, Kabel, echte Segmenttests |
| Odoo main Controller | tiefe Auth/sudo/Routenprüfung, LiveSHA identisch | Nicht jede Controller-Methode/pentested Sitzung |
| Odoo Taskqueue | Code tief + SHA + aktiver Cron32/Queuebestand | Genehmigungshistorie und vergangene Queuewirkungen |
| Nginx / Proxy | live nginx -T und Header, initial SHA identisch | Zwischenzeitliche fremde lokale Änderung; keine Deploymentbehauptung |
| Webhook / OpenClaw | Queue/Dedupe/ACK/auth/expiry/Ollama tief, LiveSHA | Telegram/Agent-Ende-zu-Ende und Neustartausfalltest |
| Paperless Router | Klassifizierung, Invoice/Task-Dedupe, payment, tags tief; SHA | Keine produktive Buchung oder vollständige Belegprüfung |
| GDrive-/Scan-Ingest | GDrive source/liveSHA; Scanquellcode gelesen | Scanproduktion Stock-Alias timeout; kein Dateiingest ausgelöst |
| Radio votes / tracker / ACL | Rollen/sudo gelesen,14 Offline-Tests | Kein echter Portalnutzer, kein Radioschreibtest |
| radio_bridge | Token/path/upload Quellcode | Stock-Ziel/SHA nicht erreichbar; leerer Tokenstart nicht failclosed |
| Monitoring | 26 Targets,18 Probeergebnisse,65 Rules, Alerts, Journal | Kein neuer Alarm-/Zustelltest; Metriküberlappung ungeklärt |
| Sicherungen | 5 Jobs, PBS-Liste, ZFS, TÜV/Odoo-Marker gelesen | Kein neuer Offsite-Download/Restore; alle Datenpfade nicht zertifiziert |
| HA210 / HA360 | 359 Registryzeilen, States/Entitäten, benannte Automationbelege | Kein Schalten; Saison/Urlaub/All-off nicht vollständig getestet |
| Physische Hardware | 4 Rechner live,18 Datenträger, dokumentiertes Netz/mobile | Keine Vor-Ort-Stückinventur, kein Serienscan aller Geräte |
| Wartung / Lager / Waren | 46 aktive physische Namen;32 positive interne Quants;176 Waren | Sets/Duplikate/physische Lagerexistenz nicht bereinigt |
| Odoo Module / Crons / Automationen | 148 /47 /21 vollständige Kataloge; ausgewählte Aktionslogik | Nicht alle Serveraktionen vollständig semantisch geprüft |
| Aufgaben / Abnahmen | Aggregationen/Locks/Stufen; #1555/#1557/#1585 fokussiert | Keine Einzelabnahme aller1173 Aufgaben |
| Benutzer / MFA / MCP | 5 active/TOTP-boolean;49 erlaubte Modelle | Cloudflare/VPN MFA, alle ACLkombinationen nicht getestet |
| Tools / Connectoren | 369 Metadatanamen, alle Provider; lokale Toolversionen | Anmeldung/Scopes/Verbindung nicht generell bestätigt |
| Windows / StudioPC | CIM CPU/RAM/Disk/GPU und Python/Git/SSH Versionen | Windowsfirewall/Updates/EDR/Treiber/GPO/USB echte Kapazität |
| Surface / Mobil | Dokumentierte Zuordnung und HA/Registereinträge | Firmware/OS/MDM/Backup/echte Geräteidentität |
| Repo Apps / Ansible / Infra | Verzeichnisse/Quellen inventarisiert; Kernpfade tief | Nicht alle Apps als deployed zugeordnet oder voll reviewed |
| Secrets / Zertifikate | Keine Werte kopiert; dokumentierter Altrotationsbedarf | Keine vollständige Secrethistorie, Rotation oder TLSzertifikatsaudit |
| Externe Dienste / Finanzen | Kataloge und ausgewählte Chatter-/Buchungsstände | OAuth,Stripe,IAP,Mailversand, vollständige Buchhaltung |
| Zeit / Zeitzonen | StudioPC/3PVE/CT140/Odoo/DB im gleichen UTCFenster | Subsekundenoffset nicht quantifiziert; DSTBerichtscode fehlerhaft |


## Das Hardwarediagramm erhält Quellen statt falscher Stückzahlen

Das Diagramm beginnt mit Standorten, ordnet echte Hosts und Netzwerkhardware zu und zeigt darunter virtuelle Gäste mit Diensten/Endpunkten. Ein Dienst, eine Integration oder ein HA-Kanal wird nie als physisches Gerät dargestellt. Rothkreuz22 enthält die drei verifizierten PVE-Hosts und StudioPC; Stockenweiler3 enthält dokumentierte FRITZ-Hardware. Mobile Geräte und Einträge ohne belastbare Ortszuordnung haben eine eigene unbekannte/mobile Gruppe.

Anker: Lenovo ThinkCentreM720q/i5-8500T6C6T/16GiB, Samsung256GB-NVMe sowie zwei WD2TB-USB-Mirrorplatten und zwei kleine USBmedien. ProDesk: live HP600G3DM/i7-7700T4C8T/16GiB, Samsung256GB-NVMe, WD1TBfamily/backup, WD2TBmusic, zwei USBmedien. OptiPlex7050/i5-7500T4C4T/16GiB, Crucial2TB-NVMe und fünf USBgeräte. StudioPC HyricanPROH610M-E/i7-14700F20C28T/32GiB/RTX4060, Kingston1TB und VendorCoUSB mit gemeldeten1,05TB. Diese USBgröße ist nicht geprüft; die dokumentierte FakeUSB-Geschichte ist damit nicht identisch belegt. Win32AdapterRAM4GB ist kein belastbarer RTXVRAMbeleg;8GiB sind dokumentiert.

Die359 HA-Zeilen bleiben einzeln sichtbar:115 ausVM210 und244 ausVM360. Heuristisch79 physische Kandidaten,183 Software/virtuell,50 Kinder/Kanäle und47 ungeklärt. 51MAC-Gruppen enthalten mehrere Registerrecords, auch aus zwei Integrationen oder HAs. Es wird keine automatische physische Deduplizierung vorgenommen. HA-Eltern läuft auf dem Rothkreuz-ProDesk; die VMHostposition beweist nicht den Standort jedes verwalteten Geräts.

Die46 aktiven physisch benannten Wartungseinträge enthalten auch Paare, Sets und Kabelplatzhalter. Das separate Lagerregister zeigt32 positive interne Quants für31 Produkte mit numerischer Mengenaddition39; unterschiedliche Einheiten und Sets verhindern einen Hardware-Stückbeweis. Vier Serienlotzeilen sind im Quantsbestand sichtbar. Der komplette176er-Warenkatalog bleibt im JSON/HTML; ein Katalogprodukt ohne realen Bestandsnachweis wird nicht als installiertes Gerät eingezeichnet.

Dokumentiert sind zusätzlich SurfaceGo, Wolf-/Franz-SurfaceLaptop, Franz-iPhone, AsusZenbook, Pi4, zwei Pi3, DellPowerEdge, TPLink5Port, DJImini4Pro, FiatDucato, Anhänger und Event-/Werkstatttechnik. USV, Rack und zusätzlicher PoESwitch erscheinen nur als Kaufkonzept, nicht als installierte Hardware. Ein Märzmanifest Stockenweiler mit Server.25, Drucker.153, MagentaTV.120 und HA.67 ist planned/legacy und wird nicht live bestätigt.

Evidenz: Inventar-2026-10-02.json; Hardware-Organisationsdiagramm-2026-10-02.pdf/.html; inventory.json; hardware_notes.json; quant.json; INFRA.md; DOCS/ADRESSPLAN.md

| Bestandsquelle | Zeilen / Status | Verwendung |
| --- | --- | --- |
| Livegraph | 489 Knoten /634 Beziehungen | Basisstruktur, 17 Gäste,42 Dienste,18 Datenträger |
| HA Registry | 359 Einzelrecords /51 MACgruppen | Alle Einzelrecords mit Klasse und Hersteller/Modell |
| Odoo Wartung | 46 aktive physisch benannte Zeilen | Separate dokumentierte Registergruppe; keine Dublettenlöschung |
| Interne Lagerquants | 32 positive Zeilen /31 Produkte | Separate Bestandsgruppe mit Menge/Ort/Lot |
| Warenkatalog | 176 Produkte | Katalog im HTML/JSON; nicht als tatsächliche Stücke gezählt |


## Werkzeuge sind verfügbar, externe Anmeldung bleibt gesondert

Der Metadaten-Snapshot zählt369 verschachtelt exponierte Toolnamen. mcp__codex_apps hat299, CodexApp42, Odoo11, NodeREPL3 und CodeReview1; dazu13 Basistools. Die direkt verfügbaren cua_repl-, collaboration- und clock-Namensräume sind separat und nicht in diese verschachtelte369er-Summe eingerechnet. Ein exponierter Name garantiert weder Connectorlogin noch erlaubten Scope oder erfolgreiche Kernfunktion.

Die299 App-Toolnamen verteilen sich nach Namenspräfix auf Canva40, Codex3, GitHub89, Gmail21, Google60, Hotline1, Pets11, Plugin6, Safety5, Sites25 und Slack38. Das ist eine Funktionsmetadatensicht, keine Liste aller physisch installierten Programme. Alle tatsächlichen Namen sind im selbständigen HTML und JSON erhalten. Externe Konten wurden nicht testweise angeschrieben oder verändert.

Lokal durch Versionsausgabe geprüft: Python3.13.7, Git2.50.1.windows.1, OpenSSH_for_Windows9.5p2/LibreSSL3.8.2. Paketweite CVE-, Patch- und Lizenzprüfung sowie alle IDE-/Browser-/Windowssettings sind offen. Die Connectorliste und installierten Odoo-Module werden deshalb nicht als gesund oder authentifiziert etikettiert.

Evidenz: tool_inventory.json; odoo_catalog.json

| Exponierter Provider | Anzahl | Nachweis / Grenze |
| --- | --- | --- |
| apply | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| clock | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| create | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| exec | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| get | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| image_gen | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| list | 2 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| mcp__code_review | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| mcp__codex_app | 42 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| mcp__codex_apps | 299 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| mcp__node_repl | 3 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| mcp__odoo | 11 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| read | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| update | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| view | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| web | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |
| write | 1 | Metadaten verfügbar; allgemeine Auth/Funktion nicht verifiziert |


## Die nächste Umsetzung braucht gezielte Abnahmen

Die unmittelbare Arbeitsfolge folgt dem möglichen Schaden: öffentliche Abrechnungs-/Radiomutationen begrenzen; Queue und Zahlerlogik korrigieren; Backup-/Monitoringnachweise wieder herstellen; danach Zeitumstellung, Portal-/Kioskrollen, Belegidentität, Ingest und SSOT bereinigen. Jeder Fix benötigt einen klaren negativen Test und einen Ergebnisnachweis am Ziel. Ein200, Exit0 oder grüner Container ersetzt diese Abnahme nicht.

Vor produktiven Änderungen gelten datierte Sicherung, Abgleich Server/Repo, kleiner überprüfbarer Umfang und Review durch einen anderen Agenten. Sperren und Fremdprojekte bleiben unangetastet; keine neuen Pollingjobs oder Webhooks aus diesem Review. Finanzentscheidungen werden nicht aus technischen Heuristiken rückgängig gemacht. Hardwarebereinigung soll Datensätze über stabile Identität verknüpfen, nicht verdächtige Dubletten blind löschen.

Das Hardwarebild ist jetzt nachvollziehbar von Standort über Host und Gast bis zum Dienst, während Wartung, Lager und HA ihre eigene Belegqualität behalten. Für belastbare Geschäftsfortführung fehlt vor allem der nachgewiesene Weg vom unabhängigen Sicherungsziel zurück zum funktionierenden Dienst. Genau dieser Nachweis hat höheren Wert als weitere pauschale Grünmeldungen.

Evidenz: AGENTS.md; DOCS/SICHERHEITSSTANDARDS.md; Befunde F01-F14


## Quellen und vollständige Originalkataloge bleiben prüfbar

Der Review basiert auf drei kuratierten Notizdateien und deren sicheren Inventardaten, nicht auf weitergereichten Klartextkonfigurationen. Private Berichtsinhalte, APIkeys, Passwörter, Tokens und potenziell geheime Aufgabentitel wurden nicht in die Lieferung kopiert. Aufgabentitel aus allgemeinen Tasklisten werden nicht exportiert.

Im HTML/JSON stehen die vollständigen Toolnamen,148 Modulnamen mit Version,47 Crons mit Aktivität/Intervall/Zeitfeldern und21 Automationsregeln mit Aktivität/Trigger/Modell. Keine Serveraction-Codeblöcke werden exportiert. Der Diagramm-PDF-Anhang enthält jede der359 HA-Zeilen sowie die getrennten46 Wartungs- und32 Lagerzeilen. Das HTML ist offline, ohne Assets oder Netzwerkabrufe; sein JSON kann bearbeitet und neu angewendet/exportiert werden.

Evidenz: Kuratiert: work/research_notes/FraWo Prüfung von Grund auf/{code_configs.md,live_inventory.md,odoo_governance.md,timestamp_check.md,inventory.json,hardware_notes.json,odoo_catalog.json,tool_inventory.json,quant.json,locations.json,products_complete.json}

| Datei / Ziel | SHA256 / Nachweis |
| --- | --- |
| CT140 main.py | 130ac3b0a7584730ca5029e9fae6978ce406d108213bd1d321357186f814b5eb |
| CT140 project_task.py | 8969740f1e8db5ad653085a2a99ee6ed44a7663a0dd1e23b9452613dddaf084d |
| CT150 odoo_webhook_handler.py | fc14c0728b68a700ba0642ec4f29148b3decd2595961592ebe7cdbe15b62c57a |
| CT110 paperless_smart_router.py | b18ed3b6484fe9845c390de4f666229dcaafca6de88f2d7dd72e73c7a62e491a |
| Anker GDrive-Ingest | 6f892d59cac06264bb4f000b165b1fc694b94bd85e48f0cbc766711e1cff7438 |
| CT140 nginx initial | 14251fc40f2719ccbb4fb7eb95ead188bcf67c94c0558cfa6b53480bd7b310e8; spätere lokale Änderung separat |
