#!/usr/bin/env python3
# FraWo M1 (22.09.2026, Claude): Surface-Ausnahmen VOR die Sperre "IoT -> Server" (20010) ziehen.
# Seit die Server wieder im Server-Netz stehen, greift 20010 zuerst - die Ausnahmen 20011-20014 kamen nie zum Zug.
# Laeuft auf dem OptiPlex (nutzt /root/m1/ucg.py und /etc/frawo/unifi.env).
import sys
sys.path.insert(0, '/root/m1')
from ucg import call

NEU = {  # Regel-ID: neuer Index (frei: 20002-20004, alle vor 20010)
    '6ab16eb872c002307596674c': 20002,  # Surface -> Odoo
    '6ab1ed7572c0023075967cd5': 20003,  # Surface -> Paperless (:8000)
    '6ab1ed7572c0023075967cd8': 20004,  # Surface -> Proxmox Anker (:8006)
}
belegt = {r['rule_index']: r['_id'] for r in call('GET', '/rest/firewallrule') if r.get('ruleset') == 'LAN_IN'}
for rid, idx in NEU.items():
    if belegt.get(idx) not in (None, rid):
        sys.exit('Index %d ist schon belegt - Abbruch' % idx)
for rid, idx in NEU.items():
    r = [x for x in call('GET', '/rest/firewallrule') if x['_id'] == rid][0]
    alt = r['rule_index']
    r['rule_index'] = idx
    call('PUT', '/rest/firewallrule/' + rid, r)
    chk = [x for x in call('GET', '/rest/firewallrule') if x['_id'] == rid][0]
    print('%s: %s -> %s  %s' % (chk['name'], alt, chk['rule_index'], 'OK' if chk['rule_index'] == idx else 'FEHLER'))
