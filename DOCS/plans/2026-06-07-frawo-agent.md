# `frawo_agent` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein Odoo-17-Addon, das jeden neuen `project.task` autonom als „🤖 Agent" (UID 7) nach CI ausformuliert, rollengerecht taggt und Owner/Deadline als Freigabe-Vorschlag anlegt — alles in Odoo, Gehirn = lokales Ollama.

**Architecture:** Override von `project.task.create()` setzt `agent_state='queued'` (statt fragiler UI-Automation). Ein `ir.cron`, der **als UID 7 läuft**, greift **genau 1** Task pro Takt auf, ruft Ollama per HTTP (hartes 90-Sek-Timeout), schreibt Beschreibung+Tags+Chatter autonom und legt für Owner/Deadline eine `mail.activity` als Vorschlag an. Ein `frawo.agent.log`-Modell + Menü bildet das Cockpit/Logbuch.

**Tech Stack:** Odoo 17 (Python), PostgreSQL 15, Ollama (`llama3:8b`) via HTTP, `requests` (in Odoo gebündelt).

---

## Deployment-Kontext (gilt für alle Tasks)

- **Zielhost:** `frawo-docker-1` (SSH-Alias, Key `hs27_ops_ed25519`). Container `odoo-web` (image `odoo:17`), DB `FraWo_GbR`.
- **Addon-Pfad im Container:** `/mnt/extra-addons/frawo_agent` (Docker-Volume, von Host gemountet).
- **Dev-Workspace (Host):** `~/workspace/frawo_agent/` auf frawo-docker-1 — dort entwickeln, dann ins Volume kopieren.
- **Ollama-Endpoint aus odoo-web:** `http://172.17.0.1:11434` (Host-Gateway; verifiziert erreichbar).
- **Agent-User:** UID 7 „🤖 Agent" (agent@frawo.tech).
- **Rollen-Tags (existieren):** DevOps-Agent=75, Review-Wolf=76, Handwerk-Franz=77.

### Hilfsbefehle (immer gleich)

Addon ins Volume spiegeln + Modul aktualisieren + Tests:
```bash
# auf frawo-docker-1:
VOL=$(docker inspect odoo-web --format '{{range .Mounts}}{{if eq .Destination "/mnt/extra-addons"}}{{.Source}}{{end}}{{end}}')
sudo rsync -a --delete ~/workspace/frawo_agent/ "$VOL/frawo_agent/"
# Modul updaten + Tests laufen (eigene DB-Kopie empfohlen; hier direkt):
docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30
```

Schnell-Verify ohne Tests (Modul lädt fehlerfrei?):
```bash
docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --stop-after-init --no-http 2>&1 | tail -15
# Erwartung: "Modules loaded." ohne Traceback
```

> ⚠️ **Vor dem ersten Install:** Snapshot/Backup der Odoo-DB (best practice, Container-Eingriff). Mit Wolf abstimmen (Wartungsfenster).

---

## File Structure

```
addons/frawo_agent/
├── __init__.py                 # importiert models
├── __manifest__.py             # Modul-Metadaten, depends, data
├── models/
│   ├── __init__.py
│   ├── ollama_client.py        # AbstractModel: HTTP-Call zu Ollama, Timeout-Guard
│   ├── task_formatter.py       # AbstractModel: Rollen-Erkennung + Prompt-Bau (rein, testbar)
│   ├── project_task.py         # erweitert project.task: agent_state, create()-Override, _cron-Worker
│   └── agent_log.py            # frawo.agent.log: Logbuch-Modell
├── data/
│   ├── config_params.xml       # ir.config_parameter: ollama url/model/timeout
│   ├── agent_queue_tag.xml      # project.tags "🤖 Agent-Queue"
│   └── ir_cron.xml             # geplante Aktion, user_id = Agent (UID 7)
├── security/
│   └── ir.model.access.csv     # Zugriff frawo.agent.log
├── views/
│   └── agent_log_views.xml     # Menü + Listen/Formular „Agent-Logbuch"
└── tests/
    ├── __init__.py
    └── test_agent.py           # TransactionCase-Tests (Ollama gemockt)
```

