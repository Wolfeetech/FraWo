#!/usr/bin/env python3
"""Fuer odoo shell: CI-Farben in ALLEN Sprachfassungen uebersetzter Felder korrigieren.

Warum eigenes Skript: `arch_db` ist ein uebersetztes Feld. Wer es ueber die
normale API schreibt, erwischt nur die Sprache der eigenen Sitzung (meist en_US).
Die Website laeuft aber auf de_DE -- dort blieben Altfarben stehen und waren
live weiter sichtbar, obwohl die Pruefung "sauber" meldete.

Aufruf im Container:
  odoo shell -d FraWo_GbR --no-http --db_host=$HOST --db_user=$USER \
      --db_password=$PASSWORD --logfile=/dev/null < ci_fix_translations.py
"""

COLOR_MAP = {
    "#00bfff": "#a050f0",
    "#0099cc": "#9d4edd",
    "#00a8e8": "#9d4edd",
    "#06b6d4": "#a050f0",
    "#00d4ff": "#a050f0",
    "#22d3ee": "#a050f0",
    "#a855f7": "#a050f0",
    "#7c3aed": "#9d4edd",
    "#00e599": "#2ecc71",
    "#10b981": "#2ecc71",
    "#4ade80": "#2ecc71",
    "#22c55e": "#2ecc71",
}
RGB_MAP = {
    (0, 191, 255): (160, 80, 240),
    (0, 153, 204): (157, 78, 221),
    (0, 168, 232): (157, 78, 221),
    (6, 182, 212): (160, 80, 240),
    (0, 212, 255): (160, 80, 240),
    (34, 211, 238): (160, 80, 240),
    (168, 85, 247): (160, 80, 240),
    (124, 58, 237): (157, 78, 221),
    (0, 229, 153): (46, 204, 113),
    (16, 185, 129): (46, 204, 113),
    (74, 222, 128): (46, 204, 113),
    (34, 197, 94): (46, 204, 113),
}

import re

RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.I)


def convert(text):
    if not text:
        return text, 0
    count = 0

    def hex_sub(m):
        nonlocal count
        found = m.group(0)
        new = COLOR_MAP.get(found.lower())
        if not new:
            return found
        count += 1
        return new.upper() if found[1:].isupper() else new

    text = re.sub(r"#[0-9A-Fa-f]{6}", hex_sub, text)

    def rgb_sub(m):
        nonlocal count
        triple = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        new = RGB_MAP.get(triple)
        if not new:
            return m.group(0)
        count += 1
        head = m.group(0).split("(")[0]
        return "%s(%d, %d, %d" % (head, new[0], new[1], new[2])

    return RGB_RE.sub(rgb_sub, text), count


langs = env["res.lang"].search([("active", "=", True)]).mapped("code")
print("aktive Sprachen:", langs)

views = env["ir.ui.view"].with_context(active_test=False).search([])
gesamt = 0
betroffen = 0

for view in views:
    for lang in langs:
        rec = view.with_context(lang=lang)
        alt = rec.arch_db or ""
        neu, n = convert(alt)
        if n:
            rec.arch_db = neu
            gesamt += n
            betroffen += 1
            print("  %s  Ansicht %s (%s): %d Farben" % (lang, view.id, view.key or view.name, n))

env.registry.clear_cache()
env.registry.signal_changes()
env.cr.commit()
print("FERTIG: %d Farbangaben in %d Sprachfassungen korrigiert" % (gesamt, betroffen))
