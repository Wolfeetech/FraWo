# Musikredaktion — Probelauf (Katalog + Messung) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An 200 zufällig gezogenen Titeln messen, wie gut die Discogs-Recherche Genre/Stil belegt und wie schnell und brauchbar eine Essentia-Audiomessung Energie-Rohwerte liefert — ohne die Bibliothek zu verändern.

**Architecture:** Zwei kleine, reine Python-Module (Discogs-Abgleich, Energie-Merkmale) mit stdlib-`unittest`-Tests auf Fixtures, dazu je ein Probelauf-Skript, das nur liest und CSV-Berichte nach `/root/musikredaktion-probe/` schreibt. Läuft in CT120 (ProDesk, `pct exec 120`), wo beets-DB und Musik direkt liegen. Der Produktivort der Messung (CT120 oder OptiPlex) wird **nach** gemessener Laufzeit entschieden (Abweichung zur Spec, bewusst: erst messen).

**Tech Stack:** Python 3.11 (CT120), `requests` + `requests-ratelimiter` (vorhanden), beets 2.13 (nur lesend, `sqlite3 mode=ro`), Essentia-Extractor als statisches Binary (`essentia_streaming_extractor_music`, v2.1_beta2, x86_64).

**Spec:** `DOCS/superpowers/specs/2026-09-30-frawo-funk-musikredaktion-design.md` (Abschnitte 3, 8 Schritt 1+2)

## Global Constraints

- Nichts wird in `musik.db` oder in Musikdateien geschrieben. DB nur über `file:/var/lib/beets/musik.db?mode=ro`.
- Kein Wert wird geraten: ohne eindeutigen Discogs-Treffer bleibt das Ergebnis `unklar`.
- Discogs-Ratenbegrenzung: höchstens 60 Anfragen/Minute (authentifiziert), User-Agent `FraWoMusikredaktion/0.1 +https://frawo.tech`.
- Der Discogs-Schlüssel kommt aus Vaultwarden in `/etc/frawo/discogs.env` (`DISCOGS_TOKEN=…`, Rechte `0600 root`), nie ins Repo, nie in Logs, nie in Odoo.
- Platte seriell lesen, nie parallel (NTFS über USB, siehe Sanierungs-Spec §8).
- Code im Repo unter `deployments/musikredaktion/`, ausgerollt nach `/opt/musikredaktion/` in CT120.

## Review Focus

- Titel mit Zusatz wie „(Original Mix)“, „feat. X“, „&“ statt „and“: sollen trotzdem den richtigen Release treffen → Test in Task 1 (`test_normalisierung_*`).
- Mehrere Discogs-Treffer mit unterschiedlichen Stilen (Compilation vs. Single): Ergebnis muss `widerspruch`, nicht der erste Treffer sein → Test in Task 1.
- Titel ohne Interpret oder Titel (517 ohne Genre, einige ohne Tags): dürfen den Lauf nicht abbrechen, Ergebnis `unklar` → Test in Task 1.
- Discogs antwortet 429/5xx: Lauf wartet und macht weiter statt abzubrechen oder den Titel als `unklar` zu verbuchen → Test in Task 1.
- Essentia scheitert an einer Datei (defekte FLAC, `.wav` ohne Tags): Zeile mit `fehler`, Lauf geht weiter → Test in Task 3.

---

### Task 1: Discogs-Abgleich (reines Modul + Tests)

**Files:**
- Create: `deployments/musikredaktion/discogs_abgleich.py`
- Create: `deployments/musikredaktion/tests/test_discogs_abgleich.py`
- Create: `deployments/musikredaktion/tests/fixtures/discogs_suche_eindeutig.json`
- Create: `deployments/musikredaktion/tests/fixtures/discogs_suche_widerspruch.json`

**Interfaces:**
- Produces:
  - `norm(text: str) -> str`
  - `bewerte(titel: dict, treffer: list[dict]) -> dict` mit Schlüsseln `status` (`belegt`|`widerspruch`|`unklar`), `genre` (str), `styles` (list[str], max 2), `quelle` (URL oder `''`)
  - `class DiscogsClient(token: str, session=None)` mit `suche(artist: str, title: str) -> list[dict]` (liefert `results` der Discogs-Suche, wiederholt bei 429/5xx bis zu 5× mit Wartezeit aus `Retry-After`, sonst 10 s)
  - `titel` hat Schlüssel `artist`, `title`, `length` (Sekunden, float)

- [ ] **Step 1: Fixtures anlegen** (echte Form der Discogs-Suchantwort `GET /database/search?type=release&artist=…&track=…`)

