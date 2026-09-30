# Radio: Redaktion beim Hören + Seite nach außen — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wolf, Franz und der Kiosk-Nutzer beurteilen beim Hören von frawo.tech/radio den laufenden Titel (Energie 1–5, passt/passt nicht); die Urteile landen in beets. Die öffentliche Seite zeigt den Sendeplan live vom Sender und wirkt professionell.

**Architecture:** Neues Odoo-Model `frawo.radio.urteil` im Addon `frawo_agent` (Upsert je Titel+Art+Person), zwei Routen (`/radio/redaktion/info` öffentlich-lesend, `/radio/redaktion/urteil` nur Gruppe „Radio-Redaktion“) plus token-geschützter Export. Die Seite (QWeb-View 3353, Quelle `views/radio_page.xml`) bekommt einen Redaktions-Bereich und einen Live-Sendeplan über einen neuen Proxy `/radio/schedule` (AzuraCast `/api/station/1/schedule`). Ein Skript auf CT120 holt nachts die Urteile und schreibt sie über die beets-Schnittstelle.

**Tech Stack:** Odoo 19 (`frawo_agent`), QWeb/Vanilla-JS, AzuraCast-API, Python 3.11 + beets 2.13 (CT120).

**Spec:** `DOCS/superpowers/specs/2026-09-30-radio-redaktionsseite-design.md` (Teil A + Teil B)

## Global Constraints

- **Titel-Kennung** wie bei den Sternen: `"Künstler|Titel"` (`window.currentTrackKey`, aus `np.song.artist + '|' + np.song.title`).
- **Urteil-Arten:** `energie` (Wert 1–5), `passt` (Wert 1 = passt hierher, 0 = passt nicht; dazu `sendung` = laufende Playlist).
- **Ein Urteil je Titel + Art + Person** (Upsert, letzter Wert zählt).
- **Nur Gruppe „Radio-Redaktion“** darf urteilen (Wolf UID 6, Franz UID 10, Kiosk). Öffentliche Besucher sehen nichts davon.
- **JavaScript in View 3353:** kein literales `<`, `>` oder `&` im neuen Code (umschreiben: `!(a >= b)` statt `a < b` usw.); Live-View nur per ORM schreiben, vorher Backup (`view3353.arch_db.bak-YYYYMMDD-N.xml`).
- **Während Live-Show** (`live.is_live`) Redaktions-Bereich ausblenden.
- **Keine Secrets im Repo.** Export-Token = vorhandenes `frawo_agent.summary_token`; auf CT120 in `/etc/frawo/odoo.env` (`0600`).
- **Odoo-Tests:** `TransactionCase`, `@tagged("post_install", "-at_install", "frawo_agent")`. Testlauf (Odoo CT140 liegt auf dem Anker):
  `ssh anker-pve "pct exec 140 -- docker exec frawotech-odoo-1 sh -c 'odoo -d FraWo_GbR -u frawo_agent --test-enable --test-tags frawo_agent --workers 0 --http-port 8079 --gevent-port 8082 --stop-after-init --db_host=\"\$HOST\" --db_user=\"\$USER\" --db_password=\"\$PASSWORD\"'"`
  (`SerializationFailure` beim Upgrade ist transient → wiederholen.)
- **Deploy:** `python scripts/tools/sync_odoo_files.py` (neue Dateien in `FILES_TO_SYNC` eintragen), danach Upgrade wie oben ohne `--test-enable`, dann `docker restart frawotech-odoo-1` (kurze Unterbrechung der Website — ankündigen).
- **Neuer Nachtdienst auf CT120** erst nach Absprache mit Jarvis; bis dahin läuft das Rückschreiben per Hand.

## Review Focus