Verantwortlichkeiten: `ollama_client` kapselt das LLM (austauschbar), `task_formatter` ist reine Logik (Rollen+Prompts, ohne Seiteneffekte → leicht testbar), `project_task` orchestriert Queue+Cron, `agent_log` ist die Audit-Spur.

---

## Task 1: Addon-Skeleton, das installiert

**Files:**
- Create: `addons/frawo_agent/__init__.py`
- Create: `addons/frawo_agent/__manifest__.py`
- Create: `addons/frawo_agent/models/__init__.py`

- [ ] **Step 1: Manifest schreiben**

`addons/frawo_agent/__manifest__.py`:
```python
{
    "name": "FraWo Agent",
    "version": "17.0.1.0.0",
    "summary": "Autonomer Task-Agent: formatiert neue Tasks nach CI via lokalem Ollama",
    "author": "FraWo GbR",
    "license": "LGPL-3",
    "depends": ["project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "data/agent_queue_tag.xml",
        "data/ir_cron.xml",
        "views/agent_log_views.xml",
    ],
    "application": False,
    "installable": True,
}
```

- [ ] **Step 2: __init__ Dateien**

`addons/frawo_agent/__init__.py`:
```python
from . import models
```

`addons/frawo_agent/models/__init__.py`:
```python
from . import ollama_client
from . import task_formatter
from . import project_task
from . import agent_log
```

- [ ] **Step 3: Leere Platzhalter anlegen, damit Import nicht bricht** (werden in Folge-Tasks gefüllt)

Lege vorerst je eine minimale Datei an:
`addons/frawo_agent/models/ollama_client.py`, `task_formatter.py`, `project_task.py`, `agent_log.py` mit Inhalt:
```python
from odoo import models  # noqa: F401
```
Und leere/minimale Daten-Dateien gemäß File Structure (security CSV mit Header, data-XML als `<odoo></odoo>`, view-XML als `<odoo></odoo>`). Konkret:

`addons/frawo_agent/security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```
`addons/frawo_agent/data/config_params.xml`, `data/agent_queue_tag.xml`, `data/ir_cron.xml`, `views/agent_log_views.xml` jeweils:
```xml
<odoo></odoo>
```

- [ ] **Step 4: Deployen & Install-Test**

Run (auf frawo-docker-1, Hilfsbefehl oben zum Spiegeln, dann):
```bash
docker exec odoo-web odoo -i frawo_agent -d FraWo_GbR --stop-after-init --no-http 2>&1 | tail -15
```
Expected: `Modules loaded.` / `Module frawo_agent: ... loaded` ohne Traceback.

- [ ] **Step 5: Commit**

```bash
cd <repo> && git add addons/frawo_agent && git commit -m "feat(frawo_agent): installierbares Addon-Skeleton"
```

---

## Task 2: Ollama-Client (mit Timeout-Guard)

**Files:**
- Modify: `addons/frawo_agent/models/ollama_client.py`
- Test: `addons/frawo_agent/tests/test_agent.py`
- Create: `addons/frawo_agent/tests/__init__.py`
- Modify: `addons/frawo_agent/data/config_params.xml`

- [ ] **Step 1: Config-Parameter anlegen**

`addons/frawo_agent/data/config_params.xml`:
```xml
<odoo>
  <data noupdate="1">
    <record id="param_ollama_url" model="ir.config_parameter">
      <field name="key">frawo_agent.ollama_url</field>
      <field name="value">http://172.17.0.1:11434</field>
    </record>
    <record id="param_ollama_model" model="ir.config_parameter">
      <field name="key">frawo_agent.ollama_model</field>
      <field name="value">llama3:8b</field>
    </record>
    <record id="param_ollama_timeout" model="ir.config_parameter">
      <field name="key">frawo_agent.ollama_timeout</field>
      <field name="value">90</field>
    </record>
  </data>
</odoo>
```

- [ ] **Step 2: Failing-Test schreiben**

`addons/frawo_agent/tests/__init__.py`:
```python
from . import test_agent
```

