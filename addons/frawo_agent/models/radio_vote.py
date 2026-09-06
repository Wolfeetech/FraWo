# -*- coding: utf-8 -*-
from odoo import models, fields


class FrawoRadioVote(models.Model):
    _name = 'frawo.radio.vote'
    _description = 'FraWo Radio Mood Vote (community steering)'
    _order = 'create_date desc'

    track_id = fields.Char(string='Track', index=True, required=True)
    vote_type = fields.Selection(
        [('energy', '⚡ Energy'), ('chill', '🌙 Chill'), ('hate', '⏭️ Skip'),
         ('like', '🔥 Banger'), ('unlike', '🔥 Banger zurückgezogen')],
        string='Vote', required=True, index=True)
    voter_ip = fields.Char(string='Absender (IP)')
