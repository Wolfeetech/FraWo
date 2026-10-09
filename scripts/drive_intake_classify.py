#!/usr/bin/env python3
"""FraWo Drive intake: classify first, move later.

Read-only by default. It never changes Drive. The output is a decision manifest
with a conservative target and an explicit confidence/review reason. A future
apply step must consume only rows with verified content and an approved target.
"""
from __future__ import annotations
import argparse, collections, csv, json, os, re, sys
from pathlib import Path

AUDIO = {'.mp3','.flac','.wav','.aiff','.aif','.m4a','.ogg','.mp2'}
DOCS = {'.pdf','.doc','.docx','.odt','.xls','.xlsx','.ods','.ppt','.pptx','.txt','.md','.csv','.eml','.ics','.html','.htm','.xml'}
IMAGES = {'.jpg','.jpeg','.png','.webp','.gif','.svg','.ico','.heic','.tif','.tiff'}
VIDEO = {'.mp4','.mov','.mkv','.avi','.webm','.m4v'}
PROGRAM = {'.exe','.dll','.msi','.tsx','.js','.py','.ps1','.bat','.cmd','.inf','.iso','.apk','.dmg'}
ARCHIVE = {'.zip','.7z','.rar','.gz','.bz2','.xz','.zst','.vma','.wh','.bak','.dump'}

SECRET_RE = re.compile(r'(?i)(client[_ -]?secret|credentials?|private[_ -]?key|access[_ -]?token|passwort|password|\.pem$|\.p12$)')
DUP_RE = re.compile(r'(?i)(\s\(\d+\)|\bcopy\b|\bkopie\b|final[_ -]?final|unbenannt|untitled)')

def ext(name: str) -> str:
    return Path(name).suffix.lower()

def top(path: str) -> str:
    return path.split('/', 1)[0] if '/' in path else '<root>'

def classify(row: dict) -> dict:
    path = row.get('Path') or row.get('path') or ''
    name = row.get('Name') or Path(path).name
    low = f'{path}/{name}'.lower()
    e = ext(name)
    # Strong path/content families first.
    if e in AUDIO or any(s in low for s in ('frawo_musik/', 'frawo_radio_library/', 'soulseek downloads/')):
        kind, target, confidence = 'musik', 'radio-bibliothek', 'hoch'
        reason = 'Audioformat oder Musikbestand'
    elif any(s in low for s in ('frawo-prodesk-vms/', '/dump', 'dump/', 'backups/', 'pbs-backups/')) or e in {'.vma','.zst','.wh','.bak','.dump'}:
        kind, target, confidence = 'backup', 'backup-archiv', 'hoch'
        reason = 'Sicherung/Dump; nicht als Arbeitsdatei einsortieren'
    elif e in PROGRAM or any(s in low for s in ('_programme-technik/', 'firmware', 'rekordbox', 'workinghours')):
        kind, target, confidence = 'technik_programm', 'nextcloud/80_Technik', 'mittel'
        reason = 'Programm/Technikbestand; Inhalt und Lizenz noch prüfen'
    elif e in IMAGES or e in VIDEO:
        kind, target, confidence = 'medien', 'nextcloud/90_Medien', 'mittel'
        reason = 'Bild/Video; Anlass und Rechte noch prüfen'
    elif e in DOCS:
        kind, target, confidence = 'dokument', 'paperless-oder-nextcloud', 'niedrig'
        reason = 'Dokument erkannt, Empfänger/Inhalt noch per OCR/Text zu bestimmen'
    elif e in ARCHIVE:
        kind, target, confidence = 'archiv_unbekannt', 'manuelle-pruefung', 'niedrig'
        reason = 'Archivcontainer; Inhalt muss vor Zielentscheidung gelesen werden'
    else:
        kind, target, confidence = 'unbekannt', 'manuelle-pruefung', 'niedrig'
        reason = 'Dateityp/Inhalt nicht sicher klassifizierbar'
    flags=[]
    if SECRET_RE.search(name) or SECRET_RE.search(path):
        flags.append('secret-kandidat')
        target='quarantaene-secrets'; confidence='hoch'
    if DUP_RE.search(name): flags.append('namens-duplikat-kandidat')
    # Never infer Wolf/Franz from a filename alone.
    recipient='unbestimmt'
    return {
        'id': row.get('ID') or row.get('id'), 'path': path, 'name': name,
        'size': int(row.get('Size') or row.get('size') or 0),
        'modified': row.get('ModTime') or row.get('modifiedTime'),
        'mime': row.get('MimeType') or row.get('mimeType'), 'extension': e,
        'kind': kind, 'proposed_target': target, 'confidence': confidence,
        'recipient': recipient, 'flags': flags, 'reason': reason,
        'content_review_required': kind in {'dokument','technik_programm','medien','archiv_unbekannt','unbekannt'} or bool(flags),
        'apply_allowed': False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--csv-out')
    a=ap.parse_args()
    data=json.load(open(a.manifest,encoding='utf-8'))
    rows=[classify(x) for x in data]
    summary=collections.defaultdict(lambda:{'files':0,'bytes':0})
    for r in rows:
        summary[r['kind']]['files']+=1; summary[r['kind']]['bytes']+=r['size']
    out={'source_manifest':a.manifest,'read_only':True,'apply_performed':False,'files':len(rows),'summary':dict(summary),'rows':rows}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    if a.csv_out:
        with open(a.csv_out,'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['id','path','size','modified','mime','kind','proposed_target','confidence','recipient','flags','content_review_required','apply_allowed','reason'],extrasaction='ignore')
            w.writeheader()
            for r in rows:
                q=dict(r); q['flags']=';'.join(q['flags']); w.writerow(q)
    print(json.dumps({'files':len(rows),'summary':dict(summary),'out':a.out,'apply_performed':False},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