`tests/fixtures/discogs_suche_eindeutig.json`:
```json
{"results": [
  {"id": 1234567, "type": "release", "title": "Chris Stussy - Won't Stop (Don't)",
   "genre": ["Electronic"], "style": ["Deep House", "Minimal"],
   "uri": "/release/1234567-Chris-Stussy-Wont-Stop-Dont"},
  {"id": 1234568, "type": "release", "title": "Chris Stussy - Won't Stop (Don't)",
   "genre": ["Electronic"], "style": ["Deep House"],
   "uri": "/release/1234568-Chris-Stussy-Wont-Stop-Dont"}
]}
```

`tests/fixtures/discogs_suche_widerspruch.json`:
```json
{"results": [
  {"id": 1, "type": "release", "title": "Artist - Track", "genre": ["Electronic"], "style": ["Techno"], "uri": "/release/1"},
  {"id": 2, "type": "release", "title": "Artist - Track", "genre": ["Electronic"], "style": ["Disco", "Nu-Disco"], "uri": "/release/2"}
]}
```

- [ ] **Step 2: Failing Tests schreiben**

`tests/test_discogs_abgleich.py`:
```python
import json, os, unittest
from unittest import mock
import discogs_abgleich as d

FIX = os.path.join(os.path.dirname(__file__), 'fixtures')
def lade(n):
    with open(os.path.join(FIX, n), encoding='utf-8') as f:
        return json.load(f)['results']

class TestNorm(unittest.TestCase):
    def test_normalisierung_mix_und_feat(self):
        self.assertEqual(d.norm("Won’t Stop (Don’t) (Original Mix) feat. X"), 'wont stop dont')
        self.assertEqual(d.norm("Won't Stop (Don't)"), d.norm("Won’t Stop (Don’t)"))
    def test_normalisierung_und(self):
        self.assertEqual(d.norm('Frankey & Sandrino'), d.norm('Frankey and Sandrino'))

class TestBewerte(unittest.TestCase):
    titel = {'artist': 'Chris Stussy', 'title': "Won't Stop (Don't)", 'length': 351.0}
    def test_eindeutig_belegt_mit_gemeinsamem_stil(self):
        r = d.bewerte(self.titel, lade('discogs_suche_eindeutig.json'))
        self.assertEqual(r['status'], 'belegt')
        self.assertEqual(r['styles'], ['Deep House'])
        self.assertTrue(r['quelle'].startswith('https://www.discogs.com/release/'))
    def test_widerspruch_nicht_erster_treffer(self):
        r = d.bewerte({'artist': 'Artist', 'title': 'Track', 'length': 300.0}, lade('discogs_suche_widerspruch.json'))
        self.assertEqual(r['status'], 'widerspruch')
        self.assertEqual(r['styles'], [])
    def test_ohne_treffer_unklar(self):
        self.assertEqual(d.bewerte(self.titel, [])['status'], 'unklar')
    def test_ohne_interpret_unklar(self):
        self.assertEqual(d.bewerte({'artist': '', 'title': 'x', 'length': 0}, lade('discogs_suche_eindeutig.json'))['status'], 'unklar')
    def test_fremder_titel_zaehlt_nicht(self):
        fremd = [{'id': 9, 'type': 'release', 'title': 'Jemand Anders - Etwas', 'genre': ['Rock'], 'style': ['Punk'], 'uri': '/release/9'}]
        self.assertEqual(d.bewerte(self.titel, fremd)['status'], 'unklar')

class TestClient(unittest.TestCase):
    def test_429_wird_wiederholt(self):
        s = mock.Mock()
        erst = mock.Mock(status_code=429, headers={'Retry-After': '0'})
        dann = mock.Mock(status_code=200); dann.json.return_value = {'results': [1]}
        s.get.side_effect = [erst, dann]
        with mock.patch('time.sleep'):
            self.assertEqual(d.DiscogsClient('x', session=s).suche('a', 'b'), [1])
        self.assertEqual(s.get.call_count, 2)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Test laufen lassen, muss scheitern**

Run: `cd deployments/musikredaktion && python -m unittest discover -s tests -v`
Expected: FAIL mit `ModuleNotFoundError: No module named 'discogs_abgleich'`

- [ ] **Step 4: Modul schreiben**

`discogs_abgleich.py`:
```python
"""Discogs-Abgleich für die FraWo-Musikredaktion. Rät nie: ohne eindeutigen Treffer 'unklar'."""
import collections, re, time, unicodedata
import requests

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

