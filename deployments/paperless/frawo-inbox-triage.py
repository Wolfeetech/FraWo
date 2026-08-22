#!/usr/bin/env python3
"""
Einmaliges Aufräumen von 00_INBOX (Google Drive): sortiert die losen
Dateien im Wurzelverzeichnis in vier Unterordner ein, OHNE etwas zu
löschen. Bereits einsortierte Unterordner (Bild & Video/, Scans/, ...)
werden nicht angefasst.

  _Dokumente-zur-Pruefung/  -> läuft danach durch die normale Pipeline
  _Fotos-Videos/            -> private Fotos/Screenshots/Videos
  _Programme-Technik/       -> Installer, Zips, Sonstiges
  _Duplikate/               -> Dateien mit gleichem Namen+Größe (Drive
                               erlaubt Dubletten-Namen, anders als ein
                               normales Dateisystem)

Läuft einmalig von Hand (nicht per Cron), resumable über eine
Fortschrittsdatei, damit ein Abbruch (z.B. Tageslimit bei Gemini)
kein Problem ist. Siehe OPERATIONS/PAPERLESS_OPERATIONS.md.
"""
import base64
import concurrent.futures
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY nicht gesetzt.", file=sys.stderr)
    sys.exit(1)

GEMINI_MODEL = "gemini-3.5-flash-lite"  # deutlich hoeheres Frei-Kontingent als 3.6-flash (dort nur 20/Tag)
PROGRESS_FILE = os.environ.get("PROGRESS_FILE", "/var/lib/frawo/inbox-triage-progress.json")

EXT_PROGRAMME = {".exe", ".msi", ".dll", ".zip", ".rar", ".7z", ".iso", ".apk", ".bat", ".ps1"}
EXT_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
EXT_GEMINI_FAEHIG = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".pdf", ".txt", ".md"}
DOC_KEYWORDS = [
    "rechnung", "vertrag", "antrag", "bescheid", "zeugnis", "versicherung",
    "finanzamt", "anmeldung", "kündigung", "mahnung", "gehalt", "lohn",
    "abrechnung", "nachweis", "beitrag", "bewerbung", "police", "deckung",
    "gesellschafter", "steuer", "amt", "behörde", "urkunde", "ausweis",
    "kontoauszug", "police", "förderung",
]

BUCKETS = {
    "dokument": "_Dokumente-zur-Pruefung",
    "foto": "_Fotos-Videos",
    "technik": "_Programme-Technik",
    "duplikat": "_Duplikate",
}


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"done": []}


