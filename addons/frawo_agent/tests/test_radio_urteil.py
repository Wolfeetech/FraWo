from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioUrteil(TransactionCase):
    def setUp(self):
        super().setUp()
        self.U = self.env["frawo.radio.urteil"]

    def test_upsert_letzter_wert_zaehlt(self):
        self.U.urteilen("A|B", "energie", 2)
        self.U.urteilen("A|B", "energie", 4)
        recs = self.U.search([("track_id", "=", "A|B"), ("art", "=", "energie")])
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs.wert, 4)

    def test_energie_nur_1_bis_5(self):
        with self.assertRaises(ValueError):
            self.U.urteilen("A|B", "energie", 6)

    def test_passt_nur_0_oder_1_mit_sendung(self):
        r = self.U.urteilen("A|B", "passt", 0, sendung="01 Sunrise")
        self.assertEqual((r.wert, r.sendung), (0, "01 Sunrise"))
        with self.assertRaises(ValueError):
            self.U.urteilen("A|B", "passt", 2)

    def test_platzhalter_nicht_urteilbar(self):
        for key in ("", "FraWo Funk", "|"):
            with self.assertRaises(ValueError):
                self.U.urteilen(key, "energie", 3)

    def test_export(self):
        self.U.urteilen("A|B", "energie", 5)
        rows = self.U.export_rows()
        self.assertTrue(any(r["track_id"] == "A|B" and r["wert"] == 5 for r in rows))

    def test_direct_create_umgeht_urteilen_nicht(self):
        with self.assertRaises(ValidationError):
            self.U.create({"track_id": "A|B", "art": "energie", "wert": 9})
