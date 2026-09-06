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


@tagged("post_install", "-at_install", "frawo_agent")
class TestWeightMath(TransactionCase):

    def setUp(self):
        super().setUp()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("frawo_agent.radio_chill_playlist_ids", "846,847")
        ICP.set_param("frawo_agent.radio_energy_playlist_ids", "848,849")

    def _compute(self, current, energy, chill):
        return self.env["frawo.radio.vote"]._compute_targets(current, energy, chill)

    def test_no_votes_returns_to_base(self):
        current = {846: 5, 847: 4, 848: 2, 849: 1}
        out = self._compute(current, energy=0, chill=0)
        self.assertEqual(out, {846: 4, 847: 3, 848: 3, 849: 2})

    def test_no_votes_at_base_changes_nothing(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=0, chill=0)
        self.assertEqual(out, {})

    def test_energy_majority_shifts_one_step(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=5, chill=1)
        self.assertEqual(out, {846: 2, 847: 2, 848: 4, 849: 4})

    def test_chill_majority_shifts_one_step(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=0, chill=3)
        self.assertEqual(out, {846: 4, 847: 4, 848: 2, 849: 2})

    def test_margin_below_threshold_changes_nothing(self):
        current = {846: 3, 847: 3, 848: 3, 849: 3}
        out = self._compute(current, energy=3, chill=2)
        self.assertEqual(out, {})

    def test_upper_bound_is_respected(self):
        current = {846: 1, 847: 1, 848: 6, 849: 6}
        out = self._compute(current, energy=9, chill=0)
        self.assertEqual(out, {})

    def test_lower_bound_is_respected(self):
        current = {846: 6, 847: 6, 848: 1, 849: 1}
        out = self._compute(current, energy=0, chill=9)
        self.assertEqual(out, {})
