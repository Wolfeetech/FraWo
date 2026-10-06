# Ablageordnung FraWo / Wolf

Stand 06.10.2026 · Odoo #1927 · gilt für alle Agenten und für Wolf/Franz.
Ersetzt die Archivpläne `Task_Archive/SHARED_STORAGE_ARCHITECTURE_PLAN.md` und `GOOGLE_DRIVE_INTEGRATION_PLAN.md`.

## 1. Grundsatz: jede Dateiart hat genau einen Ort

| Art | Ort (Original) | Warum |
|---|---|---|
| **Dokumente mit Beleg- oder Nachweischarakter**: Rechnungen, Verträge, Versicherung, Bescheide, Lohn, Zeugnisse, Kontoauszüge, Briefe | **Paperless** (`docs.frawo.tech`, CT110) | Volltextsuche (OCR), Korrespondent, Dokumenttyp, Datum, Aufbewahrungsfrist, Dublettenschutz |
| **Arbeitsdateien**: Entwürfe, Planungen, Tabellen, Konzepte, Angebote in Arbeit | **Nextcloud** (`cloud.frawo.tech`) | Bearbeiten, Versionen, Teilen mit Franz |
| **Technik**: Showfiles, Fixture-Profile, DSP-Presets, Firmware, Installer, Rekordbox | **Nextcloud** `80_Technik` | gerätebezogen, wird mit dem Equipment gebraucht |
| **Fotos & Videos** | **Nextcloud** `90_Medien` | Vorschau, Teilen, Handy-Sofortupload |
| **Musik** | **Radio-Bibliothek** (`Master_Library`, Pipeline `radio_neuzugang`) | AzuraCast, beets, Dublettenprüfung |
| **Google Drive** | **nur Sicherung** (`FraWo-Verschluesselt`, `FraWo_Musik`) | Wolf 06.10.: „Am Ende soll keine Musik in Drive liegen, nur das Backup“, sinngemäß für alles |

Ist ein fertiges Dokument zugleich Arbeitsdatei (z. B. versendetes Angebot), kommt das **versendete PDF nach Paperless** und die bearbeitbare Fassung bleibt in Nextcloud.

## 2. Nextcloud-Ordnerplan

Nummern sind dieselben wie im bisherigen Drive-Plan (10–99), damit Wolf sich nicht umgewöhnen muss. Die Bereiche 10–50 enthalten in Nextcloud **keine Belege**, die liegen in Paperless.

```
00_Eingang/            Unsortiertes; wird spätestens monatlich geleert
10_Finanzen/           Budgets, Auswertungen, Exporte (keine Belege)
20_Verträge/           Vertragsentwürfe, Vorlagen
30_Amt_und_Behörden/   Antragsentwürfe
40_Gesundheit/         (privat, nur Wolf)
50_Wohnen/             Pläne, Nebenkosten-Tabellen
60_Arbeit_und_Gewerbe/
    Ausbildung/          Berufsschule, Prüfungen, AEVO
    Bewerbungen/
    Arbeitszeiten/
    FraWo_GbR/           Gesellschaft, Strategie, Roadmaps, Konzepte
70_Projekte/
    <JJJJ>_<Projekt>/    z. B. 2026_LAGO_Weinmesse, 2026_Inselhalle
80_Technik/
    Ton/ Licht/ IT/ Software/ Rekordbox/ Projekte_und_Konfigurationen/
90_Medien/
    Fotos_Videos/<JJJJ>/<JJJJ-MM_Anlass>/
    Drohne/                  DJI-Rohmaterial
    Grafik_Branding/         Logos, Presskits, Pitchdecks
95_Privat/               Spiele, Persönliches ohne Belegcharakter
99_Archiv/<JJJJ>/        abgeschlossene Projekte, nur lesen
```

## 3. Benennung

- **Neue Dateien:** `JJJJ-MM-TT_Thema_vN.ext`, zum Beispiel `2026-10-06_Technikplanung_LAGO_v2.xlsx`. Kein „Unbenannt“, „final_FINAL“ oder „(1)“.
- **Ordner:** ohne Leerzeichen am Ende, keine Sonderzeichen `/ \ : * ? " < > |`, Umlaute erlaubt.
- **Paperless** benennt selbst. Einzurichten ist `PAPERLESS_FILENAME_FORMAT={{ created_year }}/{{ correspondent }}/{{ created }} {{ title }}`; Stand 06.10. ist kein Format gesetzt, Dateien heißen nur nach Nummer.
- **Bestandsdateien** werden **nicht** massenhaft umbenannt (Risiko > Nutzen), nur beim Anfassen.

