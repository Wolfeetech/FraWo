#!/usr/bin/env python3
"""Odoo -> Hermes Relais (Odoo #1966). Laeuft auf CT160 (10.1.0.160:8645).

Odoo-Automatiken koennen keine eigenen Kopfzeilen/Signaturen setzen. Dieses Relais nimmt den Odoo-Webhook an
(nur von CT140 10.1.0.112, nur mit geheimem Pfad), antwortet SOFORT 200 (Regel: sofortiges ACK) und reicht die
Nutzlast an den Hermes-Webhook-Adapter (127.0.0.1:8644) weiter - mit X-Gitlab-Token (Route-Secret) und
X-Request-ID (= Odoo-Datensatz-ID, Hermes verwirft Doppelte).
Geheimnisse aus /etc/frawo/odoo-relais.env (600): RELAIS_PFAD, HERMES_ROUTE_TOKEN.
"""
import json
import os
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ENV = dict(l.strip().split("=", 1) for l in open("/etc/frawo/odoo-relais.env") if "=" in l and not l.startswith("#"))
PFAD = "/odoo/" + ENV["RELAIS_PFAD"]
TOKEN = ENV["HERMES_ROUTE_TOKEN"]
ERLAUBT = {"10.1.0.112"}
ZIEL = "http://127.0.0.1:8644/webhooks/odoo"


def weiterreichen(rohdaten, anfrage_id):
    req = urllib.request.Request(ZIEL, data=rohdaten, method="POST", headers={
        "Content-Type": "application/json", "X-Gitlab-Token": TOKEN, "X-Request-ID": anfrage_id})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("weitergereicht", anfrage_id, r.status, flush=True)
    except Exception as e:  # Hermes nicht erreichbar: nur protokollieren, Odoo hat sein 200 schon
        print("FEHLER weiterreichen", anfrage_id, e, flush=True)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.client_address[0] not in ERLAUBT or self.path != PFAD:
            self.send_response(404); self.end_headers(); return
        laenge = min(int(self.headers.get("Content-Length") or 0), 1_000_000)
        roh = self.rfile.read(laenge)
        self.send_response(200); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"ok")
        try:
            d = json.loads(roh or b"{}")
            anfrage_id = "odoo-%s-%s" % (d.get("_model", "x"), d.get("_id", d.get("id", "0")))
        except ValueError:
            return
        threading.Thread(target=weiterreichen, args=(roh, anfrage_id), daemon=True).start()

    def do_GET(self):
        self.send_response(200 if self.path == "/health" else 404); self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("10.1.0.160", 8645), Handler).serve_forever()