def _passt(titel, treffer):
    # Discogs-Releasetitel: "Interpret - Releasetitel"; Interpret muss passen, Titel muss im Releasetitel stecken
    teile = treffer.get('title', '').split(' - ', 1)
    if len(teile) != 2:
        return False
    return norm(titel['artist']) in norm(teile[0]) and norm(titel['title']) in norm(teile[1])

def bewerte(titel, treffer):
    leer = {'status': 'unklar', 'genre': '', 'styles': [], 'quelle': ''}
    if not norm(titel.get('artist')) or not norm(titel.get('title')):
        return leer
    passend = [t for t in treffer if t.get('type') == 'release' and _passt(titel, t)]
    if not passend:
        return leer
    stil_sets = [set(t.get('style') or []) for t in passend]
    gemeinsam = set.intersection(*stil_sets) if stil_sets else set()
    if not gemeinsam:
        return dict(leer, status='widerspruch')
    zaehl = collections.Counter(s for t in passend for s in (t.get('style') or []) if s in gemeinsam)
    styles = [s for s, _ in zaehl.most_common(2)]
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
```

- [ ] **Step 5: Tests laufen lassen, müssen bestehen**

Run: `cd deployments/musikredaktion && python -m unittest discover -s tests -v`
Expected: 8 Tests OK

- [ ] **Step 6: Commit + Push**

```bash
git add deployments/musikredaktion
git commit -m "🤖 [Claude] Musikredaktion: Discogs-Abgleich mit Tests (#1090)"
git push
```

---

### Task 2: Katalog-Probelauf an 200 Titeln

**Files:**
- Create: `deployments/musikredaktion/probelauf_katalog.py`

**Interfaces:**
- Consumes: `discogs_abgleich.bewerte`, `discogs_abgleich.DiscogsClient` aus Task 1
- Produces: `/root/musikredaktion-probe/katalog.csv` (`id;artist;title;genre_alt;status;genre;styles;quelle`) und eine Zusammenfassung auf stdout: `ERGEBNIS belegt=N widerspruch=N unklar=N quote=P%`

- [ ] **Step 1: Skript schreiben**

```python
"""Probelauf: 200 zufällige Titel gegen Discogs. Liest nur, schreibt nur CSV."""
import csv, os, random, sqlite3, sys, collections
sys.path.insert(0, '/opt/musikredaktion')
import discogs_abgleich as d

