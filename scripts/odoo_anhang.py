#!/usr/bin/env python3
"""🤖 Dokument als Anhang an eine Odoo-Aufgabe hängen (Datei -> PDF -> Anhang + interne Notiz).

Warum: Wolf ist unterwegs am Handy. Ein Repo-Pfad („DOCS/…/x.html im Git-Repo“) nützt ihm nichts,
ein PDF an der Aufgabe schon. Regel steht in AGENTS.md, Odoo-Hausordnung („Dokumente für Wolf“).

Aufruf (aus dem Repo-Wurzelordner):
    python scripts/odoo_anhang.py 1235 DOCS/LEGAL/mietvertrag_uebergabeprotokoll_1seite.html --agent Claude
    python scripts/odoo_anhang.py 1526 DOCS/NOTFALL.md --notiz "Notfallanleitung zum Ausdrucken"
    python scripts/odoo_anhang.py 0 DOCS/NOTFALL.md --nur-pdf C:/temp   # nur PDF bauen, nichts hochladen

Was mit welcher Datei passiert:
    .html/.htm -> PDF + Original-HTML (Vorlage bleibt bearbeitbar)
    .md        -> PDF (gerendert); Original nur mit --original
    .pdf/.png/.jpg/sonstiges -> unverändert als Anhang

PDF-Wandlung: Chrome/Chromium/Edge headless (`--print-to-pdf`), Markdown über markdown-it-py.
Fehlt beides (z. B. auf CT150), wird das Original angehängt und die Notiz sagt, dass das PDF fehlt.

Zugang: API-Key des Agent-Users aus ODOO_RPC_API_KEY oder ODOO_API_KEY (Quelle: Vaultwarden).
Optional ODOO_RPC_URL / ODOO_RPC_DB / ODOO_RPC_USER.

Doppelschutz: Gleichnamiger Anhang an derselben Aufgabe wird überschrieben, nicht verdoppelt
(Merkmal: res_model + res_id + name). Die Notiz ist eine interne Notiz (subtype note) und
benachrichtigt niemanden.
"""
from __future__ import annotations

import argparse
import base64
import html
import os
import shutil
import subprocess
import sys
import tempfile
import xmlrpc.client
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from odoo_env import resolve_named_secret  # noqa: E402

BROWSER_KANDIDATEN = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge",
]

MD_CSS = """
@page { size: A4; margin: 16mm 16mm 18mm 16mm; }
body { font-family: "Inter", "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 18pt; border-bottom: 2px solid #1a1a1a; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 13.5pt; margin-top: 18px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 11.5pt; margin-top: 14px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.5pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #eee; }
tr { page-break-inside: avoid; }
code { font-family: Consolas, "DejaVu Sans Mono", monospace; font-size: 9pt; background: #f3f3f3; padding: 0 2px; }
pre { background: #f3f3f3; padding: 6px 8px; white-space: pre-wrap; word-break: break-word; font-size: 8.5pt; }
blockquote { border-left: 3px solid #999; margin: 8px 0; padding: 2px 10px; color: #444; }
.fuss { margin-top: 24px; font-size: 8pt; color: #777; border-top: 1px solid #ddd; padding-top: 4px; }
"""


def finde_browser() -> str | None:
    for kandidat in BROWSER_KANDIDATEN:
        if os.path.isabs(kandidat):
            if os.path.exists(kandidat):
                return kandidat
        else:
            pfad = shutil.which(kandidat)
            if pfad:
                return pfad
    return None


def markdown_zu_html(md_pfad: Path, quelle: str) -> str | None:
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        return None
    md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    koerper = md.render(md_pfad.read_text(encoding="utf-8"))
    return (
        "<!DOCTYPE html><html lang=\"de\"><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(md_pfad.stem)}</title><style>{MD_CSS}</style></head><body>"
        f"{koerper}<div class=\"fuss\">Quelle: {html.escape(quelle)} · Stand {date.today():%d.%m.%Y}</div>"
        "</body></html>"
    )