- Titelwechsel zwischen Anzeige und Tipp: das Urteil muss beim angezeigten Titel landen → Kennung wird beim Rendern der Knöpfe festgehalten und mitgesendet (Task 4).
- Nicht angemeldet / angemeldet ohne Gruppe (normaler Kunde): keine Knöpfe, Route antwortet 403 statt zu speichern (Task 3 Tests).
- Jingles/Live-DJ/„FraWo Funk“-Platzhalter als Kennung: nicht urteilbar (Task 3 + 4).
- Sendeplan über Mitternacht (21:00–06:00, 22:00–02:00): richtig am Tag des Beginns anzeigen, „jetzt“ korrekt (Task 5).
- beets-Zuordnung mehrdeutig (gleicher Artist+Titel mehrfach): nichts schreiben, in Liste aufnehmen (Task 7 Tests).

---

### Task 1: Gruppe „Radio-Redaktion“ + Kiosk-Nutzer

**Files:**
- Create: `addons/frawo_agent/security/radio_redaktion.xml`
- Modify: `addons/frawo_agent/__manifest__.py` (`data`: Datei vor `ir.model.access.csv`)
- Modify: `scripts/tools/sync_odoo_files.py`

**Interfaces:** Produces XML-ID `frawo_agent.group_radio_redaktion`.

- [ ] **Step 1: Gruppe anlegen**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <record id="group_radio_redaktion" model="res.groups">
    <field name="name">Radio-Redaktion</field>
    <field name="comment">Darf auf frawo.tech/radio den laufenden Titel beurteilen (Energie, passt/passt nicht). Wolf, Franz, Kiosk.</field>
  </record>
</odoo>
```

- [ ] **Step 2: Upgrade, Mitglieder setzen (Odoo-Shell, leise):** Wolf (6) und Franz (10) in die Gruppe. Kiosk-Nutzer anlegen: Name „Kiosk (interne Bildschirme)“, Login `kiosk@frawo.tech`, interner Benutzer, Gruppen nur `base.group_user` + `group_radio_redaktion`, **ohne Passwort** — Wolf setzt es selbst in Odoo (Einstellungen → Benutzer) und meldet die Bildschirme einmal an.
- [ ] **Step 3: Prüfen:** `env.ref('frawo_agent.group_radio_redaktion').user_ids.mapped('login')` → drei Logins.
- [ ] **Step 4: Commit + Push**

---

### Task 2: Model `frawo.radio.urteil`

**Files:**
- Create: `addons/frawo_agent/models/radio_urteil.py`
- Modify: `addons/frawo_agent/models/__init__.py`, `security/ir.model.access.csv`, `tests/__init__.py`, `scripts/tools/sync_odoo_files.py`
- Test: `addons/frawo_agent/tests/test_radio_urteil.py`

**Interfaces:**
- Produces: `env['frawo.radio.urteil'].urteilen(track_id: str, art: str, wert: int, sendung: str = '') -> record` (Upsert je `track_id, art, user_id`); `export_rows() -> list[dict]` mit `track_id, art, wert, sendung, user, datum`.

- [ ] **Step 1: Failing Tests**

```python
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioUrteil(TransactionCase):
    def setUp(self):
        super().setUp()
        self.U = self.env["frawo.radio.urteil"]
    def test_upsert_letzter_wert_zaehlt(self):
        self.U.urteilen("A|B", "energie", 2)
        self.U.urteilen("A|B", "energie", 4)
        recs = self.U.search([("track_id", "=", "A|B"), ("art", "=", "energie")])
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs.wert, 4)
    def test_energie_nur_1_bis_5(self):
        with self.assertRaises(ValueError):
            self.U.urteilen("A|B", "energie", 6)
    def test_passt_nur_0_oder_1_mit_sendung(self):
        r = self.U.urteilen("A|B", "passt", 0, sendung="01 Sunrise")
        self.assertEqual((r.wert, r.sendung), (0, "01 Sunrise"))
        with self.assertRaises(ValueError):
            self.U.urteilen("A|B", "passt", 2)
    def test_platzhalter_nicht_urteilbar(self):
        for key in ("", "FraWo Funk", "|"):
            with self.assertRaises(ValueError):
                self.U.urteilen(key, "energie", 3)
    def test_export(self):
        self.U.urteilen("A|B", "energie", 5)
        rows = self.U.export_rows()
        self.assertTrue(any(r["track_id"] == "A|B" and r["wert"] == 5 for r in rows))
