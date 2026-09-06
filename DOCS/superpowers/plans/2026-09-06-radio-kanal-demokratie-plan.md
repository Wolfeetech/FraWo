# Radio-Kanal-Demokratie Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Energy-/Chill-Votes der Hörer:innen verschieben die Gewichte der vier AzuraCast-Rotations-Playlisten wirklich, kollektiv über ein 15-Minuten-Fenster — und während einer Live-Show wird gar nicht gesteuert.

**Architecture:** Ein Odoo-Cron (alle 5 Min) zählt Votes aus `frawo.radio.vote`, berechnet Zielgewichte (reine Funktion, ohne Seiteneffekte, damit testbar), und schreibt sie über die AzuraCast-REST-API. Ein dünner API-Client-Model kapselt HTTP. Das Frontend blendet die Steuer-Buttons aus, sobald ein Live-DJ sendet.

**Tech Stack:** Odoo 19 (Addon `frawo_agent`), Python `requests`, AzuraCast REST-API, QWeb-View 3353 (`arch_db`), Deployment über `scripts/tools/sync_odoo_files.py`.

**Spec:** `DOCS/superpowers/specs/2026-09-06-radio-demokratie-design.md`

## Global Constraints

- **Basisgewicht je Kanal: 3.** Untergrenze **1**, Obergrenze **6**. Nie darüber hinaus schreiben.
- **Maximal ±1 Gewichtsschritt pro Cron-Lauf** je Playlist (kein Springen).
- **Zeitfenster für Votes: 15 Minuten.** Cron-Intervall: 5 Minuten.
- **Kill-Switch:** `ir.config_parameter` `frawo_agent.radio_democracy_enabled`. Fehlt der Parameter oder ist er nicht exakt `"true"` → Cron beendet sich sofort ohne Änderung (fail-closed).
- **Schreiben ausschließlich über die AzuraCast-REST-API**, niemals per MariaDB-Direktzugriff (sonst wäre ein Sender-Neustart nötig, siehe `NOW.md`-Fallentabelle).
- **Kanal-Playlist-IDs** (Stand `NOW.md`): Ch1 Acoustik&Ambient = 846, Ch2 Soft Groove = 847, Ch3 Harder Styles = 848, Ch4 Roadtrip&Classics = 849. Chill-Gruppe = {846, 847}, Energy-Gruppe = {848, 849}. Als Config-Parameter hinterlegt, nicht hart im Code.
- **Keine Secrets im Repo.** API-Key kommt aus `ir.config_parameter` `frawo_agent.azuracast_api_key`.
- **JavaScript in View 3353:** kein literales `<`, `>` oder `&` im neuen Code (umschreiben statt escapen) — dokumentierte QWeb-Escape-Falle.
- **Tests:** Odoo `TransactionCase`, `@tagged("post_install", "-at_install", "frawo_agent")`, HTTP immer mit `unittest.mock.patch` abfangen. Testlauf:
  `ssh stock-pve "pct exec 140 -- docker exec frawotech-web-1 sh -c 'odoo -d FraWo_GbR -u frawo_agent --test-enable --test-tags frawo_agent --stop-after-init --no-http --db_host=\"\$HOST\" --db_user=\"\$USER\" --db_password=\"\$PASSWORD\"'"`

---

### Task 1: AzuraCast-API-Client (Playlisten lesen und Gewicht schreiben)

**Files:**
- Create: `addons/frawo_agent/models/radio_azuracast.py`
- Modify: `addons/frawo_agent/models/__init__.py` (Import ergänzen)
- Modify: `addons/frawo_agent/security/ir.model.access.csv` (Lesezugriff für interne Benutzer)
- Test: `addons/frawo_agent/tests/test_radio_democracy.py`

