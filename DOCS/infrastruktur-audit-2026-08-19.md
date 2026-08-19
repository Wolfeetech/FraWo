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

## Offen für die nächste Runde

- Lynis-Funde priorisiert abarbeiten (fail2ban, Paket-Updates,
  Rootkit-Scanner zuerst).
- **nmap-Scan von außen** (unabhängige Sicht von einem dritten Gerät,
  nicht vom Server selbst aus) — heute noch nicht gemacht, `nmap` war
  auf keinem beteiligten Gerät installiert.
- Rest des Profi-Plans: Infrastruktur-Werkzeug (Ansible) einführen,
  RAM-Neuplanung ProDesk, Onboarding-Doku für einen künftigen IT-Profi.
