#!/usr/bin/env python3
"""Wächter für die Sendequalität: meldet unsaubere Titel, die auf Sendung sind.

Warum es das gibt: Am 04.10.2026 lief ein einmaliger Putz-Lauf (#1915). Der hat
sauber gearbeitet und Problemfälle als Nacharbeit gemeldet — aber danach kam ein
Beatport-Sampler neu rein, bei dem die Tracknummer im Künstlerfeld landete
("37 – Beatport 100 Afro House 2024 August - … - Uwrongo"). 44 Titel gingen so
auf Sendung, und niemand hat es gemerkt, weil nichts nachprüft.

Ein einmaliger Lauf kann neue Importe nicht fangen. Diese Prüfung läuft täglich.

Benutzung:
  python3 scripts/radio_metadaten_waechter.py            # Bericht im Klartext
  python3 scripts/radio_metadaten_waechter.py --json      # für Cron/Meldungen
  python3 scripts/radio_metadaten_waechter.py --nur-jetzt # nur der laufende Titel

Rückgabewert: 0 = sauber, 1 = unsaubere Titel auf Sendung.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from radio_titel_putzen import braucht_nacharbeit, entwirre_sampler  # noqa: E402

SENDER = "https://funk.frawo.tech"
JETZT = f"{SENDER}/api/nowplaying/frawo_funk"
LISTE = f"{SENDER}/api/station/1/requests"


def _hol(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "FraWo-Hermes-Waechter"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def pruefe_titel(kuenstler: str, titel: str) -> dict | None:
    """Gibt einen Befund zurück oder None, wenn der Titel sendertauglich ist."""
    if not braucht_nacharbeit(titel, kuenstler):
        return None
    vorschlag = entwirre_sampler(kuenstler, titel)
    return {
        "kuenstler": kuenstler,
        "titel": titel,
        "maschinell_loesbar": bool(vorschlag and not braucht_nacharbeit(vorschlag[1], vorschlag[0])),
        "vorschlag": (
            {"kuenstler": vorschlag[0], "titel": vorschlag[1], "album": vorschlag[2]}
            if vorschlag else None
        ),
    }


def laufender_titel() -> dict | None:
    daten = _hol(JETZT)
    song = (daten.get("now_playing") or {}).get("song") or {}
    return pruefe_titel((song.get("artist") or "").strip(), (song.get("title") or "").strip())


def ganze_liste() -> tuple[int, list[dict]]:
    gesehen: list[dict] = []
    gesamt = 0
    for seite in range(1, 40):
        try:
            daten = _hol(f"{LISTE}?per_page=500&page={seite}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            break
        posten = daten.get("rows") if isinstance(daten, dict) else daten
        if not posten:
            break
        for eintrag in posten:
            song = eintrag.get("song") or {}
            gesamt += 1
            befund = pruefe_titel(
                (song.get("artist") or "").strip(),
                (song.get("title") or "").strip(),
            )
            if befund:
                gesehen.append(befund)
        if isinstance(daten, dict) and daten.get("total") and gesamt >= daten["total"]:
            break
    return gesamt, gesehen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Maschinenausgabe")
    parser.add_argument("--nur-jetzt", action="store_true", help="nur der laufende Titel")
    args = parser.parse_args()

    jetzt = laufender_titel()

    if args.nur_jetzt:
        if args.json:
            print(json.dumps({"jetzt": jetzt}, ensure_ascii=False, indent=2))
        elif jetzt:
            print(f"⚠️  Auf Sendung unsauber: {jetzt['kuenstler']} – {jetzt['titel']}")
        else:
            print("✅ Der laufende Titel ist sendertauglich.")
        return 1 if jetzt else 0

    gesamt, befunde = ganze_liste()
    loesbar = [b for b in befunde if b["maschinell_loesbar"]]

    if args.json:
        print(json.dumps({
            "geprueft": gesamt,
            "unsauber": len(befunde),
            "maschinell_loesbar": len(loesbar),
            "jetzt_auf_sendung_unsauber": bool(jetzt),
            "befunde": befunde[:60],
        }, ensure_ascii=False, indent=2))
        return 1 if befunde else 0

    if jetzt:
        print(f"⚠️  JETZT auf Sendung unsauber: {jetzt['kuenstler']} – {jetzt['titel']}")
    if not befunde:
        print(f"✅ Alle {gesamt} geprüften Titel sind sendertauglich.")
        return 0

    anteil = (100 * len(befunde) / gesamt) if gesamt else 0
    print(f"⚠️  {len(befunde)} von {gesamt} Titeln unsauber ({anteil:.1f} %), "
          f"davon {len(loesbar)} maschinell lösbar\n")
    for b in befunde[:25]:
        marke = " " if b["maschinell_loesbar"] else "!"
        print(f" {marke} {b['kuenstler']!r} – {b['titel']!r}")
        if b["vorschlag"]:
            v = b["vorschlag"]
            print(f"      → {v['kuenstler']!r} – {v['titel']!r}  (Album: {v['album']!r})")
    if len(befunde) > 25:
        print(f"    … und {len(befunde) - 25} weitere")
    print("\n  ! = nicht maschinell lösbar, braucht Handarbeit.")
    print("  Achtung: Korrektur muss in den DATEIEN passieren, sonst holt")
    print("  AzuraCast beim nächsten Einlesen die alten Werte zurück.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