AUS = '/root/musikredaktion-probe'
os.makedirs(AUS, exist_ok=True)
token = dict(l.strip().split('=', 1) for l in open('/etc/frawo/discogs.env') if '=' in l)['DISCOGS_TOKEN']
db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
rows = db.execute('select id, artist, title, length, genre from items').fetchall()
random.seed(20260930)
probe = random.sample(rows, 200)
c = d.DiscogsClient(token)
zaehl = collections.Counter()
with open(os.path.join(AUS, 'katalog.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'artist', 'title', 'genre_alt', 'status', 'genre', 'styles', 'quelle'])
    for n, (iid, artist, title, length, genre) in enumerate(probe, 1):
        titel = {'artist': artist or '', 'title': title or '', 'length': length or 0}
        treffer = c.suche(titel['artist'], titel['title']) if titel['artist'] and titel['title'] else []
        r = d.bewerte(titel, treffer)
        zaehl[r['status']] += 1
        w.writerow([iid, artist, title, genre, r['status'], r['genre'], '|'.join(r['styles']), r['quelle']])
        if n % 25 == 0:
            print(n, dict(zaehl), flush=True)
q = 100 * zaehl['belegt'] / 200
print('ERGEBNIS belegt=%d widerspruch=%d unklar=%d quote=%.0f%%' % (zaehl['belegt'], zaehl['widerspruch'], zaehl['unklar'], q))
```

- [ ] **Step 2: Schlüssel bereitstellen** (Claude holt ihn aus Vaultwarden, Eintrag „Discogs API-Token (Musikredaktion)“)

```bash
ssh -i ~/.ssh/pve_ed25519 root@10.1.0.128 "pct exec 120 -- sh -c 'install -d -m 700 /etc/frawo && umask 077 && cat > /etc/frawo/discogs.env'" < discogs.env   # Datei lokal im Scratchpad, danach löschen
```

- [ ] **Step 3: Ausrollen und Tests in CT120 laufen lassen**

```bash
scp -r -i ~/.ssh/pve_ed25519 deployments/musikredaktion root@10.1.0.128:/tmp/musikredaktion
ssh -i ~/.ssh/pve_ed25519 root@10.1.0.128 "pct push 120 ... (je Datei nach /opt/musikredaktion/) && pct exec 120 -- sh -c 'cd /opt/musikredaktion && python3 -m unittest discover -s tests'"
```
Expected: `OK`

- [ ] **Step 4: Probelauf starten** (Laufzeit ~4 min bei 55/min)

```bash
ssh -i ~/.ssh/pve_ed25519 root@10.1.0.128 "pct exec 120 -- python3 /opt/musikredaktion/probelauf_katalog.py"
```
Expected: letzte Zeile `ERGEBNIS …`. **Abnahme:** quote ≥ 50 % → Discogs taugt als Hauptquelle; darunter: MusicBrainz-Ergänzung vorziehen (eigener Plan).

- [ ] **Step 5: Stichprobe prüfen** — 10 zufällige `belegt`-Zeilen öffnen, Quelle-URL gegen Interpret/Titel vergleichen, Befund notieren.

- [ ] **Step 6: Commit + Push** (`probelauf_katalog.py`)

---

### Task 3: Energie-Merkmale per Essentia (Modul + Probelauf)

**Files:**
- Create: `deployments/musikredaktion/energie_merkmale.py`
- Create: `deployments/musikredaktion/tests/test_energie_merkmale.py`
- Create: `deployments/musikredaktion/tests/fixtures/essentia_beispiel.json`
- Create: `deployments/musikredaktion/probelauf_messung.py`

**Interfaces:**
- Produces:
  - `merkmale(essentia_json: dict) -> dict` mit `bpm`, `tonart` (z. B. `'A minor'`), `lautheit` (LUFS), `tanzbarkeit`, `anschlagdichte` (Onsets/s), `dynamik` (LU)
  - `messe(pfad: bytes, binary: str, timeout: int = 120) -> dict` = `merkmale(...)` oder `{'fehler': '<Grund>'}`
  - `/root/musikredaktion-probe/messung.csv` mit `id;pfad;sekunden;bpm;bpm_beets;tonart;lautheit;tanzbarkeit;anschlagdichte;dynamik;fehler`

- [ ] **Step 1: Essentia-Binary installieren und prüfen**

```bash
ssh -i ~/.ssh/pve_ed25519 root@10.1.0.128 "pct exec 120 -- sh -c 'mkdir -p /opt/essentia && cd /opt/essentia && curl -fsSLO https://essentia.upf.edu/extractors/essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz && tar xzf essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz && ls */essentia_streaming_extractor_music'"
```
Expected: Pfad zum Binary. (Scheitert der Download: Paket `essentia` über `pip install essentia` in ein venv `/opt/musikredaktion/venv` — dann `messe()` über `essentia.standard.MusicExtractor` statt Binary; Schnittstelle bleibt gleich.)

- [ ] **Step 2: Fixture erzeugen** — Binary einmal auf eine bekannte Datei laufen lassen, Ausgabe-JSON als `tests/fixtures/essentia_beispiel.json` ins Repo (nur die Schlüssel `rhythm.bpm`, `rhythm.danceability`, `rhythm.onset_rate`, `tonal.key_edma.key`, `tonal.key_edma.scale`, `lowlevel.loudness_ebu128.integrated`, `lowlevel.loudness_ebu128.loudness_range` behalten).

- [ ] **Step 3: Failing Tests schreiben**

```python
import json, os, unittest
from unittest import mock
import energie_merkmale as e

FIX = os.path.join(os.path.dirname(__file__), 'fixtures', 'essentia_beispiel.json')

class TestMerkmale(unittest.TestCase):
    def test_felder_vorhanden_und_plausibel(self):
        m = e.merkmale(json.load(open(FIX, encoding='utf-8')))
        self.assertTrue(60 <= m['bpm'] <= 200)
        self.assertIn(' ', m['tonart'])
        self.assertTrue(-40 <= m['lautheit'] <= 0)
        for k in ('tanzbarkeit', 'anschlagdichte', 'dynamik'):
            self.assertIsInstance(m[k], float)

class TestMesse(unittest.TestCase):
    def test_defekte_datei_liefert_fehler_statt_abbruch(self):
        lauf = mock.Mock(returncode=1, stderr=b'Error: cannot decode')
        with mock.patch('subprocess.run', return_value=lauf):
            self.assertIn('fehler', e.messe(b'/tmp/kaputt.flac', '/bin/false'))
    def test_zeitueberschreitung_liefert_fehler(self):
        import subprocess
        with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('x', 1)):
            self.assertEqual(e.messe(b'/tmp/lang.wav', '/bin/false')['fehler'], 'zeitueberschreitung')

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 4: Tests laufen lassen, müssen scheitern** — `python -m unittest discover -s tests -v` → `ModuleNotFoundError: energie_merkmale`

- [ ] **Step 5: Modul schreiben**

```python
"""Energie-Rohmerkmale aus Essentia. Misst, rät nicht; Abbildung auf 1–5 folgt nach Eichung."""
import json, os, subprocess, tempfile

def merkmale(j):
    r, t, l = j['rhythm'], j['tonal'], j['lowlevel']
    return {'bpm': float(r['bpm']), 'tonart': '%s %s' % (t['key_edma']['key'], t['key_edma']['scale']),
            'lautheit': float(l['loudness_ebu128']['integrated']), 'tanzbarkeit': float(r['danceability']),
            'anschlagdichte': float(r['onset_rate']), 'dynamik': float(l['loudness_ebu128']['loudness_range'])}

def messe(pfad, binary, timeout=120):
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
```

- [ ] **Step 6: Tests laufen lassen, müssen bestehen** → `OK`

- [ ] **Step 7: Probelauf-Skript** `probelauf_messung.py` — dieselben 200 Titel (Seed `20260930`, gleiche Ziehung wie Task 2), nur Titel mit existierender Datei, **seriell**, Zeit je Titel messen, CSV schreiben, am Ende `ERGEBNIS gemessen=N fehler=N sekunden_median=S bpm_abweichung_ueber_3pct=N`.

```python
import csv, os, random, sqlite3, statistics, sys, time
sys.path.insert(0, '/opt/musikredaktion')
import energie_merkmale as e
BIN = next(os.path.join(w, n) for w, _, ns in os.walk('/opt/essentia') for n in ns if n == 'essentia_streaming_extractor_music')
db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
rows = db.execute('select id, artist, title, length, genre from items').fetchall()
random.seed(20260930)
probe = random.sample(rows, 200)
pfade = dict(db.execute('select id, path from items'))
bpm_b = dict(db.execute('select id, bpm from items'))
zeiten, fehler, abw = [], 0, 0
with open('/root/musikredaktion-probe/messung.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'pfad', 'sekunden', 'bpm', 'bpm_beets', 'tonart', 'lautheit', 'tanzbarkeit', 'anschlagdichte', 'dynamik', 'fehler'])
    for iid, *_ in probe:
        p = pfade[iid]
        p = p if isinstance(p, bytes) else p.encode('utf-8', 'surrogateescape')
        if not os.path.exists(p):
            continue
        t0 = time.time(); m = e.messe(p, BIN); dt = time.time() - t0
        zeiten.append(dt)
        if 'fehler' in m:
            fehler += 1
        elif bpm_b.get(iid) and abs(m['bpm'] - bpm_b[iid]) / bpm_b[iid] > 0.03:
            abw += 1
        w.writerow([iid, p.decode('utf-8', 'surrogateescape'), round(dt, 1), m.get('bpm'), bpm_b.get(iid), m.get('tonart'),
                    m.get('lautheit'), m.get('tanzbarkeit'), m.get('anschlagdichte'), m.get('dynamik'), m.get('fehler', '')])
print('ERGEBNIS gemessen=%d fehler=%d sekunden_median=%.1f bpm_abweichung_ueber_3pct=%d' % (len(zeiten), fehler, statistics.median(zeiten), abw))
```

Ausführen nachts oder mit `nice -n 10`, Hintergrund, Log `/root/musikredaktion-probe/messung.log`.
**Abnahme:** fehler ≤ 5 %; `sekunden_median` → hochgerechnet auf 10.669 Titel entscheidet den Ort (≤ 4 Nächte à 7 h in CT120 → bleibt CT120, sonst OptiPlex).

- [ ] **Step 8: Commit + Push**

---

### Task 4: Ergebnis festhalten

**Files:**
- Modify: `DOCS/superpowers/specs/2026-09-30-frawo-funk-musikredaktion-design.md` (neuer Abschnitt „11. Messergebnis Probelauf“)

- [ ] **Step 1:** Zahlen aus beiden `ERGEBNIS`-Zeilen + Stichprobenbefund in Abschnitt 11 eintragen; Entscheidung „Discogs Hauptquelle ja/nein“ und „Messort CT120/OptiPlex“ mit Begründung.
- [ ] **Step 2:** Odoo #1090 Notiz (Chatter, intern) mit denselben Zahlen; Nachtdienst-Abstimmung mit Jarvis als **eine** gebündelte Erwähnung anfragen.
- [ ] **Step 3:** Commit + Push.