**Interfaces:**
- Consumes: nichts (erste Aufgabe).
- Produces: Model `frawo.radio.azuracast` mit
  - `_api_config() -> tuple[str, str]` — `(base_url, api_key)`, base_url ohne Slash am Ende
  - `list_playlists() -> list[dict]` — Rohantwort von `GET /api/station/1/playlists`
  - `get_weights(playlist_ids: list[int]) -> dict[int, int]` — aktuelles Gewicht je ID
  - `set_weight(playlist_id: int, weight: int) -> bool` — `PUT /api/station/1/playlist/{id}`, True bei HTTP 200

- [ ] **Step 1: Write the failing test**

In `addons/frawo_agent/tests/test_radio_democracy.py`:

```python
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestAzuracastClient(TransactionCase):

    def setUp(self):
        super().setUp()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("frawo_agent.azuracast_api_url", "https://radio.test/")
        ICP.set_param("frawo_agent.azuracast_api_key", "testkey")

    def test_api_config_strips_trailing_slash(self):
        base, key = self.env["frawo.radio.azuracast"]._api_config()
        self.assertEqual(base, "https://radio.test")
        self.assertEqual(key, "testkey")

    def test_get_weights_maps_id_to_weight(self):
        payload = [
            {"id": 846, "name": "Ch1", "weight": 3},
            {"id": 848, "name": "Ch3", "weight": 5},
            {"id": 999, "name": "Andere", "weight": 1},
        ]
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.get") as m:
            m.return_value.status_code = 200
            m.return_value.json.return_value = payload
            out = self.env["frawo.radio.azuracast"].get_weights([846, 848])
        self.assertEqual(out, {846: 3, 848: 5})

    def test_set_weight_sends_put_and_reports_success(self):
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.put") as m:
            m.return_value.status_code = 200
            ok = self.env["frawo.radio.azuracast"].set_weight(846, 4)
            called_url = m.call_args.args[0]
            sent = m.call_args.kwargs["json"]
        self.assertTrue(ok)
        self.assertIn("/playlist/846", called_url)
        self.assertEqual(sent["weight"], 4)

    def test_set_weight_failure_returns_false(self):
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.put") as m:
            m.return_value.status_code = 500
            ok = self.env["frawo.radio.azuracast"].set_weight(846, 4)
        self.assertFalse(ok)
```

- [ ] **Step 2: Run test to verify it fails**

Run the test command from Global Constraints.
Expected: FAIL — `KeyError: 'frawo.radio.azuracast'` (Model existiert noch nicht).

- [ ] **Step 3: Write minimal implementation**

`addons/frawo_agent/models/radio_azuracast.py`:

```python
# -*- coding: utf-8 -*-
"""Duenner Client fuer die AzuraCast-REST-API (nur was die Kanal-Demokratie braucht).

Bewusst REST statt MariaDB-Direktzugriff: nach direkten DB-Aenderungen
muesste der Sender neu gestartet werden (NOW.md-Fallentabelle), ueber die
API benachrichtigt AzuraCast liquidsoap selbst.
"""
import logging

import requests
import urllib3

from odoo import models

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

STATION_ID = 1
TIMEOUT = 10


class FrawoRadioAzuracast(models.AbstractModel):
    _name = "frawo.radio.azuracast"
    _description = "AzuraCast REST-Client (Playlisten-Gewichte)"

    def _api_config(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        base = (get_param("frawo_agent.azuracast_api_url", "") or "").rstrip("/")
        key = get_param("frawo_agent.azuracast_api_key", "") or ""
        return base, key

    def _headers(self):
        _, key = self._api_config()
        return {"X-API-Key": key}

    def list_playlists(self):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlists"
        resp = requests.get(url, headers=self._headers(), verify=False, timeout=TIMEOUT)
        if resp.status_code != 200:
            _logger.warning("AzuraCast-Playlisten nicht lesbar (HTTP %s)", resp.status_code)
            return []
        return resp.json()

    def get_weights(self, playlist_ids):
        wanted = set(playlist_ids)
        out = {}
        for pl in self.list_playlists():
            if pl.get("id") in wanted:
                out[pl["id"]] = pl.get("weight")
        return out

    def set_weight(self, playlist_id, weight):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlist/{playlist_id}"
        resp = requests.put(
            url, headers=self._headers(), json={"weight": weight},
            verify=False, timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            _logger.warning(
                "Gewicht fuer Playlist %s nicht gesetzt (HTTP %s)",
                playlist_id, resp.status_code,
            )
            return False
        return True
```

