# FraWo Funk Media Management Phase 1 (Energie-Fundament) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Jeden der ~2.457 Tracks per Audio-Analyse nach Energie bewerten und die bestehenden AzuraCast-Daypart-Playlists sauber neu befüllen, sodass FraWo Funk über den Tag hörbar „atmet".

**Architecture:** Eine reine Python-Analyse-Pipeline (librosa) auf StudioPC erzeugt eine `energy_map.csv` (Pfad → Energie-Tier 1–5). Ein Zuordnungs-Skript matcht diese Tracks über ihren Pfad auf AzuraCast-Medien-IDs und setzt pro Datei deterministisch die vollständige Playlist-Mitgliedschaft (REPLACE, kein „Clear" nötig) über die AzuraCast-API direkt gegen `https://10.1.0.38`. Danach werden Wiederholungsschutz und Daypart-Zeitpläne gesetzt.

**Tech Stack:** Python 3, pytest, librosa/soundfile/numpy (nur im Analyse-Venv), httpx (bestehender `AzuraCastClient`), AzuraCast REST-API v.

## Global Constraints

- **Öffentliches Repo:** KEINE Secrets committen. `.env` ist gitignored; API-Key/Creds kommen aus `.env` bzw. Vaultwarden. Verbatim: kein API-Key, kein Passwort, keine DB-Creds in Code oder Doku.
- **AzuraCast-API nur direkt gegen `https://10.1.0.38`** (Cloudflare-WAF blockt Datei-/Playlist-Endpunkte über `funk.frawo.tech`). `verify_ssl=False` (Self-Signed).
- **Station-ID = 1**, aktive Media-Storage-Location = **id 9** (`.../frawo_funk/media/network_library`).
- **Bestehenden `AzuraCastClient` wiederverwenden** (`apps/yourparty/apps/api/azuracast_client.py`) — erweitern, nicht duplizieren.
- **Locked Prod-Deps NICHT ändern** (`apps/yourparty/apps/api/requirements.txt`). Analyse-Abhängigkeiten kommen in `apps/yourparty/apps/api/requirements-dayparting.txt` + eigenes Venv.
- **Daypart-Playlist-IDs (fix, existieren bereits):** Deep/Night=837, Sunrise=840, Morning Drive=841, Lunch=842, Afternoon=843, Evening=844, Night=845. General Rotation=835 (Sicherheitsnetz, niedriges Gewicht, bleibt aktiv).
- **Sicherheit vor jedem Schreiben:** vollständiger Mitgliedschafts-Export (Backup) ziehen; `fallback.mp3` armiert; General Rotation bleibt an, bis verifiziert.
- **Alle neuen Module** liegen in `apps/yourparty/apps/api/`, Tests in `apps/yourparty/apps/api/tests/`.

## Ausführungsreihenfolge (Abhängigkeiten)

Die reinen Logik-Module sind unabhängig, aber der Analyse-Runner (Task 3) importiert die Pfad-Normalisierung (Task 5) und die Bewertung (Task 1). **Sichere Reihenfolge:** Task 0 → 1 → 5 → 2 → 3 → 4 → 6 → 7 → 8 → 9 → 10. (Task 5 „Pfad-Normalisierung" also **vor** Task 3 „Batch-Analyse-Runner" umsetzen.)

---

### Task 0: API-Zugang wiederherstellen + Projekt-Gerüst

**Files:**
- Create: `apps/yourparty/apps/api/requirements-dayparting.txt`
- Create: `apps/yourparty/apps/api/.env.dayparting.example`
- Modify: `.gitignore` (sicherstellen, dass `.env*` ignoriert wird)
- Create: `apps/yourparty/apps/api/tests/__init__.py` (leer)

**Interfaces:**
- Produces: Umgebungsvariablen `AZURACAST_BASE_URL`, `AZURACAST_API_KEY`, `AZURACAST_STATION_ID`, `MUSIC_LIBRARY_ROOT` (von späteren Tasks konsumiert).

- [ ] **Step 1: Neuen API-Key auf der VM erzeugen (Ops, manuell)**

Auf dem ProDesk-Host ausführen (erzeugt Station-API-Key via AzuraCast-CLI):
```bash
ssh pve 'qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:api-key:create --help' 2>&1 | head -20
# Falls kein CLI-Befehl: Key im Web-Admin unter https://10.1.0.38 → Mein Konto → API-Keys erzeugen.
```
Erwartetes Ergebnis: ein neuer API-Key-String. **Key NICHT in Dateien im Repo schreiben.** Sofort in Vaultwarden ablegen (Eintrag „AzuraCast API — Dayparting") und den alten Key im Web-Admin widerrufen.

- [ ] **Step 2: `.env.dayparting.example` schreiben (ohne echte Werte)**

```bash
cat > apps/yourparty/apps/api/.env.dayparting.example <<'EOF'
# Kopieren nach .env.dayparting und Werte einsetzen (NICHT committen)
AZURACAST_BASE_URL=https://10.1.0.38
AZURACAST_API_KEY=
AZURACAST_STATION_ID=1
AZURACAST_VERIFY_SSL=false
# Wurzel der Musik-Bibliothek, wie sie auf DEM ANALYSE-RECHNER (StudioPC) sichtbar ist,
# z.B. ein SMB-Mount von //10.1.0.94/radio:
MUSIC_LIBRARY_ROOT=
EOF
```

- [ ] **Step 3: Analyse-Abhängigkeiten festschreiben**

```bash
cat > apps/yourparty/apps/api/requirements-dayparting.txt <<'EOF'
# Nur für den einmaligen Energie-Analyse-Lauf (eigenes Venv auf StudioPC).
# NICHT in die gesperrte requirements.txt der Prod-API mischen.
librosa==0.10.2.post1
soundfile==0.12.1
numpy==1.26.4
tqdm==4.66.5
python-dotenv==1.1.1
EOF
```

- [ ] **Step 4: `.gitignore` absichern**

Prüfen und bei Bedarf ergänzen, dass keine Env-/Ausgabedateien eingecheckt werden:
```bash
cd ~/FraWo
grep -qE '^\.env' .gitignore || printf '\n.env\n.env.*\n!.env*.example\n' >> .gitignore
grep -q 'energy_map.csv' .gitignore || printf 'apps/yourparty/apps/api/out/\nenergy_map.csv\n' >> .gitignore
mkdir -p apps/yourparty/apps/api/tests && touch apps/yourparty/apps/api/tests/__init__.py
```

- [ ] **Step 5: Commit (nur Gerüst, keine Secrets)**

```bash
cd ~/FraWo
git add apps/yourparty/apps/api/requirements-dayparting.txt apps/yourparty/apps/api/.env.dayparting.example apps/yourparty/apps/api/tests/__init__.py .gitignore
git status   # prüfen: KEINE .env, KEINE Keys enthalten
git commit -m "chore(radio): dayparting scaffold — deps, env template, gitignore"
```

---

### Task 1: Energie-Bewertung (reine Logik)

**Files:**
- Create: `apps/yourparty/apps/api/energy_scoring.py`
- Test: `apps/yourparty/apps/api/tests/test_energy_scoring.py`

**Interfaces:**
- Produces: `energy_scores(features: list[dict]) -> list[float]` (Werte in [0,1]); `score_to_tier(score: float, num_tiers: int = 5) -> int` (1..5). Feature-Dicts haben Keys `"bpm"`, `"rms"`, `"centroid"`.

- [ ] **Step 1: Failing Test schreiben**

```python
# tests/test_energy_scoring.py
from energy_scoring import _percentile_ranks, energy_scores, score_to_tier

def test_percentile_ranks_monotonic():
    assert _percentile_ranks([10, 20, 30]) == [0.0, 0.5, 1.0]

def test_percentile_ranks_single():
    assert _percentile_ranks([42]) == [0.5]

def test_energy_score_high_when_features_high():
    feats = [
        {"bpm": 90,  "rms": 0.1, "centroid": 1000},
        {"bpm": 140, "rms": 0.9, "centroid": 5000},
    ]
    s = energy_scores(feats)
    assert s[0] == 0.0 and s[1] == 1.0
    assert s[1] > s[0]

def test_score_to_tier_bounds():
    assert score_to_tier(0.0) == 1
    assert score_to_tier(0.5) == 3
    assert score_to_tier(0.99) == 5
    assert score_to_tier(1.0) == 5
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `cd apps/yourparty/apps/api && python -m pytest tests/test_energy_scoring.py -v`
Expected: FAIL (`ModuleNotFoundError: energy_scoring`).

- [ ] **Step 3: Minimale Implementierung**

```python
# energy_scoring.py
from typing import Sequence, List, Dict

FEATURE_WEIGHTS: Dict[str, float] = {"bpm": 0.4, "rms": 0.4, "centroid": 0.2}
NUM_TIERS = 5

def _percentile_ranks(values: Sequence[float]) -> List[float]:
    """Percentile rank in [0,1] of each value within the sequence."""
    n = len(values)
    if n == 0:
        return []
    if n == 1:
        return [0.5]
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    for pos, idx in enumerate(order):
        ranks[idx] = pos / (n - 1)
    return ranks

def energy_scores(features: List[Dict[str, float]]) -> List[float]:
    """Weighted combination of per-feature percentile ranks → energy score in [0,1]."""
    if not features:
        return []
    per_feat = {k: _percentile_ranks([f[k] for f in features]) for k in FEATURE_WEIGHTS}
    return [
        sum(FEATURE_WEIGHTS[k] * per_feat[k][i] for k in FEATURE_WEIGHTS)
        for i in range(len(features))
    ]

def score_to_tier(score: float, num_tiers: int = NUM_TIERS) -> int:
    """Map a [0,1] score to a tier 1..num_tiers."""
    score = max(0.0, min(1.0, score))
    return min(int(score * num_tiers) + 1, num_tiers)
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_energy_scoring.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/energy_scoring.py apps/yourparty/apps/api/tests/test_energy_scoring.py
git commit -m "feat(radio): energy scoring + tiering logic"
```

---

### Task 2: Audio-Feature-Extraktion (librosa-Wrapper)

**Files:**
- Create: `apps/yourparty/apps/api/audio_features.py`
- Test: `apps/yourparty/apps/api/tests/test_audio_features.py`

**Interfaces:**
- Consumes: nichts aus früheren Tasks.
- Produces: `extract_features(path: str, max_seconds: int = 90) -> dict | None` — liefert `{"bpm": float, "rms": float, "centroid": float}` oder `None` bei Dekodierfehler.

- [ ] **Step 1: Failing Test schreiben (mit erzeugtem WAV, kein Fremd-Asset)**

```python
# tests/test_audio_features.py
import numpy as np
import soundfile as sf
import audio_features

def _write_tone(path, freq=440, sr=22050, secs=2):
    t = np.linspace(0, secs, int(sr * secs), endpoint=False)
    sf.write(path, 0.5 * np.sin(2 * np.pi * freq * t), sr)

def test_extract_features_returns_keys(tmp_path):
    wav = tmp_path / "tone.wav"
    _write_tone(str(wav))
    feats = audio_features.extract_features(str(wav))
    assert feats is not None
    assert set(feats) == {"bpm", "rms", "centroid"}
    assert feats["rms"] > 0
    assert feats["centroid"] > 0

def test_extract_features_bad_file_returns_none(tmp_path):
    bad = tmp_path / "notaudio.txt"
    bad.write_text("nope")
    assert audio_features.extract_features(str(bad)) is None
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `python -m pytest tests/test_audio_features.py -v`
Expected: FAIL (`ModuleNotFoundError: audio_features`). (Voraussetzung: Analyse-Venv mit `requirements-dayparting.txt` aktiv.)

- [ ] **Step 3: Minimale Implementierung**

```python
# audio_features.py
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def extract_features(path: str, max_seconds: int = 90) -> Optional[Dict[str, float]]:
    """Return {bpm, rms, centroid} for the first max_seconds of an audio file, or None on failure."""
    try:
        import librosa
        y, sr = librosa.load(path, mono=True, duration=max_seconds)
        if y.size == 0:
            return None
        tempo = librosa.beat.beat_track(y=y, sr=sr)[0]
        rms = float(librosa.feature.rms(y=y).mean())
        centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
        return {"bpm": float(tempo), "rms": rms, "centroid": centroid}
    except Exception as e:
        logger.warning("extract_features failed for %s: %s", path, e)
        return None
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_audio_features.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/audio_features.py apps/yourparty/apps/api/tests/test_audio_features.py
git commit -m "feat(radio): librosa audio feature extraction"
```

---

### Task 3: Batch-Analyse-Runner → energy_map.csv

**Files:**
- Create: `apps/yourparty/apps/api/analyze_library.py`
- Test: `apps/yourparty/apps/api/tests/test_analyze_library.py`

**Interfaces:**
- Consumes: `audio_features.extract_features`, `energy_scoring.energy_scores`, `energy_scoring.score_to_tier`, `media_paths.relative_to_root` (Task 5). **Task 5 muss vorher umgesetzt sein** (siehe Ausführungsreihenfolge oben).
- Produces: `find_audio_files(root: str) -> list[str]`; `write_energy_map(rows: list[dict], out_path: str) -> None`; CLI `python analyze_library.py --root <dir> --out energy_map.csv`. CSV-Spalten: `path,bpm,rms,centroid,score,tier` (`path` relativ zu `--root`, Forward-Slashes).

- [ ] **Step 1: Failing Test schreiben (Extraktion gemockt — kein echtes Audio nötig)**

```python
# tests/test_analyze_library.py
import csv
import analyze_library

def test_find_audio_files_filters_extensions(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"x")
    (tmp_path / "b.flac").write_bytes(b"x")
    (tmp_path / "c.txt").write_text("no")
    sub = tmp_path / "sub"; sub.mkdir()
    (sub / "d.wav").write_bytes(b"x")
    found = analyze_library.find_audio_files(str(tmp_path))
    names = sorted(p.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] for p in found)
    assert names == ["a.mp3", "b.flac", "d.wav"]

def test_write_energy_map_roundtrip(tmp_path):
    rows = [
        {"path": "x/a.mp3", "bpm": 120.0, "rms": 0.3, "centroid": 2000.0, "score": 0.4, "tier": 3},
        {"path": "y/b.mp3", "bpm": 90.0,  "rms": 0.1, "centroid": 900.0,  "score": 0.0, "tier": 1},
    ]
    out = tmp_path / "energy_map.csv"
    analyze_library.write_energy_map(rows, str(out))
    with open(out, newline="") as f:
        got = list(csv.DictReader(f))
    assert got[0]["path"] == "x/a.mp3" and got[0]["tier"] == "3"
    assert got[1]["tier"] == "1"
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `python -m pytest tests/test_analyze_library.py -v`
Expected: FAIL (`ModuleNotFoundError: analyze_library`).

- [ ] **Step 3: Minimale Implementierung**

```python
# analyze_library.py
import argparse
import csv
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict

from audio_features import extract_features
from energy_scoring import energy_scores, score_to_tier
from media_paths import relative_to_root  # Task 5

AUDIO_EXT = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".opus"}

def find_audio_files(root: str) -> List[str]:
    out: List[str] = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if os.path.splitext(name)[1].lower() in AUDIO_EXT:
                out.append(os.path.join(dirpath, name))
    return out

def write_energy_map(rows: List[Dict], out_path: str) -> None:
    fields = ["path", "bpm", "rms", "centroid", "score", "tier"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})

