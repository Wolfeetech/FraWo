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
