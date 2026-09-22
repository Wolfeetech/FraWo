#!/usr/bin/env python3
# FraWo M1 (22.09.2026, Claude): Surface-Portal von den Notnetz-Adressen (10.0.0.x) auf das Server-Netz (10.1.0.x).
# Aufruf: surface_adressen.py DATEI [DATEI ...]   (legt DATEI.bak-20260922-m1 an)
import re, shutil, sys, os
MAP = {'183': '10.1.0.40', '99': '10.1.0.92', '191': '10.1.0.128', '227': '10.1.0.227', '215': '10.1.0.248',
       '64': '10.1.0.95', '204': '10.1.0.21', '106': '10.1.0.100', '186': '10.1.0.38', '100': '10.1.0.35',
       '55': '10.1.0.112'}
PAT = re.compile(r'(?<![\d.])10\.0\.0\.(\d{1,3})(?!\d)')
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    n = [0]
    def rep(m):
        if m.group(1) in MAP:
            n[0] += 1
            return MAP[m.group(1)]
        return m.group(0)
    neu = PAT.sub(rep, s)
    rest = sorted(set(PAT.findall(neu)))
    if n[0]:
        bak = p + '.bak-20260922-m1'
        if not os.path.exists(bak):
            shutil.copy2(p, bak)
        open(p, 'w', encoding='utf-8', newline='').write(neu)
    print('%s: %d ersetzt, verbleibende 10.0.0.x: %s' % (p, n[0], rest or 'keine'))
