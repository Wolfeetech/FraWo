"""Energie-Rohmerkmale aus Essentia (streaming_extractor_music v2.1_beta2), Odoo #1090.

Misst, rät nicht. Die Abbildung der Rohwerte auf Energie 1–5 folgt erst nach
der Eichung an ~50 von Wolf gehörten Titeln (Spec Abschnitt 7).
"""
import json
import os
import subprocess
import tempfile


def merkmale(j):
    r, t, l = j['rhythm'], j['tonal'], j['lowlevel']
    return {'bpm': float(r['bpm']),
            'tonart': '%s %s' % (t['key_key'], t['key_scale']),
            'tonart_sicherheit': float(t['key_strength']),
            'lautheit': float(l['average_loudness']),
            'tanzbarkeit': float(r['danceability']),
            'anschlagdichte': float(r['onset_rate']),
            'dynamik': float(l['dynamic_complexity'])}


def messe(pfad, binary, timeout=300):
    with tempfile.TemporaryDirectory() as tmp:
        aus = os.path.join(tmp, 'out.json')
        try:
            lauf = subprocess.run([binary, pfad, aus], capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'fehler': 'zeitueberschreitung'}
        if lauf.returncode != 0 or not os.path.exists(aus):
            return {'fehler': (lauf.stderr or b'')[-200:].decode('utf-8', 'replace').strip() or 'rc=%s' % lauf.returncode}
        try:
            with open(aus, encoding='utf-8') as f:
                return merkmale(json.load(f))
        except (KeyError, ValueError) as ex:
            return {'fehler': 'ausgabe unvollstaendig: %s' % ex}
