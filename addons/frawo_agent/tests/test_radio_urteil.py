import json

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import HttpCase, TransactionCase, tagged


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

    def test_ohne_gruppe_kein_schreibrecht(self):
        kunde = self.env["res.users"].create({
            "name": "Kunde", "login": "kunde_test_urteil",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        with self.assertRaises(AccessError):
            self.U.with_user(kunde).urteilen("A|B", "energie", 3)


@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioUrteilRoutes(HttpCase):
    def setUp(self):
        super().setUp()
        self.env["frawo.radio.urteil"].search([]).unlink()
        self.env["ir.config_parameter"].sudo().set_param("frawo_agent.summary_token", "urteiltok")
        redaktion_group = self.env.ref("frawo_agent.group_radio_redaktion")
        self.redakteur = self.env["res.users"].create({
            "name": "Redakteurin", "login": "redakteurin_test_urteil",
            "password": "redakteurin_test_urteil_pw",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id, redaktion_group.id])],
        })
        self.kunde = self.env["res.users"].create({
            "name": "Kunde Route", "login": "kunde_test_urteil_route",
            "password": "kunde_test_urteil_route_pw",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })

    def test_info_public_ohne_model_zugriff(self):
        r = self.url_open("/radio/redaktion/info?track_id=A%7CB")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "redakteur": False, "eigene": {"energie": None, "passt": None}})

    def test_info_redakteur_zeigt_eigene_urteile(self):
        self.env["frawo.radio.urteil"].with_user(self.redakteur).urteilen("A|B", "energie", 4)
        self.authenticate("redakteurin_test_urteil", "redakteurin_test_urteil_pw")
        r = self.url_open("/radio/redaktion/info?track_id=A%7CB")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["redakteur"])
        self.assertEqual(data["eigene"], {"energie": 4, "passt": None})

    def test_urteil_ohne_gruppe_403(self):
        self.authenticate("kunde_test_urteil_route", "kunde_test_urteil_route_pw")
        r = self.url_open(
            "/radio/redaktion/urteil",
            data=json.dumps({"track_id": "A|B", "art": "energie", "wert": 3}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json(), {"ok": False, "error": "forbidden"})

    def test_urteil_mit_gruppe_200(self):
        self.authenticate("redakteurin_test_urteil", "redakteurin_test_urteil_pw")
        r = self.url_open(
            "/radio/redaktion/urteil",
            data=json.dumps({"track_id": "A|B", "art": "energie", "wert": 5}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True})
        rec = self.env["frawo.radio.urteil"].sudo().search(
            [("track_id", "=", "A|B"), ("art", "=", "energie"), ("user_id", "=", self.redakteur.id)])
        self.assertEqual(rec.wert, 5)

    def test_urteil_ungueltig_400(self):
        self.authenticate("redakteurin_test_urteil", "redakteurin_test_urteil_pw")
        r = self.url_open(
            "/radio/redaktion/urteil",
            data=json.dumps({"track_id": "A|B", "art": "energie", "wert": 9}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()["ok"])

    def test_export_ohne_token_401(self):
        r = self.url_open("/radio/redaktion/export")
        self.assertEqual(r.status_code, 401)

    def test_export_mit_token_liefert_export_rows(self):
        self.env["frawo.radio.urteil"].with_user(self.redakteur).urteilen("A|B", "energie", 5)
        r = self.url_open("/radio/redaktion/export", headers={"X-Agent-Token": "urteiltok"})
        self.assertEqual(r.status_code, 200)
        rows = r.json()
        self.assertTrue(any(row["track_id"] == "A|B" and row["wert"] == 5 for row in rows))