In `addons/frawo_agent/models/__init__.py` ergänzen (ans Ende):

```python
from . import radio_azuracast
```

In `addons/frawo_agent/security/ir.model.access.csv` ergänzen — AbstractModel braucht keinen Eintrag, daher **keine Änderung nötig**. (Schritt bewusst dokumentiert, damit niemand danach sucht.)

- [ ] **Step 4: Run test to verify it passes**

Run the test command from Global Constraints.
Expected: PASS, 4 Tests in `TestAzuracastClient`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/models/radio_azuracast.py addons/frawo_agent/models/__init__.py addons/frawo_agent/tests/test_radio_democracy.py
git commit -m "feat(radio): AzuraCast-Client fuer Playlisten-Gewichte"
```

---

### Task 2: Gewichtsberechnung (reine Logik, ohne HTTP)

**Files:**
- Modify: `addons/frawo_agent/models/radio_vote.py`
- Test: `addons/frawo_agent/tests/test_radio_democracy.py` (Klasse ergänzen)

**Interfaces:**
- Consumes: nichts aus Task 1 (bewusst getrennt, damit ohne HTTP testbar).
- Produces: `frawo.radio.vote._compute_targets(current, energy, chill) -> dict[int, int]`
  - `current`: `dict[int, int]` — Playlist-ID → aktuelles Gewicht
  - `energy`, `chill`: `int` — Stimmenzahl im Fenster
  - Rückgabe: Playlist-ID → **neues** Gewicht (nur geänderte Einträge enthalten)
  - Nutzt Konstanten `BASE_WEIGHT = 3`, `MIN_WEIGHT = 1`, `MAX_WEIGHT = 6`, `VOTE_MARGIN = 2`

- [ ] **Step 1: Write the failing test**

In `addons/frawo_agent/tests/test_radio_democracy.py` ergänzen:

```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestWeightMath(TransactionCase):

    CHILL = [846, 847]
    ENERGY = [848, 849]

    def _compute(self, current, energy, chill):
        return self.env["frawo.radio.vote"]._compute_targets(current, energy, chill)

    def test_no_votes_returns_to_base(self):
        current = {846: 5, 847: 4, 848: 2, 849: 1}
        out = self._compute(current, energy=0, chill=0)
        self.assertEqual(out, {846: 4, 847: 3, 848: 3, 849: 2})

    def test_no_votes_at_base_changes_nothing(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=0, chill=0)
        self.assertEqual(out, {})

    def test_energy_majority_shifts_one_step(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=5, chill=1)
        self.assertEqual(out, {846: 2, 847: 2, 848: 4, 849: 4})

    def test_chill_majority_shifts_one_step(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=0, chill=3)
        self.assertEqual(out, {846: 4, 847: 4, 848: 2, 849: 2})

    def test_margin_below_threshold_changes_nothing(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=3, chill=2)
        self.assertEqual(out, {})

    def test_upper_bound_is_respected(self):
        current = {846: 1, 847: 1, 848: 6, 849: 6}
        out = self._compute(current, energy=9, chill=0)
        self.assertEqual(out, {})

    def test_lower_bound_is_respected(self):
        current = {846: 6, 847: 6, 848: 1, 849: 1}
        out = self._compute(current, energy=0, chill=9)
        self.assertEqual(out, {})
