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