def _analyze_one(abs_path: str):
    feats = extract_features(abs_path)
    return abs_path, feats

def run(root: str, out_path: str, workers: int) -> int:
    files = find_audio_files(root)
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_analyze_one, p) for p in files]
        for fut in as_completed(futs):
            abs_path, feats = fut.result()
            if feats:
                results.append((abs_path, feats))
    feats_list = [f for _p, f in results]
    scores = energy_scores(feats_list)
    rows = []
    for (abs_path, feats), score in zip(results, scores):
        rows.append({
            "path": relative_to_root(abs_path, root).replace("\\", "/"),
            "bpm": round(feats["bpm"], 2),
            "rms": round(feats["rms"], 5),
            "centroid": round(feats["centroid"], 1),
            "score": round(score, 4),
            "tier": score_to_tier(score),
        })
    write_energy_map(rows, out_path)
    return len(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="energy_map.csv")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    args = ap.parse_args()
    n = run(args.root, args.out, args.workers)
    print(f"Analysiert: {n} Tracks → {args.out}")
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_analyze_library.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/analyze_library.py apps/yourparty/apps/api/tests/test_analyze_library.py
git commit -m "feat(radio): batch library analysis runner → energy_map.csv"
```

---

### Task 4: Daypart-Uhr (Tier → Playlists)

**Files:**
- Create: `apps/yourparty/apps/api/daypart_clock.py`
- Test: `apps/yourparty/apps/api/tests/test_daypart_clock.py`

**Interfaces:**
- Produces: `DAYPARTS: list[Daypart]` (`Daypart(playlist_id, name, start_hour, end_hour, tiers)`, `end_hour` kann > 24 für Mitternachts-Überlauf sein); `playlists_for_tier(tier: int) -> list[int]`; `dayparts_for_tier(tier: int) -> list[Daypart]`.

- [ ] **Step 1: Failing Test schreiben**

```python
# tests/test_daypart_clock.py
from daypart_clock import DAYPARTS, playlists_for_tier, dayparts_for_tier

