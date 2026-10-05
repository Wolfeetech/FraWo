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


# Zweite Lücke (Odoo #1917, 05.10.2026): Die drei Webhook-Secrets des Jarvis-Handlers
# standen seit 12.09. in alertmanager.yml, Odoo-XML und Handler-Code — gitleaks schlug
# nicht an. Diese Muster prüfen Konfigurations- und Skriptdateien auf feste Werte.
import re

CONFIG_ENDUNGEN = (".yml", ".yaml", ".xml", ".py", ".sh", ".service", ".json", ".toml", ".conf", ".env")
CONFIG_MUSTER = [
    # Alertmanager/Prometheus: credentials: <Wert> statt credentials_file
    (re.compile(r"^\s*credentials:\s*['\"]?([^\s'\"#$]{12,})", re.M), "credentials: mit Klartextwert"),
    # fester Bearer-Token im Code/Config (Variablen wie ${X}, {x}, %s sind erlaubt)
    (re.compile(r"Bearer\s+([A-Za-z0-9_\-\.]{16,})"), "fester Bearer-Token"),
    # Secret im Pfad einer Webhook-Adresse
    (re.compile(r"/(?:klausi-chatter|email-hook)/([A-Za-z0-9_\-]{8,})"), "Secret im Webhook-Pfad"),
    # fester Wert fuer X-Webhook-Secret
    (re.compile(r"X-Webhook-Secret['\"]?\s*[:=,]\s*['\"]([A-Za-z0-9_\-]{12,})['\"]"), "fester X-Webhook-Secret"),
    # Python/JS-Konstante mit Geheimnis-Namen und festem Wert (so stand es bis 12.09. im Handler:
    # ALERT_SECRET = "..."). Lesen aus der Umgebung (_need(...), os.environ...) faellt nicht darunter.
    (re.compile(r"^\s*[A-Za-z_]*(?:SECRET|TOKEN|PASSWORD|PASSWORT|API_KEY)\s*[:=]\s*['\"](?!\$)([^'\"\s]{12,})['\"]", re.M),
     "Geheimnis-Konstante mit festem Wert"),
    # .env-/Shell-Zuweisung ohne Anfuehrungszeichen (FRAWO_X_SECRET=wert); Variablen ($X) sind erlaubt
    (re.compile(r"^\s*(?:export\s+)?[A-Z_]*(?:SECRET|TOKEN|PASSWORD|API_KEY)=([^\s'\"$]{12,})", re.M),
     "Geheimnis-Zuweisung mit festem Wert"),
]
CONFIG_AUSNAHMEN = ("SETZE_", "<", "EXAMPLE", "example", "REPLACE", "PLACEHOLDER", "CHANGEME")


def check_configs(dateien: list[Path]) -> list[str]:
    problems: list[str] = []
    for rel_path in dateien:
        path = rel_path if rel_path.is_absolute() else REPO_ROOT / rel_path
        if path.suffix not in CONFIG_ENDUNGEN or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for muster, art in CONFIG_MUSTER:
            for m in muster.finditer(text):
                wert = m.group(1)
                if any(a in wert for a in CONFIG_AUSNAHMEN):
                    continue
                zeile = text.count("\n", 0, m.start()) + 1
                problems.append(f"{rel_path}:{zeile}: {art} (Wert beginnt mit '{wert[:3]}…')")
    return problems


def repo_dateien() -> list[Path]:
    import subprocess
    out = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True).stdout
    return [Path(p) for p in out.splitlines()
            if p.startswith(("deployments/", "infra/", "addons/", "scripts/")) and "/.venv" not in p]


def main() -> int:
    # Ohne Argumente werden die fest hinterlegten Datendateien geprüft;
    # explizite Pfade erlauben Tests gegen Beispieldateien.
    targets = [Path(a) for a in sys.argv[1:]] or DATA_FILES

    all_problems: list[str] = []
    for rel_path in targets:
        if rel_path.suffix == ".xml" and rel_path in DATA_FILES:
            all_problems.extend(check_file(rel_path))
    all_problems.extend(check_configs([Path(a) for a in sys.argv[1:]] or repo_dateien()))
    if not sys.argv[1:]:
        for rel_path in DATA_FILES:
            if rel_path not in targets:
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