`addons/frawo_agent/tests/test_agent.py`:
```python
from unittest.mock import patch
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestOllamaClient(TransactionCase):

    def test_generate_returns_text(self):
        client = self.env["frawo.ollama.client"]
        fake = {"response": "Hallo Welt"}
        with patch("odoo.addons.frawo_agent.models.ollama_client.requests.post") as m:
            m.return_value.json.return_value = fake
            m.return_value.raise_for_status.return_value = None
            out = client.generate("irgendein prompt")
        self.assertEqual(out, "Hallo Welt")

    def test_generate_timeout_returns_none(self):
        import requests
        client = self.env["frawo.ollama.client"]
        with patch("odoo.addons.frawo_agent.models.ollama_client.requests.post",
                   side_effect=requests.exceptions.Timeout()):
            out = client.generate("prompt")
        self.assertIsNone(out)
```

- [ ] **Step 3: Test laufen lassen — muss fehlschlagen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: FAIL — Modell `frawo.ollama.client` existiert nicht.

- [ ] **Step 4: Client implementieren**

`addons/frawo_agent/models/ollama_client.py`:
```python
import logging
import requests
from odoo import api, models

_logger = logging.getLogger(__name__)


class OllamaClient(models.AbstractModel):
    _name = "frawo.ollama.client"
    _description = "Ollama HTTP Client (lokales LLM)"

    @api.model
    def _cfg(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(
            "frawo_agent.%s" % key, default)

    @api.model
    def generate(self, prompt):
        """Ruft Ollama. Gibt Text zurueck oder None bei Fehler/Timeout.
        Blockiert NIE laenger als das konfigurierte Timeout."""
        url = self._cfg("ollama_url", "http://172.17.0.1:11434")
        model = self._cfg("ollama_model", "llama3:8b")
        timeout = int(self._cfg("ollama_timeout", "90"))
        try:
            resp = requests.post(
                "%s/api/generate" % url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            resp.raise_for_status()
            return (resp.json().get("response") or "").strip()
        except Exception as e:  # Timeout, ConnectionError, HTTPError
            _logger.warning("frawo_agent: Ollama-Call fehlgeschlagen: %s", e)
            return None
```

- [ ] **Step 5: Test laufen lassen — muss bestehen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: `2 passed` (0 failed).

- [ ] **Step 6: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): Ollama-Client mit hartem Timeout"
```

---

## Task 3: Rollen-Erkennung + Format-Prompts (reine Logik)

**Files:**
- Modify: `addons/frawo_agent/models/task_formatter.py`
- Modify: `addons/frawo_agent/tests/test_agent.py`

- [ ] **Step 1: Failing-Tests schreiben** (an Datei anhängen)

In `tests/test_agent.py` ergänzen:
```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestFormatter(TransactionCase):

    def test_role_handwerk_by_keyword(self):
        f = self.env["frawo.task.formatter"]
        self.assertEqual(f.detect_role("Schrank montieren Gehäuse"), "handwerk")

    def test_role_devops_by_keyword(self):
        f = self.env["frawo.task.formatter"]
        self.assertEqual(f.detect_role("Docker Tailscale Exporter prüfen"), "devops")

    def test_role_default_review(self):
        f = self.env["frawo.task.formatter"]
        self.assertEqual(f.detect_role("Strategie überlegen"), "review")

    def test_prompt_franz_mentions_masse(self):
        f = self.env["frawo.task.formatter"]
        p = f.build_prompt("Lüfter tauschen", "handwerk")
        self.assertIn("Maße", p)
        self.assertNotIn("Root Cause", p)

    def test_prompt_wolf_mentions_dod(self):
        f = self.env["frawo.task.formatter"]
        p = f.build_prompt("Backup prüfen", "devops")
        self.assertIn("Definition of Done", p)
```

- [ ] **Step 2: Tests laufen — müssen fehlschlagen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: FAIL — `frawo.task.formatter` existiert nicht.

- [ ] **Step 3: Formatter implementieren**

`addons/frawo_agent/models/task_formatter.py`:
```python
from odoo import api, models

HANDWERK = [
    "schrank", "gehäuse", "gehause", "holz", "montier", "verkabel", "löten",
    "loten", "tweeter", "frequenzweiche", "subwoofer", "einbauen", "säubern",
    "werkstatt", "bestückung", "patchplan", "lieferung", "🔨", "🛠️",
]
DEVOPS = [
    "docker", "tailscale", "exporter", "prometheus", "grafana", "vlan", "dhcp",
    "shelly", "backup", "watchdog", "rclone", "cloudflare", "tunnel", "mount",
    "container", "script", "skript", "api", "n8n", "automat", "🤖",
    "[fundament]", "[ha]", "[backup]", "[integration]", "[security]", "[wartung]",
]

