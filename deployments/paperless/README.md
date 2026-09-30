# Paperless GDrive-Pipeline — Skripte

Quellcode-Spiegel der Skripte, die live auf den Servern laufen. Aenderungen
hier haben keine Wirkung, bis sie auch auf dem Server deployt werden — siehe
Zielpfade unten. Details zum Gesamtablauf: `OPERATIONS/PAPERLESS_OPERATIONS.md`.

| Datei | Server-Zielpfad | Ausgeloest durch |
|---|---|---|
| `frawo-inbox-triage.py` | `stock-pve:/usr/local/bin/frawo-inbox-triage.py` | `frawo-inbox-triage.timer` (taeglich 05:00) |
| `frawo-gdrive-watch-renew.sh` | `stock-pve:/usr/local/bin/frawo-gdrive-watch-renew.sh` | `frawo-gdrive-watch-renew.timer` (alle 6 Tage) |
| `frawo-gdrive-inbox-pull.sh` | `stock-pve:/usr/local/bin/frawo-gdrive-inbox-pull.sh` | `frawo-gdrive-inbox-pull.timer` (alle 4h, Sicherheitsnetz) + vom Webhook direkt aufgerufen |
| `frawo-gdrive-webhook.py` | `stock-pve:/usr/local/bin/frawo-gdrive-webhook.py` | `frawo-gdrive-webhook.service` (Dauerlaeufer, nimmt Google-Push entgegen) |
| `paperless_smart_router.py` | `CT110:/opt/paperless/paperless_smart_router.py` | Paperless `PAPERLESS_POST_CONSUME_SCRIPT` nach jedem eingelesenen Dokument |

## Stand 22.08.2026 (erster Git-Import)

Diese Skripte liefen bis dahin nur auf den Servern, nirgends versioniert.
Beim Nachpruefen mehrere echte Fehler gefunden und auf dem Server bereits
behoben (Server-Version = dieser Stand):

- `frawo-inbox-triage.py`: eine haengende Datei (rclone-Zeitlimit) riss
  bisher den kompletten Lauf mit ab — jetzt pro Datei abgefangen.
- `frawo-gdrive-watch-renew.sh`: schlug beim Booten regelmaessig fehl
  (`OnBootSec=2min` reichte nach einem echten Stromausfall nicht) —
  jetzt mit 5 Wiederholungsversuchen.
- `paperless_smart_router.py`: Dokumente ohne OCR-Text (meist Fotos ohne
  Text, die die Triage faelschlich als "Dokument" einsortiert hatte)
  bekamen einen erfundenen Titel + Odoo-Aufgabe — jetzt nur markiert,
  nicht mehr klassifiziert. Ausserdem schrieb Gemini bei fehlendem Datum
  woertlich "null" in den generierten Titel — Prompt praezisiert +
  Sicherheitsnetz ergaenzt.
- Beide `frawo-gdrive-*`-systemd-Units liefen unter der System-Locale
  `POSIX`/`C` (keine UTF-8-Locale konfiguriert) — Dateien mit Umlauten im
  Namen scheiterten beim Uebertragen nach CT110. Fix: `LC_ALL=C.utf8` in
  den betroffenen `.service`-Dateien gesetzt.

**Keine Zugangsdaten in diesen Dateien** — API-Keys/Tokens kommen zur
Laufzeit aus Umgebungsvariablen (`.env`-Dateien auf den Servern, nicht im
Repo).

## Stand 30.09.2026 (Odoo #1585): keine Muell-Aufgaben mehr

Anlass: Aufgabe #1585 „Unbekannt — github-…-receipt, 0,00 €“. Am 24.09. waren
StudioPC-KI (aus) und Gemini (503) gleichzeitig weg; der Router legte dann mit
Notfallwerten blind eine Aufgabe an und haengte am 27.09. einen fremden
Amazon-Beleg dazu, weil beide „Unbekannt“ hiessen.

- **KI ausgefallen** → keine Aufgabe, keine Buchung, nur Paperless-Schlagwort
  `ki-ausfall-nachholen`. Nachholen per Neulauf (unten).
- **Qualitaetsregel fuer Aufgaben** (`aufgabe_pruefen()`): nur bei echtem
  Handlungsbedarf, bekanntem Absender und konkreter Aktion. Titel = Aktion +
  Absender, erste Zeile = Was · Warum · Bis · Wer, Beleg haengt an.
- **Bezahlte Belege** (auch englisch „payment received / charged to“, Quittungen,
  Amazon) → Eingangsrechnung, keine Aufgabe. Sieht man die Zahlungsquelle und
  ist es ein GbR-Beleg (Entity FraWo, „FraWo“/„Wolfeetech“ im Text) und kein
  GbR-Konto → **Auslage Wolf**: Nummer `Wolf_Einkauf_JJJJ_NN`, gebucht, Zahlung
  im Journal BNK1. Sonst bleibt die Rechnung Entwurf.
- **Fremdwaehrung** → EZB-Referenzkurs am Belegdatum, Originalbetrag im Zeilentext.

Probelauf (schreibt nichts) bzw. Neulauf eines Dokuments, in CT110:

    docker exec -e DOCUMENT_ID=229 -e ROUTER_PROBE=1 paperless-webserver python3 /usr/local/bin/paperless_smart_router.py
    docker exec -e DOCUMENT_ID=229 paperless-webserver python3 /usr/local/bin/paperless_smart_router.py
