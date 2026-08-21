# Paperless Operations

> Ersetzt die Fassung vom 08.04.2026 (verwies auf das alte Nextcloud-System
> auf Flos inzwischen abgeschaltetem Server `frawo-docker-1` — das gibt es
> nicht mehr). Neu geschrieben am 21.08.2026.

## Zweck

Paperless ist das Dokumentenarchiv mit OCR, KI-Auswertung und
automatischer Ablage. Eingang ist Google Drive, Ablage erfolgt zurück
in die bestehende Drive-Ordnerstruktur, zusätzlich durchsuchbar in
Paperless selbst. Für jedes Dokument mit Handlungsbedarf entsteht eine
Odoo-Aufgabe bei der zuständigen Person.

## Die eine echte Instanz

- **CT110** (ProDesk/stockenweiler-pve), Docker `paperless-webserver` +
  `paperless-broker`. Erreichbar intern `http://10.1.0.100:8000`,
  extern **`https://paperless.frawo.tech`** (Cloudflare-Tunnel
  „FraWo-RK", seit 21.08.2026). Persönliche Konten `wolf`, `alois`,
  `heidi` (kein `admin` mehr — Skripte laufen über einen API-Token,
  nicht über das Passwort).
- **CT121** existierte als leere Zweitinstanz (nie produktiv, hing in
  einer Neustartschleife) — am 21.08.2026 auf Wolfs Entscheidung entfernt.
  Es gibt nur noch CT110.

## Ablauf (seit 21.08.2026) — Push, kein Zeittakt

Der Auslöser ist eine echte Google-Drive-Benachrichtigung ("der Postbote
klingelt"), kein wiederkehrendes Nachfragen. Ein Zeittakt läuft nur noch
als seltenes Sicherheitsnetz (alle 4 Std.) und für die Pflicht-Erneuerung
des Google-Kanals (alle 6 Tage, Google erzwingt max. 7 Tage Laufzeit).

```
Datei landet in Google Drive 00_INBOX/_Dokumente-zur-Pruefung/
        │  Google Drive Push-Benachrichtigung (Sekunden später)
        ▼
Webhook-Empfänger (stock-pve:8001, systemd-Dienst
frawo-gdrive-webhook), erreichbar von aussen nur über
paperless-hook.frawo.tech → Cloudflare-Tunnel FraWo-RK (läuft als
Docker-Container auf CT140) → Firewall erlaubt nur 10.1.0.112
        │  stösst sofort frawo-gdrive-inbox-pull.sh an
        ▼
rclone move nach CT110 Consume-Ordner (/opt/paperless/consume)
        │  Paperless: OCR (deu+eng)
        ▼
Post-Consume-Skript paperless_smart_router.py (v3, läuft im Container,
rclone dorthin reinegemountet)
        │  Gemini API liest Volltext: Person/Entität, Kategorie,
        │  Absender, Betrag, Frist, Handlungsbedarf
        ├─▶ Correspondent, Dokumenttyp (Rechnung/Vertrag/Bescheid/...),
        │   2 Tags (Person + Kategorie) und ein sauberer Titel
        │   ("Dokumenttyp Absender Datum") in Paperless gesetzt
        ├─▶ archivierte Datei direkt (rclone) in den passenden
        │   bestehenden Drive-Ordner abgelegt (10_Finanzen,
        │   20_Verträge, 30_Amt & Behörden, 40_Gesundheit, 50_Wohnen,
        │   60_Arbeit, 70_Projekte, 99_Archiv)
        └─▶ bei Handlungsbedarf: Odoo-Aufgabe in Projekt
            „📥 Eingang / Inbox" (ID 32), zugewiesen an die
            zuständige Person, mit Frist + Link zum Paperless-Dokument
```

**Beteiligte Dauer-Dienste (stock-pve):**
- `frawo-gdrive-webhook.service` — nimmt die Push-Benachrichtigung entgegen
- `frawo-gdrive-watch-renew.timer` — erneuert den Google-Kanal alle 6 Tage
- `frawo-gdrive-inbox-pull.timer` — Sicherheitsnetz alle 4 Std. (Google
  garantiert Zustellung nicht zu 100 %)

## Einmaliges Aufräumen (seit 21.08.2026, läuft noch)

`00_INBOX` enthielt vor der Einrichtung über 1150 Dateien direkt im
Ordner (Mischung aus echten Dokumenten, privaten Fotos/Videos,
Programm-Installern, Dubletten) plus 87 lose Dateien im Drive-Root.
Ein KI-gestützter Sortierlauf (`frawo-inbox-triage.py`, stock-pve) teilt
das in Unterordner auf, **ohne etwas zu löschen**:

- `_Dokumente-zur-Pruefung/` — geht danach durch die laufende Pipeline
- `_Fotos-Videos/`, `_Programme-Technik/`, `_Duplikate/` — liegt für
  Wolf zur manuellen Durchsicht bereit

🔴 **Gemini-Freikontingent ist TÄGLICH begrenzt, nicht nur pro Minute**
(bei `gemini-3.6-flash` nur 20 Anfragen/Tag, beim „Lite"-Modell auch nur
niedrig zweistellig) — reicht für den laufenden Betrieb locker, aber
nicht für 1150 Dateien an einem Tag. Deshalb läuft `frawo-inbox-triage.timer`
**täglich um 05:00** automatisch weiter (Fortschritt in
`/var/lib/frawo/inbox-triage-progress.json`, resumable). Bei rund 60
Dateien/Tag dauert der komplette Rückstand ca. 2–3 Wochen. Erkennt das
Skript ein *tägliches* Kontingent-Limit (nicht ein kurzes Minutenlimit),
schaltet es für den Rest des Laufs automatisch auf reine
Stichwort-Erkennung um, statt jede Datei einzeln erfolglos anzufragen.

## Zugang

- Paperless: `https://paperless.frawo.tech` (überall) oder
  `http://10.1.0.100:8000` (Tailscale/LAN)
- Login mit den persönlichen Konten `wolf`/`alois`/`heidi`. Automatisierung
  läuft über einen API-Token (Django `drf_create_token`), nicht über das
  Passwort — Passwort ändern bricht die Automatik nicht.
- Zugangsdaten (API-Token, Odoo-Zugang, Gemini-Key) liegen in
  `/opt/paperless/.env` auf CT110 (nicht mehr im Klartext in der
  `docker-compose.yml`, nicht im Repo). Rotation macht Wolf selbst.
- Webhook-Geheimnis + URL: `/etc/frawo/gdrive-webhook.env` auf stock-pve.

## Tägliche/normale Checks

- Login funktioniert
- neue Datei in `00_INBOX/_Dokumente-zur-Pruefung` wird binnen ~5 Min
  aus Drive abgeholt
- OCR/Klassifikation laufen durch (Log: `docker logs paperless-webserver`
  bzw. Konsole des Post-Consume-Skripts)
- Odoo-Aufgabe entsteht bei Handlungsbedarf im richtigen Projekt bei
  der richtigen Person

## Bekannte Fallstricke

- **rclone ohne `--drive-chunk-size 64M`**: Faktor 8 langsamer (siehe
  NOW.md-Fallentabelle) — im Sync-Skript berücksichtigt.
- Gemini-Free-Tier hat ein Tageslimit — bei großen Nachschüben (z. B.
  während des einmaligen Aufräumens) kann die Verarbeitung sich über
  mehrere Tage strecken. Kein Fehler, nur Warteschlange.
- Personen-Erkennung im Skript ist textbasiert (Gemini liest den
  OCR-Text) — bei sehr schlechten Scans ohne erkennbaren Namen/Bezug
  landet das Dokument ohne Personen-Zuordnung bei Wolf als Standard.

## Eskalation

Bei fehlenden Dokumenten: zuerst `00_INBOX` auf Drive prüfen, dann den
rclone-Sync-Log auf stock-pve, dann Paperless-Consume-Ordner, dann das
Post-Consume-Skript-Log.