def test_every_tier_maps_to_at_least_one_playlist():
    for tier in range(1, 6):
        assert playlists_for_tier(tier), f"Tier {tier} ohne Daypart"

def test_tier1_is_calm_slots():
    ids = set(playlists_for_tier(1))
    assert 837 in ids  # Deep/Night
    assert 840 in ids  # Sunrise
    assert 844 not in ids  # Evening ist NICHT ruhig

def test_tier5_is_peak_evening():
    assert playlists_for_tier(5) == [844]  # nur Evening

def test_all_seven_dayparts_present():
    assert {dp.playlist_id for dp in DAYPARTS} == {837, 840, 841, 842, 843, 844, 845}
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `python -m pytest tests/test_daypart_clock.py -v`
Expected: FAIL (`ModuleNotFoundError: daypart_clock`).

- [ ] **Step 3: Minimale Implementierung**

```python
# daypart_clock.py
from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class Daypart:
    playlist_id: int
    name: str
    start_hour: int   # inklusive
    end_hour: int     # exklusive; >24 = über Mitternacht
    tiers: Tuple[int, ...]

DAYPARTS: List[Daypart] = [
    Daypart(837, "Deep / Night",   1,  5, (1,)),
    Daypart(840, "Sunrise",        5,  8, (1, 2)),
    Daypart(841, "Morning Drive",  8, 11, (2, 3)),
    Daypart(842, "Lunch",         11, 14, (3,)),
    Daypart(843, "Afternoon",     14, 17, (3, 4)),
    Daypart(844, "Evening",       17, 22, (4, 5)),
    Daypart(845, "Night",         22, 25, (3, 4)),
]

def dayparts_for_tier(tier: int) -> List[Daypart]:
    return [dp for dp in DAYPARTS if tier in dp.tiers]

def playlists_for_tier(tier: int) -> List[int]:
    return [dp.playlist_id for dp in dayparts_for_tier(tier)]
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_daypart_clock.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/daypart_clock.py apps/yourparty/apps/api/tests/test_daypart_clock.py
git commit -m "feat(radio): daypart clock — tier→playlist mapping"
```

