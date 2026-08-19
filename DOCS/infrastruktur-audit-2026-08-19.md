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

## Offen für die nächste Runde

- Lynis-Funde priorisiert abarbeiten (fail2ban, Paket-Updates,
  Rootkit-Scanner zuerst).
- **nmap-Scan von außen** (unabhängige Sicht von einem dritten Gerät,
  nicht vom Server selbst aus) — heute noch nicht gemacht, `nmap` war
  auf keinem beteiligten Gerät installiert.
- Rest des Profi-Plans: Infrastruktur-Werkzeug (Ansible) einführen,
  RAM-Neuplanung ProDesk, Onboarding-Doku für einen künftigen IT-Profi.
