# Infrastruktur-Audit 19.08.2026 — Schritt 1: Doku-gegen-Wirklichkeit

Erste Etappe des "Profi-Aufräum"-Vorhabens (siehe Erinnerung
`project_frawo_2026-08-17_serverumzug.md`, Teil 4/5). Geprüft mit
**Lynis** (unabhängiges, etabliertes Prüfwerkzeug), nicht mit
selbstgeschriebenen Skripten — Wolfs berechtigter Einwand, dass eine
Prüfung nicht von derselben Partei kommen sollte, die das System gebaut
hat.

## Härtegrad (Lynis)

| Server | Punktzahl |
|---|---|
| ProDesk (`stock-pve`) | 71/100 |
| Anker (`anker-pve`) | 66/100 |

Voller Bericht auf den Servern selbst: `/var/log/lynis-report.dat`.
Lynis hat beim Installieren automatisch einen eigenen wöchentlichen
Zeitplan (`lynis.timer`) aktiviert — bewusst gelassen, ist ein
sinnvoller Fall für Zeittakt (periodische Sicherheitsprüfung), kein
Anti-Muster wie die anderen heute gefundenen toten Zeittakt-Dienste.

## Wichtigste, echte Funde (Auswahl aus ~50 je Server)

1. **Veraltete/verwundbare Pakete** auf beiden Servern — `apt update &&
   apt upgrade` fällig.
2. **Kein fail2ban** auf dem Anker (automatische Sperre bei
   wiederholten fehlgeschlagenen Anmeldeversuchen fehlt komplett).
3. **Kein Schadsoftware-/Rootkit-Scanner** (rkhunter/chkrootkit) auf
   beiden Servern installiert.
4. **Ungenutzte Firewall-Regeln vorhanden** (`iptables` Regeln ohne
   Treffer) — passt zum wiederkehrenden Muster: Dinge werden
   "entfernt", hinterlassen aber Reste (siehe `musicstick`-Freigabe,
   Backup-Cron-Lücke).
5. SSH-Feinjustierung möglich (Port ändern, TCPKeepAlive/
   AllowAgentForwarding aus, MaxSessions runter) — das Wichtigste
   (nur Schlüssel-Anmeldung, kein Passwort) ist bereits korrekt
   eingerichtet, das sind nur Zusatzhärtungen.
6. Kein Datei-Integritäts-Werkzeug (würde unbemerkte Änderungen an
   wichtigen Dateien erkennen).

## Eigener Vorab-Check (händisches Skript) — mit Vorbehalt

Bevor auf Lynis umgestiegen wurde, gab es einen Versuch mit einem
eigenen Inventar-Skript. Zwei Lehren daraus, bevor es verworfen wurde:

- Ein selbstgeschriebener Check hatte einen echten Fehler (`head -5`
  hat die Firewall-Kette unvollständig abgefragt, hätte fast zu einer
  falschen Schlussfolgerung geführt: "Grundregel ist ACCEPT statt
  DROP" — Proxmox nutzt aber eine eigene Kette (`PVEFW-INPUT`), die
  in der gekürzten Ausgabe nicht mehr auftauchte).
- **Deshalb der Wechsel auf Lynis**: nicht von derselben Partei
  geschrieben, die das System kennt/gebaut hat.

## Behoben (19.08.2026, selber Tag)

- **Paket-Updates:** ProDesk 149 Pakete + Kernel (7.0.14-12-pve), Anker 89
  Pakete + Kernel, beide neu gestartet und vollständig verifiziert
  (Radio-Stream, Odoo, Grafana, alle VMs/Container). Dabei einen
  Grafana-Paketkonflikt gefunden und behoben (`plugins-bundled`-Verzeichnis
  blockierte die Installation, verschoben statt gelöscht).
- **fail2ban:** war auf dem ProDesk schon installiert (nur `jail.local`
  gefehlt), auf dem Anker komplett neu installiert. Beide jetzt mit
  aktivem SSH-Schutz (5 Fehlversuche = 1 Stunde Sperre).
- **Rootkit-Scanner (rkhunter):** auf beiden installiert, Basis-Datenbank
  aufgebaut, erster Lauf durchgeführt. **Keine Rootkits gefunden** auf
  beiden Servern. Zwei harmlose Fehlalarme auf dem Anker (Perl-/Python-
  Skript-Werkzeuge, die absichtlich Skripte statt Programme sind) als
  bekannt-unbedenklich eingetragen.