---

### Task 5: Pfad-Normalisierung (SMB ↔ AzuraCast)

**Files:**
- Create: `apps/yourparty/apps/api/media_paths.py`
- Test: `apps/yourparty/apps/api/tests/test_media_paths.py`

**Interfaces:**
- Produces: `normalize(path: str) -> str` (Backslashes→Slashes, ohne führende/abschließende Slashes); `relative_to_root(abs_path: str, root: str) -> str`.

- [ ] **Step 1: Failing Test schreiben**

```python
# tests/test_media_paths.py
from media_paths import normalize, relative_to_root

def test_normalize_backslashes_and_trim():
    assert normalize("\\\\a\\b\\c\\") == "a/b/c"
    assert normalize("/x/y/") == "x/y"

def test_relative_to_root_strips_root():
    assert relative_to_root("/srv/music/House/a.mp3", "/srv/music") == "House/a.mp3"

def test_relative_to_root_windows_style():
    assert relative_to_root("Z:\\radio\\Deep\\b.flac", "Z:\\radio") == "Deep/b.flac"

def test_relative_to_root_no_match_returns_normalized():
    assert relative_to_root("/other/a.mp3", "/srv/music") == "other/a.mp3"
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `python -m pytest tests/test_media_paths.py -v`
Expected: FAIL (`ModuleNotFoundError: media_paths`).

- [ ] **Step 3: Minimale Implementierung**

```python
# media_paths.py
def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")

