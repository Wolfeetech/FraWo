from unittest.mock import patch
from odoo.tests.common import TransactionCase, tagged

AGENT_LOGIN = "agent@frawo.tech"


@tagged("post_install", "-at_install", "frawo_agent")
class TestOllamaClient(TransactionCase):

    def test_generate_returns_text(self):
        client = self.env["frawo.ollama.client"]
        with patch("odoo.addons.frawo_agent.models.ollama_client.requests.post") as m:
            m.return_value.json.return_value = {"response": "Hallo Welt"}
            m.return_value.raise_for_status.return_value = None
            out = client.generate("irgendein prompt")
        self.assertEqual(out, "Hallo Welt")

    def test_generate_caps_token_length(self):
        client = self.env["frawo.ollama.client"]
        with patch("odoo.addons.frawo_agent.models.ollama_client.requests.post") as m:
            m.return_value.json.return_value = {"response": "ok"}
            m.return_value.raise_for_status.return_value = None
            client.generate("prompt")
            payload = m.call_args.kwargs["json"]
        self.assertIn("num_predict", payload["options"])

    def test_generate_timeout_returns_none(self):
        import requests
        client = self.env["frawo.ollama.client"]
        with patch("odoo.addons.frawo_agent.models.ollama_client.requests.post",
                   side_effect=requests.exceptions.Timeout()):
            out = client.generate("prompt")
        self.assertIsNone(out)


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


@tagged("post_install", "-at_install", "frawo_agent")
class TestQueue(TransactionCase):

    def setUp(self):
        super().setUp()
        # Tests duerfen nicht von Prod-Daten abhaengen: Agent-User sicherstellen.
        Users = self.env["res.users"].sudo()
        if not Users.search([("login", "=", AGENT_LOGIN)], limit=1):
            Users.create({
                "name": "FraWo Agent",
                "login": AGENT_LOGIN,
                "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
            })

    def _project(self):
        return self.env["project.project"].create({"name": "T-Proj"})

    def _agent_uid(self):
        return self.env["res.users"].sudo().search(
            [("login", "=", AGENT_LOGIN)], limit=1).id

    def test_human_create_sets_queued(self):
        t = self.env["project.task"].create(
            {"name": "neuer task", "project_id": self._project().id})
        self.assertEqual(t.agent_state, "queued")

    def test_agent_create_does_not_queue(self):
        t = self.env["project.task"].with_user(self._agent_uid()).create(
            {"name": "agent task", "project_id": self._project().id})
        self.assertEqual(t.agent_state, "skip")

    def test_agent_write_does_not_requeue(self):
        t = self.env["project.task"].create(
            {"name": "x", "project_id": self._project().id})
        t.agent_state = "done"
        t.with_user(self._agent_uid()).write({"description": "<p>fertig</p>"})
        self.assertEqual(t.agent_state, "done")


@tagged("post_install", "-at_install", "frawo_agent")
class TestLog(TransactionCase):

    def test_log_create(self):
        rec = self.env["frawo.agent.log"].create(
            {"name": "Test", "level": "info", "message": "hallo"})
        self.assertTrue(rec.id)


@tagged("post_install", "-at_install", "frawo_agent")
class TestProcessor(TransactionCase):

    def _queued_task(self, name):
        proj = self.env["project.project"].create({"name": "P"})
        return self.env["project.task"].create(
            {"name": name, "project_id": proj.id})

    def test_process_sets_description_tag_activity_log(self):
        t = self._queued_task("Lüfter Gehäuse einbauen")  # -> handwerk
        self.assertEqual(t.agent_state, "queued")
        with patch(
            "odoo.addons.frawo_agent.models.ollama_client.OllamaClient.generate",
            return_value="🔨 Lüfter tauschen\n\n📐 Maße / Material:\n- (Maß vor Ort)",
        ):
            self.env["project.task"]._cron_process_agent_queue()
        t.invalidate_recordset()
        self.assertEqual(t.agent_state, "done")
        self.assertIn("Lüfter", t.description or "")
        self.assertIn("Handwerk-Franz", t.tag_ids.mapped("name"))
        self.assertTrue(t.activity_ids)   # Owner/Deadline-Vorschlag
        self.assertTrue(self.env["frawo.agent.log"].search(
            [("task_id", "=", t.id)]))

    def test_process_skips_already_documented(self):
        t = self._queued_task("Schon dokumentierte Aufgabe")
        t.description = "<p>" + ("Ausfuehrliche bestehende Beschreibung. " * 6) + "</p>"
        with patch(
            "odoo.addons.frawo_agent.models.ollama_client.OllamaClient.generate",
            return_value="NEUER LLM TEXT",
        ) as gen:
            self.env["project.task"]._cron_process_agent_queue()
        t.invalidate_recordset()
        self.assertEqual(t.agent_state, "skip")
        self.assertNotIn("NEUER LLM TEXT", t.description or "")
        self.assertFalse(gen.called)

    def test_process_handles_ollama_failure(self):
        t = self._queued_task("irgendwas")
        with patch(
            "odoo.addons.frawo_agent.models.ollama_client.OllamaClient.generate",
            return_value=None,
        ):
            self.env["project.task"]._cron_process_agent_queue()
        t.invalidate_recordset()
        self.assertEqual(t.agent_state, "error")  # blockiert Queue nicht
