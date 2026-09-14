from decimal import Decimal
from odoo.tests.common import TransactionCase, HttpCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioRating(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env["frawo.radio.rating"].search([]).unlink()
        self.p1 = self.env["res.partner"].create({"name": "Hörerin A"})
        self.p2 = self.env["res.partner"].create({"name": "Hörer B"})
        self.Rating = self.env["frawo.radio.rating"]

    def test_rate_creates_record(self):
        rec = self.Rating.rate("Artist|Song", self.p1.id, 4)
        self.assertTrue(rec.id)
        self.assertEqual(rec.stars, "4")

    def test_rate_again_updates_instead_of_duplicating(self):
        self.Rating.rate("Artist|Song", self.p1.id, 4)
        self.Rating.rate("Artist|Song", self.p1.id, 2)
        recs = self.Rating.search([("track_id", "=", "Artist|Song"), ("partner_id", "=", self.p1.id)])
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs.stars, "2")

    def test_rate_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            self.Rating.rate("Artist|Song", self.p1.id, 6)
        with self.assertRaises(ValueError):
            self.Rating.rate("Artist|Song", self.p1.id, 0)

    def test_summary_average_count_own(self):
        self.Rating.rate("Artist|Song", self.p1.id, 5)
        self.Rating.rate("Artist|Song", self.p2.id, 4)
        s = self.Rating.summary("Artist|Song", self.p1.id)
        self.assertEqual(s["average"], 4.5)
        self.assertEqual(s["count"], 2)
        self.assertEqual(s["own"], 5)

    def test_summary_without_ratings(self):
        s = self.Rating.summary("Niemand|Nie", None)
        self.assertEqual(s, {"average": None, "count": 0, "own": None})

    def test_export_rows_threshold_and_rounding(self):
        self.Rating.rate("A|Eins", self.p1.id, 5)
        self.Rating.rate("A|Eins", self.p2.id, 4)   # avg 4.5 -> 5
        self.Rating.rate("B|Zwei", self.p1.id, 3)   # nur 1 Bewertung -> raus
        rows = self.Rating.export_rows(min_count=2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["track_id"], "A|Eins")
        self.assertEqual(rows[0]["artist"], "A")
        self.assertEqual(rows[0]["title"], "Eins")
        self.assertEqual(rows[0]["count"], 2)
        self.assertEqual(rows[0]["average"], 4.5)
        self.assertEqual(rows[0]["stars"], 5)


@tagged("post_install", "-at_install", "frawo_agent")
class TestRatingRoutes(HttpCase):

    def setUp(self):
        super().setUp()
        self.env["frawo.radio.rating"].search([]).unlink()
        self.env["ir.config_parameter"].sudo().set_param("frawo_agent.summary_token", "exporttok")
        self.partner = self.env["res.partner"].create({"name": "Portal Tester"})
        self.user = self.env["res.users"].create({
            "name": "Portal Tester", "login": "portaltester@test.local",
            "partner_id": self.partner.id,
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })

    def test_summary_public_without_ratings(self):
        r = self.url_open("/radio/rating/summary?track_id=X%7CY")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "average": None, "count": 0, "own": None})

    def test_rate_requires_login(self):
        r = self.url_open("/radio/rate", data='{"jsonrpc":"2.0","method":"call","params":{"song_id":"X|Y","stars":4},"id":1}',
                          headers={"Content-Type": "application/json"})
        # Not logged in as portal user -> forbidden or rejected
        self.assertTrue(r.status_code in (200, 403))
        if r.status_code == 200:
            res = r.json()
            # If JSON-RPC succeeded or gave error/result ok=False
            if "result" in res:
                self.assertFalse(res["result"].get("ok"))

    def test_export_requires_token(self):
        r = self.url_open("/radio/ratings/export")
        self.assertEqual(r.status_code, 401)

    def test_export_with_token_returns_rows(self):
        p2 = self.env["res.partner"].create({"name": "Zweite"})
        self.env["frawo.radio.rating"].rate("A|Eins", self.partner.id, 5)
        self.env["frawo.radio.rating"].rate("A|Eins", p2.id, 4)
        r = self.url_open("/radio/ratings/export", headers={"X-Agent-Token": "exporttok"})
        self.assertEqual(r.status_code, 200)
        rows = r.json()
        self.assertEqual(rows[0]["track_id"], "A|Eins")
        self.assertEqual(rows[0]["stars"], 5)