```

- [ ] **Step 2: Run test to verify it fails**

Run the test command from Global Constraints.
Expected: FAIL — `AttributeError: '_compute_targets'`.

- [ ] **Step 3: Write minimal implementation**

In `addons/frawo_agent/models/radio_vote.py` die Import-Zeile oben erweitern (Bestand ist `from odoo import models, fields`):

```python
from odoo import api, fields, models
```

Modul-Konstanten direkt unter den Imports:

```python
BASE_WEIGHT = 3
MIN_WEIGHT = 1
MAX_WEIGHT = 6
VOTE_MARGIN = 2
```

Beide Methoden in der Klasse `FrawoRadioVote`:

```python
    @api.model
    def _channel_groups(self):
        """Playlist-IDs je Stimmungsrichtung, aus den Systemparametern."""
        get_param = self.env["ir.config_parameter"].sudo().get_param

        def _ids(key, default):
            raw = get_param(key, default) or ""
            return [int(p) for p in raw.replace(" ", "").split(",") if p]

        return (
            _ids("frawo_agent.radio_chill_playlist_ids", "846,847"),
            _ids("frawo_agent.radio_energy_playlist_ids", "848,849"),
        )

    @api.model
    def _compute_targets(self, current, energy, chill):
        """Zielgewichte berechnen. Reine Funktion: kein HTTP, keine Seiteneffekte.

        Ohne klare Mehrheit (Abstand kleiner VOTE_MARGIN) wandert jedes Gewicht
        einen Schritt Richtung BASE_WEIGHT zurueck. Mit Mehrheit bekommt die
        gewaehlte Richtung einen Schritt mehr, die Gegenrichtung einen weniger.
        Alles hart auf MIN_WEIGHT..MAX_WEIGHT begrenzt, maximal ein Schritt.
        """
        chill_ids, energy_ids = self._channel_groups()
        margin = energy - chill

        if abs(margin) >= VOTE_MARGIN:
            direction = {}
            for pid in energy_ids:
                direction[pid] = 1 if margin > 0 else -1
            for pid in chill_ids:
                direction[pid] = -1 if margin > 0 else 1
        else:
            direction = {}
            for pid, weight in current.items():
                if weight > BASE_WEIGHT:
                    direction[pid] = -1
                elif weight < BASE_WEIGHT:
                    direction[pid] = 1

        targets = {}
        for pid, step in direction.items():
            old = current.get(pid)
            if old is None:
                continue
            new = min(MAX_WEIGHT, max(MIN_WEIGHT, old + step))
            if new != old:
                targets[pid] = new
        return targets
```

- [ ] **Step 4: Run test to verify it passes**

Run the test command from Global Constraints.
Expected: PASS, 7 Tests in `TestWeightMath`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/models/radio_vote.py addons/frawo_agent/tests/test_radio_democracy.py
git commit -m "feat(radio): Gewichtsberechnung aus Energy/Chill-Votes"
```

---

### Task 3: Cron-Methode, die beides verbindet

**Files:**
- Modify: `addons/frawo_agent/models/radio_vote.py`
- Test: `addons/frawo_agent/tests/test_radio_democracy.py` (Klasse ergänzen)

**Interfaces:**
- Consumes: `frawo.radio.azuracast.get_weights/set_weight` (Task 1), `_compute_targets/_channel_groups` (Task 2).
- Produces: `frawo.radio.vote._cron_apply_vote_weights() -> None` — wird vom Cron-Record (Task 4) aufgerufen.

- [ ] **Step 1: Write the failing test**

In `addons/frawo_agent/tests/test_radio_democracy.py` die beiden Imports **oben zu den bestehenden Imports** ergänzen:

```python
from datetime import timedelta
from odoo import fields
```

und die Testklasse ans Dateiende anfügen:

