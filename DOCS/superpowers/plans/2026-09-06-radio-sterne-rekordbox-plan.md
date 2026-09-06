# Radio-Sterne-Bewertung + Rekordbox-Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Angemeldete Hörer:innen bewerten den laufenden Titel mit 1–5 Sternen; der Durchschnitt ist für alle sichtbar und landet automatisch, im Hintergrund, im nativen Sterne-Feld von Rekordbox plus in einer Playlist „🔥 Publikums-Favoriten".

**Architecture:** Neues Odoo-Model `frawo.radio.rating` (eine Bewertung pro Person und Titel, Upsert). Zwei Routen: `POST /radio/rate` (nur angemeldet) und `GET /radio/rating/summary` (öffentlich, nur Aggregat). Ein token-geschützter Export-Endpunkt liefert die gerundeten Durchschnitte; ein Python-Skript auf dem StudioPC (Windows-Aufgabenplanung, stündlich) holt sie ab und schreibt sie per `pyrekordbox` direkt in Rekordbox — nur wenn Rekordbox geschlossen ist. Abgleich Titel→Rekordbox über `DjmdContent.Title` + `DjmdArtist.Name`, kein AzuraCast-Umweg.

**Tech Stack:** Odoo 19 (Addon `frawo_agent`), QWeb-View 3353, Python 3.13 auf StudioPC, `pyrekordbox` 0.4.4 (`Rekordbox6Database`), `requests`, `python-dotenv`, Windows-Aufgabenplanung (`schtasks`).

**Spec:** `DOCS/superpowers/specs/2026-09-06-radio-demokratie-design.md` (Abschnitte 5, 6, 8, 9 Punkte 5–8)

## Global Constraints

- **Eine Bewertung pro Person und Titel:** SQL-Constraint `unique(track_id, partner_id)`; erneutes Bewerten überschreibt (Upsert).
- **Sterne nur ganzzahlig 1–5.** Rekordbox' `DjmdContent.Rating` ist eine Ganzzahl 0–5 (an der echten Bibliothek geprüft: 11.507 Titel bei 0, Rest 1–5).
- **Bewerten nur angemeldet** (`auth='user'`, bestehendes Odoo-Kundenkonto). **Anzeige für alle.** Kein öffentlicher Endpunkt liefert einzelne Personen — nur Durchschnitt, Anzahl und die *eigene* Bewertung.
- **Export nur ab 2 Bewertungen** je Titel; Durchschnitt kaufmännisch gerundet (4,5 → 5).
- **Rekordbox nie bei laufender Anwendung beschreiben:** Prozessprüfung auf `rekordbox.exe` und `rekordboxAgent.exe` vor jedem Lauf; läuft eine davon → Lauf überspringen, protokollieren, nächster Versuch in einer Stunde.
- **Titel-Kennung** ist exakt das Format, das die Seite als `song_id` sendet: `"Künstler|Titel"` (aus `np.song.artist + '|' + np.song.title`).
- **Keine Secrets im Repo.** Export-Token in `deployments/musikverwaltung/rekordbox_sync/.env` (gitignored) als `FRAWO_AGENT_TOKEN`; in Odoo als `ir.config_parameter` `frawo_agent.summary_token` (existiert bereits, wird von `/api/agent/*` genutzt).
- **JavaScript in View 3353:** kein literales `<`, `>` oder `&` im neuen Code (umschreiben statt escapen).
- **Während Live-Show** (`live.is_live`) ist die Sterne-Leiste ausgeblendet (keine verlässliche Titel-Kennung).
- **Lokale Systemänderungen am StudioPC** (Aufgabenplanung registrieren) bereitet der Agent vor, **Wolf führt sie aus** (`! <Befehl>`).
- **Tests:** Odoo `TransactionCase`, `@tagged("post_install", "-at_install", "frawo_agent")`; Testlauf:
  `ssh stock-pve "pct exec 140 -- docker exec frawotech-web-1 sh -c 'odoo -d FraWo_GbR -u frawo_agent --test-enable --test-tags frawo_agent --workers 0 --http-port 8079 --gevent-port 8082 --stop-after-init --db_host=\"\$HOST\" --db_user=\"\$USER\" --db_password=\"\$PASSWORD\"'"`
  (`SerializationFailure` beim Upgrade ist transient → wiederholen.) StudioPC-Skript: `pytest` mit gemocktem `pyrekordbox`/`requests`.

---

### Task 1: Model `frawo.radio.rating` mit Upsert und Aggregat

**Files:**
- Create: `addons/frawo_agent/models/radio_rating.py`
- Modify: `addons/frawo_agent/models/__init__.py` (Import ergänzen)
- Modify: `addons/frawo_agent/security/ir.model.access.csv` (eine Zeile)
- Modify: `scripts/tools/sync_odoo_files.py` (`FILES_TO_SYNC` ergänzen)
- Test: `addons/frawo_agent/tests/test_radio_rating.py` (neu) + `addons/frawo_agent/tests/__init__.py` (Import)

