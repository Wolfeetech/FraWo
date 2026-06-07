import logging
import requests
from odoo import api, models

_logger = logging.getLogger(__name__)


class OllamaClient(models.AbstractModel):
    _name = "frawo.ollama.client"
    _description = "Ollama HTTP Client (lokales LLM)"

    @api.model
    def _cfg(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(
            "frawo_agent.%s" % key, default)

    @api.model
    def generate(self, prompt):
        """Ruft Ollama. Gibt Text zurueck oder None bei Fehler/Timeout.
        Blockiert NIE laenger als das konfigurierte Timeout."""
        url = self._cfg("ollama_url", "http://172.17.0.1:11434")
        model = self._cfg("ollama_model", "llama3:8b")
        timeout = int(self._cfg("ollama_timeout", "90"))
        try:
            resp = requests.post(
                "%s/api/generate" % url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            resp.raise_for_status()
            return (resp.json().get("response") or "").strip()
        except Exception as e:  # Timeout, ConnectionError, HTTPError
            _logger.warning("frawo_agent: Ollama-Call fehlgeschlagen: %s", e)
            return None