def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def rclone_lsjson(path):
    result = subprocess.run(
        ["rclone", "lsjson", path, "--files-only"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"rclone lsjson Fehler für {path}: {result.stderr[:300]}")
        return []
    return json.loads(result.stdout)


def rclone_move(src, dst):
    result = subprocess.run(
        ["rclone", "moveto", src, dst, "--drive-chunk-size", "64M"],
        capture_output=True, text=True, timeout=120,
    )
    return result.returncode == 0, result.stderr[:300]


_quota_exhausted = threading.Event()


def classify_with_gemini(local_path, filename):
    if _quota_exhausted.is_set():
        # Tageskontingent schon als erschöpft erkannt — nicht mehr jede
        # einzelne Datei nutzlos anfragen, direkt auf Stichwörter ausweichen.
        return _keyword_fallback(filename)

    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        return _keyword_fallback(filename)

    try:
        with open(local_path, "rb") as f:
            data = f.read()
    except Exception:
        return _keyword_fallback(filename)

    if len(data) > 15 * 1024 * 1024:  # zu groß für Inline-Daten
        return "dokument" if any(k in filename.lower() for k in DOC_KEYWORDS) else "technik"

    prompt = ("Ist diese Datei ein amtliches/geschäftliches Dokument (Rechnung, "
              "Vertrag, Bescheid, Ausweis, Kontoauszug, Zeugnis, Bewerbung, "
              "Versicherung o.ä.), das archiviert werden sollte? Oder ein "
              "privates Foto/Screenshot/Sonstiges? Antworte NUR mit einem Wort: "
              "DOKUMENT oder SONSTIGES.")
    body = json.dumps({
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}},
        ]}],
        "generationConfig": {"temperature": 0.0},
    }).encode()

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                resp = json.loads(r.read().decode())
            answer = resp["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
            return "dokument" if "DOKUMENT" in answer else "foto"
        except urllib.error.HTTPError as e:
            body_txt = e.read().decode(errors="replace")
            if e.code == 429 and "PerDay" in body_txt:
                if not _quota_exhausted.is_set():
                    print("Tageskontingent erschöpft — Rest läuft nur noch über Stichwörter.")
                _quota_exhausted.set()
                return _keyword_fallback(filename)
            if e.code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            print(f"Gemini-Fehler ({filename}): {e.code} — Stichwort-Rückfall")
            return _keyword_fallback(filename)
        except Exception as e:
            print(f"Gemini-Fehler ({filename}): {e} — Stichwort-Rückfall")
            return _keyword_fallback(filename)
    print(f"Gemini dauerhaft nicht erreichbar ({filename}) — Stichwort-Rückfall")
    return _keyword_fallback(filename)


def _keyword_fallback(filename):
    # Bei Gemini-Ausfall NICHT blind "technik" — lieber im Zweifel als
    # Dokument markieren (landet dann in der Pruefung, nichts geht verloren).
    return "dokument" if any(k in filename.lower() for k in DOC_KEYWORDS) else "technik"


WORKERS = int(os.environ.get("TRIAGE_WORKERS", "5"))
_progress_lock = threading.Lock()
_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def process_duplicate(f, base, done, done_lock):
    uid = f"{base}/{f['Name']}#{f['Size']}#{f.get('ID','')}"
    try:
        src = f"{base}/{f['Name']}" if base != "gdrive:" else f"gdrive:{f['Name']}"
        dst = f"gdrive:00_INBOX/{BUCKETS['duplikat']}/{f['Name']}"
        ok, err = rclone_move(src, dst)
        if ok:
            with done_lock:
                done.add(uid)
            log(f"[Duplikat] {f['Name']}")
        else:
            log(f"[FEHLER Duplikat] {f['Name']}: {err}")
    except Exception as e:
        # Eine einzelne haengende/fehlerhafte Datei (z.B. rclone-Zeitlimit)
        # darf nicht den ganzen Lauf abbrechen — naechster Lauf versucht es erneut.
        log(f"[FEHLER Duplikat unerwartet] {f['Name']}: {e}")


def process_primary(f, base, done, done_lock):
    uid = f"{base}/{f['Name']}#{f['Size']}#{f.get('ID','')}"
    name = f["Name"]
    try:
        ext = os.path.splitext(name)[1].lower()
        src = f"{base}/{name}" if base != "gdrive:" else f"gdrive:{name}"

        if ext in EXT_PROGRAMME:
            bucket = "technik"
        elif ext in EXT_VIDEO:
            bucket = "foto"
        elif ext in EXT_GEMINI_FAEHIG:
            with tempfile.TemporaryDirectory() as tmp:
                local = os.path.join(tmp, name)
                try:
                    dl = subprocess.run(["rclone", "copyto", src, local], capture_output=True, timeout=60)
                except subprocess.TimeoutExpired:
                    log(f"[FEHLER Download-Zeitlimit] {name} — naechster Lauf versucht es erneut")
                    return
                if dl.returncode != 0:
                    log(f"[FEHLER Download] {name}")
                    return
                bucket = classify_with_gemini(local, name)
        else:
            bucket = "dokument" if any(k in name.lower() for k in DOC_KEYWORDS) else "technik"

        dst = f"gdrive:00_INBOX/{BUCKETS[bucket]}/{name}"
        ok, err = rclone_move(src, dst)
        if ok:
            with done_lock:
                done.add(uid)
            log(f"[{bucket}] {name}")
        else:
            log(f"[FEHLER] {name}: {err}")
    except Exception as e:
        # Eine einzelne haengende/fehlerhafte Datei darf nicht den ganzen
        # Lauf abbrechen — naechster Lauf versucht es erneut (resumable).
        log(f"[FEHLER unerwartet] {name}: {e}")


def main():
    progress = load_progress()
    done = set(progress["done"])
    done_lock = threading.Lock()

    print("Liste Wurzel-Dateien...", flush=True)
    root_files = rclone_lsjson("gdrive:")
    print("Liste 00_INBOX-Dateien...", flush=True)
    inbox_files = rclone_lsjson("gdrive:00_INBOX")

    all_files = (
        [(f, "gdrive:") for f in root_files]
        + [(f, "gdrive:00_INBOX") for f in inbox_files]
    )

    # Dubletten erkennen: gleicher Name + gleiche Größe, mehrfach vorhanden
    seen = {}
    for f, base in all_files:
        key = (f["Name"], f["Size"])
        seen.setdefault(key, []).append((f, base))

    jobs = []
    for key, entries in seen.items():
        first, *rest = entries
        for f, base in rest:
            uid = f"{base}/{f['Name']}#{f['Size']}#{f.get('ID','')}"
            if uid not in done:
                jobs.append(("duplikat", f, base))
        f, base = first
        uid = f"{base}/{f['Name']}#{f['Size']}#{f.get('ID','')}"
        if uid not in done:
            jobs.append(("primaer", f, base))

    total_all = len(all_files)
    total_open = len(jobs)
    print(f"{total_open} von {total_all} noch offen ({WORKERS} parallele Worker).", flush=True)

    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = []
        for kind, f, base in jobs:
            fn = process_duplicate if kind == "duplikat" else process_primary
            futures.append(pool.submit(fn, f, base, done, done_lock))
        for fut in concurrent.futures.as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                # Sichtbar bleiben (geloggt), aber den Lauf nicht abbrechen —
                # frueher liess eine einzelne haengende Datei alles abstuerzen.
                log(f"[FEHLER unerwartet im Worker] {e}")
            completed += 1
            if completed % 10 == 0:
                with _progress_lock, done_lock:
                    save_progress({"done": list(done)})
                log(f"--- {completed}/{total_open} verarbeitet ---")

    with done_lock:
        save_progress({"done": list(done)})
    print(f"Fertig. {len(done)}/{total_all} insgesamt erledigt.", flush=True)


if __name__ == "__main__":
    main()