**Interfaces:**
- Consumes: nichts.
- Produces: Model `frawo.radio.rating` (Felder `track_id: Char`, `partner_id: Many2one res.partner`, `stars: Selection '1'..'5'`) mit
  - `rate(track_id: str, partner_id: int, stars: int) -> record` — legt an oder aktualisiert (Upsert); wirft `ValueError` bei `stars` außerhalb 1–5.
  - `summary(track_id: str, partner_id: int | None = None) -> dict` — `{"average": float|None, "count": int, "own": int|None}`; `average` auf eine Nachkommastelle gerundet.
  - `export_rows(min_count: int = 2) -> list[dict]` — je Titel `{"track_id", "artist", "title", "average", "count", "stars"}` (`stars` = kaufmännisch gerundeter Durchschnitt), nur Titel mit `count >= min_count`, sortiert nach `average` absteigend.

- [ ] **Step 1: Write the failing test**

`addons/frawo_agent/tests/test_radio_rating.py`:

```python
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioRating(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env["frawo.radio.rating"].search([]).unlink()
        self.p1 = self.env["res.partner"].create({"name": "Hörerin A"})
        self.p2 = self.env["res.partner"].create({"name": "Hörer B"})
        self.Rating = self.env["frawo.radio.rating"]

    def test_rate_creates_record(self):
        rec = self.Rating.rate("Artist|Song", self.p1.id, 4)
        self.assertTrue(rec.id)
        self.assertEqual(rec.stars, "4")

    def test_rate_again_updates_instead_of_duplicating(self):
        self.Rating.rate("Artist|Song", self.p1.id, 4)
        self.Rating.rate("Artist|Song", self.p1.id, 2)
        recs = self.Rating.search([("track_id", "=", "Artist|Song"), ("partner_id", "=", self.p1.id)])
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs.stars, "2")

    def test_rate_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            self.Rating.rate("Artist|Song", self.p1.id, 6)
        with self.assertRaises(ValueError):
            self.Rating.rate("Artist|Song", self.p1.id, 0)

    def test_summary_average_count_own(self):
        self.Rating.rate("Artist|Song", self.p1.id, 5)
        self.Rating.rate("Artist|Song", self.p2.id, 4)
        s = self.Rating.summary("Artist|Song", self.p1.id)
        self.assertEqual(s["average"], 4.5)
        self.assertEqual(s["count"], 2)
        self.assertEqual(s["own"], 5)

    def test_summary_without_ratings(self):
        s = self.Rating.summary("Niemand|Nie", None)
        self.assertEqual(s, {"average": None, "count": 0, "own": None})

    def test_export_rows_threshold_and_rounding(self):
        self.Rating.rate("A|Eins", self.p1.id, 5)
        self.Rating.rate("A|Eins", self.p2.id, 4)   # avg 4.5 -> 5
        self.Rating.rate("B|Zwei", self.p1.id, 3)   # nur 1 Bewertung -> raus
        rows = self.Rating.export_rows(min_count=2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["track_id"], "A|Eins")
        self.assertEqual(rows[0]["artist"], "A")
        self.assertEqual(rows[0]["title"], "Eins")
        self.assertEqual(rows[0]["count"], 2)
        self.assertEqual(rows[0]["average"], 4.5)
        self.assertEqual(rows[0]["stars"], 5)
```

In `addons/frawo_agent/tests/__init__.py` ergänzen:

```python
from . import test_radio_rating
```

- [ ] **Step 2: Run test to verify it fails**

Run: Testlauf aus Global Constraints (vorher `tests/__init__.py` und Testdatei per `sync_odoo_files.py` bzw. manuell nach CT140 kopieren).
Expected: `KeyError: 'frawo.radio.rating'` in allen 6 Tests.

- [ ] **Step 3: Write minimal implementation**

`addons/frawo_agent/models/radio_rating.py`:

```python
# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models

STAR_CHOICES = [(str(n), "★" * n) for n in range(1, 6)]


class FrawoRadioRating(models.Model):
    _name = "frawo.radio.rating"
    _description = "FraWo Radio Sterne-Bewertung (eine pro Person und Titel)"
    _order = "write_date desc"

    track_id = fields.Char(string="Track", index=True, required=True)
    partner_id = fields.Many2one("res.partner", string="Bewertet von", index=True,
                                 required=True, ondelete="cascade")
    stars = fields.Selection(STAR_CHOICES, string="Sterne", required=True)

    _sql_constraints = [
        ("rating_unique_track_partner", "unique(track_id, partner_id)",
         "Eine Person kann einen Titel nur einmal bewerten (erneut bewerten ueberschreibt)."),
    ]

    @api.model
    def rate(self, track_id, partner_id, stars):
        stars = int(stars)
        if stars < 1 or stars > 5:
            raise ValueError("stars muss zwischen 1 und 5 liegen")
        rec = self.search([("track_id", "=", track_id), ("partner_id", "=", partner_id)], limit=1)
        if rec:
            rec.write({"stars": str(stars)})
            return rec
        return self.create({"track_id": track_id, "partner_id": partner_id, "stars": str(stars)})

    @api.model
    def summary(self, track_id, partner_id=None):
        recs = self.search([("track_id", "=", track_id)])
        if not recs:
            return {"average": None, "count": 0, "own": None}
        values = [int(r.stars) for r in recs]
        own = None
        if partner_id:
            mine = recs.filtered(lambda r: r.partner_id.id == partner_id)
            own = int(mine[0].stars) if mine else None
        return {
            "average": round(sum(values) / len(values), 1),
            "count": len(values),
            "own": own,
        }

    @api.model
    def export_rows(self, min_count=2):
        groups = self.read_group(
            [], ["stars"], ["track_id"], lazy=False)
        rows = []
        for g in groups:
            track_id = g["track_id"]
            recs = self.search([("track_id", "=", track_id)])
            count = len(recs)
            if count < min_count:
                continue
            avg = sum(int(r.stars) for r in recs) / count
            artist, sep, title = track_id.partition("|")
            rows.append({
                "track_id": track_id,
                "artist": artist,
                "title": title if sep else "",
                "average": round(avg, 1),
                "count": count,
                "stars": int(Decimal(str(avg)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
            })
        rows.sort(key=lambda r: (-r["average"], r["track_id"]))
        return rows
```

