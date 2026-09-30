#!/usr/bin/env python3
"""Tests für scripts/odoo_anhang.py — Browser-Fallback bei PDF-Erzeugung.

Deckt die zwei Jarvis-Review-Befunde zu Aufgabe #1235 (Nachricht 21242) ab:
1. html_zu_pdf() darf bei Timeout/Startfehler des Browsers nicht crashen,
   sondern muss False liefern, damit baue_anhaenge() auf das Original zurückfällt.
2. --nur-pdf muss mit Exit-Code != 0 enden, wenn kein PDF entstanden ist.

Aufruf: python -m pytest scripts/test_odoo_anhang.py -v
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import odoo_anhang  # noqa: E402


# ---------------------------------------------------------------------------
# 1. html_zu_pdf(): TimeoutExpired / FileNotFoundError / OSError abgefangen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "ausnahme",
    [
        subprocess.TimeoutExpired(cmd=["chrome"], timeout=120),
        FileNotFoundError("Browser-Pfad existiert nicht"),
        OSError("Startfehler des Browsers"),
    ],
)
def test_html_zu_pdf_faengt_startfehler_ab(monkeypatch, tmp_path, ausnahme):
    """subprocess.run wirft -> html_zu_pdf() liefert False statt zu crashen."""

    def kaputter_run(*args, **kwargs):
        raise ausnahme

    monkeypatch.setattr(odoo_anhang.subprocess, "run", kaputter_run)

    html_pfad = tmp_path / "eingabe.html"
    html_pfad.write_text("<html><body>Test</body></html>", encoding="utf-8")
    pdf_pfad = tmp_path / "ausgabe.pdf"

    ergebnis = odoo_anhang.html_zu_pdf("chrome-attrappe", html_pfad, pdf_pfad)

    assert ergebnis is False
    assert not pdf_pfad.exists()


def test_html_zu_pdf_ok_bei_erfolgreichem_lauf(monkeypatch, tmp_path):
    """Gegenprobe: wenn der Browser ein echtes PDF schreibt, liefert die Funktion True."""

    def erfolgreicher_run(befehl, **kwargs):
        pdf_ziel = [teil for teil in befehl if teil.startswith("--print-to-pdf=")][0]
        pdf_pfad = Path(pdf_ziel.split("=", 1)[1])
        pdf_pfad.write_bytes(b"%PDF-1.4\n" + b"0" * 2000)

    monkeypatch.setattr(odoo_anhang.subprocess, "run", erfolgreicher_run)

    html_pfad = tmp_path / "eingabe.html"
    html_pfad.write_text("<html><body>Test</body></html>", encoding="utf-8")
    pdf_pfad = tmp_path / "ausgabe.pdf"

    ergebnis = odoo_anhang.html_zu_pdf("chrome-attrappe", html_pfad, pdf_pfad)

    assert ergebnis is True
    assert pdf_pfad.exists()


# ---------------------------------------------------------------------------
# 2. baue_anhaenge(): dokumentierter Rückfall (Original + Warnung "PDF fehlt")
# ---------------------------------------------------------------------------

def test_baue_anhaenge_faellt_bei_timeout_auf_original_zurueck(monkeypatch, tmp_path):
    html_pfad = tmp_path / "vorlage.html"
    html_pfad.write_text("<html><body>Vorlage</body></html>", encoding="utf-8")
    arbeitsordner = tmp_path / "arbeit"
    arbeitsordner.mkdir()

    monkeypatch.setattr(odoo_anhang, "finde_browser", lambda: "chrome-attrappe")

    def timeout_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["chrome"], timeout=120)

    monkeypatch.setattr(odoo_anhang.subprocess, "run", timeout_run)

    anhaenge, warnungen = odoo_anhang.baue_anhaenge(html_pfad, arbeitsordner, mit_original=False)

    assert anhaenge == [html_pfad]
    assert any("PDF fehlt" in w for w in warnungen)


# ---------------------------------------------------------------------------
# 3. --nur-pdf: Exit-Code != 0, wenn kein PDF erzeugt wurde
# ---------------------------------------------------------------------------

def test_nur_pdf_exit_code_ungleich_null_ohne_pdf(monkeypatch, tmp_path, capsys):
    html_pfad = tmp_path / "vorlage.html"
    html_pfad.write_text("<html><body>Vorlage</body></html>", encoding="utf-8")
    ausgabeordner = tmp_path / "ausgabe"

    # Kein Browser installiert/gefunden -> baue_anhaenge() muss warnen, kein PDF entsteht.
    monkeypatch.setattr(odoo_anhang, "finde_browser", lambda: None)
    monkeypatch.setattr(
        sys, "argv",
        ["odoo_anhang.py", "0", str(html_pfad), "--nur-pdf", str(ausgabeordner)],
    )

    rc = odoo_anhang.main()

    assert rc != 0
    ausgabe = capsys.readouterr()
    assert "PDF fehlt" in ausgabe.err


def test_nur_pdf_exit_code_null_mit_pdf(monkeypatch, tmp_path, capsys):
    """Gegenprobe: entsteht ein echtes PDF, bleibt --nur-pdf bei Exit-Code 0."""
    html_pfad = tmp_path / "vorlage.html"
    html_pfad.write_text("<html><body>Vorlage</body></html>", encoding="utf-8")
    ausgabeordner = tmp_path / "ausgabe"

    monkeypatch.setattr(odoo_anhang, "finde_browser", lambda: "chrome-attrappe")

    def erfolgreicher_run(befehl, **kwargs):
        pdf_ziel = [teil for teil in befehl if teil.startswith("--print-to-pdf=")][0]
        pdf_pfad = Path(pdf_ziel.split("=", 1)[1])
        pdf_pfad.write_bytes(b"%PDF-1.4\n" + b"0" * 2000)

    monkeypatch.setattr(odoo_anhang.subprocess, "run", erfolgreicher_run)
    monkeypatch.setattr(
        sys, "argv",
        ["odoo_anhang.py", "0", str(html_pfad), "--nur-pdf", str(ausgabeordner)],
    )

    rc = odoo_anhang.main()

    assert rc == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