```

- [ ] **Step 2: Testlauf → FAIL** (`KeyError: 'frawo.radio.urteil'`)
- [ ] **Step 3: Model**

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models

ARTEN = [("energie", "Energie 1–5"), ("passt", "Passt in die Sendung")]


class FrawoRadioUrteil(models.Model):
    _name = "frawo.radio.urteil"
    _description = "FraWo Radio-Redaktion: Urteil zum laufenden Titel"
    _order = "write_date desc"

    track_id = fields.Char(string="Titel (Künstler|Titel)", index=True, required=True)
    art = fields.Selection(ARTEN, required=True, index=True)
    wert = fields.Integer(required=True)
    sendung = fields.Char(string="Sendung")
    user_id = fields.Many2one("res.users", required=True, index=True, default=lambda s: s.env.user, ondelete="cascade")

    _urteil_unique = models.Constraint("UNIQUE(track_id, art, user_id)", "Ein Urteil je Titel, Art und Person.")

    @api.model
    def urteilen(self, track_id, art, wert, sendung=""):
        track_id = (track_id or "").strip()
        teile = track_id.split("|", 1)
        if len(teile) != 2 or not teile[0].strip() or not teile[1].strip():
            raise ValueError("Titel nicht urteilbar")
        wert = int(wert)
        if art == "energie" and not (1 <= wert <= 5):
            raise ValueError("Energie muss 1–5 sein")
        if art == "passt" and wert not in (0, 1):
            raise ValueError("passt muss 0 oder 1 sein")
        if art not in dict(ARTEN):
            raise ValueError("unbekannte Art")
        vals = {"wert": wert, "sendung": sendung or ""}
        rec = self.search([("track_id", "=", track_id), ("art", "=", art), ("user_id", "=", self.env.uid)], limit=1)
        if rec:
            rec.write(vals)
            return rec
        return self.create(dict(vals, track_id=track_id, art=art))

    @api.model
    def export_rows(self):
        return [{"track_id": r.track_id, "art": r.art, "wert": r.wert, "sendung": r.sendung,
                 "user": r.user_id.login, "datum": fields.Datetime.to_string(r.write_date)}
                for r in self.sudo().search([])]
```

ACL-Zeilen:
```
access_radio_urteil_redaktion,frawo.radio.urteil.redaktion,model_frawo_radio_urteil,frawo_agent.group_radio_redaktion,1,1,1,0
access_radio_urteil_user,frawo.radio.urteil.user,model_frawo_radio_urteil,base.group_user,1,0,0,0
```

- [ ] **Step 4: Testlauf → PASS** · **Step 5: Commit + Push**

---

### Task 3: Routen `/radio/redaktion/info`, `/radio/redaktion/urteil`, `/radio/redaktion/export`

**Files:**
- Modify: `addons/frawo_agent/controllers/radio_votes.py`
- Test: `addons/frawo_agent/tests/test_radio_urteil.py` (Rechte-Tests über `with_user`)

**Interfaces:**
- `GET /radio/redaktion/info?track_id=…` (auth public) → `{"ok": true, "redakteur": bool, "eigene": {"energie": int|null, "passt": int|null}}`
- `POST /radio/redaktion/urteil` (auth user, JSON `{track_id, art, wert, sendung}`) → `{"ok": true}` · ohne Gruppe HTTP 403 `{"ok": false, "error": "forbidden"}` · ungültig 400.
- `GET /radio/redaktion/export` (Token `X-Agent-Token` = `frawo_agent.summary_token`, gleiche Prüfung wie `/radio/ratings/export`) → Liste aus `export_rows()`.