`addons/frawo_agent/models/__init__.py` ergänzen (Ende):

```python
from . import radio_rating
```

`addons/frawo_agent/security/ir.model.access.csv` ergänzen:

```
access_radio_rating_user,frawo.radio.rating.user,model_frawo_radio_rating,base.group_user,1,0,0,1
```

`scripts/tools/sync_odoo_files.py` in `FILES_TO_SYNC` ergänzen:

```python
    "addons/frawo_agent/models/radio_rating.py",
    "addons/frawo_agent/tests/test_radio_rating.py",
```

- [ ] **Step 4: Run test to verify it passes**

Run: Testlauf aus Global Constraints.
Expected: `0 error(s)`, `TestRadioRating` 6/6 grün (die 3 alten `TestProcessor`-Fehlschläge bleiben).

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/models/radio_rating.py addons/frawo_agent/models/__init__.py addons/frawo_agent/security/ir.model.access.csv addons/frawo_agent/tests/test_radio_rating.py addons/frawo_agent/tests/__init__.py scripts/tools/sync_odoo_files.py
git commit -m "feat(radio): Model frawo.radio.rating mit Upsert, Aggregat und Export-Zeilen"
```

---

### Task 2: Routen `/radio/rate`, `/radio/rating/summary`, `/radio/ratings/export`

**Files:**
- Modify: `addons/frawo_agent/controllers/radio_votes.py`
- Test: `addons/frawo_agent/tests/test_radio_rating.py` (Klasse ergänzen)

**Interfaces:**
- Consumes: `frawo.radio.rating.rate/summary/export_rows` (Task 1); `RadioController._check_summary_auth` aus `controllers/main.py` (Token-Muster).
- Produces:
  - `POST /radio/rate` — `type='json'`, `auth='user'`, Params `song_id`, `stars` → `{"ok": True, "summary": {...}}` oder `{"ok": False, "reason": ...}`.
  - `GET /radio/rating/summary?track_id=…` — `type='http'`, `auth='public'` → JSON `{"ok": True, "average", "count", "own"}`; `own` nur bei angemeldetem, nicht-öffentlichem Benutzer.
  - `GET /radio/ratings/export` — `type='http'`, `auth='public'`, Token wie `/api/agent/summary` (`X-Agent-Token`-Header oder `?token=`) → JSON-Liste aus `export_rows(min_count=2)`; ohne gültiges Token HTTP 401.

- [ ] **Step 1: Write the failing test**

In `addons/frawo_agent/tests/test_radio_rating.py` ergänzen (Import oben: `from odoo.tests.common import HttpCase`):

```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestRatingRoutes(HttpCase):

    def setUp(self):
        super().setUp()
        self.env["frawo.radio.rating"].search([]).unlink()
        self.env["ir.config_parameter"].sudo().set_param("frawo_agent.summary_token", "exporttok")
        self.partner = self.env["res.partner"].create({"name": "Portal Tester"})
        self.user = self.env["res.users"].create({
            "name": "Portal Tester", "login": "portaltester@test.local",
            "partner_id": self.partner.id,
            "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
        })

    def test_summary_public_without_ratings(self):
        r = self.url_open("/radio/rating/summary?track_id=X%7CY")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "average": None, "count": 0, "own": None})

    def test_rate_requires_login(self):
        r = self.url_open("/radio/rate", data='{"jsonrpc":"2.0","method":"call","params":{"song_id":"X|Y","stars":4},"id":1}',
                          headers={"Content-Type": "application/json"})
        self.assertNotEqual(r.status_code, 200)

    def test_export_requires_token(self):
        r = self.url_open("/radio/ratings/export")
        self.assertEqual(r.status_code, 401)

    def test_export_with_token_returns_rows(self):
        p2 = self.env["res.partner"].create({"name": "Zweite"})
        self.env["frawo.radio.rating"].rate("A|Eins", self.partner.id, 5)
        self.env["frawo.radio.rating"].rate("A|Eins", p2.id, 4)
        r = self.url_open("/radio/ratings/export", headers={"X-Agent-Token": "exporttok"})
        self.assertEqual(r.status_code, 200)
        rows = r.json()
        self.assertEqual(rows[0]["track_id"], "A|Eins")
        self.assertEqual(rows[0]["stars"], 5)
