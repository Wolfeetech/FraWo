#!/usr/bin/env python3
"""Minimal Home Assistant WebSocket Lovelace helper using only stdlib."""
import argparse, base64, json, os, secrets, socket, struct
from pathlib import Path

def load_env():
    for p in (Path.home()/'.hermes/.env', Path.home()/'.ai-tools-shared/.env', Path('/home/hermes/.hermes/.env')):
        if p.exists():
            for line in p.read_text(errors='replace').splitlines():
                line=line.strip()
                if '=' in line and not line.startswith('#'):
                    k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip())

def ws(url):
    host=url.split('://',1)[-1].split(':')[0].split('/')[0]
    port=int(url.split(':')[-1].split('/')[0]) if ':' in url.split('://',1)[-1].split('/')[0] else 80
    s=socket.create_connection((host,port),10)
    key=base64.b64encode(secrets.token_bytes(16)).decode()
    s.sendall((f'GET /api/websocket HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
    head=b''
    while b'\r\n\r\n' not in head: head += s.recv(4096)
    if b' 101 ' not in head.split(b'\r\n',1)[0]: raise RuntimeError(head[:200].decode(errors='replace'))
    return s

def recv(s):
    while True:
        h=s.recv(2); op=h[0]&15; b2=h[1]; n=b2&127
        if n==126: n=struct.unpack('>H',s.recv(2))[0]
        elif n==127: n=struct.unpack('>Q',s.recv(8))[0]
        masked=b2>>7; mask=s.recv(4) if masked else b''; data=b''
        while len(data)<n: data += s.recv(n-len(data))
        if masked: data=bytes(x^mask[i%4] for i,x in enumerate(data))
        if op==9: continue
        if op==8: raise RuntimeError('Home Assistant WebSocket closed')
        if op==1: return json.loads(data.decode())

def send(s,obj):
    data=json.dumps(obj,separators=(',',':')).encode(); n=len(data); mask=secrets.token_bytes(4)
    if n<126: hdr=bytes([129,128|n])
    elif n<65536: hdr=bytes([129,254])+struct.pack('>H',n)
    else: hdr=bytes([129,255])+struct.pack('>Q',n)
    s.sendall(hdr+mask+bytes(x^mask[i%4] for i,x in enumerate(data)))

def main():
    load_env(); token=(os.environ.get('HASS_TOKEN') or os.environ.get('HOMEASSISTANT_TOKEN') or os.environ.get('HASS_API_KEY') or '').removeprefix('Bearer ').strip()
    if not token: raise SystemExit('HASS_TOKEN fehlt')
    base=(os.environ.get('HASS_URL') or os.environ.get('HOMEASSISTANT_URL') or 'http://10.1.0.40:8123').rstrip('/')
    s=ws(base); assert recv(s).get('type')=='auth_required'; send(s,{'type':'auth','access_token':token}); assert recv(s).get('type')=='auth_ok'
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['get','save','create']); ap.add_argument('--url-path',default='kiosk-frawo'); ap.add_argument('--file'); a=ap.parse_args()
    if a.action=='create':
        send(s,{'id':1,'type':'lovelace/dashboards/create','url_path':a.url_path,'title':'FraWo Betrieb & Monitoring','icon':'mdi:server-network','show_in_sidebar':True,'require_admin':False}); r=recv(s)
    elif a.action=='get': send(s,{'id':1,'type':'lovelace/config','url_path':a.url_path}); r=recv(s); 
    else:
        if not a.file: raise SystemExit('--file fehlt')
        config=json.loads(Path(a.file).read_text()); send(s,{'id':1,'type':'lovelace/config/save','url_path':a.url_path,'config':config}); r=recv(s)
    if not r.get('success'): raise SystemExit(json.dumps(r,ensure_ascii=False))
    print(json.dumps(r.get('result',{}),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
