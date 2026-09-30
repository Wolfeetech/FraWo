"""Discogs-Abgleich für die FraWo-Musikredaktion (Odoo #1090).

Rät nie: ohne eindeutigen Treffer ist das Ergebnis 'unklar', bei
widersprüchlichen Stilen 'widerspruch'. Spec:
DOCS/superpowers/specs/2026-09-30-frawo-funk-musikredaktion-design.md
"""
import collections
import re
import time
import unicodedata

API = 'https://api.discogs.com/database/search'
UA = 'FraWoMusikredaktion/0.1 +https://frawo.tech'


def norm(text):
    t = re.sub(r"['’‘`´]", '', text or '')   # gerade und typografische Apostrophe gleich behandeln
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'\((original|extended|radio|club|album)[^)]*\)', ' ', t)
    t = re.sub(r'\b(feat|ft|featuring)\b.*', ' ', t)
    t = t.replace('&', ' and ')
    t = re.sub(r'\band\b', ' ', t)
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def suchbegriffe(titel):
    """(erster Interpret, Grundtitel) — ohne Mix-/Remix-Zusatz, Tempo-Zahl, doppelten Interpreten."""
    artist = re.split(r',|\s&\s|\sx\s|\sfeat\.?\s|\sft\.?\s|\svs\.?\s', titel.get('artist') or '', flags=re.I)[0].strip()
    t = titel.get('title') or ''
    if artist and t.lower().startswith(artist.lower() + ' - '):
        t = t[len(artist) + 3:]
    t = re.sub(r'[\(\[].*?[\)\]]', ' ', t)          # (Original Mix), [Remixes], (xyz Remix)
    t = re.sub(r'\s+-\s+.*$', '', t)                # "Good Luck, Babe! - Leondis Remix"
    t = re.sub(r'\s+\d{2,3}\s*$', '', t)            # angehängtes Tempo "… 125"
    t = re.sub(r'\b(feat|ft)\b.*', '', t, flags=re.I)
    return artist, re.sub(r'\s+', ' ', t).strip(' -')


def _passt(titel, treffer):
    # Die Suche lief bereits über den Tracktitel; hier muss der Interpret der Veröffentlichung stimmen.
    teile = treffer.get('title', '').split(' - ', 1)
    if len(teile) != 2:
        return False
    return norm(suchbegriffe(titel)[0]) in norm(teile[0])


def bewerte(titel, treffer):
    leer = {'status': 'unklar', 'genre': '', 'styles': [], 'quelle': ''}
    if not norm(titel.get('artist')) or not norm(titel.get('title')):
        return leer
    passend = [t for t in treffer if t.get('type') == 'release' and _passt(titel, t)]
    if not passend:
        return leer
    # Mehrheit der Ausgaben: ein Stil zählt, wenn er in mehr als der Hälfte der passenden Veröffentlichungen steht
    zaehl = collections.Counter(s for t in passend for s in set(t.get('style') or []))
    mehrheit = [(s, n) for s, n in zaehl.most_common() if n * 2 > len(passend)]
    if not mehrheit:
        return dict(leer, status='widerspruch')
    styles = [s for s, _ in mehrheit[:2]]
    erster = next(t for t in passend if set(styles) <= set(t.get('style') or []))
    return {'status': 'belegt', 'genre': (erster.get('genre') or [''])[0], 'styles': styles,
            'quelle': 'https://www.discogs.com' + erster['uri']}


class DiscogsClient:
    def __init__(self, token, session=None):
        self.token = token
        if session is None:
            from requests_ratelimiter import LimiterSession
            session = LimiterSession(per_minute=55)
        self.s = session

    def suche(self, artist, title):
        params = {'type': 'release', 'artist': artist, 'track': title, 'per_page': 10}
        kopf = {'User-Agent': UA, 'Authorization': 'Discogs token=' + self.token}
        for _ in range(5):
            r = self.s.get(API, params=params, headers=kopf, timeout=30)
            if r.status_code == 200:
                return r.json().get('results', [])
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(float(r.headers.get('Retry-After', 10)))
                continue
            r.raise_for_status()
        raise RuntimeError('Discogs antwortet nicht (5 Versuche)')
