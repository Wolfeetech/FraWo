#!/usr/bin/env python3
"""Build a read-only editorial audit from an AzuraCast media/playlist snapshot."""
from __future__ import annotations
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "backups/radio-library-curated-20261009.json"
out = ROOT / "reports/radio-voll-audit-20261009.md"
D = json.loads(source.read_text())
playlists = {int(k): v for k, v in D["playlists"].items()}
rows = D["rows"]


def bucket(genre: str) -> str:
    g = (genre or "").lower()
    if any(x in g for x in ("afro", "reggae", "dub", "latin", "world")):
        return "Afro / Global"
    if any(x in g for x in ("ambient", "downtempo", "minimal", "detroit", "hypnotic")):
        return "Deep / Night"
    if any(x in g for x in ("disco", "soul", "funk", "r&b", "new wave")):
        return "Disco / Soul"
    if any(x in g for x in ("techno", "tech house", "house", "electro", "electronic", "indie dance")):
        return "House / Club"
    if any(x in g for x in ("pop", "rock", "alternative")):
        return "Pop / Rock"
    return "Unklar / sonstige"

lines = [
    "# FraWo Funk – Voll-Audit der Tages-Playlists",
    "",
    "Stand: 2026-10-09. Read-only-Auswertung des tatsächlichen AzuraCast-Medienbestands.",
    "",
    "## Ziel",
    "",
    "Die bisherigen großen 9–11-Stunden-Playlists werden nicht blind umbenannt. Dieser Audit zeigt, welche Mood-Blöcke tatsächlich vorhanden sind und wo daraus belastbare 2–4-Stunden-Pools entstehen können.",
    "",
    "## Übersicht",
    "",
    "| ID | Playlist | Titel | Stunden | stärkste Mood-Blöcke | Metadaten-Lücken |",
    "|---:|---|---:|---:|---|---:|",
]

for pid, p in sorted(playlists.items(), key=lambda kv: kv[1].get("name", "")):
    rs = [r for r in rows if pid in r["playlists"]]
    if not rs:
        continue
    total = sum((r.get("length") or 0) for r in rs) / 3600
    moods = collections.Counter(bucket(r.get("genre", "")) for r in rs)
    missing = sum(not (r.get("genre") or "").strip() for r in rs)
    top = ", ".join(f"{k} ({v})" for k, v in moods.most_common(3))
    lines.append(f"| {pid} | {p['name']} | {len(rs)} | {total:.2f} | {top} | {missing} |")

lines += [
    "",
    "## Redaktionelle Konsequenz",
    "",
    "- **Afro-/Global-Pools:** Afro-Noon, Afro-Noon Thursday und Afro-Noon Friday sind nah verwandt und sollten als rotierende Tagespools statt als drei fast identische Langläufer behandelt werden.",
    "- **Morning-/Flow-Pools:** Morning Flow, Morning Bloom, Midweek Rise, Weekend Rise und Sunrise Ritual liefern die Basis für wechselnde 2–4-Stunden-Morgenprogramme.",
    "- **Lunch-/Sunset-Pools:** City Lunch, Tropical Noon, Golden Hour, Sunset Pulse und Sunday Sunset haben starke Disco-/Soul-/House-Anteile und brauchen eine redaktionelle Trennung nach Energie und Tageszeit.",
    "- **Club-Pools:** Afterwork Club, Thursday Heat, Saturday Club und die Freitagspools können in Warm-up, Peak-Time und Techno aufgeteilt werden.",
    "- **Deep-/Night-Pools:** Deep Night, Late Night Society, Moonlight Motion, Night Drive, Night Owls, Night Shift und Sunday Deep bilden mehrere dunkle, hypnotische Rotationen.",
    "- **Sonderfall FraWo Selects:** mit rund 2,6 Stunden bereits ein geeigneter Kandidat für eine bewusst kuratierte, selten wiederkehrende Session.",
    "",
    "## Reihenfolge der nächsten Umsetzung",
    "",
    "1. Afro-Noon-Familie zusammenführen und rotieren.",
    "2. Morgen- und Lunch-Familie in 2–4-Stunden-Pools aufteilen.",
    "3. Afterwork/Golden-Hour/Sunset als warmen Abendblock neu ordnen.",
    "4. Deep-/Night-Familie in mehrere Intensitätsstufen trennen.",
    "5. Samstag und Sonntag mit wechselnden Mood-Kombinationen ausstatten.",
    "",
    "Alle Änderungen bleiben bis zum jeweiligen Queue-Readback deaktiviert oder werden als datierte Piloten eingeplant.",
]
out.write_text("\n".join(lines) + "\n")
print(out)
print("playlists", len(playlists), "rows", len(rows))
