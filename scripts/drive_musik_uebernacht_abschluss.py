#!/usr/bin/env python3
"""Sicherer Abschluss fuer den Drive-Musikimport 2026-10-08.

Nur nach erfolgreichem Import werden die tatsaechlich uebernommenen oder als
verifiziert doppelt erkannten Drive-Audiodateien in den Drive-Papierkorb gelegt.
Unklare/defekte Dateien bleiben in Drive erhalten.
"""
import json, os, re, shlex, subprocess, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ENV_PY = '/home/hermes/.hermes/installs/019d0d114d22b7e6/environments/1db7944fea354a16b8b78b762533d67c/venv/bin/python'
ROOT_ID = '1uhprtEiXswf1Cho3Vg5hwmaiqE_DIeBI'
REPORT = Path('/home/hermes/FraWo/reports/drive-musik-uebernacht-20261008.json')
MANIFEST = Path('/home/hermes/FraWo/backups/drive-musik-uebernacht-20261008.json')
REMOTE = 'root@10.1.0.128'
LOG = '/root/drive-musik-neuzugang-20261008.log'
BACKUP = '/var/lib/beets/neuzugang-20261008'
INBOX = '/mnt/music/Inbox/neuzugang-20261008'
AUDIO = ('.mp3','.flac','.wav','.aiff','.aif','.m4a','.ogg')

def api():
    c = Credentials.from_authorized_user_file('/home/hermes/.hermes/google_token.json')
    return build('drive','v3',credentials=c,cache_discovery=False)

def children(svc, pid):
    out=[]; token=None
    while True:
        r=svc.files().list(q=f"'{pid}' in parents and trashed=false", spaces='drive',
            fields='nextPageToken,files(id,name,mimeType,size,md5Checksum,modifiedTime,parents)',
            pageSize=1000, pageToken=token).execute()
        out += r.get('files',[]); token=r.get('nextPageToken')
        if not token: return out

def inventory():
    svc=api(); rows=[]
    def walk(pid, rel):
        for f in children(svc,pid):
            p=f'{rel}/{f["name"]}' if rel else f['name']
            if f['mimeType']=='application/vnd.google-apps.folder': walk(f['id'],p)
            elif f['name'].lower().endswith(AUDIO):
                rows.append({'id':f['id'],'name':f['name'],'relpath':p,'size':int(f.get('size') or 0),
                    'md5Checksum':f.get('md5Checksum'),'modifiedTime':f.get('modifiedTime'),'parents':f.get('parents',[])})
    walk(ROOT_ID,'')
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps({'source_folder_id':ROOT_ID,'files':rows},ensure_ascii=False,indent=2)+'\n')
    return rows

def ssh(cmd, check=True):
    r=subprocess.run(['ssh','-o','BatchMode=yes',REMOTE,cmd],text=True,capture_output=True)
    if check and r.returncode: raise RuntimeError(f'ssh {r.returncode}: {r.stderr[-1000:]}')
    return r