## 4. Aufbewahrung (Paperless-Feld „Aufbewahren bis“, einzurichten)

| Dokument | Frist | Grundlage |
|---|---|---|
| Rechnungen, Buchungsbelege der GbR | 8 Jahre ab Jahresende | § 147 AO, § 257 HGB (seit 2025: 8 statt 10 Jahre) |
| Bücher, Jahresabschlüsse, Inventare | 10 Jahre | § 147 Abs. 3 AO |
| Geschäftsbriefe (empfangen/gesendet) | 6 Jahre | § 147 AO |
| Lohnabrechnungen, Arbeitsverträge, Zeugnisse, SV-Meldungen | dauerhaft (Rente) | Empfehlung |
| Private Rechnungen mit Handwerkerleistung | 2 Jahre | § 14b UStG |
| Versicherungspolicen | Laufzeit + 3 Jahre | Verjährung § 195 BGB |

Fristen sind eine praktische Richtschnur, keine Steuerberatung. Im Zweifel länger aufbewahren.

## 5. Trennung GbR / privat

- **Paperless:** Jedes Dokument bekommt das Schlagwort **„FraWo GbR“** oder **„Privat“** (beide vorhanden). Franz soll nur „FraWo GbR“ sehen (über Rechte, einzurichten).
- **Vorhandene Ordnung in Paperless (06.10.):** 251 Dokumente, 149 Korrespondenten, 20 Dokumenttypen (Rechnung, Vertrag, Bescheid, Gehaltsabrechnung, Zeugnis, Versicherungspolice …). Bereichs-Schlagworte `finanzen`, `vertraege`, `amt_behoerden`, `arbeit`, `wohnen`, `projekte` entsprechen den Nummern 10–70. Diese Ordnung wird beibehalten.
- **Nextcloud:** Private Bereiche (40, 95, Teile von 60) bleiben bei **wolf** und werden **nie** geteilt. Mit Franz geteilt werden **80_Technik**, **70_Projekte** und **60_Arbeit_und_Gewerbe/FraWo_GbR**.

## 6. Dubletten

- **Paperless** lehnt Dateien mit gleicher Prüfsumme ab.
- **Nextcloud:** Vor dem Einsortieren werden identische Dateien (gleiche Größe und Prüfsumme) zusammengeführt. Name mit „(1)“ und gleichem Inhalt heißt löschen.
- **Musik:** Abgleich über Künstler-Titel-Dauer (`radio_neuzugang_ablegen.py`).

## 7. Sicherung (3-2-1)

| Daten | Kopie 1 | Kopie 2 | Kopie 3 außer Haus |
|---|---|---|---|
| Nextcloud (VM300 inkl. Datenplatte) | live | PBS nachts 01:00 | wöchentlich verschlüsselt in Drive (`cloud-woche-mo`) |
| Paperless (CT110) | live | PBS nachts | wöchentlich (`cloud-woche-fr`) |
| Musik | live (Anker/SSD) | Anker-ZFS-Kopie | `FraWo_Musik` in Drive |

**Drive-Originale werden erst gelöscht**, wenn das Ziel nachgeprüft ist (Anzahl und Größe je Ordner) **und** eine PBS-Sicherung nach dem Einsortieren gelaufen ist. Gelöscht wird in den Drive-Papierkorb (30 Tage zurückholbar), mit Liste je Ordner im Odoo-Chatter.

## 8. Laufender Betrieb

- **Drive-Eingang `00_INBOX`:** Paperless holt alle 15 min **nur Dokumente** direkt im Ordner (`frawo-gdrive-inbox-pull.sh`). Alles andere sortiert ein Agent nach dieser Ordnung.
- **Handy-Fotos:** Nextcloud-App mit Sofortupload nach `90_Medien/Fotos_Videos/<JJJJ>`.
- **Neue Musik:** Drive `00_INBOX` oder Nextcloud `00_Eingang`, dann `radio_neuzugang.sh`.
