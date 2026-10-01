#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FraWo — Cover-Ersatz: Werbe- und Sampler-Cover durch echte Release-Cover ersetzen (Odoo #1471).

Wolf:
- Werbe-Cover wie "www.djsoundtop.com Exclusive" aus den Musikdateien entfernen
  und durch das echte Release-Cover von Beatport/Discogs ersetzen.
- Gibt es kein echtes Release-Cover, bleibt das Bild leer (Entfernung des Werbebanners).

Sicherheits-Garantien:
- Standardmäßig DRY-RUN / PROBE: schreibt NIE ohne explizites '--anwenden'.
- Vor jedem Schreibvorgang: Original-Bild wird unter /root/musikredaktion-cover/backups/<hash> gesichert.
- Protokoll: Jede Änderung wird in aenderungen.jsonl dokumentiert.
- Verifikation nach dem Schreiben: Die Datei wird sofort wieder eingelesen und der SHA256-Hash
  des neu eingebetteten Bildes gegen die Bilddaten verprobt.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import sys
import time

try:
    import mutagen
    import mutagen.id3
    import mutagen.flac
    import mutagen.mp4
except ImportError:
    mutagen = None

try:
    from PIL import Image
except ImportError:
    Image = None

AUSGABE_DIR = '/root/musikredaktion-cover'
CSV_PFAD = os.path.join(AUSGABE_DIR, 'kandidaten.csv')
BACKUP_DIR = os.path.join(AUSGABE_DIR, 'backups')
CACHE_DIR = os.path.join(AUSGABE_DIR, 'cache')
LOG_PFAD = os.path.join(AUSGABE_DIR, 'aenderungen.jsonl')


def bild_hash(daten: bytes) -> str:
    return hashlib.sha256(daten).hexdigest()


def ist_gueltiges_bild(daten: bytes) -> tuple[bool, str]:
    """Prüft, ob die Bytes ein gültiges JPEG oder PNG sind.
    Rückgabe: (gueltig, mime_type)"""
    if not daten or len(daten) < 16:
        return False, ''
    if daten.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    elif daten.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    else:
        return False, ''

    if Image is not None:
        try:
            with Image.open(io.BytesIO(daten)) as img:
                img.verify()
            return True, mime
        except Exception:
            return False, ''
    return True, mime


def eingebettetes_bild(pfad: str):
    """(bytes, mime, breite, hoehe) des ersten eingebetteten Bilds einer
    Musikdatei, sonst None."""
    if mutagen is None:
        raise RuntimeError("mutagen nicht installiert")
    try:
        f = mutagen.File(pfad)
    except Exception:
        f = None

    if f is None:
        try:
            id3 = mutagen.id3.ID3(pfad)
            for key in id3.keys():
                if str(key).startswith('APIC'):
                    frame = id3[key]
                    return frame.data, frame.mime, None, None
        except Exception:
            pass
        return None

    pics = getattr(f, 'pictures', None)
    if pics:
        p = pics[0]
        return p.data, p.mime, (p.width or None), (p.height or None)

    tags = f.tags
    if tags is None:
        return None

    for key in tags.keys():
        if str(key).startswith('APIC'):
            frame = tags[key]
            return frame.data, frame.mime, None, None

    if 'covr' in tags and tags['covr']:
        img = tags['covr'][0]
        mime = 'image/png' if getattr(img, 'imageformat', None) == getattr(img, 'FORMAT_PNG', -1) else 'image/jpeg'
        return bytes(img), mime, None, None

    for key in ('metadata_block_picture', 'METADATA_BLOCK_PICTURE'):
        if key in tags:
            try:
                block = mutagen.flac.Picture(base64.b64decode(tags[key][0]))
                return block.data, block.mime, (block.width or None), (block.height or None)
            except Exception:
                pass
    return None