```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestDemocracyCron(TransactionCase):

    def setUp(self):
        super().setUp()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("frawo_agent.radio_democracy_enabled", "true")
        ICP.set_param("frawo_agent.radio_chill_playlist_ids", "846,847")
        ICP.set_param("frawo_agent.radio_energy_playlist_ids", "848,849")
        self.env["frawo.radio.vote"].search([]).unlink()

    def _vote(self, vote_type, minutes_ago=0):
        rec = self.env["frawo.radio.vote"].create({
            "track_id": "T", "vote_type": vote_type, "voter_ip": "1.2.3.4",
        })
        if minutes_ago:
            self.env.cr.execute(
                "UPDATE frawo_radio_vote SET create_date = %s WHERE id = %s",
                (fields.Datetime.now() - timedelta(minutes=minutes_ago), rec.id),
            )
            rec.invalidate_recordset()
        return rec

    def test_disabled_switch_writes_nothing(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "frawo_agent.radio_democracy_enabled", "false")
        self._vote("energy")
        self._vote("energy")
        self._vote("energy")
        with patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.set_weight") as m:
            self.env["frawo.radio.vote"]._cron_apply_vote_weights()
        self.assertFalse(m.called)

    def test_energy_majority_writes_new_weights(self):
        for _ in range(4):
            self._vote("energy")
        with patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.get_weights",
                   return_value={846: 3, 847: 3, 848: 3, 849: 3}), \
             patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.set_weight", return_value=True) as m:
            self.env["frawo.radio.vote"]._cron_apply_vote_weights()
        written = {c.args[0]: c.args[1] for c in m.call_args_list}
        self.assertEqual(written, {846: 2, 847: 2, 848: 4, 849: 4})

    def test_votes_outside_window_are_ignored(self):
        for _ in range(4):
            self._vote("energy", minutes_ago=30)
        with patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.get_weights",
                   return_value={846: 3, 847: 3, 848: 3, 849: 3}), \
             patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.set_weight", return_value=True) as m:
            self.env["frawo.radio.vote"]._cron_apply_vote_weights()
        self.assertFalse(m.called)

    def test_writes_a_log_entry(self):
        for _ in range(4):
            self._vote("chill")
        before = self.env["frawo.agent.log"].search_count([])
        with patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.get_weights",
                   return_value={846: 3, 847: 3, 848: 3, 849: 3}), \
             patch("odoo.addons.frawo_agent.models.radio_azuracast."
                   "FrawoRadioAzuracast.set_weight", return_value=True):
            self.env["frawo.radio.vote"]._cron_apply_vote_weights()
        self.assertGreater(self.env["frawo.agent.log"].search_count([]), before)
```

- [ ] **Step 2: Run test to verify it fails**

Run the test command from Global Constraints.
Expected: FAIL — `AttributeError: '_cron_apply_vote_weights'`.

- [ ] **Step 3: Write minimal implementation**

In `addons/frawo_agent/models/radio_vote.py` ergänzen — oben:

```python
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

VOTE_WINDOW_MINUTES = 15
```

und als Methode in der Klasse:

```python
    @api.model
    def _cron_apply_vote_weights(self):
        """Verschiebt die Kanal-Gewichte anhand der Votes der letzten Minuten."""
        ICP = self.env["ir.config_parameter"].sudo()
        if (ICP.get_param("frawo_agent.radio_democracy_enabled", "") or "").strip().lower() != "true":
            return

        cutoff = fields.Datetime.now() - timedelta(minutes=VOTE_WINDOW_MINUTES)
        energy = self.search_count([
            ("create_date", ">=", cutoff), ("vote_type", "=", "energy")])
        chill = self.search_count([
            ("create_date", ">=", cutoff), ("vote_type", "=", "chill")])

        chill_ids, energy_ids = self._channel_groups()
        api_client = self.env["frawo.radio.azuracast"]
        current = api_client.get_weights(chill_ids + energy_ids)
        if not current:
            _logger.warning("Radio-Demokratie: keine Gewichte lesbar, Lauf uebersprungen.")
            return

        targets = self._compute_targets(current, energy, chill)
        if not targets:
            return

        written, failed = {}, []
        for pid, weight in targets.items():
            if api_client.set_weight(pid, weight):
                written[pid] = weight
            else:
                failed.append(pid)

        # Am Ergebnis pruefen, nicht am Vorgang: Gewichte zurueckelesen.
        verify = api_client.get_weights(list(targets.keys()))
        mismatch = {pid: (targets[pid], verify.get(pid))
                    for pid in targets if verify.get(pid) != targets[pid]}

        self.env["frawo.agent.log"].sudo().create({
            "name": "Radio-Demokratie: Gewichte angepasst",
            "level": "warning" if (failed or mismatch) else "info",
            "message": (
                f"Fenster {VOTE_WINDOW_MINUTES} Min: energy={energy}, chill={chill}. "
                f"Vorher={current}. Ziel={targets}. Geschrieben={written}. "
                f"Fehlgeschlagen={failed}. Abweichung nach Rueckprobe={mismatch}."
            ),
        })
```