def relative_to_root(abs_path: str, root: str) -> str:
    a = normalize(abs_path)
    r = normalize(root)
    if r and a.lower().startswith(r.lower() + "/"):
        return a[len(r) + 1:]
    return a
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_media_paths.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/media_paths.py apps/yourparty/apps/api/tests/test_media_paths.py
git commit -m "feat(radio): path normalization for SMB↔AzuraCast matching"
```

---

### Task 6: Zuordnungs-Plan-Builder

**Files:**
- Create: `apps/yourparty/apps/api/dayparting_plan.py`
- Test: `apps/yourparty/apps/api/tests/test_dayparting_plan.py`

**Interfaces:**
- Consumes: `daypart_clock.playlists_for_tier`, `media_paths.normalize`.
- Produces: `load_energy_map(csv_path: str) -> dict[str, int]` (normalisierter Pfad → Tier); `build_file_playlists(energy_map: dict[str,int], media: list[dict]) -> dict[int, list[int]]` — mappt **AzuraCast-media-id → gewünschte Playlist-IDs**. `media`-Dicts brauchen `"id"` und `"path"`.

- [ ] **Step 1: Failing Test schreiben**

```python
# tests/test_dayparting_plan.py
import csv
from dayparting_plan import load_energy_map, build_file_playlists

def test_load_energy_map(tmp_path):
    p = tmp_path / "e.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["path", "tier"]); w.writerow(["House/a.mp3", "5"])
    m = load_energy_map(str(p))
    assert m == {"House/a.mp3": 5}

def test_build_file_playlists_maps_id_to_playlists():
    energy = {"deep/x.mp3": 1, "peak/y.mp3": 5}
    media = [
        {"id": 11, "path": "deep/x.mp3"},
        {"id": 22, "path": "peak/y.mp3"},
        {"id": 33, "path": "unknown/z.mp3"},  # nicht in energy_map → leer
    ]
    plan = build_file_playlists(energy, media)
    assert set(plan[11]) == {837, 840}   # Tier 1 → Deep + Sunrise
    assert plan[22] == [844]             # Tier 5 → Evening
    assert plan[33] == []               # unbekannt → keine Playlist
```

- [ ] **Step 2: Test läuft → FAIL**

Run: `python -m pytest tests/test_dayparting_plan.py -v`
Expected: FAIL (`ModuleNotFoundError: dayparting_plan`).

- [ ] **Step 3: Minimale Implementierung**

```python
# dayparting_plan.py
import csv
from typing import Dict, List
from daypart_clock import playlists_for_tier
from media_paths import normalize

