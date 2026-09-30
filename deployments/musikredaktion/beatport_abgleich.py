"""Beatport-Abgleich für die FraWo-Musikredaktion (Odoo #1090).

Beatport führt je Titel Genre, Untergenre, Tempo und Tonart. Es gibt keinen
offiziellen Zugang für Privatkonten; die Anmeldung läuft wie im Browser bzw.
wie das beets-Modul "beatport4": Konto-Login -> OAuth-Code -> Token, mit der
öffentlichen Client-ID der Beatport-API-Doku. Nur lesen, gebremst.
Zugangsdaten nur aus /etc/frawo/beatport.env, nie loggen.
"""
import re
import time

import requests

from discogs_abgleich import norm, suchbegriffe

API = 'https://api.beatport.com/v4'
REDIRECT = API + '/auth/o/post-message/'
UA = 'Mozilla/5.0 (FraWoMusikredaktion/0.1 +https://frawo.tech)'


def client_id(s):
    html = s.get(API + '/docs/', timeout=30).text
    for src in re.findall(r'src="([^"]+\.js)"', html):
        js = s.get(src if src.startswith('http') else 'https://api.beatport.com' + src, timeout=30).text
        m = re.search(r"API_CLIENT_ID:\s*['\"]([A-Za-z0-9]+)['\"]", js)
        if m:
            return m.group(1)
    raise RuntimeError('Beatport-Client-ID nicht gefunden')


def anmelden(user, passwort, s=None):
    s = s or requests.Session()
    s.headers['User-Agent'] = UA
    cid = client_id(s)
    r = s.post(API + '/auth/login/', json={'username': user, 'password': passwort}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError('Beatport-Login fehlgeschlagen: HTTP %s' % r.status_code)
    r = s.get(API + '/auth/o/authorize/', params={'client_id': cid, 'response_type': 'code', 'redirect_uri': REDIRECT},
              allow_redirects=False, timeout=30)
    m = re.search(r'code=([A-Za-z0-9]+)', r.headers.get('Location', ''))
    if not m:
        raise RuntimeError('Beatport-Autorisierung ohne Code: HTTP %s' % r.status_code)
    r = s.post(API + '/auth/o/token/', data={'code': m.group(1), 'grant_type': 'authorization_code',
                                             'redirect_uri': REDIRECT, 'client_id': cid}, timeout=30)
    r.raise_for_status()
    s.headers['Authorization'] = 'Bearer ' + r.json()['access_token']
    return s


def suche(s, artist, title, pause=1.5):
    time.sleep(pause)   # gebremst: Beatport ist kein offizieller Partnerzugang
    r = s.get(API + '/catalog/search/', params={'q': '%s %s' % (artist, title), 'type': 'tracks', 'per_page': 10}, timeout=30)
    if r.status_code == 429:
        time.sleep(30)
        r = s.get(API + '/catalog/search/', params={'q': '%s %s' % (artist, title), 'type': 'tracks', 'per_page': 10}, timeout=30)
    r.raise_for_status()
    return r.json().get('tracks', [])


def _mix(titel):
    m = re.search(r'\(([^)]*(mix|edit|remix|dub|version|rework)[^)]*)\)', titel or '', re.I)
    return norm(m.group(1)) if m else ''


def bewerte(titel, treffer):
    """Beatport-Treffer bewerten. Rät nie: ohne passenden Titel 'unklar', bei uneinigen Genres 'widerspruch'."""
    leer = {'status': 'unklar', 'genre': '', 'styles': [], 'quelle': '', 'bpm': None, 'tonart': ''}
    artist, grund = suchbegriffe(titel)
    if not norm(artist) or not norm(grund):
        return leer
    passend = [t for t in treffer
               if norm(t.get('name')) == norm(grund)
               and any(norm(artist) in norm(a.get('name')) for a in t.get('artists') or [])]
    if not passend:
        return leer
    mix = _mix(titel.get('title'))
    if mix:
        gleich = [t for t in passend if norm(t.get('mix_name')) == mix]
        passend = gleich or passend
    genres = {(t.get('genre') or {}).get('name') for t in passend}
    if len(genres) != 1:
        return dict(leer, status='widerspruch')
    t = passend[0]
    styles = [(t.get('genre') or {}).get('name')] + ([(t.get('sub_genre') or {}).get('name')] if t.get('sub_genre') else [])
    return {'status': 'belegt', 'genre': styles[0], 'styles': styles,
            'quelle': 'https://www.beatport.com/track/%s/%s' % (t.get('slug'), t.get('id')),
            'bpm': t.get('bpm'), 'tonart': (t.get('key') or {}).get('name', '')}