- [ ] **Step 4: Run test to verify it passes**

Run the test command from Global Constraints.
Expected: PASS, 4 Tests in `TestDemocracyCron`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/models/radio_vote.py addons/frawo_agent/tests/test_radio_democracy.py
git commit -m "feat(radio): Cron verbindet Vote-Auswertung mit AzuraCast-Gewichten"
```

---

### Task 4: Cron-Record und Systemparameter ausliefern

**Files:**
- Modify: `addons/frawo_agent/data/ir_cron.xml`
- Modify: `addons/frawo_agent/data/config_params.xml`
- Modify: `scripts/tools/sync_odoo_files.py` (neue Dateien in `FILES_TO_SYNC`)

**Interfaces:**
- Consumes: `frawo.radio.vote._cron_apply_vote_weights()` (Task 3).
- Produces: Cron-Record `cron_radio_democracy`, Parameter `frawo_agent.radio_democracy_enabled` (Default `false`), `frawo_agent.radio_chill_playlist_ids`, `frawo_agent.radio_energy_playlist_ids`.

- [ ] **Step 1: Cron-Record ergänzen**

In `addons/frawo_agent/data/ir_cron.xml` innerhalb `<data noupdate="1">` ergänzen:

```xml
    <record id="cron_radio_democracy" model="ir.cron">
      <field name="name">FraWo Radio: Kanal-Gewichte aus Hörer-Votes</field>
      <field name="model_id" ref="model_frawo_radio_vote"/>
      <field name="state">code</field>
      <field name="code">model._cron_apply_vote_weights()</field>
      <field name="interval_number">5</field>
      <field name="interval_type">minutes</field>
      <field name="active" eval="True"/>
      <field name="user_id" ref="base.user_root"/>
    </record>
```

- [ ] **Step 2: Systemparameter ergänzen**

In `addons/frawo_agent/data/config_params.xml` innerhalb `<data noupdate="1">` ergänzen:

```xml
    <record id="param_radio_democracy_enabled" model="ir.config_parameter">
      <field name="key">frawo_agent.radio_democracy_enabled</field>
      <field name="value">false</field>
    </record>
    <record id="param_radio_chill_playlists" model="ir.config_parameter">
      <field name="key">frawo_agent.radio_chill_playlist_ids</field>
      <field name="value">846,847</field>
    </record>
    <record id="param_radio_energy_playlists" model="ir.config_parameter">
      <field name="key">frawo_agent.radio_energy_playlist_ids</field>
      <field name="value">848,849</field>
    </record>
```

Default bewusst `false`: Der Cron läuft nach dem Deploy zunächst wirkungslos mit, bis er in Task 6 nach der Live-Prüfung bewusst eingeschaltet wird.

- [ ] **Step 3: Sync-Liste ergänzen**

In `scripts/tools/sync_odoo_files.py` in `FILES_TO_SYNC` ergänzen:

```python
    "addons/frawo_agent/models/radio_azuracast.py",
    "addons/frawo_agent/data/ir_cron.xml",
    "addons/frawo_agent/data/config_params.xml",
    "addons/frawo_agent/tests/test_radio_democracy.py",
```

- [ ] **Step 4: Modul-Upgrade lokal gegenprüfen**

Run:
```bash
python -m py_compile addons/frawo_agent/models/radio_azuracast.py addons/frawo_agent/models/radio_vote.py
python -c "import xml.dom.minidom as m; m.parse('addons/frawo_agent/data/ir_cron.xml'); m.parse('addons/frawo_agent/data/config_params.xml'); print('XML OK')"
```
Expected: keine Ausgabe von `py_compile`, `XML OK` von der zweiten Zeile.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/data/ir_cron.xml addons/frawo_agent/data/config_params.xml scripts/tools/sync_odoo_files.py
git commit -m "feat(radio): Cron-Record und Systemparameter fuer die Kanal-Demokratie"
```