- [ ] **Step 1: Failing Tests** — Rechte über das Model prüfen, das die Route aufruft:

```python
    def test_ohne_gruppe_kein_schreibrecht(self):
        kunde = self.env["res.users"].create({"name": "Kunde", "login": "kunde_test_urteil", "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        from odoo.exceptions import AccessError
        with self.assertRaises(AccessError):
            self.U.with_user(kunde).urteilen("A|B", "energie", 3)
```

- [ ] **Step 2–4:** Routen implementieren (Gruppenprüfung `request.env.user.has_group('frawo_agent.group_radio_redaktion')` vor dem Aufruf; `ValueError` → 400), Testlauf → PASS.
- [ ] **Step 5: Commit + Push**

---

### Task 4: Redaktions-Bereich auf der Seite

**Files:** Modify `addons/frawo_agent/views/radio_page.xml` (direkt unter `id="ff-rating-box"`-Block)

- [ ] **Step 1:** HTML-Block `id="ff-redaktion"` (standardmäßig `display:none`): Zeile „Energie“ mit Knöpfen 1–5 (`data-art="energie" data-wert="n"`), Zeile „Passt in <Sendung>?“ mit „👍 passt“ (`data-art="passt" data-wert="1"`) / „👎 passt nicht“ (`data-wert="0"`), kleine Rückmeldung „gespeichert“.
- [ ] **Step 2:** JS `window.ffLoadRedaktion()` — wird nach jedem Titelwechsel aufgerufen (dort, wo `ffLoadRating()` aufgerufen wird): holt `/radio/redaktion/info?track_id=…`; zeigt den Block nur bei `redakteur === true` und nicht bei `live.is_live`; merkt sich `key` **und** aktuelle Playlist in `data-track`/`data-sendung` des Blocks; markiert eigene Werte.
- [ ] **Step 3:** Klick → `fetch('/radio/redaktion/urteil', {method:'POST', …JSON-RPC-Body…})` mit den **am Block gespeicherten** `data-track`/`data-sendung` (Review Focus 1). Kein literales `<`, `>`, `&`.
- [ ] **Step 4:** Lokal Syntax prüfen (XML parsen mit `python -c "import lxml.etree as e; e.parse('addons/frawo_agent/views/radio_page.xml')"`), Commit + Push.

---

### Task 5: Sendeplan live vom Sender

**Files:**
- Modify: `addons/frawo_agent/controllers/main.py` (neue Route neben `radio_nowplaying_proxy`)
- Modify: `addons/frawo_agent/views/radio_page.xml` (Block „Wochenprogramm & Sendeplan“, heute ab Zeile ~1348, statisch)

- [ ] **Step 1: Route** `/radio/schedule` (auth public, GET, cache 5 min im Speicher): ruft `GET {base}/api/station/1/schedule?rows=200` (öffentlicher AzuraCast-Endpunkt), gibt JSON-Liste `{name, beschreibung, start, ende, jetzt}` zurück (Zeiten ISO, Europe/Berlin). Nur Sendungen (Playlists) — keine Jingles.
- [ ] **Step 2: Test** (Model-freie Hilfsfunktion `_schedule_vereinfachen(rohliste)` in `radio_azuracast.py`, TransactionCase mit fester Beispielliste): Über-Mitternacht-Eintrag 21:00–06:00 wird dem Beginn-Tag zugeordnet; `jetzt` genau bei einem Eintrag gesetzt.
- [ ] **Step 3: Seite:** statische Tages-Karten (alle `ff-card-time`-Blöcke) ersetzen durch einen leeren Container `id="ff-schedule-live"` + JS, das `/radio/schedule` lädt und die 7 Tagesreiter aus den Daten baut (heutiger Tag vorausgewählt, laufende Sendung hervorgehoben, „Danach“-Hinweis oben). Fällt der Abruf aus: Hinweis „Sendeplan gerade nicht erreichbar“ statt leerer Fläche.
- [ ] **Step 4: Steckbriefe:** Beschreibungen der Playlists 859–868 in AzuraCast pflegen (ein Satz + Stil, deutsch) — per AzuraCast-API `PUT /api/station/1/playlist/{id}` (Feld `description`), vorher alte Werte sichern.
- [ ] **Step 5:** Commit + Push.

