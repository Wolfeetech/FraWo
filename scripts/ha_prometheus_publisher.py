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

def remote(host, command):
    try:
        return subprocess.check_output(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=5","root@"+host,command], text=True, timeout=15, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

def task_state(entity, name, state, attrs):
    attrs=dict(attrs); attrs.update({'friendly_name':name,'icon':'mdi:progress-clock','source':'FraWo Betriebsmonitoring'})
    publish(entity,state,attrs)

def metric(entity, value, name, unit='%', icon='mdi:chart-line'):
    publish(entity, 'unavailable' if value is None else round(value,2), {'friendly_name':name,'unit_of_measurement':unit,'icon':icon,'source':'Prometheus CT155'})

def run_tasks():
    drive_proc=remote('10.1.0.92', "pgrep -af 'fingerprint_reconcile.py.*--source /mnt/google-drive' | grep -v 'pgrep' || true")
    drive_lines=remote('10.1.0.92', "wc -l < /anker-backup/drive-inventar-20261009/fingerprints-global/all-drive-audio.jsonl 2>/dev/null || true")
    drive_tail=remote('10.1.0.92', "tail -n 1 /anker-backup/drive-inventar-20261009/fingerprints-global/all-drive-audio.log 2>/dev/null || true")
    task_state('sensor.frawo_drive_fingerprint_status','Drive-Audio-Fingerprint','läuft' if drive_proc else 'nicht aktiv', {'pid':drive_proc.split()[0] if drive_proc else '', 'datensätze':drive_lines or '0','letzter_logeintrag':drive_tail})
    radio_proc=remote('10.1.0.128', "pgrep -af 'radio_neuzugang|rclone copy.*neuzugang-music-clean' | grep -v 'pgrep' || true")
    radio_tail=remote('10.1.0.128', "tail -n 1 /root/radio_neuzugang_music_clean_ausfuehren.log 2>/dev/null || true")
    radio_log=remote('10.1.0.128', "tail -n 20 /root/radio_neuzugang_music_clean_ausfuehren.log 2>/dev/null || true")
    task_state('sensor.frawo_radio_import_status','Radio-Import','läuft' if radio_proc else 'nicht aktiv', {'pid':radio_proc.split()[0] if radio_proc else '', 'letzter_logeintrag':radio_tail,'log_auszug':radio_log[-1000:]})


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
    metric('sensor.frawo_studiopc_temperatur', scalar('windows_thermalzone_temperature_celsius{instance="studiopc"}'), 'StudioPC Temperatur', '°C', 'mdi:thermometer')
    publish('sensor.frawo_studiopc_prozesse', int(scalar('windows_system_processes{instance="studiopc"}',0) or 0), {'friendly_name':'StudioPC Prozesse','icon':'mdi:application-cog-outline','source':'Prometheus CT155'})
    metric('sensor.frawo_studiopc_systemlaufwerk', scalar('100 * (1 - windows_logical_disk_free_bytes{instance="studiopc",volume="C:"} / windows_logical_disk_size_bytes{instance="studiopc",volume="C:"})'), 'StudioPC Systemlaufwerk')
    publish('sensor.frawo_monitoring_aktualisiert', time.strftime('%Y-%m-%d %H:%M:%S %z'), {'friendly_name':'Monitoring zuletzt aktualisiert','icon':'mdi:clock-check-outline','source':'Prometheus CT155'})

def main():
    load_env()
    while True:
        try: run_tasks()
        except Exception as e: print('publisher error:',type(e).__name__,flush=True)
        time.sleep(60)
if __name__=='__main__': main()