---

### Task 5: Frontend — während einer Live-Show nicht steuern

**Files:**
- Modify: `addons/frawo_agent/views/radio_page.xml` (lokale Kopie der Live-View 3353)

**Interfaces:**
- Consumes: `data.live.is_live` aus dem Now-Playing-Payload (wird in `loadNowPlaying()` bereits gelesen).
- Produces: sichtbares Umschalten der Mood-Box; keine Backend-Schnittstelle.

- [ ] **Step 1: Reaktions-Ansicht ins Markup einfügen**

In `addons/frawo_agent/views/radio_page.xml` direkt **nach** dem schließenden `</div>` der `ff-mood-grid` und **vor** `<div class="ff-mood-tally" id="ff-mood-tally">` einfügen:

```xml
      <div class="ff-mood-grid" id="ff-show-reactions" style="display:none;">
        <button class="ff-mood-btn" type="button" onclick="if(window.ffShowReaction) window.ffShowReaction('👏')">
          <div class="ff-mood-btn-title"><span>👏</span> Applaus</div>
          <div class="ff-mood-btn-sub">Für den DJ</div>
        </button>
        <button class="ff-mood-btn" type="button" onclick="if(window.ffShowReaction) window.ffShowReaction('🔥')">
          <div class="ff-mood-btn-title"><span>🔥</span> Feuer</div>
          <div class="ff-mood-btn-sub">Geht ab</div>
        </button>
        <button class="ff-mood-btn" type="button" onclick="if(window.ffShowReaction) window.ffShowReaction('❤️')">
          <div class="ff-mood-btn-title"><span>❤️</span> Liebe</div>
          <div class="ff-mood-btn-sub">Für den Mix</div>
        </button>
      </div>
```

- [ ] **Step 2: Umschalt-Logik ergänzen**

Im vorhandenen `<script>`-Block am Ende der Mood-Box (der Block, der `ff-mood-tally` befüllt) **innerhalb der bestehenden IIFE** ergänzen:

```javascript
        window.ffShowReaction = function (emoji) {
          if (window.spawnReaction) window.spawnReaction(emoji);
        };

        window.ffSetLiveMode = function (isLive) {
          var voteGrid = document.querySelector('.ff-mood-grid');
          var showGrid = document.getElementById('ff-show-reactions');
          var tally = document.getElementById('ff-mood-tally');
          if (!voteGrid) return;
          if (!showGrid) return;
          if (isLive) {
            voteGrid.style.display = 'none';
            showGrid.style.display = '';
            if (tally) tally.textContent = 'Live-Show läuft — der DJ übernimmt';
            return;
          }
          voteGrid.style.display = '';
          showGrid.style.display = 'none';
        };
```

Kein `<`, `>` oder `&` im neuen Code — bewusst mit `if (...) return;` statt `&&` geschrieben.

- [ ] **Step 3: An den Now-Playing-Abruf anschließen**

In `loadNowPlaying()` direkt nach der bestehenden Zeile `var live = data.live || {};` ergänzen:

```javascript
        if (window.ffSetLiveMode) window.ffSetLiveMode(!!live.is_live);
```

- [ ] **Step 4: Gegenprüfen, dass die Datei gültig bleibt**

