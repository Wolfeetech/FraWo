import os
import unittest
from unittest.mock import patch


TEST_ENV = {
    "FRAWO_TASK_SECRET": "test",
    "FRAWO_ALERT_SECRET": "test",
    "FRAWO_CHATTER_SECRET": "test",
    "ODOO_URL": "http://odoo.invalid",
    "ODOO_DB": "test",
    "ODOO_LOGIN": "test",
    "ODOO_APIKEY": "test",
    "OLLAMA_URL": "http://ollama.invalid",
    "OLLAMA_POWER_PARTNER_ID": "321",
}

with patch.dict(os.environ, TEST_ENV):
    from odoo_webhook_handler import _is_power_mention, _post


class RecordingRPC:
    def __init__(self):
        self.call_args = None

    def call(self, model, method, record_ids, values):
        self.call_args = (model, method, record_ids, values)


class PowerMentionTests(unittest.TestCase):
    def test_ollama_post_defaults_to_internal_note(self):
        rpc = RecordingRPC()

        _post(rpc, "project.task", 1581, "<p>Antwort</p>")

        self.assertEqual(rpc.call_args[3]["subtype_xmlid"], "mail.mt_note")

    def test_routes_only_the_linked_power_partner_to_power(self):
        body = (
            '<a data-oe-id="321" data-oe-model="res.partner">'
            '@🤖 Ollama Power</a>'
        )

        self.assertTrue(_is_power_mention(body, 321))

    def test_other_ollama_partner_remains_routine(self):
        body = (
            '<a data-oe-id="160" data-oe-model="res.partner">'
            '@🤖 Ollama Mitarbeiter</a>'
        )

        self.assertFalse(_is_power_mention(body, 321))

    def test_unlinked_word_power_does_not_select_power(self):
        body = '<p>@🤖 Ollama Mitarbeiter please use power reasoning</p>'

        self.assertFalse(_is_power_mention(body, 321))

    def test_same_partner_id_on_another_model_is_not_a_mention(self):
        body = '<a data-oe-id="321" data-oe-model="res.users">@Power</a>'

        self.assertFalse(_is_power_mention(body, 321))


if __name__ == "__main__":
    unittest.main()
