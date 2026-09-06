# -*- coding: utf-8 -*-
"""Community mood-voting for FraWo Funk (DB-backed, multi-worker safe).
Public routes:
  GET  /radio/api/votes?track_id=<id>          -> {votes, percentages, total, winner}
  POST /radio/api/mood-vote {mood,track_id,voter} -> {ok, reason, ...}
  POST /radio/api/round-reset {track_id,secret} -> {ok, cleared}   (conductor only)
"""
import json
from odoo import http
from odoo.http import request
from odoo.tools import consteq

_MOODS = ('energy', 'chill', 'deep')
RESET_SECRET_PARAM = 'frawo_agent.radio_reset_secret'


def _counts(track_id):
    Vote = request.env['frawo.radio.vote'].sudo()
    tid = track_id or 'live'
    return {m: Vote.search_count([('track_id', '=', tid), ('mood', '=', m)]) for m in _MOODS}


def _payload(track_id):
    c = _counts(track_id)
    tot = c['energy'] + c['chill'] + c['deep']
    def pct(n):
        return int(round(n * 100.0 / tot)) if tot else 0
    winner = max(c, key=c.get) if tot else None
    return {'votes': c,
            'percentages': {k: pct(v) for k, v in c.items()},
            'total': tot, 'winner': winner, 'track_id': track_id or 'live'}


def _json(data):
    return request.make_response(
        json.dumps(data),
        headers=[('Content-Type', 'application/json'),
                 ('Access-Control-Allow-Origin', '*'),
                 ('Cache-Control', 'no-store')])


def _cors_preflight():
    return request.make_response('', headers=[
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')])


class FrawoRadioVotes(http.Controller):

    @http.route('/radio/api/votes', type='http', auth='public', csrf=False, cors='*', methods=['GET'])
    def votes(self, track_id=None, **kw):
        return _json(_payload(track_id or 'live'))

    @http.route('/radio/api/mood-vote', type='http', auth='public', csrf=False, cors='*', methods=['POST', 'OPTIONS'])
    def mood_vote(self, mood=None, track_id=None, voter=None, **kw):
        if request.httprequest.method == 'OPTIONS':
            return _cors_preflight()
        if not mood:
            try:
                b = json.loads(request.httprequest.get_data(as_text=True) or '{}')
                mood = b.get('mood')
                track_id = track_id or b.get('track_id')
                voter = voter or b.get('voter')
            except Exception:
                pass
        track_id = track_id or 'live'
        voter = str(voter or request.httprequest.remote_addr or 'anon')
        if mood not in _MOODS:
            return _json({'ok': False, 'reason': 'bad_mood'})
        Vote = request.env['frawo.radio.vote'].sudo()
        if Vote.search_count([('track_id', '=', track_id), ('voter', '=', voter)]):
            out = {'ok': False, 'reason': 'already_voted'}
            out.update(_payload(track_id))
            return _json(out)
        Vote.create({'track_id': track_id, 'mood': mood, 'voter': voter})
        out = {'ok': True}
        out.update(_payload(track_id))
        return _json(out)

    @http.route('/radio/api/round-reset', type='http', auth='public', csrf=False, cors='*', methods=['POST', 'GET', 'OPTIONS'])
    def round_reset(self, track_id=None, secret=None, **kw):
        if request.httprequest.method == 'OPTIONS':
            return _cors_preflight()
        # Secret lebt ausschliesslich in der Datenbank (ir.config_parameter),
        # niemals im Quellcode -- das Repo ist public. Ist keins gesetzt,
        # wird der Zugriff verweigert (fail closed).
        expected = (request.env['ir.config_parameter'].sudo()
                    .get_param(RESET_SECRET_PARAM, '') or '').strip()
        if not expected or not secret or not consteq(str(secret), expected):
            return _json({'ok': False, 'reason': 'forbidden'})
        Vote = request.env['frawo.radio.vote'].sudo()
        recs = Vote.search([('track_id', '=', track_id or 'live')])
        n = len(recs)
        recs.unlink()
        return _json({'ok': True, 'cleared': n})
