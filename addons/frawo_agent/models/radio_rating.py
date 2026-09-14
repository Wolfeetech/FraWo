# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models

STAR_CHOICES = [(str(n), "★" * n) for n in range(1, 6)]


class FrawoRadioRating(models.Model):
    _name = "frawo.radio.rating"
    _description = "FraWo Radio Sterne-Bewertung (eine pro Person und Titel)"
    _order = "write_date desc"

    track_id = fields.Char(string="Track", index=True, required=True)
    partner_id = fields.Many2one("res.partner", string="Bewertet von", index=True,
                                 required=True, ondelete="cascade")
    stars = fields.Selection(STAR_CHOICES, string="Sterne", required=True)

    _rating_unique_track_partner = models.Constraint(
        "UNIQUE(track_id, partner_id)",
        "Eine Person kann einen Titel nur einmal bewerten (erneut bewerten ueberschreibt).",
    )

    @api.model
    def rate(self, track_id, partner_id, stars):
        try:
            stars = int(stars)
        except (TypeError, ValueError):
            raise ValueError("stars muss eine Ganzzahl zwischen 1 und 5 sein")
        if stars < 1 or stars > 5:
            raise ValueError("stars muss zwischen 1 und 5 liegen")
        rec = self.search([("track_id", "=", track_id), ("partner_id", "=", partner_id)], limit=1)
        if rec:
            rec.write({"stars": str(stars)})
            return rec
        return self.create({"track_id": track_id, "partner_id": partner_id, "stars": str(stars)})

    @api.model
    def summary(self, track_id, partner_id=None):
        recs = self.search([("track_id", "=", track_id)])
        if not recs:
            return {"average": None, "count": 0, "own": None}
        values = [int(r.stars) for r in recs]
        own = None
        if partner_id:
            mine = recs.filtered(lambda r: r.partner_id.id == partner_id)
            own = int(mine[0].stars) if mine else None
        return {
            "average": round(sum(values) / len(values), 1),
            "count": len(values),
            "own": own,
        }

    @api.model
    def export_rows(self, min_count=1):
        groups = self.read_group(
            [], ["stars"], ["track_id"], lazy=False)
        rows = []
        Vote = self.env["frawo.radio.vote"].sudo()
        for g in groups:
            track_id = g["track_id"]
            recs = self.search([("track_id", "=", track_id)])
            count = len(recs)
            if count < min_count:
                continue
            avg = sum(int(r.stars) for r in recs) / count
            artist, sep, title = track_id.partition("|")
            likes = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "like")])
            unlikes = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "unlike")])
            hates = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "hate")])
            rows.append({
                "track_id": track_id,
                "artist": artist.strip(),
                "title": title.strip() if sep else "",
                "average": round(avg, 1),
                "count": count,
                "stars": int(Decimal(str(avg)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
                "likes": max(0, likes - unlikes),
                "hates": hates,
            })

        # Also capture tracks with mood votes (likes/skips) that have no star ratings yet
        voted_tracks = Vote.read_group([], ["vote_type"], ["track_id"], lazy=False)
        for vg in voted_tracks:
            track_id = vg["track_id"]
            if any(r["track_id"] == track_id for r in rows):
                continue
            likes = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "like")])
            unlikes = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "unlike")])
            hates = Vote.search_count([("track_id", "=", track_id), ("vote_type", "=", "hate")])
            net_likes = max(0, likes - unlikes)
            if net_likes == 0 and hates == 0:
                continue
            artist, sep, title = track_id.partition("|")
            rows.append({
                "track_id": track_id,
                "artist": artist.strip(),
                "title": title.strip() if sep else "",
                "average": None,
                "count": 0,
                "stars": None,
                "likes": net_likes,
                "hates": hates,
            })

        rows.sort(key=lambda r: (-(r["average"] or 0), -r.get("likes", 0), r["track_id"]))
        return rows