PROMPT_WOLF = """Du bist technischer Projekt-Dokumentar. Formuliere die folgende \
Aufgabe professionell auf Deutsch, mit GENAU diesen Abschnitten als Markdown-\
Überschriften: **Problem**, **Impact**, **Root Cause**, **Definition of Done**, \
**Aufwand**, **Abhängigkeiten**. Sei knapp und sachlich. Erfinde keine Fakten; \
wo Infos fehlen, schreibe „(zu klären)". Antworte NUR mit der Dokumentation.

Aufgabe: %s"""

PROMPT_FRANZ = """Du schreibst für einen Handwerker (Zimmermann). Formuliere die \
Aufgabe KURZ auf Deutsch, alles auf einen Blick, KEIN IT-Fachjargon. Nutze GENAU \
dieses Format als Markdown:
🔨 <Was ist zu tun, 1 Zeile>

📐 Maße / Material:
- <konkrete Zahlen, Maße, Stückzahl, Material — falls unbekannt: „(Maß vor Ort)">

✅ Fertig wenn:
- <prüfbares Ergebnis, 1 Zeile>

💬 Warum:
- <kurze Begründung, 1-2 Sätze>

Antworte NUR mit dem ausgefüllten Format.

Aufgabe: %s"""


class TaskFormatter(models.AbstractModel):
    _name = "frawo.task.formatter"
    _description = "Rollen-Erkennung und Prompt-Bau"

    @api.model
    def detect_role(self, name):
        low = (name or "").lower()
        if any(k in low for k in HANDWERK):
            return "handwerk"
        if any(k in low for k in DEVOPS):
            return "devops"
        return "review"

    @api.model
    def build_prompt(self, name, role):
        if role == "handwerk":
            return PROMPT_FRANZ % name
        return PROMPT_WOLF % name
```

- [ ] **Step 4: Tests laufen — müssen bestehen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: alle Formatter-Tests `passed`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): Rollen-Erkennung + Franz/Wolf-Prompts"
```

---

## Task 4: `project.task`-Erweiterung — Queue ohne Endlosschleife

**Files:**
- Modify: `addons/frawo_agent/models/project_task.py`
- Modify: `addons/frawo_agent/data/agent_queue_tag.xml`
- Modify: `addons/frawo_agent/tests/test_agent.py`

- [ ] **Step 1: Queue-Tag als Daten anlegen**

`addons/frawo_agent/data/agent_queue_tag.xml`:
```xml
<odoo>
  <data noupdate="1">
    <record id="tag_agent_queue" model="project.tags">
      <field name="name">🤖 Agent-Queue</field>
      <field name="color">3</field>
    </record>
  </data>
</odoo>
```

- [ ] **Step 2: Failing-Tests schreiben** (anhängen)

In `tests/test_agent.py` ergänzen:
```python
AGENT_UID = 7

@tagged("post_install", "-at_install", "frawo_agent")
class TestQueue(TransactionCase):

    def _project(self):
        return self.env["project.project"].create({"name": "T-Proj"})

    def test_human_create_sets_queued(self):
        t = self.env["project.task"].create(
            {"name": "neuer task", "project_id": self._project().id})
        self.assertEqual(t.agent_state, "queued")

    def test_agent_create_does_not_queue(self):
        t = self.env["project.task"].with_user(AGENT_UID).create(
            {"name": "agent task", "project_id": self._project().id})
        self.assertEqual(t.agent_state, "skip")

    def test_agent_write_does_not_requeue(self):
        t = self.env["project.task"].create(
            {"name": "x", "project_id": self._project().id})
        t.agent_state = "done"
        t.with_user(AGENT_UID).write({"description": "<p>fertig</p>"})
        self.assertEqual(t.agent_state, "done")
```

- [ ] **Step 3: Tests laufen — müssen fehlschlagen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: FAIL — Feld `agent_state` unbekannt.

- [ ] **Step 4: Feld + create()-Override implementieren**