---

### Task 6: Seite aufräumen (Teil B2 Punkte 3–6)

**Files:** Modify `addons/frawo_agent/views/radio_page.xml`

- [ ] **Step 1:** „Auf YouTube suchen“-Knopf entfernen.
- [ ] **Step 2:** Technik-Angaben („320 kbps Master Audio“, „Liquidsoap v2 Engine“, „M3U … (VLC / iTunes)“) in einen zugeklappten `<details>`-Bereich „In anderen Apps hören“ mit Stream-Adressen und Playlist-Datei, ohne Engine-/iTunes-Namen.
- [ ] **Step 3:** Ladetexte „Lade nächsten Track…“, „Stimmen werden laden…“ → „—“.
- [ ] **Step 4:** Emojis in Überschriften/Knöpfen auf höchstens eines je Abschnitt reduzieren; Texte deutsch und kurz.
- [ ] **Step 5:** Commit + Push.

---

### Task 7: Rückschreiben in beets (CT120)

**Files:**
- Create: `deployments/musikredaktion/rueckschreiben.py`
- Test: `deployments/musikredaktion/tests/test_rueckschreiben.py`

**Interfaces:** Consumes `/radio/redaktion/export`; `zuordnen(track_id, items) -> item_id | None` (Normalisierung `discogs_abgleich.norm` auf Artist und Titel; mehrdeutig → None).

- [ ] **Step 1: Failing Tests** (eindeutig → id; zwei Kandidaten → None; kein Treffer → None; `"A feat. X|Song (Original Mix)"` findet `A|Song`).
- [ ] **Step 2: Implementieren:** Export holen (Token aus `/etc/frawo/odoo.env`), je Titel Mittelwert der Energie-Urteile (gerundet) → beets `energie`, `quelle_energie = "Redaktion <Datum>"`; `passt=0` → `passt_nicht` (Liste der Sendungen, kommagetrennt); mehrdeutige/unzugeordnete in `/root/musikredaktion/rueckschreiben-offen.csv`. Schreiben nur über `beets.library` (`item.store()`), DB-Sicherung vor dem Lauf.
- [ ] **Step 3: Tests → PASS**, Probelauf mit `--probe` (schreibt nichts), dann echter Lauf per Hand.
- [ ] **Step 4:** Commit + Push. Nachtdienst: Vorschlag an Jarvis (eine gebündelte Nachricht).

---

### Task 8: Ausrollen und Abnahme

- [ ] **Step 1:** Deploy + Upgrade + Tests (Global Constraints), View 3353 per ORM aktualisieren (Backup vorher), `docker restart frawotech-odoo-1`.
- [ ] **Step 2:** Anonym prüfen: `https://frawo.tech/radio` → 200, Sendeplan = AzuraCast (Mo, Sa, So Stichprobe), keine Redaktions-Knöpfe, Player/Wunsch/Abstimmung funktionieren, keine Befund-Stellen aus B1.
- [ ] **Step 3:** Als Wolf angemeldet (Browser): Knöpfe sichtbar, Energie 3 → Datensatz vorhanden; Energie 4 → derselbe Datensatz = 4.
- [ ] **Step 4:** Odoo #1090 Notiz mit Ergebnis; Jarvis-Review in **einer** gebündelten Nachricht (zusammen mit Abendfragen #1661 und Nachtdienst Rückschreiben); Wolf gibt die Seite am Handy frei.
