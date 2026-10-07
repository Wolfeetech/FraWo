#!/usr/bin/env python3
"""Sparbetrieb-Endpunkt fuer Hermes (Odoo #1966). Letzte Stufe der Ausweichkette.

Wolf 07.10.2026: "Fallback Claude, Codex vor Ollama, und Ollama soll nur 'aktuell Sparbetrieb, da keine Token
verfuegbar' antworten, damit nicht aus Versehen etwas zerschossen wird."

Statt eines Sprachmodells antwortet hier ein fester Text. Er enthaelt nie Werkzeug-Aufrufe, kann also technisch
nichts ausfuehren oder aendern. OpenAI-kompatibel (/v1/chat/completions, mit und ohne Streaming, /v1/models),
lauscht nur auf 127.0.0.1.
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODELL = "frawo-sparbetrieb"
TEXT = ("⚠️ Sparbetrieb: Codex und Claude sind gerade nicht verfügbar (Kontingent aufgebraucht oder Störung). "
        "Ich führe nichts aus und ändere nichts. Dein Auftrag bleibt liegen – bitte später nochmal schicken "
        "oder direkt in Odoo anlegen.")


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            self._json({"object": "list", "data": [{"id": MODELL, "object": "model", "owned_by": "frawo"}]})
        else:
            self._json({"ok": True, "modell": MODELL})

    def do_POST(self):
        laenge = int(self.headers.get("Content-Length") or 0)
        try:
            anfrage = json.loads(self.rfile.read(laenge) or b"{}")
        except ValueError:
            anfrage = {}
        jetzt = int(time.time())
        if anfrage.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            for delta, ende in (({"role": "assistant", "content": TEXT}, None), ({}, "stop")):
                stueck = {"id": "spar-%d" % jetzt, "object": "chat.completion.chunk", "created": jetzt, "model": MODELL,
                          "choices": [{"index": 0, "delta": delta, "finish_reason": ende}]}
                self.wfile.write(b"data: " + json.dumps(stueck).encode() + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
            return
        self._json({"id": "spar-%d" % jetzt, "object": "chat.completion", "created": jetzt, "model": MODELL,
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": TEXT}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