`addons/frawo_agent/models/project_task.py`:
```python
from odoo import api, fields, models

AGENT_LOGIN = "agent@frawo.tech"


class ProjectTask(models.Model):
    _inherit = "project.task"

    agent_state = fields.Selection(
        [("skip", "Nicht zu bearbeiten"),
         ("queued", "In Agent-Queue"),
         ("done", "Vom Agent aufbereitet"),
         ("error", "Agent-Fehler")],
        default="skip", index=True, copy=False,
        string="Agent-Status",
    )

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        agent = self.env.ref("base.user_admin").browse()  # placeholder, see below
        agent_uid = self.env["res.users"].sudo().search(
            [("login", "=", AGENT_LOGIN)], limit=1).id
        # Nur menschlich angelegte Tasks in die Queue; Agent-eigene NICHT
        if self.env.uid != agent_uid:
            for t in tasks:
                if t.agent_state == "skip":
                    t.agent_state = "queued"
        return tasks
```
> Hinweis: Die Zeile `agent = ...placeholder` entfernen — sie ist nur Erklärung. Finale Methode nutzt ausschließlich `agent_uid` über `login`. (Robust gegen abweichende ID.)

Finale, bereinigte `create`:
```python
    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        agent_uid = self.env["res.users"].sudo().search(
            [("login", "=", AGENT_LOGIN)], limit=1).id
        if self.env.uid != agent_uid:
            for t in tasks:
                if t.agent_state == "skip":
                    t.agent_state = "queued"
        return tasks
```

- [ ] **Step 5: Tests laufen — müssen bestehen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: TestQueue alle `passed`.

- [ ] **Step 6: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): agent_state-Queue ohne Endlosschleife"
```

---

## Task 5: Logbuch-Modell `frawo.agent.log`

**Files:**
- Modify: `addons/frawo_agent/models/agent_log.py`
- Modify: `addons/frawo_agent/security/ir.model.access.csv`
- Modify: `addons/frawo_agent/tests/test_agent.py`

- [ ] **Step 1: Failing-Test** (anhängen)
```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestLog(TransactionCase):
    def test_log_create(self):
        rec = self.env["frawo.agent.log"].create(
            {"name": "Test", "level": "info", "message": "hallo"})
        self.assertTrue(rec.id)
```

- [ ] **Step 2: Test laufen — fehlschlagen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: FAIL — Modell unbekannt.

- [ ] **Step 3: Modell implementieren**

`addons/frawo_agent/models/agent_log.py`:
```python
from odoo import fields, models


class AgentLog(models.Model):
    _name = "frawo.agent.log"
    _description = "FraWo Agent Logbuch"
    _order = "create_date desc"

    name = fields.Char(string="Aktion", required=True)
    level = fields.Selection(
        [("info", "Info"), ("warning", "Warnung"), ("error", "Fehler")],
        default="info", required=True)
    task_id = fields.Many2one("project.task", string="Task", ondelete="set null")
    message = fields.Text(string="Details")
```

- [ ] **Step 4: Zugriffsrechte** — `security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_agent_log_user,frawo.agent.log.user,model_frawo_agent_log,base.group_user,1,0,0,0
access_agent_log_system,frawo.agent.log.system,model_frawo_agent_log,base.group_system,1,1,1,1
```

- [ ] **Step 5: Test laufen — bestehen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: TestLog `passed`.

- [ ] **Step 6: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): Agent-Logbuch-Modell"
```

---

## Task 6: Der Prozessor — 1 Task aufbereiten (Herzstück)

**Files:**
- Modify: `addons/frawo_agent/models/project_task.py`
- Modify: `addons/frawo_agent/tests/test_agent.py`

