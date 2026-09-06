# -*- coding: utf-8 -*-
"""Auswertung fuers Mood-Voting auf frawo.tech/radio (View 3353).

Das eigentliche Schreiben passiert in controllers/main.py::RadioController
.radio_vote (bereits live, POST /radio/vote) -- der schreibt zusaetzlich
zum bestehenden agent.log-Eintrag jetzt auch in frawo.radio.vote, damit
die Stimmen hier auswertbar sind. Dieser Controller ist rein lesend.
"""
import json
from datetime import timedelta

from odoo import fields, http
from odoo.http import request

_VOTE_TYPES = ('energy', 'chill', 'hate', 'like', 'unlike')


class FrawoRadioVotes(http.Controller):

    @http.route('/radio/votes/summary', type='http', auth='public', csrf=False, methods=['GET'])
    def radio_votes_summary(self, track_id=None, minutes=30, **kw):
        """Schlanker Live-Tally fuer ein kuenftiges Frontend-Element (letzte N Minuten)."""
        try:
            minutes = min(max(int(minutes), 1), 180)
        except (TypeError, ValueError):
            minutes = 30
        cutoff = fields.Datetime.now() - timedelta(minutes=minutes)
        Vote = request.env['frawo.radio.vote'].sudo()
        domain = [('create_date', '>=', cutoff)]
        if track_id:
            domain.append(('track_id', '=', track_id))
        counts = {vt: Vote.search_count(domain + [('vote_type', '=', vt)]) for vt in _VOTE_TYPES}
        return request.make_response(
            json.dumps({'ok': True, 'counts': counts, 'window_minutes': minutes}),
            headers=[('Content-Type', 'application/json'), ('Cache-Control', 'no-store')],
        )