Run:
```bash
python -c "import xml.dom.minidom as m; m.parse(r'addons/frawo_agent/views/radio_page.xml'); print('XML OK')"
python - <<'EOF'
with open(r'addons/frawo_agent/views/radio_page.xml', encoding='utf-8') as f:
    c = f.read()
i = c.find('window.ffSetLiveMode = function')
j = c.find('};', i)
print('Sonderzeichen im neuen Code:', any(ch in c[i:j] for ch in '<>&'))
EOF
```
Expected: `XML OK` und `Sonderzeichen im neuen Code: False`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent/views/radio_page.xml
git commit -m "feat(radio): waehrend Live-Show Reaktionen statt Steuerung"
```

---

### Task 6: Deployment und Live-Verifikation

**Files:**
- Keine Code-Änderung. Deployment + Nachweis.

**Interfaces:**
- Consumes: alles aus Task 1–5.
- Produces: laufende Automatik auf CT140, dokumentierter Nachweis im Odoo-Task.

- [ ] **Step 1: Dateien nach CT140 synchronisieren**

Run:
```bash
python scripts/tools/sync_odoo_files.py
```
Expected: jede Zeile endet mit `[OK] Success`.

- [ ] **Step 2: Modul-Upgrade und Testlauf auf CT140**

Run (eine Zeile):
```bash
ssh -o BatchMode=yes stock-pve "pct exec 140 -- docker exec frawotech-web-1 sh -c 'odoo -d FraWo_GbR -u frawo_agent --test-enable --test-tags frawo_agent --stop-after-init --no-http --db_host=\"\$HOST\" --db_user=\"\$USER\" --db_password=\"\$PASSWORD\"'"
```
Expected: `0 failed, 0 error(s)` in der Zusammenfassung; Cron-Record und Parameter geladen.

- [ ] **Step 3: Container neu starten und Grundzustand prüfen**

Run:
```bash
ssh -o BatchMode=yes stock-pve "pct exec 140 -- docker restart frawotech-web-1"
sleep 10
curl -s -o /dev/null -w "radio: %{http_code}\n" https://frawo.tech/radio --max-time 15
```
Expected: `radio: 200`.

- [ ] **Step 4: Trockenlauf mit ausgeschaltetem Schalter**

Aktuelle Gewichte notieren, Cron einmal von Hand auslösen, prüfen dass sich **nichts** ändert (Schalter steht auf `false`):

```bash
ssh -o BatchMode=yes stock-pve "pct exec 140 -- docker exec -i frawotech-web-1 sh -c 'odoo shell -d FraWo_GbR --db_host=\"\$HOST\" --db_user=\"\$USER\" --db_password=\"\$PASSWORD\" --no-http'" <<'EOF'
print(env['frawo.radio.azuracast'].get_weights([846,847,848,849]))
env['frawo.radio.vote']._cron_apply_vote_weights()
print(env['frawo.radio.azuracast'].get_weights([846,847,848,849]))
EOF
```
Expected: beide Ausgaben identisch.

- [ ] **Step 5: Scharfschalten und echten Effekt nachweisen**

Schalter auf `true` setzen, drei Chill-Votes über die echte öffentliche Route senden, Cron auslösen, Gewichte vergleichen, danach Testvotes entfernen:

```bash
curl -s -X POST https://frawo.tech/radio/vote -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"song_id":"__abnahme__","vote_type":"chill"},"id":1}'
```
(dreimal, mit jeweils anderem `song_id`-Suffix, damit die 5-Sekunden-Dedupe nicht greift)

Erwartung: Ch1/Ch2 je +1, Ch3/Ch4 je −1, Log-Eintrag in `frawo.agent.log` vorhanden. Danach Testvotes löschen:

```python
env['frawo.radio.vote'].sudo().search([('track_id','like','__abnahme__%')]).unlink()
env.cr.commit()
```

- [ ] **Step 6: Ergebnis dokumentieren und Review anfordern**

Odoo-Task anlegen bzw. bespielen: Chatter-Eintrag mit Vorher/Nachher-Gewichten, Testlauf-Ausgabe, Schalterzustand. Danach `@🦞 OpenClaw (Jarvis)` um Review bitten, Stage auf „In Arbeit" lassen (AGENTS.md Vier-Augen-Prinzip). Zeit erfassen (`account.analytic.line`, `employee_id` 11).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore(radio): Kanal-Demokratie live geschaltet und abgenommen"
```