- [ ] **Step 1: Failing-Test** (anhängen) — Ollama gemockt, prüft autonome Teile + Vorschlag
```python
@tagged("post_install", "-at_install", "frawo_agent")
class TestProcessor(TransactionCase):

    def _queued_task(self, name):
        proj = self.env["project.project"].create({"name": "P"})
        return self.env["project.task"].create(
            {"name": name, "project_id": proj.id})

    def test_process_sets_description_tag_activity_log(self):
        t = self._queued_task("Lüfter in growbox tauschen")
        self.assertEqual(t.agent_state, "queued")
        with patch(
            "odoo.addons.frawo_agent.models.ollama_client.OllamaClient.generate",
            return_value="🔨 Lüfter tauschen\n\n📐 Maße / Material:\n- (Maß vor Ort)",
        ):
            self.env["project.task"]._cron_process_agent_queue()
        t.invalidate_recordset()
        self.assertEqual(t.agent_state, "done")
        self.assertIn("Lüfter", t.description or "")
        self.assertIn(77, t.tag_ids.ids)  # Handwerk-Franz
        self.assertTrue(t.activity_ids)   # Owner/Deadline-Vorschlag
        self.assertTrue(self.env["frawo.agent.log"].search(
            [("task_id", "=", t.id)]))

    def test_process_handles_ollama_failure(self):
        t = self._queued_task("irgendwas")
        with patch(
            "odoo.addons.frawo_agent.models.ollama_client.OllamaClient.generate",
            return_value=None,
        ):
            self.env["project.task"]._cron_process_agent_queue()
        t.invalidate_recordset()
        self.assertEqual(t.agent_state, "error")  # blockiert Queue nicht
```

- [ ] **Step 2: Test laufen — fehlschlagen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: FAIL — `_cron_process_agent_queue` existiert nicht.

- [ ] **Step 3: Prozessor implementieren** — an `project_task.py` anhängen (innerhalb der Klasse):
```python
    ROLE_TAG = {"devops": 75, "review": 76, "handwerk": 77}

    @api.model
    def _cron_process_agent_queue(self):
        """Verarbeitet GENAU 1 Task pro Aufruf (Stabilitaet: kein Batch)."""
        task = self.search([("agent_state", "=", "queued")],
                           order="create_date asc", limit=1)
        if not task:
            return
        Log = self.env["frawo.agent.log"]
        try:
            role = self.env["frawo.task.formatter"].detect_role(task.name)
            prompt = self.env["frawo.task.formatter"].build_prompt(task.name, role)
            text = self.env["frawo.ollama.client"].generate(prompt)
            if not text:
                task.agent_state = "error"
                Log.create({"name": "Ollama ohne Antwort", "level": "error",
                            "task_id": task.id,
                            "message": "Kein Text vom Modell – Task uebersprungen."})
                return
            # 🟢 autonom: Beschreibung + Rollen-Tag + Chatter
            tag_id = self.ROLE_TAG.get(role, 76)
            task.write({
                "description": "<pre>%s</pre>" % text,
                "tag_ids": [(4, tag_id)],
                "agent_state": "done",
            })
            task.message_post(
                body="🤖 Agent hat den Task nach CI aufbereitet (Rolle: %s)." % role)
            # 🟡 Vorschlag: Owner/Deadline als Aktivitaet (NICHT autonom setzen)
            self._post_suggestion_activity(task, role)
            Log.create({"name": "Task aufbereitet", "level": "info",
                        "task_id": task.id, "message": "Rolle=%s" % role})
        except Exception as e:
            task.agent_state = "error"
            Log.create({"name": "Verarbeitungsfehler", "level": "error",
                        "task_id": task.id, "message": str(e)})

    def _post_suggestion_activity(self, task, role):
        owner = {"handwerk": "Franz Bienert", "devops": "🤖 Agent"}.get(role, "Wolf")
        note = ("Agent-Vorschlag — bitte freigeben:<br/>"
                "• Owner: <b>%s</b><br/>• Deadline: <b>(bitte setzen)</b><br/>"
                "Zum Freigeben diese Aktivitaet als erledigt markieren." % owner)
        task.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Agent-Vorschlag: Owner/Deadline",
            note=note,
            user_id=task.env["res.users"].sudo().search(
                [("login", "=", "wolf@frawo.tech")], limit=1).id or task.env.uid,
        )
```

- [ ] **Step 4: Test laufen — bestehen**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --test-enable --test-tags /frawo_agent --stop-after-init --no-http 2>&1 | tail -30`
Expected: TestProcessor `passed`.

- [ ] **Step 5: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): Prozessor – 1 Task/Aufruf, autonom + Vorschlag + Fehler-isoliert"
```

---

## Task 7: Geplante Aktion (Cron) als UID 7

**Files:**
- Modify: `addons/frawo_agent/data/ir_cron.xml`

- [ ] **Step 1: Cron-Datensatz schreiben**