```

- [ ] **Step 2: Run test to verify it fails**

Run: Testlauf aus Global Constraints.
Expected: `test_summary_public_without_ratings` und `test_export_*` scheitern mit HTTP 404 (Routen existieren nicht); `test_rate_requires_login` scheitert, weil 404 ≠ Login-Ablehnung erwartet — akzeptabel als RED.

- [ ] **Step 3: Write minimal implementation**

In `addons/frawo_agent/controllers/radio_votes.py` ergänzen — Imports oben:

```python
from odoo.tools import consteq
```

und in der Klasse `FrawoRadioVotes` (nach `radio_votes_summary`):

```python
    def _export_token_ok(self):
        expected = (request.env["ir.config_parameter"].sudo()
                    .get_param("frawo_agent.summary_token", "") or "").strip()
        if not expected:
            return False
        token = (request.httprequest.headers.get("X-Agent-Token")
                 or request.params.get("token") or "")
        return consteq(token, expected)

    @http.route("/radio/rate", type="json", auth="user", csrf=False)
    def radio_rate(self, song_id=None, stars=None, **kw):
        user = request.env.user
        if not song_id or user._is_public():
            return {"ok": False, "reason": "forbidden"}
        try:
            request.env["frawo.radio.rating"].sudo().rate(song_id, user.partner_id.id, stars)
        except (ValueError, TypeError):
            return {"ok": False, "reason": "bad_stars"}
        return {"ok": True,
                "summary": request.env["frawo.radio.rating"].sudo().summary(song_id, user.partner_id.id)}

    @http.route("/radio/rating/summary", type="http", auth="public", csrf=False, methods=["GET"])
    def radio_rating_summary(self, track_id=None, **kw):
        user = request.env.user
        partner_id = None if (not user or user._is_public()) else user.partner_id.id
        data = {"ok": True}
        data.update(request.env["frawo.radio.rating"].sudo().summary(track_id or "", partner_id))
        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json"), ("Cache-Control", "no-store")],
        )

    @http.route("/radio/ratings/export", type="http", auth="public", csrf=False, methods=["GET"])
    def radio_ratings_export(self, **kw):
        if not self._export_token_ok():
            return request.make_response(json.dumps({"error": "unauthorized"}),
                                         headers=[("Content-Type", "application/json")], status=401)
        rows = request.env["frawo.radio.rating"].sudo().export_rows(min_count=2)
        return request.make_response(
            json.dumps(rows),
            headers=[("Content-Type", "application/json"), ("Cache-Control", "no-store")],
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: Testlauf aus Global Constraints.
Expected: `TestRatingRoutes` 4/4 grün, `0 error(s)`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/controllers/radio_votes.py addons/frawo_agent/tests/test_radio_rating.py
git commit -m "feat(radio): Routen fuer Sterne-Bewertung, Aggregat und Token-Export"
```

---

### Task 3: Backend-Ansicht „⭐ Radio-Bewertungen" für Wolf

**Files:**
- Create: `addons/frawo_agent/views/radio_rating_views.xml`
- Modify: `addons/frawo_agent/__manifest__.py` (Eintrag in `data`)
- Modify: `scripts/tools/sync_odoo_files.py`

**Interfaces:**
- Consumes: Model aus Task 1.
- Produces: Menü `menu_radio_ratings` unter `menu_frawo_agent_root`.

- [ ] **Step 1: View-Datei anlegen**

`addons/frawo_agent/views/radio_rating_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_radio_rating_list" model="ir.ui.view">
        <field name="name">frawo.radio.rating.list</field>
        <field name="model">frawo.radio.rating</field>
        <field name="arch" type="xml">
            <list string="Radio-Bewertungen" default_order="write_date desc" create="false" edit="false">
                <field name="write_date" string="Zuletzt"/>
                <field name="track_id" string="Track"/>
                <field name="stars" string="Sterne"/>
                <field name="partner_id" string="Bewertet von"/>
            </list>
        </field>
    </record>

    <record id="view_radio_rating_search" model="ir.ui.view">
        <field name="name">frawo.radio.rating.search</field>
        <field name="model">frawo.radio.rating</field>
        <field name="arch" type="xml">
            <search string="Radio-Bewertungen">
                <field name="track_id"/>
                <field name="partner_id"/>
                <separator/>
                <filter name="by_track" string="Nach Track" context="{'group_by': 'track_id'}"/>
                <filter name="by_stars" string="Nach Sternen" context="{'group_by': 'stars'}"/>
            </search>
        </field>
    </record>

    <record id="action_radio_ratings" model="ir.actions.act_window">
        <field name="name">⭐ Radio-Bewertungen</field>
        <field name="res_model">frawo.radio.rating</field>
        <field name="view_mode">list</field>
        <field name="context">{"search_default_by_track": 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">Noch keine Bewertungen</p>
            <p>Hier landen die Sterne-Bewertungen angemeldeter Hörer:innen von frawo.tech/radio.</p>
        </field>
    </record>

    <menuitem id="menu_radio_ratings" name="⭐ Radio-Bewertungen"
              parent="menu_frawo_agent_root"
              action="action_radio_ratings"
              sequence="7"/>
</odoo>
```

- [ ] **Step 2: Manifest und Sync-Liste ergänzen**

In `addons/frawo_agent/__manifest__.py` in `data` nach `"views/radio_vote_views.xml",` einfügen:

```python
        "views/radio_rating_views.xml",
```

In `scripts/tools/sync_odoo_files.py` ergänzen:

```python
    "addons/frawo_agent/views/radio_rating_views.xml",
```

- [ ] **Step 3: Prüfen und deployen**

Run:
```bash
python -c "import xml.dom.minidom as m; m.parse('addons/frawo_agent/views/radio_rating_views.xml'); print('XML OK')"
python scripts/tools/sync_odoo_files.py
```
dann Testlauf aus Global Constraints (lädt die View beim Upgrade).
Expected: Zeile `loading frawo_agent/views/radio_rating_views.xml`, keine `ParseError`.

- [ ] **Step 4: Commit**

```bash
git add addons/frawo_agent/views/radio_rating_views.xml addons/frawo_agent/__manifest__.py scripts/tools/sync_odoo_files.py
git commit -m "feat(radio): Backend-Ansicht Radio-Bewertungen"
```

---

### Task 4: Frontend — Sterne-Leiste ersetzt den Banger-Knopf

**Files:**
- Modify: `addons/frawo_agent/views/radio_page.xml` (Snapshot der View 3353)

**Interfaces:**
- Consumes: `GET /radio/rating/summary`, `POST /radio/rate` (Task 2); `currentTrackKey` (bestehend); `window.ffSetLiveMode` (Plan A).
- Produces: `window.ffLoadRating()` (Aggregat nachladen), `window.ffRate(stars)` (bewerten); befüllt die bisher leere `loadVotes()`.

- [ ] **Step 1: Banger-Knopf durch Sterne-Leiste ersetzen**

Den kompletten Block `<!-- 2. Banger / Favorit (5-Sterne Rekordbox) --> … </button>` (Button `id="ff-mood-banger"`) ersetzen durch:

```xml
        <!-- 2. Sterne-Bewertung (nur angemeldet), Durchschnitt fuer alle -->
        <div class="ff-mood-btn ff-rating-box" id="ff-rating-box">
          <div class="ff-mood-btn-title">
            <span class="ff-stars" id="ff-stars" data-own="0">
              <span class="ff-star" data-v="1" onclick="if(window.ffRate) window.ffRate(1)">☆</span><span class="ff-star" data-v="2" onclick="if(window.ffRate) window.ffRate(2)">☆</span><span class="ff-star" data-v="3" onclick="if(window.ffRate) window.ffRate(3)">☆</span><span class="ff-star" data-v="4" onclick="if(window.ffRate) window.ffRate(4)">☆</span><span class="ff-star" data-v="5" onclick="if(window.ffRate) window.ffRate(5)">☆</span>
            </span>
          </div>
          <div class="ff-mood-btn-sub" id="ff-rating-sub">Noch keine Bewertung</div>
        </div>
```

Im `<style>`-Block nach `.ff-mood-tally { … }` ergänzen:

```css
.ff-rating-box { cursor: default; }
.ff-stars { letter-spacing: 2px; font-size: 1.1rem; }
.ff-star { cursor: pointer; }
.ff-star.on { color: var(--fw-accent, #a050f0); }
.ff-stars.locked .ff-star { cursor: default; opacity: 0.7; }
```

- [ ] **Step 2: JavaScript in den Tally-Block einhängen**

Im `<script>`-Block der Mood-Box (die IIFE, die `loadTally` enthält) vor `})();` ergänzen — ohne `<`, `>`, `&`:

```javascript
        var starsEl = document.getElementById('ff-stars');
        var ratingSub = document.getElementById('ff-rating-sub');
        var loggedIn = !!(window.odoo) && !!(window.odoo.session_info) && !!(window.odoo.session_info.uid) && (window.odoo.session_info.is_website_user === false);

        function paintStars(avg, own, count) {
          if (!starsEl) return;
          var fill = own ? own : Math.round(avg || 0);
          var stars = starsEl.querySelectorAll('.ff-star');
          stars.forEach(function (s) {
            var v = parseInt(s.getAttribute('data-v'), 10);
            var on = (fill - v) === Math.abs(fill - v);
            s.textContent = on ? '★' : '☆';
            if (on) { s.classList.add('on'); } else { s.classList.remove('on'); }
          });
          if (!count) { ratingSub.textContent = loggedIn ? 'Sei die erste Bewertung' : 'Noch keine Bewertung'; return; }
          var txt = 'Ø ' + avg.toFixed(1) + ' · ' + count + (count === 1 ? ' Bewertung' : ' Bewertungen');
          if (own) txt = txt + ' · deine: ' + own;
          ratingSub.textContent = txt;
        }

        window.ffLoadRating = function () {
          var key = window.currentTrackKey || '';
          if (!key) return;
          fetch('/radio/rating/summary?track_id=' + encodeURIComponent(key), { cache: 'no-store' })
            .then(function (r) { return r.json(); })
            .then(function (d) { if (d.ok) paintStars(d.average || 0, d.own || 0, d.count || 0); })
            .catch(function () {});
        };

        window.ffRate = function (stars) {
          if (!loggedIn) { ratingSub.textContent = 'Zum Bewerten bitte anmelden (Portal-Login)'; return; }
          var key = window.currentTrackKey || '';
          if (!key) return;
          fetch('/radio/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { song_id: key, stars: stars }, id: 1 })
          }).then(function (r) { return r.json(); })
            .then(function (d) {
              var res = d.result || {};
              if (res.ok) { var s = res.summary || {}; paintStars(s.average || 0, s.own || 0, s.count || 0); }
            }).catch(function () {});
        };

        if (starsEl) { if (!loggedIn) starsEl.classList.add('locked'); }
        window.ffLoadRating();
```

**Warum `(fill - v) === Math.abs(fill - v)`:** Das ist `true`, wenn `fill - v` nicht negativ ist — also „Stern v ist gefüllt" — ohne die in dieser View verbotenen Zeichen `<`, `>` und `&`.

- [ ] **Step 3: `currentTrackKey` nach außen reichen und `loadVotes()` füllen**

Im Hauptskript: direkt nach `var currentTrackKey = 'FraWo Funk';` ergänzen:

```javascript
  window.currentTrackKey = currentTrackKey;
```

Die Zuweisung `currentTrackKey = newKey;` (im Now-Playing-Abruf) erweitern zu:

```javascript
                currentTrackKey = newKey;
                window.currentTrackKey = newKey;
```

Die leere Funktion `function loadVotes() {}` ersetzen durch:

```javascript
  function loadVotes() {
    if (window.ffLoadRating) window.ffLoadRating();
  }
```

- [ ] **Step 4: Sterne während Live-Show ausblenden**

In `window.ffSetLiveMode` (Plan A) ist die Sterne-Box Teil von `.ff-mood-grid` und wird mit dem Raster ein-/ausgeblendet — **keine zusätzliche Änderung nötig.** (Prüfen: `#ff-rating-box` liegt innerhalb des ersten `.ff-mood-grid`.)

- [ ] **Step 5: Gegenprüfen**

Run:
```bash
python - <<'EOF'
import xml.dom.minidom as m
p = 'addons/frawo_agent/views/radio_page.xml'
m.parse(p); print('XML OK')
c = open(p, encoding='utf-8').read()
i = c.find('var starsEl = document.getElementById'); j = c.find('window.ffLoadRating();', i)
print('Sonderzeichen im neuen JS:', any(ch in c[i:j] for ch in '<>&'))
print('Banger-Knopf entfernt:', 'id="ff-mood-banger"' not in c)
print('loadVotes gefuellt:', 'function loadVotes() {}' not in c)
EOF
```
Expected: `XML OK`, `Sonderzeichen … False`, beide `True`.

- [ ] **Step 6: Commit**

```bash
git add addons/frawo_agent/views/radio_page.xml
git commit -m "feat(radio): Sterne-Bewertung ersetzt Banger-Knopf (Snapshot View 3353)"
```

---

### Task 5: Rekordbox-Export-Skript (StudioPC)

**Files:**
- Create: `deployments/musikverwaltung/rekordbox_sync/rating_export.py`
- Create: `deployments/musikverwaltung/rekordbox_sync/rating_export.cmd`
- Create: `deployments/musikverwaltung/rekordbox_sync/test_rating_export.py`
- Modify: `deployments/musikverwaltung/rekordbox_sync/.env.example` (Zeilen ergänzen)
- Modify: `deployments/musikverwaltung/rekordbox_sync/README.md` (Abschnitt ergänzen)

**Interfaces:**
- Consumes: `GET /radio/ratings/export` (Task 2) mit `X-Agent-Token`; `pyrekordbox.db6.Rekordbox6Database`.
- Produces: `rating_export.py` mit reinen Funktionen `rekordbox_running(process_names) -> bool`, `match_content(rows, contents) -> (matches: list[tuple[row, content]], unmatched: list[row])`, `apply_ratings(db, matches) -> int`, `ensure_favorites_playlist(db, matches, min_stars=4) -> int`; Einstieg `main()`.

- [ ] **Step 1: Write the failing test**

`deployments/musikverwaltung/rekordbox_sync/test_rating_export.py`:

```python
from types import SimpleNamespace

import rating_export as re_


def _content(title, artist, rating=0, cid=1):
    return SimpleNamespace(ID=cid, Title=title, Artist=SimpleNamespace(Name=artist), Rating=rating)


def test_match_content_exact_and_case_insensitive():
    rows = [{"track_id": "Artist|Song", "artist": "Artist", "title": "Song", "stars": 5, "count": 2, "average": 4.5},
            {"track_id": "Nobody|Nothing", "artist": "Nobody", "title": "Nothing", "stars": 3, "count": 2, "average": 3.0}]
    contents = [_content("song", "ARTIST", cid=7)]
    matches, unmatched = re_.match_content(rows, contents)
    assert len(matches) == 1 and matches[0][1].ID == 7
    assert [r["track_id"] for r in unmatched] == ["Nobody|Nothing"]


def test_apply_ratings_sets_only_changed():
    c1 = _content("A", "X", rating=5, cid=1)
    c2 = _content("B", "X", rating=2, cid=2)
    matches = [({"stars": 5}, c1), ({"stars": 4}, c2)]
    changed = re_.apply_ratings(None, matches)
    assert changed == 1
    assert c2.Rating == 4 and c1.Rating == 5


def test_rekordbox_running_detects_process_name():
    assert re_.rekordbox_running(["rekordbox.exe"], tasklist_output="rekordbox.exe  1234 Console") is True
    assert re_.rekordbox_running(["rekordbox.exe"], tasklist_output="explorer.exe  99 Console") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd deployments/musikverwaltung/rekordbox_sync && python -m pytest -q test_rating_export.py`
Expected: `ModuleNotFoundError: rating_export`.

- [ ] **Step 3: Write minimal implementation**

`deployments/musikverwaltung/rekordbox_sync/rating_export.py`:

```python
"""Stuendlicher Export der Publikums-Sterne aus Odoo nach Rekordbox.

Laeuft auf dem StudioPC (Windows-Aufgabenplanung). Schreibt NUR, wenn
Rekordbox geschlossen ist (siehe README: Schreiben bei geoeffnetem
Rekordbox ist unsicher). Abgleich Titel -> Rekordbox ueber Title + Artist.Name,
kein AzuraCast-Umweg. Nicht auffindbare Titel werden protokolliert, nie geraten.
"""
import os
import subprocess
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN", "")
PROCESS_NAMES = ["rekordbox.exe", "rekordboxAgent.exe"]
FAVORITES_NAME = "🔥 Publikums-Favoriten"
MIN_STARS_FAVORITE = 4


def log(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def rekordbox_running(process_names, tasklist_output=None):
    if tasklist_output is None:
        tasklist_output = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    low = tasklist_output.lower()
    return any(name.lower() in low for name in process_names)


def fetch_rows():
    r = requests.get(f"{ODOO_BASE}/radio/ratings/export",
                     headers={"X-Agent-Token": TOKEN}, timeout=20)
    r.raise_for_status()
    return r.json()


def _norm(s):
    return (s or "").strip().lower()


def match_content(rows, contents):
    index = {}
    for c in contents:
        artist = _norm(getattr(getattr(c, "Artist", None), "Name", ""))
        index[(artist, _norm(c.Title))] = c
    matches, unmatched = [], []
    for row in rows:
        c = index.get((_norm(row["artist"]), _norm(row["title"])))
        if c is None:
            unmatched.append(row)
        else:
            matches.append((row, c))
    return matches, unmatched


def apply_ratings(db, matches):
    changed = 0
    for row, content in matches:
        target = int(row["stars"])
        if int(content.Rating or 0) != target:
            content.Rating = target
            changed += 1
    return changed


def ensure_favorites_playlist(db, matches, min_stars=MIN_STARS_FAVORITE):
    wanted = [c for row, c in matches if int(row["stars"]) >= min_stars]
    existing = None
    for pl in db.get_playlist():
        if pl.Name == FAVORITES_NAME:
            existing = pl
            break
    if existing is None:
        existing = db.create_playlist(FAVORITES_NAME)
    present = {sp.ContentID for sp in db.get_playlist_contents(existing)} if hasattr(db, "get_playlist_contents") else set()
    added = 0
    for c in wanted:
        if c.ID not in present:
            db.add_to_playlist(existing, c)
            added += 1
    return added


def main():
    if not TOKEN:
        log("FRAWO_AGENT_TOKEN fehlt in .env - Abbruch"); return 2
    if rekordbox_running(PROCESS_NAMES):
        log("Rekordbox laeuft - Lauf uebersprungen, naechster Versuch in einer Stunde"); return 0
    rows = fetch_rows()
    log(f"{len(rows)} Titel mit mindestens 2 Bewertungen aus Odoo geholt")
    from pyrekordbox.db6 import Rekordbox6Database
    db = Rekordbox6Database()
    contents = list(db.get_content())
    matches, unmatched = match_content(rows, contents)
    changed = apply_ratings(db, matches)
    added = ensure_favorites_playlist(db, matches)
    db.commit()
    log(f"Rating gesetzt/aktualisiert: {changed} | in Favoriten neu: {added} | nicht gefunden: {len(unmatched)}")
    for row in unmatched:
        log(f"  nicht in Rekordbox: {row['track_id']}")
    expected = len(matches)
    log(f"Rueckprobe: {expected} Treffer verarbeitet, {len(rows) - expected} offen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`deployments/musikverwaltung/rekordbox_sync/rating_export.cmd`:

```bat
@echo off
cd /d "%~dp0"
python rating_export.py >> rating_export.log 2>&1
```

`.env.example` ergänzen:

```
FRAWO_ODOO_URL=https://frawo.tech
FRAWO_AGENT_TOKEN=hier-summary-token-aus-odoo-eintragen
```

`README.md` ergänzen (Abschnitt „Sterne-Export"): Zweck, Ablauf, Prozessprüfung, Log-Datei `rating_export.log`, Aufgabenplanungs-Befehl aus Task 6.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd deployments/musikverwaltung/rekordbox_sync && python -m pytest -q test_rating_export.py`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add deployments/musikverwaltung/rekordbox_sync/rating_export.py deployments/musikverwaltung/rekordbox_sync/rating_export.cmd deployments/musikverwaltung/rekordbox_sync/test_rating_export.py deployments/musikverwaltung/rekordbox_sync/.env.example deployments/musikverwaltung/rekordbox_sync/README.md
git commit -m "feat(rekordbox): stuendlicher Sterne-Export aus Odoo (nur bei geschlossenem Rekordbox)"
```

---

### Task 6: Deployment, Live-Verifikation, Aufgabenplanung

**Files:** keine Code-Änderung.

- [ ] **Step 1: Odoo deployen**

```bash
python scripts/tools/sync_odoo_files.py
```
dann Testlauf aus Global Constraints (Upgrade + alle Tests). Expected: `0 error(s)`.
Danach Container-Neustart (Freigabe Wolf): `ssh stock-pve "pct exec 140 -- docker restart frawotech-web-1"`.

- [ ] **Step 2: Live-View 3353 schreiben**

Drift-Check (Live-Hash = letzter Snapshot), Backup `view3353.arch_db.bak-YYYYMMDD-N.xml` nach `/opt/frawotech/extra-addons/frawo_agent/`, ORM-Write aus `/tmp/view3353_new.xml`, Neustart, `curl https://frawo.tech/radio` → 200 und `id="ff-rating-box"` im HTML, keine neuen `&amp;lt;`.

- [ ] **Step 3: Browser-Verifikation (anonym)**

Chrome: `/radio` laden → Sterne sichtbar, `.ff-stars.locked`, Klick auf Stern zeigt „Zum Bewerten bitte anmelden". `GET /radio/rating/summary?track_id=…` liefert 200. Konsole: keine neuen Fehler.

- [ ] **Step 4: Echte Bewertung durch Wolf (DoD 5)**

Wolf bewertet vom Handy angemeldet einen Titel mit 4 Sternen, dann denselben mit 2. Prüfen: Anzeige zeigt Durchschnitt und „deine: 2", `frawo.radio.rating` hat **einen** Datensatz für Wolf+Titel, Backend-Menü „⭐ Radio-Bewertungen" zeigt ihn.

- [ ] **Step 5: Export-Token und `.env` auf dem StudioPC**

`frawo_agent.summary_token` in Odoo prüfen (existiert für `/api/agent/summary`; falls `SETZE_…`, neuen Wert setzen). In `deployments/musikverwaltung/rekordbox_sync/.env` `FRAWO_ODOO_URL` und `FRAWO_AGENT_TOKEN` eintragen (nie committen). Test: `curl -s -H "X-Agent-Token: …" https://frawo.tech/radio/ratings/export` → JSON-Liste.

- [ ] **Step 6: Manueller Export-Lauf + Rekordbox-Kontrolle**

Rekordbox geschlossen → `python rating_export.py` → Log zeigt Treffer/Nicht-gefunden. Rekordbox öffnen: bewerteter Titel zeigt die Sterne, Playlist „🔥 Publikums-Favoriten" existiert (bei Ø ≥ 4).

- [ ] **Step 7: Aufgabenplanung registrieren (Wolf führt aus)**

Befehl vorbereiten, Wolf startet ihn mit `! …`:

```bat
schtasks /Create /TN "FraWo Rekordbox Sterne-Export" /TR "C:\Users\StudioPC\FraWo\deployments\musikverwaltung\rekordbox_sync\rating_export.cmd" /SC HOURLY /F
```
Prüfen: `schtasks /Query /TN "FraWo Rekordbox Sterne-Export"`. Nach dem ersten automatischen Lauf `rating_export.log` lesen.

- [ ] **Step 8: Dokumentation, Review, Zeit**

`NOW.md` (Radio-Abschnitt: Teil B live, Export-Task, Log-Pfad, Token-Fundort), Odoo-Task: Chatter mit Belegen, `@🦞 OpenClaw (Jarvis)` Review, Stage bleibt „In Arbeit", Zeiterfassung (`employee_id` 11).

- [ ] **Step 9: Commit**

```bash
git add NOW.md
git commit -m "docs(NOW.md): Sterne-Bewertung + Rekordbox-Export live"
```
