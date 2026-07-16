from html import escape as html_escape

from odoo import api, fields, models
from odoo.tools import html2plaintext

AGENT_LOGIN = "agent@frawo.tech"
# Ab dieser Laenge (Klartext) gilt ein Task als bereits dokumentiert -> nicht ueberschreiben
DOC_THRESHOLD = 150


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

    # Rolle -> bestehender project.tags-Name (per Name aufgeloest, robust gg. IDs)
    ROLE_TAG_NAME = {
        "devops": "DevOps-Agent",
        "review": "Review-Wolf",
        "handwerk": "Handwerk-Franz",
    }

    @api.model
    def _role_tag_id(self, role):
        name = self.ROLE_TAG_NAME.get(role, "Review-Wolf")
        Tags = self.env["project.tags"].sudo()
        tag = Tags.search([("name", "=", name)], limit=1)
        if not tag:
            tag = Tags.create({"name": name})
        return tag.id

    @api.model
    def _agent_uid(self):
        return self.env["res.users"].sudo().search(
            [("login", "=", AGENT_LOGIN)], limit=1).id

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        agent_uid = self._agent_uid()
        # Nur menschlich angelegte Tasks in die Queue; Agent-eigene NICHT
        if self.env.uid != agent_uid:
            for t in tasks:
                if t.agent_state == "skip":
                    t.agent_state = "queued"
        return tasks

    @api.model
    def _cron_process_agent_queue(self):
        """Verarbeitet GENAU 1 Task pro Aufruf (Stabilitaet: kein Batch)."""
        task = self.search([("agent_state", "=", "queued")],
                           order="create_date asc", limit=1)
        if not task:
            return
        Log = self.env["frawo.agent.log"].sudo()
        try:
            # Schutz: bereits ausfuehrlich dokumentierte Tasks NICHT ueberschreiben
            existing = html2plaintext(task.description or "").strip()
            if len(existing) >= DOC_THRESHOLD:
                task.sudo().agent_state = "skip"
                Log.create({"name": "Bereits dokumentiert", "level": "info",
                            "task_id": task.id,
                            "message": "Beschreibung >=%d Zeichen – Agent ueberschreibt "
                                       "nicht." % DOC_THRESHOLD})
                return
            role = self.env["frawo.task.formatter"].detect_role(task.name)
            prompt = self.env["frawo.task.formatter"].build_prompt(task.name, role)
            text = self.env["frawo.ollama.client"].generate(prompt)
            if not text:
                task.sudo().agent_state = "error"
                Log.create({"name": "Ollama ohne Antwort", "level": "error",
                            "task_id": task.id,
                            "message": "Kein Text vom Modell – Task uebersprungen."})
                return
            # autonom: Beschreibung + Rollen-Tag + Chatter
            tag_id = self._role_tag_id(role)
            task.sudo().write({
                "description": "<pre>%s</pre>" % html_escape(text),
                "tag_ids": [(4, tag_id)],
                "agent_state": "done",
            })
            task.message_post(
                body="🤖 Agent hat den Task nach CI aufbereitet (Rolle: %s)." % role)
            # Vorschlag: Owner/Deadline als Aktivitaet (NICHT autonom setzen)
            self._post_suggestion_activity(task, role)
            Log.create({"name": "Task aufbereitet", "level": "info",
                        "task_id": task.id, "message": "Rolle=%s" % role})
        except Exception as e:
            task.sudo().agent_state = "error"
            Log.create({"name": "Verarbeitungsfehler", "level": "error",
                        "task_id": task.id, "message": str(e)})

    def _post_suggestion_activity(self, task, role):
        owner = {"handwerk": "Franz Bienert", "devops": "🤖 Agent"}.get(role, "Wolf")
        note = ("Agent-Vorschlag — bitte freigeben:<br/>"
                "• Owner: <b>%s</b><br/>• Deadline: <b>(bitte setzen)</b><br/>"
                "Zum Freigeben diese Aktivitaet als erledigt markieren." % owner)
        wolf = self.env["res.users"].sudo().search(
            [("login", "=", "wolf@frawo.tech")], limit=1)
        task.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Agent-Vorschlag: Owner/Deadline",
            note=note,
            user_id=wolf.id or self.env.uid,
        )

    def _trigger_servassi_webhook(self):
        import urllib.request
        import json
        secret = self.env["ir.config_parameter"].sudo().get_param(
            "frawo_agent.servassi_webhook_secret", "")
        url = self.env["ir.config_parameter"].sudo().get_param(
            "frawo_agent.servassi_webhook_url", "http://10.1.0.31:19001/odoo-task")
        for record in self:
            try:
                payload = json.dumps({
                    "task_id": record.id,
                    "name": record.name,
                    "description": record.description or "",
                }).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Secret": secret,
                    },
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