`addons/frawo_agent/data/ir_cron.xml`:
```xml
<odoo>
  <data noupdate="1">
    <record id="cron_agent_queue" model="ir.cron">
      <field name="name">FraWo Agent: Task-Queue abarbeiten</field>
      <field name="model_id" ref="project.model_project_task"/>
      <field name="state">code</field>
      <field name="code">model._cron_process_agent_queue()</field>
      <field name="interval_number">2</field>
      <field name="interval_type">minutes</field>
      <field name="active" eval="True"/>
      <field name="user_id" ref="base.user_root"/>
    </record>
  </data>
</odoo>
```
> Setze `user_id` nach Install per Post-Init auf den Agent-User (UID 7), damit Chatter-Einträge als „🤖 Agent" erscheinen. Da der Agent-User keine feste XML-ID hat, in einer kurzen `post_init_hook` zuweisen (Step 2).

- [ ] **Step 2: post_init_hook zum Setzen des Cron-Users**

In `__manifest__.py` ergänzen: `"post_init_hook": "post_init",`

In `addons/frawo_agent/__init__.py`:
```python
from . import models


def post_init(env):
    agent = env["res.users"].search([("login", "=", "agent@frawo.tech")], limit=1)
    cron = env.ref("frawo_agent.cron_agent_queue", raise_if_not_found=False)
    if agent and cron:
        cron.user_id = agent.id
```
> Odoo 17 post_init_hook-Signatur ist `def post_init(env)`.

- [ ] **Step 3: Update + Verify Cron-User**

Run:
```bash
docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --stop-after-init --no-http 2>&1 | tail -10
docker exec odoo-web odoo shell -d FraWo_GbR --no-http <<'PY' 2>&1 | tail -5
cron = env.ref("frawo_agent.cron_agent_queue")
print("CRON-USER:", cron.user_id.login)
PY
```
Expected: `CRON-USER: agent@frawo.tech`

- [ ] **Step 4: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): ir.cron alle 2 Min, laeuft als Agent (UID 7)"
```

---

## Task 8: Cockpit — Logbuch-Menü & Ansichten

**Files:**
- Modify: `addons/frawo_agent/views/agent_log_views.xml`

- [ ] **Step 1: Views + Menü schreiben**

`addons/frawo_agent/views/agent_log_views.xml`:
```xml
<odoo>
  <record id="view_agent_log_tree" model="ir.ui.view">
    <field name="name">frawo.agent.log.tree</field>
    <field name="model">frawo.agent.log</field>
    <field name="arch" type="xml">
      <tree decoration-danger="level=='error'" decoration-warning="level=='warning'">
        <field name="create_date"/>
        <field name="name"/>
        <field name="level"/>
        <field name="task_id"/>
        <field name="message"/>
      </tree>
    </field>
  </record>

  <record id="view_agent_log_form" model="ir.ui.view">
    <field name="name">frawo.agent.log.form</field>
    <field name="model">frawo.agent.log</field>
    <field name="arch" type="xml">
      <form>
        <sheet>
          <group>
            <field name="name"/><field name="level"/>
            <field name="task_id"/><field name="create_date"/>
          </group>
          <field name="message"/>
        </sheet>
      </form>
    </field>
  </record>

  <record id="action_agent_log" model="ir.actions.act_window">
    <field name="name">Agent-Logbuch</field>
    <field name="res_model">frawo.agent.log</field>
    <field name="view_mode">tree,form</field>
  </record>

  <menuitem id="menu_frawo_agent_root" name="🤖 Agent"
            web_icon="project,static/description/icon.png" sequence="95"/>
  <menuitem id="menu_agent_log" name="Logbuch"
            parent="menu_frawo_agent_root" action="action_agent_log" sequence="10"/>