def sichere_original_bild(bild_daten: bytes, backup_dir: str = BACKUP_DIR) -> str:
    """Speichert das bisherige Bild im Backup-Ordner. Rückgabe: Pfad der Sicherung."""
    os.makedirs(backup_dir, exist_ok=True)
    h = bild_hash(bild_daten)
    ext = '.png' if bild_daten.startswith(b'\x89PNG') else '.jpg'
    ziel = os.path.join(backup_dir, f"{h}{ext}")
    if not os.path.exists(ziel):
        with open(ziel, 'wb') as f:
            f.write(bild_daten)
    return ziel


def lade_bild_aus_url(url: str, cache_dir: str = CACHE_DIR, timeout: int = 25) -> tuple[bytes, str]:
    """Lädt Bild aus URL oder lokalem Cache. Prüft Gültigkeit."""
    os.makedirs(cache_dir, exist_ok=True)
    url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
    cache_meta = os.path.join(cache_dir, f"{url_hash}.meta")
    cache_file = os.path.join(cache_dir, f"{url_hash}.bin")

    if os.path.exists(cache_file) and os.path.exists(cache_meta):
        with open(cache_file, 'rb') as f:
            daten = f.read()
        with open(cache_meta, 'r', encoding='utf-8') as f:
            mime = f.read().strip()
        gueltig, _ = ist_gueltiges_bild(daten)
        if gueltig:
            return daten, mime

    import requests
    headers = {"User-Agent": "FraWo-Musikredaktion/1.0 (+https://frawo.tech)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    daten = r.content

    gueltig, mime = ist_gueltiges_bild(daten)
    if not gueltig:
        raise ValueError(f"Heruntergeladene Daten von {url} sind kein gültiges JPEG/PNG Bild")

    with open(cache_file, 'wb') as f:
        f.write(daten)
    with open(cache_meta, 'w', encoding='utf-8') as f:
        f.write(mime)

    return daten, mime


def ersetze_cover(pfad: str, bild_daten: bytes, mime: str) -> bool:
    """Schreibt neues Bild in Datei (MP3, FLAC, M4A)."""
    if mutagen is None:
        raise RuntimeError("mutagen nicht installiert")
    ext = os.path.splitext(pfad)[1].lower()

    if ext == '.mp3':
        try:
            id3 = mutagen.id3.ID3(pfad)
        except mutagen.id3.ID3NoHeaderError:
            id3 = mutagen.id3.ID3()
        id3.delall('APIC')
        id3.add(mutagen.id3.APIC(
            encoding=3,  # UTF-8
            mime=mime,
            type=3,      # Cover (front)
            desc='Cover',
            data=bild_daten
        ))
        id3.save(pfad, v2_version=3)
        return True

    elif ext == '.flac':
        fl = mutagen.flac.FLAC(pfad)
        fl.clear_pictures()
        pic = mutagen.flac.Picture()
        pic.type = 3
        pic.mime = mime
        pic.desc = 'Cover'
        pic.data = bild_daten
        if Image is not None:
            try:
                with Image.open(io.BytesIO(bild_daten)) as img:
                    pic.width, pic.height = img.size
                    pic.depth = 24
            except Exception:
                pass
        fl.add_picture(pic)
        fl.save()
        return True

    elif ext in ('.m4a', '.mp4'):
        mp4 = mutagen.mp4.MP4(pfad)
        if mp4.tags is None:
            mp4.add_tags()
        fmt = mutagen.mp4.MP4Cover.FORMAT_PNG if 'png' in mime else mutagen.mp4.MP4Cover.FORMAT_JPEG
        mp4.tags['covr'] = [mutagen.mp4.MP4Cover(bild_daten, imageformat=fmt)]
        mp4.save()
        return True

    else:
        raise ValueError(f"Nicht unterstütztes Format für Cover-Schreiben: {ext}")


MUELL_TAGS = re.compile(
    r'https?://\S*'
    r'|(?:www\.)?t\.me/\S*'
    r'|www\.\S+'
    r'|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|net|club|ru|org|info|biz|to|cc|de|eu|me|io|fm|pl|xyz|top|site|online|co|us|in|uk)\b\S*'
    r'|\bmyfreemp3\w*|\bmp3juices?\w*|\bzippyshare\w*|\biptorrents?\w*|\btorrentday\w*'
    r'|\bpromo only\b|\bfree download\b|\bfull version free\b',
    re.IGNORECASE)

NIE_FRAME = re.compile(r'^(APIC|PIC|GEOB|PRIV|UFID|RVA2|MCDI|covr|METADATA_BLOCK_PICTURE|'
                       r'metadata_block_picture|coverart|replaygain_.*|REPLAYGAIN_.*)', re.I)


def frame_text(wert):
    try:
        if hasattr(wert, 'text'):
            return ' '.join(str(x) for x in wert.text)
        if hasattr(wert, 'url'):
            return str(wert.url)
        if isinstance(wert, (list, tuple)):
            return ' '.join(str(x) for x in wert)
        return str(wert)
    except Exception:
        return ''


def putze_datei_tags(pfad: str) -> list[str]:
    """Entfernt Werbe-Frames und Werbe-URLs aus den Datei-Tags.
    Gibt die Liste der entfernten Frame-Schlüssel zurück."""
    if mutagen is None:
        return []
    try:
        f = mutagen.File(pfad)
    except Exception:
        f = None

    tags_obj = None
    save_func = None
    if f is not None and getattr(f, 'tags', None) is not None:
        tags_obj = f.tags
        save_func = f.save
    else:
        try:
            id3 = mutagen.id3.ID3(pfad)
            tags_obj = id3
            save_func = lambda: id3.save(pfad, v2_version=3)
        except Exception:
            return []

    if tags_obj is None:
        return []

    entfernt = []
    for key in list(tags_obj.keys()):
        k = str(key)
        if NIE_FRAME.match(k):
            continue
        if re.match(r'^W[A-Z0-9]{3}', k):
            entfernt.append(k)
            del tags_obj[key]
            continue
        txt = frame_text(tags_obj[key])
        if MUELL_TAGS.search(txt):
            entfernt.append(k)
            del tags_obj[key]

    if entfernt and save_func:
        try:
            save_func()
        except Exception:
            pass
    return entfernt


def entferne_cover(pfad: str) -> bool:
    """Entfernt eingebettetes Cover aus der Datei."""
    if mutagen is None:
        raise RuntimeError("mutagen nicht installiert")
    ext = os.path.splitext(pfad)[1].lower()

    if ext == '.mp3':
        try:
            id3 = mutagen.id3.ID3(pfad)
            id3.delall('APIC')
            id3.save(pfad, v2_version=3)
            return True
        except mutagen.id3.ID3NoHeaderError:
            return True

    elif ext == '.flac':
        fl = mutagen.flac.FLAC(pfad)
        if fl.pictures:
            fl.clear_pictures()
            fl.save()
        return True

    elif ext in ('.m4a', '.mp4'):
        mp4 = mutagen.mp4.MP4(pfad)
        if mp4.tags and 'covr' in mp4.tags:
            del mp4.tags['covr']
            mp4.save()
        return True

    else:
        raise ValueError(f"Nicht unterstütztes Format für Cover-Entfernung: {ext}")


def protokolliere_aenderung(log_pfad: str, eintrag: dict):
    os.makedirs(os.path.dirname(log_pfad), exist_ok=True)
    with open(log_pfad, 'a', encoding='utf-8') as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + '\n')


