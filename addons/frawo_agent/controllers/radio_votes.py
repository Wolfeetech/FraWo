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
from odoo.tools import consteq

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

    def _export_token_ok(self):
        expected = (request.env["ir.config_parameter"].sudo()
                    .get_param("frawo_agent.summary_token", "") or "").strip()
        if not expected:
            return False
        token = (request.httprequest.headers.get("X-Agent-Token")
                 or request.params.get("token") or "")
        return consteq(token, expected)

    @http.route("/radio/rate", type="jsonrpc", auth="user", csrf=False)
    def radio_rate(self, song_id=None, stars=None, **kw):
        user = request.env.user
        if not song_id or user._is_public():
            return {"ok": False, "reason": "forbidden"}
        try:
            request.env["frawo.radio.rating"].sudo().rate(song_id, user.partner_id.id, stars)
        except (ValueError, TypeError):
            return {"ok": False, "reason": "bad_stars"}
        return {
            "ok": True,
            "summary": request.env["frawo.radio.rating"].sudo().summary(song_id, user.partner_id.id),
        }

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
            return request.make_response(
                json.dumps({"error": "unauthorized"}),
                headers=[("Content-Type", "application/json")],
                status=401,
            )
        rows = request.env["frawo.radio.rating"].sudo().export_rows(min_count=2)
        return request.make_response(
            json.dumps(rows),
            headers=[("Content-Type", "application/json"), ("Cache-Control", "no-store")],
        )
