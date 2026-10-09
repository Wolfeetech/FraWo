#!/usr/bin/env python3
"""Publish read-only Prometheus admin metrics into Home Assistant."""
import json, os, shlex, subprocess, time, urllib.request
from pathlib import Path

PROM_QUERY = "http://127.0.0.1:9090/api/v1/query"
PROM_SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "root@10.1.0.92", "pct", "exec", "155", "--", "curl", "-gfsS", "--max-time", "8"]

def load_env():
    for p in (Path('/home/hermes/.hermes/.env'), Path('/home/hermes/.ai-tools-shared/.env')):
        if p.exists():
            for line in p.read_text(errors='replace').splitlines():
                line=line.strip()
                if '=' in line and not line.startswith('#'):
                    k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip())

def prom(query):
    remote='pct exec 155 -- curl -gfsS --max-time 8 --data-urlencode '+shlex.quote('query='+query)+' '+PROM_QUERY
    raw=subprocess.check_output(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=5","root@10.1.0.92",remote], text=True, timeout=20)
    data=json.loads(raw)
    if data.get('status')!='success': raise RuntimeError(data)
    return data.get('data',{}).get('result',[])

def scalar(query, default=None):
    rows=prom(query)
    if not rows: return default
    try: return float(rows[0]['value'][1])
    except (KeyError,IndexError,ValueError): return default

def publish(entity, state, attrs):
    url=os.environ.get('HASS_URL') or os.environ.get('HOMEASSISTANT_URL') or 'http://10.1.0.40:8123'
    tok=(os.environ.get('HASS_TOKEN') or os.environ.get('HOMEASSISTANT_TOKEN') or '').removeprefix('Bearer ').strip()
    if not tok: raise RuntimeError('HASS_TOKEN missing')
    body=json.dumps({'state':str(state), 'attributes':attrs}).encode()
    req=urllib.request.Request(url.rstrip('/')+'/api/states/'+entity, data=body, method='POST', headers={'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        if r.status not in (200,201): raise RuntimeError(f'{entity}: HTTP {r.status}')

def metric(entity, value, name, unit='%', icon='mdi:chart-line'):
    publish(entity, 'unavailable' if value is None else round(value,2), {'friendly_name':name,'unit_of_measurement':unit,'icon':icon,'source':'Prometheus CT155'})

def run_once():
    total=scalar('count(up{job=~"node_exporter|windows_studiopc"})',0)
    up=scalar('count(up{job=~"node_exporter|windows_studiopc"} == 1)',0)
    publish('sensor.frawo_monitoring_ziele_gesamt', int(total), {'friendly_name':'Monitoring-Ziele gesamt','icon':'mdi:monitor-dashboard','source':'Prometheus CT155'})
    publish('sensor.frawo_monitoring_ziele_erreichbar', int(up), {'friendly_name':'Monitoring-Ziele erreichbar','icon':'mdi:check-network','source':'Prometheus CT155'})
    publish('binary_sensor.frawo_monitoring_alle_ziele_erreichbar','on' if total and up==total else 'off', {'friendly_name':'Alle Monitoring-Ziele erreichbar','device_class':'connectivity','source':'Prometheus CT155'})
    for inst,label in {'anker-pve':'Anker','prodesk-pve':'ProDesk','optiplex-pve':'OptiPlex'}.items():
        sel='{instance="'+inst+'"}'
        cpusel='{instance="'+inst+'",mode="idle"}'
        root='{instance="'+inst+'",mountpoint="/",fstype!=""}'
        metric('sensor.frawo_'+inst.replace('-','_')+'_cpu_auslastung', scalar('(1 - avg by(instance) (rate(node_cpu_seconds_total'+cpusel+'[5m]))) * 100'), label+' CPU-Auslastung')
        metric('sensor.frawo_'+inst.replace('-','_')+'_ram_auslastung', scalar('100 * (1 - node_memory_MemAvailable_bytes'+sel+' / node_memory_MemTotal_bytes'+sel+')'), label+' RAM-Auslastung')
        metric('sensor.frawo_'+inst.replace('-','_')+'_root_speicher', scalar('100 * (1 - node_filesystem_avail_bytes'+root+' / node_filesystem_size_bytes'+root+')'), label+' Root-Speicher')
    metric('sensor.frawo_studiopc_cpu_auslastung', scalar('(1 - avg by(instance) (rate(windows_cpu_time_total{instance="studiopc",mode="idle"}[5m]))) * 100'), 'StudioPC CPU-Auslastung')
    metric('sensor.frawo_studiopc_ram_auslastung', scalar('100 * (1 - windows_memory_available_bytes{instance="studiopc"} / windows_cs_physical_memory_bytes{instance="studiopc"})'), 'StudioPC RAM-Auslastung')
    publish('sensor.frawo_monitoring_aktualisiert', time.strftime('%Y-%m-%d %H:%M:%S %z'), {'friendly_name':'Monitoring zuletzt aktualisiert','icon':'mdi:clock-check-outline','source':'Prometheus CT155'})

def main():
    load_env()
    while True:
        try: run_once()
        except Exception as e: print('publisher error:',type(e).__name__,flush=True)
        time.sleep(60)
if __name__=='__main__': main()
