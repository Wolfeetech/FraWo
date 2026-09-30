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
