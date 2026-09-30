# -*- coding: utf-8 -*-
"""Duenner Client fuer die AzuraCast-REST-API (nur was die Kanal-Demokratie braucht).

Bewusst REST statt MariaDB-Direktzugriff: nach direkten DB-Aenderungen
muesste der Sender neu gestartet werden (NOW.md-Fallentabelle), ueber die
API benachrichtigt AzuraCast liquidsoap selbst.
"""
import logging

import requests
import urllib3

from odoo import models

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

STATION_ID = 1
TIMEOUT = 10


def _ist_teilmenge(klein, gross):
    """True, wenn der Zeitraum von ``klein`` vollstaendig in ``gross`` liegt
    (gleicher Sendungsname) und ``gross`` mindestens genauso weit reicht.

    Deckt die bei AzuraCast beobachtete Dublette ab: eine Sendung, die ueber
    Mitternacht laeuft (z.B. 21:00-06:00), taucht im Rohabruf manchmal
    zusaetzlich als zweiter Eintrag ab 00:00 desselben Resttages auf. Der
    zweite Eintrag ist eine echte Teilmenge des ersten und wird verworfen,
    damit die Sendung dem Beginn-Tag (21:00) zugeordnet bleibt und nicht
    doppelt erscheint.
    """
    if klein is gross:
        return False
    if klein.get("name") != gross.get("name"):
        return False
    ks, ke = klein.get("start_timestamp"), klein.get("end_timestamp")
    gs, ge = gross.get("start_timestamp"), gross.get("end_timestamp")
    if None in (ks, ke, gs, ge):
        return False
    innerhalb = (gs <= ks) and (ge >= ke)
    echt_kleiner = (gs < ks) or (ge > ke)
    return innerhalb and echt_kleiner


def _schedule_vereinfachen(rohliste):
    """Reduziert die Rohantwort von GET /api/station/1/schedule auf
    {name, beschreibung, start, ende, jetzt} -- nur Sendungen (Playlists),
    keine Jingles. Ueber-Mitternacht-Dubletten (siehe ``_ist_teilmenge``)
    werden auf den Eintrag mit dem fruehesten Start zusammengefasst, damit
    eine Sendung immer dem Tag ihres Beginns zugeordnet bleibt und ``jetzt``
    bei Ueberlappung nicht an mehreren Eintraegen gleichzeitig steht.

    Reine Funktion ohne Odoo-Env -- bewusst model-frei und damit ohne
    Datenbank testbar.
    """
    sendungen = [r for r in (rohliste or []) if r.get("type") == "playlist"]

    behalten = [
        eintrag for eintrag in sendungen
        if not any(_ist_teilmenge(eintrag, andere) for andere in sendungen)
    ]
    behalten.sort(key=lambda e: (e.get("start_timestamp") or 0))

    return [
        {
            "name": e.get("name") or e.get("title") or "",
            "beschreibung": e.get("description") or "",
            "start": e.get("start"),
            "ende": e.get("end"),
            "jetzt": bool(e.get("is_now")),
        }
        for e in behalten
    ]


class FrawoRadioAzuracast(models.AbstractModel):
    _name = "frawo.radio.azuracast"
    _description = "AzuraCast REST-Client (Playlisten-Gewichte)"

    def _api_config(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        base = (get_param("frawo_agent.azuracast_api_url", "") or "").rstrip("/")
        key = get_param("frawo_agent.azuracast_api_key", "") or ""
        return base, key

    def _headers(self):
        _, key = self._api_config()
        return {"X-API-Key": key}

    def list_playlists(self):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlists"
        resp = requests.get(url, headers=self._headers(), verify=False, timeout=TIMEOUT)
        if resp.status_code != 200:
            _logger.warning("AzuraCast-Playlisten nicht lesbar (HTTP %s)", resp.status_code)
            return []
        return resp.json()

    def get_weights(self, playlist_ids):
        wanted = set(playlist_ids)
        out = {}
        for pl in self.list_playlists():
            if pl.get("id") in wanted:
                out[pl["id"]] = pl.get("weight")
        return out

    def set_weight(self, playlist_id, weight):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlist/{playlist_id}"
        resp = requests.put(
            url, headers=self._headers(), json={"weight": weight},
            verify=False, timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            _logger.warning(
                "Gewicht fuer Playlist %s nicht gesetzt (HTTP %s)",
                playlist_id, resp.status_code,
            )
            return False
        return True
