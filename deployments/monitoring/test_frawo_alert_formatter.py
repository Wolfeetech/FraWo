"""Tests fuer frawo_alert_formatter (Odoo #1541): kein Alarm darf still verloren gehen.

Aufruf: python3 -m pytest -q deployments/monitoring/test_frawo_alert_formatter.py
Kein Netz noetig: Ollama und Telegram werden ersetzt, es geht keine echte Nachricht raus.
"""
import importlib.util
import io
import json
import threading
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location("fmt", Path(__file__).with_name("frawo_alert_formatter.py"))
fmt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fmt)


def _alarm(name, fp, status="firing"):
    return {"status": status, "fingerprint": fp, "startsAt": "2026-10-06T08:00:00Z",
            "labels": {"alertname": name, "severity": "critical"}, "annotations": {"summary": name}}


@pytest.fixture(autouse=True)
def _sauber(monkeypatch):
    fmt._zugestellt.clear()
    monkeypatch.setattr(fmt, "formulate_with_ollama", lambda a: None)  # Rohmeldung erzwingen


def test_zustellung_ok_liefert_true(monkeypatch):
    gesendet = []
    monkeypatch.setattr(fmt, "send_telegram", lambda t: gesendet.append(t) or True)
    assert fmt.process_alertmanager_payload({"alerts": [_alarm("A", "1"), _alarm("B", "2")]}) is True
    assert len(gesendet) == 2


def test_telegram_fehler_liefert_false(monkeypatch):
    monkeypatch.setattr(fmt, "send_telegram", lambda t: False)
    assert fmt.process_alertmanager_payload({"alerts": [_alarm("A", "1")]}) is False


def test_wiederholung_schickt_nur_fehlende(monkeypatch):
    # 1. Lauf: A geht durch, B scheitert
    erg = {"A": True, "B": False}
    gesendet = []
    def senden(text):
        name = "A" if "A" in text.splitlines()[0] or "A" in text else "B"
        gesendet.append(name)
        return erg[name]
    monkeypatch.setattr(fmt, "build_raw_message", lambda a: a["labels"]["alertname"])
    monkeypatch.setattr(fmt, "send_telegram", senden)
    payload = {"alerts": [_alarm("A", "1"), _alarm("B", "2")]}
    assert fmt.process_alertmanager_payload(payload) is False
    # 2. Lauf (Alertmanager wiederholt): jetzt klappt alles, A darf NICHT erneut kommen
    erg["B"] = True
    assert fmt.process_alertmanager_payload(payload) is True
    assert gesendet == ["A", "B", "B"]


def test_entwarnung_ist_eigene_meldung(monkeypatch):
    gesendet = []
    monkeypatch.setattr(fmt, "send_telegram", lambda t: gesendet.append(t) or True)
    fmt.process_alertmanager_payload({"alerts": [_alarm("A", "1")]})
    fmt.process_alertmanager_payload({"alerts": [_alarm("A", "1", status="resolved")]})
    assert len(gesendet) == 2


@pytest.mark.parametrize("ok,code", [(True, 200), (False, 502)])
def test_http_antwort(monkeypatch, ok, code):
    monkeypatch.setattr(fmt, "send_telegram", lambda t: ok)
    srv = HTTPServer(("127.0.0.1", 0), fmt.AlertHandler)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    req = urllib.request.Request(f"http://127.0.0.1:{srv.server_port}/alert",
                                 data=json.dumps({"alerts": [_alarm("A", "x" + str(code))]}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    srv.server_close()
    assert status == code


@pytest.mark.parametrize("token,code", [("x", 200), ("", 503)])
def test_health(monkeypatch, token, code):
    monkeypatch.setattr(fmt, "TELEGRAM_BOT_TOKEN", token)
    srv = HTTPServer(("127.0.0.1", 0), fmt.AlertHandler)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{srv.server_port}/health", timeout=5) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    srv.server_close()
    assert status == code