- **SSH-Konfiguration bereinigt (ProDesk):** eine überflüssige, aber
  wirkungslose `PermitRootLogin yes`-Zeile in der Hauptkonfiguration
  entfernt (wurde durch eine strengere Regel in einer zweiten Datei
  bereits überschrieben — nur lesend, nicht funktional). Effektive
  Einstellung bleibt: nur Schlüssel, kein Passwort.

## nmap-Scan von außen (unabhängige Sicht, 19.08.2026 nachmittags)

Von der StudioPC aus gescannt (nicht vom Server selbst aus).

| Server | Offene Ports | Einordnung |
|---|---|---|
| ProDesk | 22 (SSH), 111+2049 (NFS), 3128 (Proxmox-Konsole, nmap zeigt "squid" — falsch geraten), **8888 (unbekannt!)** | |
| Anker | 22 (SSH), 111 (rpcbind), 3128 (Proxmox-Konsole) | |

✅ Bestätigt: Die Prometheus-Weiterleitungsports (19022/19100/19182) sind
von hier aus **nicht** sichtbar — genau wie dokumentiert.

🔴 **Fund: Port 8888 war ein komplett undokumentierter eigener
Webdienst** (`frawo_radio_daemon.py`) — siehe
`deployments/radio_bridge/README.md` für die volle Geschichte. Kurz:
Fernbedienung fürs Radio-Programm (Upload vom Handy unterwegs), war
gewollt aber kaputt — der Ziel-Ordner zeigte auf den gefälschten,
nicht eingehängten USB-Stick vom Vormittag. Repariert, dokumentiert,
ins Repo aufgenommen.

## Boot-Zeitproblem behoben (ProDesk)

Zwei Netzwerk-Freigaben (`/mnt/radio_rw`, `/mnt/paperless_scans`)
scheiterten nach jedem Neustart, weil der ProDesk sie einzuhängen
versuchte, bevor der Dateiserver-Container (CT120) mit Samba bereit
war — reines Zeitproblem, keine Fehlkonfiguration. Auf
"automatisch beim ersten Zugriff einhängen" umgestellt
(`x-systemd.automount`) statt fest beim Hochfahren — passt zum
Ereignis-statt-Zeittakt-Prinzip von heute. Server zeigt jetzt 0
fehlgeschlagene Dienste.

## Schritt 1: Doku-gegen-Wirklichkeit-Abgleich (19.08.2026 nachmittags)