def remote_verify():
    ps=ssh("pgrep -af '/root/radio_neuzugang_20261008.sh' | grep -v 'pgrep -af' || true").stdout
    if '/root/radio_neuzugang_20261008.sh' in ps:
        return {'ok':False,'reason':'Import laeuft noch','processes':ps.strip()}
    log=ssh(f"test -s {LOG} && cat {LOG} || true").stdout
    marker=ssh("test -s /root/drive-musik-neuzugang-20261008.SUCCESS && cat /root/drive-musik-neuzugang-20261008.SUCCESS || true").stdout.strip()
    if not marker:
        return {'ok':False,'reason':'Kein verifizierter Abschlussmarker vorhanden','log_tail':log[-2000:]}
    if re.search(r'Traceback',log):
        return {'ok':False,'reason':'Importprotokoll enthaelt Traceback','log_tail':log[-4000:]}
    code = r'''import json, os, sys
from pathlib import Path
import mutagen
base=Path('/var/lib/beets/neuzugang-20261008')
abl=base/'ablage/ablage.tsv'; dub=base/'ablage/dubletten.tsv'
# ablage.tsv records moved files; dubletten.tsv is written by the ablage step in the same backup dir.
rows=[]; missing=[]; bad=[]
if abl.exists():
  for line in abl.read_text(errors='replace').splitlines():
    p,z=line.split('\t',1); rows.append({'kind':'new','source':p,'target':z})
if dub.exists():
  for line in dub.read_text(errors='replace').splitlines():
    p,z=line.split('\t',1); rows.append({'kind':'duplicate','source':p,'target':z})
for x in rows:
  if x['kind']=='new': p=x['target']
  else: p=x['target']
  if not os.path.exists(p) or os.path.getsize(p)==0: missing.append(x)
  else:
    try:
      f=mutagen.File(p)
      if f is None or not getattr(f,'info',None): bad.append(x)
    except Exception: bad.append(x)
print(json.dumps({'rows':rows,'missing':missing,'bad':bad,'inbox_audio':sum(1 for p in Path('/mnt/music/Inbox/neuzugang-20261008').rglob('*') if p.is_file() and p.suffix.lower() in {'.mp3','.flac','.wav','.aiff','.aif','.m4a','.ogg'}),'master_audio':sum(1 for p in Path('/mnt/music/Master_Library').rglob('*') if p.is_file() and p.suffix.lower() in {'.mp3','.flac','.wav','.aiff','.aif','.m4a','.ogg'})},ensure_ascii=False))'''
    val=ssh("pct exec 120 -- python3 -c " + shlex.quote(code), check=False)
    if val.returncode: return {'ok':False,'reason':'Validierung in CT120 fehlgeschlagen','stderr':val.stderr[-2000:]}
    try: v=json.loads(val.stdout.strip().splitlines()[-1])
    except Exception: return {'ok':False,'reason':'Validierung lieferte kein JSON','stdout':val.stdout[-2000:]}
    if v['missing'] or v['bad'] or not v['rows']:
        return {'ok':False,'reason':'Zielbestand nicht vollstaendig lesbar','validation':v}
    return {'ok':True,'validation':v,'log_tail':log[-2000:]}

def rel_from_source(p):
    p=p.strip(); marker=INBOX+'/'
    return p[len(marker):] if p.startswith(marker) else None

def main():
    rows=inventory()
    status=remote_verify()
    result={'manifest':str(MANIFEST),'source_audio_files':len(rows),'verification':status,'trashed':0,'trash_readback':[]}
    if not status.get('ok'):
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False)); return 2
    if '--check-only' in sys.argv:
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False)); return 0
    approved=[]
    for x in status['validation']['rows']:
        rel=rel_from_source(x['source'])
        if rel: approved.append(rel)
    by_rel={x['relpath']:x for x in rows}
    targets=[]; missing_manifest=[]
    for rel in sorted(set(approved)):
        if rel in by_rel: targets.append(by_rel[rel])
        else: missing_manifest.append(rel)
    if missing_manifest or not targets:
        result['verification']={'ok':False,'reason':'Importpfade nicht eindeutig auf Drive-Inventar abbildbar','missing_manifest':missing_manifest,'approved_paths':approved}
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False)); return 3
    svc=api()
    for f in targets:
        svc.files().update(fileId=f['id'],body={'trashed':True},fields='id,trashed').execute()
    for f in targets:
        got=svc.files().get(fileId=f['id'],fields='id,name,trashed').execute()
        result['trash_readback'].append(got)
    result['trashed']=sum(1 for x in result['trash_readback'] if x.get('trashed') is True)
    result['not_trashed']=[x for x in result['trash_readback'] if x.get('trashed') is not True]
    result['source_untrashed_retained']=len(rows)-result['trashed']
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['trashed']==len(targets) else 4

if __name__=='__main__': sys.exit(main())
