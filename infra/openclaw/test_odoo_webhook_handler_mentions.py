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
    from odoo_webhook_handler import (
        _is_power_mention,
        _post,
        _ask_ollama,
        KeinRechenknoten,
        EMAIL_PROMPT_TEMPLATE,
    )


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

    def test_power_unreachable_raises_kein_rechenknoten_without_fallback(self):
        with patch("odoo_webhook_handler.OLLAMA_POWER_ZIELE", [("http://studiopc.invalid:11434", "power-model")]), \
             patch("odoo_webhook_handler._erreichbar", return_value=False):
            with self.assertRaises(KeinRechenknoten) as ctx:
                _ask_ollama("system", "prompt", power=True)
            self.assertIn("(aus)", str(ctx.exception))

    def test_power_not_configured_raises_kein_rechenknoten(self):
        with patch("odoo_webhook_handler.OLLAMA_POWER_ZIELE", []):
            with self.assertRaises(KeinRechenknoten) as ctx:
                _ask_ollama("system", "prompt", power=True)
            self.assertIn("Power-Lama ist nicht konfiguriert", str(ctx.exception))

    def test_power_failure_posts_unavailability_note(self):
        rpc = RecordingRPC()
        power = True
        body = (
            "<p>🤖 <b>Ollama Mitarbeiter</b> konnte nicht antworten: "
            + ("Power-Lama (StudioPC)" if power else "Routine-Lama (OptiPlex)")
            + " ist gerade nicht erreichbar. Die Frage bleibt offen — bitte später erneut erwähnen.</p>"
        )
        _post(rpc, "project.task", 1517, body, note=True)

        self.assertEqual(rpc.call_args[0], "project.task")
        self.assertEqual(rpc.call_args[2], [1517])
        self.assertEqual(rpc.call_args[3]["subtype_xmlid"], "mail.mt_note")
        self.assertIn("Power-Lama (StudioPC) ist gerade nicht erreichbar", rpc.call_args[3]["body"])

    def test_email_prompt_template_formatting(self):
        rendered = EMAIL_PROMPT_TEMPLATE.format(
            sender="kunde@example.com",
            recipient="agent@frawo.tech",
            subject="Anfrage Beschallung",
            date="2026-10-03 10:00:00",
            body="Hallo, wir brauchen eine Anlage für unser Event.",
        )
        self.assertIn("kunde@example.com", rendered)
        self.assertIn("agent@frawo.tech", rendered)
        self.assertIn("Anfrage Beschallung", rendered)
        self.assertIn("SPAM- & RELEVANZ-CHECK", rendered)
        self.assertIn("Shelly 10.4.0.11", rendered)


if __name__ == "__main__":
    unittest.main()
