import json, os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

class TestSuchbegriffe(unittest.TestCase):
    def test_beiwerk_weg(self):
        self.assertEqual(d.suchbegriffe({'artist': 'Boris Brejcha', 'title': 'Bells Of Eternity (Original Mix) 125'}),
                         ('Boris Brejcha', 'Bells Of Eternity'))
    def test_interpret_im_titel_und_liste(self):
        self.assertEqual(d.suchbegriffe({'artist': 'CHIC', 'title': 'CHIC - Everybody Dance (4NEY Edit)'}),
                         ('CHIC', 'Everybody Dance'))
        self.assertEqual(d.suchbegriffe({'artist': 'Damian Cotto, Marcos Calegari', 'title': 'Brooklyn Mambo  (Roudkav Remix)'}),
                         ('Damian Cotto', 'Brooklyn Mambo'))
        self.assertEqual(d.suchbegriffe({'artist': 'Sted-E & Hybrid Heights, Mr. V', 'title': 'Home'})[0], 'Sted-E')

class TestMehrheit(unittest.TestCase):
    def test_klare_mehrheit_ist_belegt(self):
        t = [{'id': i, 'type': 'release', 'title': 'Commodores - Brick House', 'genre': ['Funk / Soul'],
              'style': s, 'uri': '/release/%d' % i}
             for i, s in enumerate([['Funk'], ['Funk', 'Disco'], ['Funk'], ['Soul']])]
        r = d.bewerte({'artist': 'Commodores', 'title': 'Brick House (live)', 'length': 0}, t)
        self.assertEqual((r['status'], r['styles']), ('belegt', ['Funk']))
    def test_haelfte_reicht_nicht(self):
        t = [{'id': i, 'type': 'release', 'title': 'BK - Flash', 'genre': ['Electronic'], 'style': s, 'uri': '/release/%d' % i}
             for i, s in enumerate([['Hard House'], ['Trance']])]
        self.assertEqual(d.bewerte({'artist': 'BK', 'title': 'Flash', 'length': 0}, t)['status'], 'widerspruch')

class TestBewerteRemix(unittest.TestCase):
    def test_remix_ep_zaehlt_ueber_interpret(self):
        t = [{'id': 5, 'type': 'release', 'title': 'Depeche Mode - Cover Me [Remixes]', 'genre': ['Electronic'],
              'style': ['House', 'Synth-pop', 'Techno'], 'uri': '/release/5'}]
        r = d.bewerte({'artist': 'Depeche Mode', 'title': 'Cover Me (Dixon remix)', 'length': 400.0}, t)
        self.assertEqual(r['status'], 'belegt')

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
