#!/usr/bin/env python3
"""Prüft, dass in Odoo-Datendateien keine echten Secrets im Klartext stehen.

Hintergrund: Am 22.07.2026 wurden die Klartext-Secrets aus
``addons/frawo_agent/data/config_params.xml`` entfernt (Commit 6f912a9).
Am 24.07.2026 hat Commit dde6b9c die Datei aus einer veralteten lokalen
Kopie überschrieben und damit beide Werte wieder ins **öffentliche** Repo
zurückgeholt — ohne dass der gitleaks-Lauf angeschlagen hat, weil die
Werte zu unauffällig sind (kein Anbieter-Muster, niedrige Entropie).

Diese Prüfung schliesst genau diese Lücke: Jeder Parameter, dessen
Schlüsselname nach einem Geheimnis aussieht, muss den Platzhalter
``SETZE_...`` tragen. Echte Werte gehören ausschliesslich in die
Datenbank (ir.config_parameter), nie in den Quellcode.

Aufruf: python3 scripts/tools/check_no_plaintext_secrets.py
Rückgabe: 0 = sauber, 1 = Klartext-Secret gefunden
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Datendateien, die ir.config_parameter-Datensätze enthalten.
DATA_FILES = [
    Path("addons/frawo_agent/data/config_params.xml"),
]

# Schlüsselnamen mit diesen Bestandteilen gelten als geheim.
SECRET_HINTS = ("token", "key", "secret", "password", "passwort", "api_key")

# Erlaubte Platzhalter-Form.
PLACEHOLDER_PREFIX = "SETZE_"

# Zusätzlich: konkrete Werte, die nachweislich schon einmal geleakt sind.
# Sie sind inzwischen rotiert und damit tot, dürfen aber nie wieder auftauchen.
KNOWN_LEAKED = (
    "aa55fde5c0958c9b",
    "frawo_radio_bridge_secret_2026",
    "frawo_secret_2026",
)


def check_file(rel_path: Path) -> list[str]:
    path = rel_path if rel_path.is_absolute() else REPO_ROOT / rel_path
    if not path.exists():
        return [f"{rel_path}: Datei fehlt"]

    problems: list[str] = []
    raw = path.read_text(encoding="utf-8")

    for leaked in KNOWN_LEAKED:
        if leaked in raw:
            problems.append(
                f"{rel_path}: enthält bekannten Leak-Wert '{leaked}' — "
                f"dieser Wert darf nie wieder ins Repo."
            )

    root = ET.fromstring(raw)
    for record in root.iter("record"):
        if record.get("model") != "ir.config_parameter":
            continue

        key = value = None
        for field in record.findall("field"):
            if field.get("name") == "key":
                key = (field.text or "").strip()
            elif field.get("name") == "value":
                value = (field.text or "").strip()

        if not key or value is None:
            continue

        if not any(hint in key.lower() for hint in SECRET_HINTS):
            continue

        if not value.startswith(PLACEHOLDER_PREFIX):
            problems.append(
                f"{rel_path}: Parameter '{key}' enthält einen Klartext-Wert. "
                f"Erwartet wird ein Platzhalter '{PLACEHOLDER_PREFIX}...'; "
                f"der echte Wert gehört in die Datenbank."
            )

    return problems


def main() -> int:
    # Ohne Argumente werden die fest hinterlegten Datendateien geprüft;
    # explizite Pfade erlauben Tests gegen Beispieldateien.
    targets = [Path(a) for a in sys.argv[1:]] or DATA_FILES

    all_problems: list[str] = []
    for rel_path in targets:
        all_problems.extend(check_file(rel_path))

    if all_problems:
        print("FEHLER: Klartext-Secrets im Repo gefunden\n")
        for problem in all_problems:
            print(f"  - {problem}")
        print(
            "\nDas Repo ist öffentlich (github.com/Wolfeetech/FraWo). "
            "Echte Werte per ir.config_parameter in der Datenbank setzen."
        )
        return 1

    print("OK: keine Klartext-Secrets in den geprüften Datendateien.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