Systematischer Abgleich von NOW.md gegen den tatsächlichen Zustand
beider Server (frisches Inventar nach allen heutigen Reparaturen).
**Das ist der Abgleich selbst — nicht jeder Fund wurde heute schon
behoben, das ist bewusst getrennt (siehe Prinzip "eine Sache fertig
machen, bevor wir größer denken").**

### Bestätigt korrekt
- Node-Tabelle (IPs, Rollen) — stimmt
- ProDesk CT/VM-Tabelle (IDs, Namen, IPs) — stimmt
- Firewall auf beiden Knoten aktiv (`pve-firewall enabled/running`,
  eigene `PVEFW-INPUT`-Kette) — stimmt, aber auf dem ProDesk nicht bis
  zum Ende durchgeprüft (siehe unten)
- SSH nur Schlüssel, kein Passwort — stimmt (heute schon per
  `sshd -T` verifiziert)
- Backup-Zeitplan (Odoo stündlich, Radio/PBS-Config nachts) — stimmt
- WD-Elements-Seriennummern/Zuordnung — stimmt

### 🔴 Echte Lücken gefunden (NOW.md sagt nichts, obwohl es läuft)

1. **CT121-Beschreibung veraltet:** NOW.md nennt nur "nie produktiv
   geworden", erwähnt nicht die 1133×-Neustartschleife vom 17./18.08.
   und dass die Container seither bewusst gestoppt sind (nicht nur
   "leer").
2. **`frawo_radio_daemon.py` (Port 8888) war komplett undokumentiert**
   — heute gefunden und repariert, siehe oben und
   `deployments/radio_bridge/`.
3. **Anker hat eine eigene, komplett undokumentierte
   Überwachungs-Ecke:** `netdata` (volle Suite, seit 31.05.2026 laut
   Konfig-Datum), `glances` (systemd-Dienst, seit heute Mittag aktiv —
   evtl. von der parallelen Sitzung gestartet), `otel-plugin` gehört zu
   netdata selbst (kein separater Dienst). NOW.md beschreibt im
   Überwachungs-Abschnitt nur die Prometheus/Grafana/Alertmanager-Kette
   auf dem ProDesk, nichts davon. **Geklärt:** der lokale
   `cloudflared`-Tunnel mit Ziel `frawo-tech.de`/`10.4.0.x` ist die
   **alte Domain vor der Umbenennung**, wird 1:1 weitergeleitet,
   Wolf bestätigt harmlos — nicht weiter verfolgt.
4. **Zwei weitere, nirgends erwähnte Netzwerk-Freigaben:**
   `/mnt/wolf-ee` (NFS, Anker → ProDesk) und `/mnt/frawo-library`
   (CIFS-Mount auf dem Anker, zeigt auf dieselbe `//10.1.0.94/radio`-
   Freigabe wie VM210). Zweck unklar, nicht weiter untersucht.
5. **Google-Drive-Speicher auf dem Anker ist zu 70% voll** (3,8 von
   5,4 TB) — kein Alarm dafür in NOW.md/Grafana erwähnt.
6. **Zwei neue Zeitpläne auf dem Anker ohne Dokumentation:**
   `rclone-gdrive-watchdog.timer` (alle ~30 Min.) und
   `pve-root-disk-monitor.timer`.
7. **`sda`/`sdb`-Laufwerksbuchstaben auf dem ProDesk haben sich seit
   dem 01.08. verschoben** (Quarantäne-Aufräumaktion heute hat das
   nochmal gezeigt) — Tabelle in NOW.md nennt `sdc`/`sdd`/`sdb`/`sda`,
   aktuell sind es andere Buchstaben für dieselben Platten. Text warnt
   davor, aber die Tabelle selbst nutzt trotzdem Buchstaben statt nur
   Seriennummern als Referenz.

### ⚠️ Möglicher Konflikt mit einer parallelen Sitzung

Zwischen zwei Inventar-Scans heute (11:47 und 17:34 Uhr) haben sich
mehrere Arbeitsspeicher-Zuteilungen geändert (u. a. CT120 3072→2048,
CT150 6144→2048, CT108 1024→512, CT121 2048→512, VM360-Balloon
6144→3072), **ohne dass wir das veranlasst haben.** Zeitlich passt das
zu dem parallelen Sicherheits-Commit von heute Nachmittag (Wolf hat
bestätigt: gewollte parallele Sitzung). Sieht nach demselben
"RAM-Neuplanung"-Vorhaben aus, das wir uns für Schritt 3 vorgenommen
hatten — **möglicherweise arbeitet die andere Sitzung bereits daran.**
Vor eigenen RAM-Änderungen abklären, damit sich nichts überschneidet.

### Nachträglich geprüft (nach dem ersten Schritt-1-Durchgang)

- **`PVEFW-INPUT`-Kette komplett geprüft:** Grundregel ist wirklich
  DROP, wie dokumentiert (1.932 abgewiesene Pakete, explizite
  Sperrregel am Ende). Bestätigt korrekt.
- **Alopri-Anbindung erneut verifiziert, aber zunächst am falschen
  Ende getestet:** Direkte IP-Pings vom ProDesk zum Elternnetz
  (192.168.178.x) scheitern — das ist aber **erwartungsgemäß**, der
  ProDesk selbst steht gar nicht auf der Freigabeliste in NOW.md (nur
  HA-Eltern, Drucker→Fileserver, Wolfs SSH-Zugang). Der echte,
  vorgesehene Zugangsweg (`home.prinz-stockenweiler.de`, Alopris
  eigene Domain für Home Assistant, von Wolf verwaltet/betreut)
  antwortet mit **HTTP 200** — funktioniert einwandfrei.

### Nicht abschliessend geprüft

- Odoo/Datenbank-Inhalte gegen die "Odoo = Quelle der Wahrheit"-Aussage
- Radio-Sendeplan-Tabelle (Titelzahlen) — mit Sicherheit veraltet nach
  der heutigen Quarantäne-Löschung (1,1 TB) und dem laufenden
  Rekordbox-Projekt, nicht neu gemessen

## Offen für die nächste Runde

- Lynis-Funde priorisiert abarbeiten (fail2ban, Paket-Updates,
  Rootkit-Scanner zuerst).
- **nmap-Scan von außen** (unabhängige Sicht von einem dritten Gerät,
  nicht vom Server selbst aus) — heute noch nicht gemacht, `nmap` war
  auf keinem beteiligten Gerät installiert.
- Rest des Profi-Plans: Infrastruktur-Werkzeug (Ansible) einführen,
  RAM-Neuplanung ProDesk, Onboarding-Doku für einen künftigen IT-Profi.
