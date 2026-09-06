from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "frawo_agent")
class TestAzuracastClient(TransactionCase):

    def setUp(self):
        super().setUp()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("frawo_agent.azuracast_api_url", "https://radio.test/")
        ICP.set_param("frawo_agent.azuracast_api_key", "testkey")

    def test_api_config_strips_trailing_slash(self):
        base, key = self.env["frawo.radio.azuracast"]._api_config()
        self.assertEqual(base, "https://radio.test")
        self.assertEqual(key, "testkey")

    def test_get_weights_maps_id_to_weight(self):
        payload = [
            {"id": 846, "name": "Ch1", "weight": 3},
            {"id": 848, "name": "Ch3", "weight": 5},
            {"id": 999, "name": "Andere", "weight": 1},
        ]
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.get") as m:
            m.return_value.status_code = 200
            m.return_value.json.return_value = payload
            out = self.env["frawo.radio.azuracast"].get_weights([846, 848])
        self.assertEqual(out, {846: 3, 848: 5})

    def test_set_weight_sends_put_and_reports_success(self):
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.put") as m:
            m.return_value.status_code = 200
            ok = self.env["frawo.radio.azuracast"].set_weight(846, 4)
            called_url = m.call_args.args[0]
            sent = m.call_args.kwargs["json"]
        self.assertTrue(ok)
        self.assertIn("/playlist/846", called_url)
        self.assertEqual(sent["weight"], 4)

    def test_set_weight_failure_returns_false(self):
        with patch("odoo.addons.frawo_agent.models.radio_azuracast.requests.put") as m:
            m.return_value.status_code = 500
            ok = self.env["frawo.radio.azuracast"].set_weight(846, 4)
        self.assertFalse(ok)