</odoo>
```

- [ ] **Step 2: Update + Verify Menü lädt**

Run: `docker exec odoo-web odoo -u frawo_agent -d FraWo_GbR --stop-after-init --no-http 2>&1 | tail -10`
Expected: kein Traceback. (UI-Sichtprüfung mit Wolf: Menü „🤖 Agent → Logbuch" erscheint.)

- [ ] **Step 3: Commit**

```bash
git add addons/frawo_agent && git commit -m "feat(frawo_agent): Cockpit – Agent-Logbuch Menue & Ansichten"
```

---

## Task 9: End-to-End auf echter DB + Netz-Härtung

**Files:** keine (Betrieb/Verifikation)

- [ ] **Step 1: odoo-web ans Ollama-Netz hängen (saubere DNS-Auflösung)**

Run (auf frawo-docker-1):
```bash
docker network connect infra_shared odoo-web
docker exec odoo-web python3 -c "import socket; socket.create_connection(('ollama',11434),3); print('ollama per DNS OK')"
```
Expected: `ollama per DNS OK`. Danach Config-Param auf DNS umstellen:
```bash
docker exec odoo-web odoo shell -d FraWo_GbR --no-http <<'PY'
env["ir.config_parameter"].sudo().set_param("frawo_agent.ollama_url","http://ollama:11434")
env.cr.commit()
PY
```
> Fällt `infra_shared` weg, bleibt der Host-Gateway-Wert `http://172.17.0.1:11434` als funktionierender Fallback.

- [ ] **Step 2: Live-Rauchtest — echten Task anlegen, Cron 1× manuell triggern**

Run:
```bash
docker exec odoo-web odoo shell -d FraWo_GbR --no-http <<'PY' 2>&1 | tail -15
proj = env["project.project"].search([], limit=1)
t = env["project.task"].create({"name":"TESTAGENT lüfter growbox tauschen zu laut","project_id":proj.id})
print("queued?", t.agent_state)
env["project.task"]._cron_process_agent_queue()
t.invalidate_recordset()
print("state:", t.agent_state)
print("desc:", (t.description or "")[:120])
print("tags:", t.tag_ids.mapped("name"))
print("aktivitaet:", t.activity_ids.mapped("summary"))
env.cr.rollback()  # Testtask nicht behalten
PY
```
Expected: `queued? queued` → `state: done`, Beschreibung gefüllt, Tag „Handwerk-Franz", Aktivität „Agent-Vorschlag: Owner/Deadline".

- [ ] **Step 3: Latenz messen (Stabilitäts-Beleg)**

Run:
```bash
docker exec odoo-web odoo shell -d FraWo_GbR --no-http <<'PY' 2>&1 | tail -3
import time; s=time.time()
print(env["frawo.ollama.client"].generate("Test: formuliere 'kabel verlegen' kurz."))
print("Sekunden:", round(time.time()-s,1))
PY
```
Expected: Antworttext + `Sekunden:` im Bereich ~10–60. (Liegt's dauerhaft >70, Modell `llama3.2:3b` nachladen + Param umstellen.)

- [ ] **Step 4: Cron scharf schalten beobachten**

Run: `docker exec odoo-web odoo shell -d FraWo_GbR --no-http <<'PY'
c = env.ref("frawo_agent.cron_agent_queue"); print(c.active, c.nextcall, c.user_id.login)
PY`
Expected: `True <zeit> agent@frawo.tech`. 24 h beobachten: Weboberfläche bleibt flüssig, Logbuch füllt sich, keine `error`-Häufung.

- [ ] **Step 5: Commit (Doku/Changelog)**

```bash
git add -A && git commit -m "chore(frawo_agent): E2E verifiziert + Netz-Haertung (ollama DNS)"
```

---

## Self-Review-Notiz (Plan ↔ Spec)

- Spec §3 Trigger: Plan nutzt `create()`-Override statt `base.automation` — **bewusst** (stabiler, testbar, gleicher Effekt). 
- Spec §3 Identität UID 7: Task 7 setzt Cron-`user_id` auf Agent → Chatter als „🤖 Agent". ✅
- Spec §4 Autonomie-Matrix: Task 6 — Beschreibung/Tags/Log autonom; Owner/Deadline nur als Aktivität (Vorschlag); Löschen nirgends autonom. ✅
- Spec §5 Formate: Task 3 Franz vs Wolf Prompts. ✅
- Spec §8 Schutzregeln: limit=1 (Task 6), Timeout (Task 2), Fehler-Isolation (Task 6 try/except → `error`). ✅
- Spec §6 Identitäts-Fix: zusätzlich sollten bestehende Task-Skripte künftig UID 7 nutzen (separat, nicht Teil dieses Addons).
- Offen/Impl: UID-7-Schreibrechte auf ALLE Tasks — falls Record-Rules blocken, Agent-User Gruppe *Project/Administrator* geben (in Task 9 Schritt 2 verifizieren; bei Fehler nachziehen).