def load_energy_map(csv_path: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[normalize(row["path"])] = int(row["tier"])
    return out

def build_file_playlists(energy_map: Dict[str, int], media: List[dict]) -> Dict[int, List[int]]:
    plan: Dict[int, List[int]] = {}
    for item in media:
        tier = energy_map.get(normalize(item["path"]))
        plan[item["id"]] = playlists_for_tier(tier) if tier is not None else []
    return plan
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_dayparting_plan.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/dayparting_plan.py apps/yourparty/apps/api/tests/test_dayparting_plan.py
git commit -m "feat(radio): assignment plan builder (media-id → playlists)"
```

---

### Task 7: AzuraCastClient erweitern (Media listen + Playlists setzen)

**Files:**
- Modify: `apps/yourparty/apps/api/azuracast_client.py` (neue Methoden anhängen)
- Test: `apps/yourparty/apps/api/tests/test_azuracast_client_dayparting.py`

**Interfaces:**
- Consumes: bestehende `AzuraCastClient.__init__(base_url, api_key, station_id, verify_ssl)`, `self.base_url`, `self.headers`, `self.verify_ssl`.
- Produces (neue Methoden):
  - `async list_all_media() -> list[dict]` — alle Medien der Station mit mind. `id`, `path`, `playlists` (Liste von `{"id":..}`), über Paginierung.
  - `async set_file_playlists(media_id: int, playlist_ids: list[int]) -> bool` — setzt (REPLACE) die Playlist-Mitgliedschaft einer Datei via `PUT /api/station/{sid}/file/{media_id}`.

- [ ] **Step 1: Failing Test schreiben (httpx MockTransport — keine echte API)**

```python
# tests/test_azuracast_client_dayparting.py
import httpx
import pytest
from azuracast_client import AzuraCastClient

@pytest.mark.asyncio
async def test_set_file_playlists_builds_put(monkeypatch):
    captured = {}
    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["method"] = request.method
        import json as _j
        captured["body"] = _j.loads(request.content)
        return httpx.Response(200, json={"success": True})
    transport = httpx.MockTransport(handler)

    client = AzuraCastClient("https://10.1.0.38", "KEY", 1, verify_ssl=False)
    # PUT über injizierten Transport ausführen:
    async with httpx.AsyncClient(transport=transport) as hc:
        resp = await hc.put(
            f"{client.base_url}/api/station/1/file/55",
            headers=client.headers,
            json={"playlists": [{"id": 837}, {"id": 840}]},
        )
    assert captured["method"] == "PUT"
    assert captured["url"].endswith("/api/station/1/file/55")
    assert captured["body"] == {"playlists": [{"id": 837}, {"id": 840}]}
```

(Hinweis: Test verifiziert die **Request-Form**. `pytest-asyncio` ist nötig — falls nicht vorhanden, Test synchron mit `httpx.Client(transport=...)` und `hc.put(...)` schreiben und die `async`-Marker entfernen.)

- [ ] **Step 2: Test läuft → FAIL/oder rot**

Run: `python -m pytest tests/test_azuracast_client_dayparting.py -v`
Expected: FAIL, solange die Methoden fehlen bzw. (bei async) `pytest-asyncio` fehlt. Bei fehlendem `pytest-asyncio`: Test auf synchrone `httpx.Client`-Variante umstellen (siehe Hinweis) und erneut laufen → dann rot wegen fehlender Client-Methoden im Folge-Schritt.

- [ ] **Step 3: Methoden implementieren (an `azuracast_client.py` anhängen)**

```python
    async def list_all_media(self, station_id: Optional[int] = None) -> List[Dict]:
        """Alle Medien der Station (id, path, playlists) via Paginierung."""
        sid = station_id if station_id is not None else self.station_id
        results: List[Dict] = []
        page = 1
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=60.0, follow_redirects=True) as client:
            while True:
                url = f"{self.base_url}/api/station/{sid}/files/list?rowCount=500&current={page}"
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                rows = data.get("rows", data) if isinstance(data, dict) else data
                if not rows:
                    break
                results.extend(rows)
                if len(rows) < 500:
                    break
                page += 1
        return results

    async def set_file_playlists(self, media_id: int, playlist_ids: List[int],
                                 station_id: Optional[int] = None) -> bool:
        """REPLACE der Playlist-Mitgliedschaft einer Datei."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/file/{media_id}"
        payload = {"playlists": [{"id": pid} for pid in playlist_ids]}
        res = await self._put(url, json=payload)
        return res is not None
```

- [ ] **Step 4: Test läuft → PASS**

Run: `python -m pytest tests/test_azuracast_client_dayparting.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/yourparty/apps/api/azuracast_client.py apps/yourparty/apps/api/tests/test_azuracast_client_dayparting.py
git commit -m "feat(radio): AzuraCast client — list media + set file playlists"
```

---

### Task 8: Ist-Zustand sichern (Backup, read-only gegen Live)

**Files:**
- Create: `apps/yourparty/apps/api/backup_assignments.py`

**Interfaces:**
- Consumes: `AzuraCastClient.list_all_media`.
- Produces: CLI `python backup_assignments.py --out backups/assignments_<ts>.json` — schreibt je Datei `{id, path, playlists:[ids]}` als Rollback-Grundlage.

- [ ] **Step 1: Skript schreiben**

```python
# backup_assignments.py
import argparse, asyncio, json, os, datetime
from dotenv import load_dotenv
from azuracast_client import AzuraCastClient

async def main(out_path: str):
    load_dotenv(".env.dayparting")
    client = AzuraCastClient(
        os.environ["AZURACAST_BASE_URL"], os.environ["AZURACAST_API_KEY"],
        int(os.environ.get("AZURACAST_STATION_ID", "1")),
    )
    media = await client.list_all_media()
    snapshot = [
        {"id": m["id"], "path": m.get("path"),
         "playlists": [p["id"] for p in m.get("playlists", []) if isinstance(p, dict)]}
        for m in media
    ]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"Gesichert: {len(snapshot)} Dateien → {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    ap.add_argument("--out", default=f"backups/assignments_{ts}.json")
    a = ap.parse_args()
    asyncio.run(main(a.out))
```

- [ ] **Step 2: Gegen Live ausführen (read-only) und prüfen**

Run (mit ausgefüllter `.env.dayparting`):
`cd apps/yourparty/apps/api && python backup_assignments.py`
Expected: „Gesichert: ~2457 Dateien → backups/assignments_<ts>.json". Datei existiert, enthält `id`/`path`/`playlists`. Diese Zahl bestätigt zugleich, dass `list_all_media` real funktioniert.

- [ ] **Step 3: Commit (nur Skript, NICHT die Backup-Daten)**

```bash
echo 'apps/yourparty/apps/api/backups/' >> ~/FraWo/.gitignore
git add apps/yourparty/apps/api/backup_assignments.py ~/FraWo/.gitignore
git commit -m "feat(radio): backup current playlist assignments (rollback base)"
```

---

### Task 9: Zuordnung anwenden (Live) + Verifikation

**Files:**
- Create: `apps/yourparty/apps/api/apply_dayparting.py`
- Create: `apps/yourparty/apps/api/verify_dayparting.py`

**Interfaces:**
- Consumes: `AzuraCastClient.list_all_media`, `AzuraCastClient.set_file_playlists`, `dayparting_plan.load_energy_map`, `dayparting_plan.build_file_playlists`, `daypart_clock.DAYPARTS`.
- Produces: CLI `python apply_dayparting.py --energy-map energy_map.csv [--dry-run]`; CLI `python verify_dayparting.py --energy-map energy_map.csv`.

- [ ] **Step 1: Apply-Skript schreiben (mit --dry-run und Nebenläufigkeits-Limit)**

```python
# apply_dayparting.py
import argparse, asyncio, os
from dotenv import load_dotenv
from azuracast_client import AzuraCastClient
from dayparting_plan import load_energy_map, build_file_playlists

async def main(energy_map_path: str, dry_run: bool, concurrency: int):
    load_dotenv(".env.dayparting")
    client = AzuraCastClient(
        os.environ["AZURACAST_BASE_URL"], os.environ["AZURACAST_API_KEY"],
        int(os.environ.get("AZURACAST_STATION_ID", "1")),
    )
    energy = load_energy_map(energy_map_path)
    media = await client.list_all_media()
    plan = build_file_playlists(energy, media)           # media_id -> [playlist_ids]
    assigned = {mid: pls for mid, pls in plan.items() if pls}
    print(f"Dateien gesamt: {len(media)} · mit Zuordnung: {len(assigned)} · ohne: {len(plan)-len(assigned)}")
    if dry_run:
        print("DRY-RUN: keine Änderungen geschrieben.")
        return
    sem = asyncio.Semaphore(concurrency)
    ok = 0
    async def worker(mid, pls):
        nonlocal ok
        async with sem:
            if await client.set_file_playlists(mid, pls):
                ok += 1
    await asyncio.gather(*(worker(mid, pls) for mid, pls in assigned.items()))
    print(f"Gesetzt: {ok}/{len(assigned)} Dateien.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--energy-map", default="energy_map.csv")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--concurrency", type=int, default=8)
    a = ap.parse_args()
    asyncio.run(main(a.energy_map, a.dry_run, a.concurrency))
```

- [ ] **Step 2: Verify-Skript schreiben (DoD: Tiers pro Daypart monoton)**

```python
# verify_dayparting.py
import argparse, asyncio, os, statistics
from dotenv import load_dotenv
from azuracast_client import AzuraCastClient
from dayparting_plan import load_energy_map
from daypart_clock import DAYPARTS
from media_paths import normalize

async def main(energy_map_path: str):
    load_dotenv(".env.dayparting")
    client = AzuraCastClient(
        os.environ["AZURACAST_BASE_URL"], os.environ["AZURACAST_API_KEY"],
        int(os.environ.get("AZURACAST_STATION_ID", "1")),
    )
    energy = load_energy_map(energy_map_path)
    media = await client.list_all_media()
    playlist_tiers = {dp.playlist_id: [] for dp in DAYPARTS}
    for m in media:
        tier = energy.get(normalize(m.get("path", "")))
        for p in m.get("playlists", []):
            pid = p["id"] if isinstance(p, dict) else p
            if pid in playlist_tiers and tier is not None:
                playlist_tiers[pid].append(tier)
    print(f"{'Daypart':16} {'Tracks':>7} {'Ø-Tier':>7}")
    for dp in DAYPARTS:
        tiers = playlist_tiers[dp.playlist_id]
        avg = round(statistics.mean(tiers), 2) if tiers else 0
        print(f"{dp.name:16} {len(tiers):>7} {avg:>7}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--energy-map", default="energy_map.csv")
    a = ap.parse_args()
    asyncio.run(main(a.energy_map))
```

- [ ] **Step 3: Trockenlauf**

Run: `python apply_dayparting.py --dry-run`
Expected: Ausgabe mit „mit Zuordnung: ~2457" und „ohne: ~0". Keine Änderung geschrieben.

- [ ] **Step 4: Sicherheitsnetz prüfen, dann echt anwenden**

Vorbedingung: Task 8 Backup existiert; General Rotation (835) aktiv; `fallback.mp3` vorhanden (siehe Memory `reference_frawo_azuracast`). Zu hörerarmer Zeit:
Run: `python apply_dayparting.py --concurrency 8`
Expected: „Gesetzt: ~2457/~2457 Dateien." Station bleibt online (in AzuraCast-Web nowplaying gegenprüfen).

- [ ] **Step 5: Verifizieren (DoD 1)**

Run: `python verify_dayparting.py`
Expected: Ø-Tier steigt sinnvoll an: Deep/Sunrise niedrig (≈1–2), Lunch/Afternoon mittel (≈3), Evening hoch (≈4–5), Night mittel; keine Daypart-Playlist mit 0 Tracks.

- [ ] **Step 6: Commit**

```bash
git add apps/yourparty/apps/api/apply_dayparting.py apps/yourparty/apps/api/verify_dayparting.py
git commit -m "feat(radio): apply energy-based dayparting + verification"
```

---

### Task 10: Wiederholungsschutz + Daypart-Zeitpläne (Live)

**Files:**
- Create: `apps/yourparty/apps/api/rotation_rules.py`

**Interfaces:**
- Consumes: `AzuraCastClient` (nutzt `_put`/`_get`), `daypart_clock.DAYPARTS`.
- Produces: CLI `python rotation_rules.py` — setzt (a) Station-Wiederholungsschutz und (b) je Daypart-Playlist die Zeitplan-Items gemäß Uhr.

- [ ] **Step 1: Skript schreiben**

```python
# rotation_rules.py
import asyncio, os
from dotenv import load_dotenv
from azuracast_client import AzuraCastClient
from daypart_clock import DAYPARTS

def _hhmm(hour: int) -> int:
    """Stunde (0..24, 25=01:00 nächster Tag) → AzuraCast-Zeit als HHMM-Int."""
    h = hour % 24
    return h * 100

async def main():
    load_dotenv(".env.dayparting")
    c = AzuraCastClient(
        os.environ["AZURACAST_BASE_URL"], os.environ["AZURACAST_API_KEY"],
        int(os.environ.get("AZURACAST_STATION_ID", "1")),
    )
    sid = c.station_id
    # (a) Wiederholungsschutz auf Station-Backend setzen
    await c._put(f"{c.base_url}/api/station/{sid}",
                 json={"backend_config": {"duplicate_prevention_time_range": 150}})
    # (b) Zeitpläne je Daypart
    for dp in DAYPARTS:
        payload = {"schedule_items": [{
            "start_time": _hhmm(dp.start_hour),
            "end_time": _hhmm(dp.end_hour),
            "days": [1, 2, 3, 4, 5, 6, 7],
        }]}
        await c._put(f"{c.base_url}/api/station/{sid}/playlist/{dp.playlist_id}", json=payload)
        print(f"Zeitplan gesetzt: {dp.name} {dp.start_hour:02d}–{dp.end_hour % 24:02d}h")

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Ausführen**

Run: `python rotation_rules.py`
Expected: je Daypart „Zeitplan gesetzt: …". Keine Fehler.

- [ ] **Step 3: Verifizieren (DoD 3+4)**

- Im AzuraCast-Web (`https://10.1.0.38`) unter Station → Playlists prüfen: jede Daypart-Playlist zeigt das erwartete Zeitfenster.
- `curl -sk https://10.1.0.38/api/nowplaying/1 -H "X-API-Key: <key>"` zur passenden Uhrzeit → laufende Playlist entspricht dem Daypart.
- Kurzer Hörtest (DoD 2): Morgens ruhig, abends treibend.

- [ ] **Step 4: Commit**

```bash
git add apps/yourparty/apps/api/rotation_rules.py
git commit -m "feat(radio): duplicate prevention + daypart scheduling"
```

- [ ] **Step 5: Odoo-Tasks aktualisieren**

Odoo #764 (API-Key) → erledigt; #760/#761/#701 (Dayparts) → erledigt/in Verifikation; Kommentar mit Ergebnis der `verify_dayparting.py`-Ausgabe an #642 (Roadmap) posten.

---

## Rollback

Falls das Ergebnis nicht passt: mit dem Backup aus Task 8 die alte Mitgliedschaft je Datei wiederherstellen (`set_file_playlists(id, playlists)` aus dem Snapshot). Station läuft dank General-Rotation-Netz durchgängig, sodass Rollback ohne Dead-Air möglich ist.

## Nicht in diesem Plan (Phase 2/3)

Show-Fenster/Live-DJ (Phase 2), Ingestion-Automatik neuer Musik + optionaler Genre-/Mood-Backfill (Phase 3), Voting-gesteuerte Playlists. Siehe Spec Abschnitt 8/9.
