# -*- coding: utf-8 -*-
from odoo import models, fields


class FrawoRadioVote(models.Model):
    _name = 'frawo.radio.vote'
    _description = 'FraWo Radio Mood Vote (community steering)'

    track_id = fields.Char(index=True, required=True)
    mood = fields.Char(required=True)   # energy | chill | deep
    voter = fields.Char(index=True, required=True)