def bearbeite_kandidat(kandidat: dict, anwenden: bool = False,
                       entfernen_wenn_ohne_ersatz: bool = False,
                       backup_dir: str = BACKUP_DIR,
                       cache_dir: str = CACHE_DIR,
                       log_pfad: str = LOG_PFAD) -> dict:
    """Verarbeitet einen einzelnen Kandidaten.
    Rückgabe: Dict mit Status und Verifikationsergebnis."""
    pfad = kandidat.get('pfad')
    ersatzquelle = (kandidat.get('ersatzquelle') or '').strip()
    if not pfad or not os.path.exists(pfad):
        return {'status': 'uebersprungen', 'grund': 'Datei nicht gefunden', 'pfad': pfad}

    altes_bild = eingebettetes_bild(pfad)
    alt_hash = bild_hash(altes_bild[0]) if altes_bild else None

    # Fall 1: Echtes Ersatzcover vorhanden
    if ersatzquelle and ersatzquelle.startswith('http'):
        if not anwenden:
            return {
                'status': 'dry_run_ersetzen',
                'pfad': pfad,
                'alt_hash': alt_hash,
                'quelle': ersatzquelle
            }

        # Backup anlegen
        backup_pfad = None
        if altes_bild:
            backup_pfad = sichere_original_bild(altes_bild[0], backup_dir=backup_dir)

        # Neues Bild laden & verifizieren
        neu_daten, mime = lade_bild_aus_url(ersatzquelle, cache_dir=cache_dir)
        neu_hash = bild_hash(neu_daten)

        # In Datei schreiben
        ersetze_cover(pfad, neu_daten, mime)

        # Track-Tags von Werbelinks / Promo-Frames säubern
        bereinigte_tags = putze_datei_tags(pfad)

        # Sofortige Rücklese-Verifikation
        nachher_bild = eingebettetes_bild(pfad)
        if not nachher_bild:
            raise RuntimeError(f"Verifikation fehlgeschlagen: Kein Bild nach Schreiben in {pfad}")
        nachher_hash = bild_hash(nachher_bild[0])
        if nachher_hash != neu_hash:
            raise RuntimeError(f"Verifikation fehlgeschlagen: Hash-Diskrepanz in {pfad} ({nachher_hash} != {neu_hash})")

        eintrag = {
            'timestamp': int(time.time()),
            'pfad': pfad,
            'aktion': 'ersetzt',
            'alt_hash': alt_hash,
            'neu_hash': neu_hash,
            'backup': backup_pfad,
            'quelle': ersatzquelle,
            'tags_bereinigt': bereinigte_tags
        }
        protokolliere_aenderung(log_pfad, eintrag)
        return {'status': 'ersetzt', 'pfad': pfad, 'alt_hash': alt_hash, 'neu_hash': neu_hash, 'tags_bereinigt': bereinigte_tags}

    # Fall 2: Bestätigtes Werbebanner ohne Ersatz -> auf Wunsch entfernen
    elif entfernen_wenn_ohne_ersatz and (kandidat.get('ocr_bestaetigt') in (True, 'True', '1')):
        if not anwenden:
            return {
                'status': 'dry_run_entfernen',
                'pfad': pfad,
                'alt_hash': alt_hash,
                'grund': 'Werbebanner per OCR bestätigt, keine Ersatzquelle'
            }

        backup_pfad = None
        if altes_bild:
            backup_pfad = sichere_original_bild(altes_bild[0], backup_dir=backup_dir)

        entferne_cover(pfad)
        bereinigte_tags = putze_datei_tags(pfad)

        # Verifikation: Bild muss jetzt weg sein
        nachher = eingebettetes_bild(pfad)
        if nachher is not None:
            raise RuntimeError(f"Verifikation fehlgeschlagen: Bild konnte in {pfad} nicht entfernt werden")

        eintrag = {
            'timestamp': int(time.time()),
            'pfad': pfad,
            'aktion': 'entfernt',
            'alt_hash': alt_hash,
            'neu_hash': None,
            'backup': backup_pfad,
            'grund': 'Werbebanner entfernt',
            'tags_bereinigt': bereinigte_tags
        }
        protokolliere_aenderung(log_pfad, eintrag)
        return {'status': 'entfernt', 'pfad': pfad, 'alt_hash': alt_hash, 'tags_bereinigt': bereinigte_tags}

    return {'status': 'uebersprungen', 'pfad': pfad, 'grund': 'Keine Ersatzquelle und nicht als Werbebanner zum Entfernen markiert'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', default=CSV_PFAD, help='Pfad zur kandidaten.csv')
    ap.add_argument('--limit', type=int, default=None, help='Maximale Anzahl zu bearbeitender Tracks')
    ap.add_argument('--anwenden', action='store_true', help='Echte Schreiboperationen ausführen (Standard: Dry-Run)')
    ap.add_argument('--entfernen-ohne-ersatz', action='store_true', help='OCR-bestätigte Werbebanner auch dann entfernen, wenn kein Release-Cover gefunden wurde')
    ap.add_argument('--pfad', default=None, help='Nur eine einzige Datei gezielt bearbeiten')
    ap.add_argument('--url', default=None, help='Ersatzquelle-URL bei Einzeldatei')

    args = ap.parse_args(argv)

    if args.pfad:
        kandidat = {
            'pfad': args.pfad,
            'ersatzquelle': args.url or '',
            'ocr_bestaetigt': True
        }
        print(f"Bearbeite Einzeldatei: {args.pfad} [Anwenden={args.anwenden}]")
        res = bearbeite_kandidat(kandidat, anwenden=args.anwenden,
                                entfernen_wenn_ohne_ersatz=args.entfernen_ohne_ersatz)
        print("Ergebnis:", res)
        return 0

    if not os.path.exists(args.csv):
        print(f"Fehler: CSV-Datei {args.csv} existiert nicht. Bitte vorher 'cover_probe.py erkennen' ausführen.", file=sys.stderr)
        return 1

    with open(args.csv, encoding='utf-8') as f:
        zeilen = list(csv.DictReader(f, delimiter=';'))

    mit_ersatz = [z for z in zeilen if (z.get('ersatzquelle') or '').startswith('http')]
    mit_ocr = [z for z in zeilen if z.get('ocr_bestaetigt') in (True, 'True', '1') and not (z.get('ersatzquelle') or '').startswith('http')]

    print(f"Kandidaten gesamt: {len(zeilen)}")
    print(f"  mit verifizierter Ersatzquelle: {len(mit_ersatz)}")
    print(f"  OCR-bestätigte Werbebanner ohne Ersatz: {len(mit_ocr)}")
    print(f"Modus: {'🔴 LIVE ANWENDEN' if args.anwenden else '🟢 DRY-RUN (Lesend)'}")

    zu_bearbeiten = mit_ersatz
    if args.entfernen_ohne_ersatz:
        zu_bearbeiten.extend(mit_ocr)

    if args.limit:
        zu_bearbeiten = zu_bearbeiten[:args.limit]

    print(f"Verarbeite {len(zu_bearbeiten)} Tracks ...")
    statistik = {'ersetzt': 0, 'entfernt': 0, 'dry_run_ersetzen': 0, 'dry_run_entfernen': 0, 'fehler': 0, 'uebersprungen': 0}

    for i, z in enumerate(zu_bearbeiten, 1):
        try:
            res = bearbeite_kandidat(z, anwenden=args.anwenden,
                                    entfernen_wenn_ohne_ersatz=args.entfernen_ohne_ersatz)
            st = res.get('status', 'uebersprungen')
            statistik[st] = statistik.get(st, 0) + 1
            if args.anwenden:
                print(f"  [{i}/{len(zu_bearbeiten)}] {st}: {os.path.basename(z['pfad'])}")
        except Exception as e:
            statistik['fehler'] += 1
            print(f"  [{i}/{len(zu_bearbeiten)}] FEHLER bei {z.get('pfad')}: {e}", file=sys.stderr)

    print("\nZusammenfassung:")
    for k, v in statistik.items():
        if v > 0:
            print(f"  {k}: {v}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