def html_zu_pdf(browser: str, html_pfad: Path, pdf_pfad: Path) -> bool:
    with tempfile.TemporaryDirectory(prefix="odoo_anhang_profil_") as profil:
        befehl = [
            browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
            f"--user-data-dir={profil}", f"--print-to-pdf={pdf_pfad}", html_pfad.resolve().as_uri(),
        ]
        subprocess.run(befehl, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return pdf_pfad.exists() and pdf_pfad.stat().st_size > 1000 and pdf_pfad.read_bytes()[:5] == b"%PDF-"


def baue_anhaenge(datei: Path, arbeitsordner: Path, mit_original: bool) -> tuple[list[Path], list[str]]:
    """Liefert (anzuhängende Dateien, Warnungen)."""
    endung = datei.suffix.lower()
    warnungen: list[str] = []
    if endung not in (".html", ".htm", ".md"):
        return [datei], warnungen

    browser = finde_browser()
    pdf = arbeitsordner / f"{datei.stem}.pdf"
    ergebnis: list[Path] = []
    if endung == ".md":
        quelle = datei.resolve().as_posix()
        if "/FraWo/" in quelle:
            quelle = quelle.split("/FraWo/", 1)[1]
        inhalt = markdown_zu_html(datei, quelle)
        if inhalt is None:
            warnungen.append("markdown-it-py fehlt – kein PDF, Original angehängt")
            return [datei], warnungen
        zwischen = arbeitsordner / f"{datei.stem}.render.html"
        zwischen.write_text(inhalt, encoding="utf-8")
        quelle_html = zwischen
    else:
        quelle_html = datei
        mit_original = True  # Vorlagen immer auch als bearbeitbares Original

    if browser and html_zu_pdf(browser, quelle_html, pdf):
        ergebnis.append(pdf)
    else:
        warnungen.append("kein Chrome/Chromium/Edge gefunden oder PDF-Druck gescheitert – PDF fehlt")
        mit_original = True
    if mit_original:
        ergebnis.append(datei)
    return ergebnis, warnungen


class Odoo:
    def __init__(self) -> None:
        self.url = os.getenv("ODOO_RPC_URL", "http://10.1.0.112:8069")
        self.db = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
        benutzer = os.getenv("ODOO_RPC_USER", "agent@frawo.tech")
        self.secret = resolve_named_secret("ODOO_RPC_API_KEY", "ODOO_API_KEY", prompt_label="Odoo-API-Key")
        self.uid = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common").authenticate(self.db, benutzer, self.secret, {})
        if not self.uid:
            raise SystemExit("Odoo-Anmeldung fehlgeschlagen (API-Key prüfen).")
        self.obj = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

    def call(self, model: str, methode: str, args: list, kwargs: dict | None = None):
        return self.obj.execute_kw(self.db, self.uid, self.secret, model, methode, args, kwargs or {})


def main() -> int:
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(encoding="utf-8")  # Windows-Konsole (cp1252) verträgt keine Emoji
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="Dokument als PDF-Anhang an eine Odoo-Aufgabe hängen")
    p.add_argument("task_id", type=int, help="ID der Odoo-Aufgabe (project.task)")
    p.add_argument("dateien", nargs="+", type=Path)
    p.add_argument("--agent", default="Claude", help="Name für die Notiz: Claude / Jarvis / Antigravity")
    p.add_argument("--notiz", default="", help="Ein Satz, was das Dokument ist")
    p.add_argument("--original", action="store_true", help="bei Markdown zusätzlich die .md anhängen")
    p.add_argument("--nur-pdf", type=Path, metavar="ORDNER", help="nur PDFs in ORDNER erzeugen, nichts hochladen")
    a = p.parse_args()

    for d in a.dateien:
        if not d.is_file():
            raise SystemExit(f"Datei nicht gefunden: {d}")

    with tempfile.TemporaryDirectory(prefix="odoo_anhang_") as tmp:
        arbeitsordner = a.nur_pdf or Path(tmp)
        arbeitsordner.mkdir(parents=True, exist_ok=True)
        anhaenge: list[Path] = []
        warnungen: list[str] = []
        for d in a.dateien:
            teile, w = baue_anhaenge(d, arbeitsordner, a.original)
            anhaenge += teile
            warnungen += [f"{d.name}: {x}" for x in w]
        for w in warnungen:
            print("WARNUNG:", w, file=sys.stderr)
        if a.nur_pdf:
            for x in anhaenge:
                print(x)
            return 0

        odoo = Odoo()
        task = odoo.call("project.task", "read", [[a.task_id]], {"fields": ["name"]})
        if not task:
            raise SystemExit(f"Aufgabe {a.task_id} nicht gefunden.")
        ids: list[int] = []
        for datei in anhaenge:
            werte = {
                "name": datei.name,
                "datas": base64.b64encode(datei.read_bytes()).decode(),
                "res_model": "project.task",
                "res_id": a.task_id,
            }
            vorhanden = odoo.call("ir.attachment", "search",
                                  [[("res_model", "=", "project.task"), ("res_id", "=", a.task_id), ("name", "=", datei.name)]],
                                  {"limit": 1})
            if vorhanden:
                odoo.call("ir.attachment", "write", [vorhanden, {"datas": werte["datas"]}])
                ids.append(vorhanden[0])
            else:
                ids.append(odoo.call("ir.attachment", "create", [werte]))

        liste = "".join(f"<li>{html.escape(x.name)}</li>" for x in anhaenge)
        text = f"<p>🤖 [{html.escape(a.agent)}] Dokument als Anhang an dieser Aufgabe:</p><ul>{liste}</ul>"
        if a.notiz:
            text += f"<p>{html.escape(a.notiz)}</p>"
        if warnungen:
            text += "<p>Hinweis: " + html.escape("; ".join(warnungen)) + "</p>"
        msg = odoo.call("project.task", "message_post", [[a.task_id]], {
            "body": text, "body_is_html": True, "message_type": "comment",
            "subtype_xmlid": "mail.mt_note", "attachment_ids": ids,
            "context": {"mail_post_autofollow": False, "mail_create_nosubscribe": True},
        })
        print(f"OK: Aufgabe {a.task_id} „{task[0]['name']}“ – Anhänge {ids}, Notiz {msg}")
        print(f"   {odoo.url}/odoo/action-project.action_view_all_task/{a.task_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
