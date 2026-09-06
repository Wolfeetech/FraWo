# -*- coding: utf-8 -*-
from odoo import api, fields, models

# Kanal-Demokratie: Gewichtsgrenzen fuer die AzuraCast-Rotationsplaylisten.
BASE_WEIGHT = 3
MIN_WEIGHT = 1
MAX_WEIGHT = 6
VOTE_MARGIN = 2


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
