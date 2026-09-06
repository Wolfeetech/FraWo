# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Kanal-Demokratie: Gewichtsgrenzen fuer die AzuraCast-Rotationsplaylisten.
BASE_WEIGHT = 3
MIN_WEIGHT = 1
MAX_WEIGHT = 6
VOTE_MARGIN = 2
VOTE_WINDOW_MINUTES = 15


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

    @api.model
    def _channel_groups(self):
        """Playlist-IDs je Stimmungsrichtung, aus den Systemparametern."""
        get_param = self.env["ir.config_parameter"].sudo().get_param

        def _ids(key, default):
            raw = get_param(key, default) or ""
            return [int(p) for p in raw.replace(" ", "").split(",") if p]

        return (
            _ids("frawo_agent.radio_chill_playlist_ids", "846,847"),
            _ids("frawo_agent.radio_energy_playlist_ids", "848,849"),
        )

    @api.model
    def _compute_targets(self, current, energy, chill):
        """Zielgewichte berechnen. Reine Funktion: kein HTTP, keine Seiteneffekte.

        Ohne klare Mehrheit (Abstand kleiner VOTE_MARGIN) wandert jedes Gewicht
        einen Schritt Richtung BASE_WEIGHT zurueck. Mit Mehrheit bekommt die
        gewaehlte Richtung einen Schritt mehr, die Gegenrichtung einen weniger.
        Alles hart auf MIN_WEIGHT..MAX_WEIGHT begrenzt, maximal ein Schritt.
        Rueckgabe: nur die Playlists, deren Gewicht sich tatsaechlich aendert.
        """
        chill_ids, energy_ids = self._channel_groups()
        margin = energy - chill

        direction = {}
        if abs(margin) >= VOTE_MARGIN:
            for pid in energy_ids:
                direction[pid] = 1 if margin > 0 else -1
            for pid in chill_ids:
                direction[pid] = -1 if margin > 0 else 1
        else:
            for pid, weight in current.items():
                if weight > BASE_WEIGHT:
                    direction[pid] = -1
                elif weight < BASE_WEIGHT:
                    direction[pid] = 1

        targets = {}
        for pid, step in direction.items():
            old = current.get(pid)
            if old is None:
                continue
            new = min(MAX_WEIGHT, max(MIN_WEIGHT, old + step))
            if new != old:
                targets[pid] = new
        return targets

    @api.model
    def _cron_apply_vote_weights(self):
        """Verschiebt die Kanal-Gewichte anhand der Votes der letzten Minuten.

        Fail-closed: ohne Schalter frawo_agent.radio_democracy_enabled == "true"
        passiert nichts. Schreibt ueber die AzuraCast-REST-API, liest danach
        zurueck (am Ergebnis pruefen, nicht am Vorgang) und protokolliert jeden
        Lauf mit Aenderung in frawo.agent.log.
        """
        ICP = self.env["ir.config_parameter"].sudo()
        enabled = (ICP.get_param("frawo_agent.radio_democracy_enabled", "") or "").strip().lower()
        if enabled != "true":
            return

        cutoff = fields.Datetime.now() - timedelta(minutes=VOTE_WINDOW_MINUTES)
        energy = self.search_count([
            ("create_date", ">=", cutoff), ("vote_type", "=", "energy")])
        chill = self.search_count([
            ("create_date", ">=", cutoff), ("vote_type", "=", "chill")])

        chill_ids, energy_ids = self._channel_groups()
        api_client = self.env["frawo.radio.azuracast"]
        current = api_client.get_weights(chill_ids + energy_ids)
        if not current:
            _logger.warning("Radio-Demokratie: keine Gewichte lesbar, Lauf uebersprungen.")
            return

        targets = self._compute_targets(current, energy, chill)
        if not targets:
            return

        written, failed = {}, []
        for pid, weight in targets.items():
            if api_client.set_weight(pid, weight):
                written[pid] = weight
            else:
                failed.append(pid)

        # Am Ergebnis pruefen, nicht am Vorgang: Gewichte zurueckelesen.
        verify = api_client.get_weights(list(targets.keys()))
        mismatch = {pid: (targets[pid], verify.get(pid))
                    for pid in targets if verify.get(pid) != targets[pid]}

        self.env["frawo.agent.log"].sudo().create({
            "name": "Radio-Demokratie: Gewichte angepasst",
            "level": "warning" if (failed or mismatch) else "info",
            "message": (
                f"Fenster {VOTE_WINDOW_MINUTES} Min: energy={energy}, chill={chill}. "
                f"Vorher={current}. Ziel={targets}. Geschrieben={written}. "
                f"Fehlgeschlagen={failed}. Abweichung nach Rueckprobe={mismatch}."
            ),
        })
