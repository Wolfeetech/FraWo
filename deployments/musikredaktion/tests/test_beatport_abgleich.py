import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import beatport_abgleich as b

def tr(i, artist, name, mix, genre, sub=None, bpm=125, key='G Major'):
    return {'id': i, 'name': name, 'mix_name': mix, 'artists': [{'name': artist}],
            'genre': {'name': genre}, 'sub_genre': {'name': sub} if sub else None,
            'bpm': bpm, 'key': {'name': key}, 'slug': 'x'}

class TestBewerteBeatport(unittest.TestCase):
    def test_eindeutig(self):
        t = [tr(1, 'Boris Brejcha', 'Bells Of Eternity', 'Original Mix', 'Techno (Peak Time / Driving)'),
             tr(2, 'Chris Avantgarde', 'Eternity', 'Extended Mix', 'Melodic House & Techno')]
        r = b.bewerte({'artist': 'Boris Brejcha', 'title': 'Bells Of Eternity (Original Mix) 125'}, t)
        self.assertEqual(r['status'], 'belegt')
        self.assertEqual(r['styles'], ['Techno (Peak Time / Driving)'])
        self.assertEqual((r['bpm'], r['tonart']), (125, 'G Major'))
        self.assertTrue(r['quelle'].startswith('https://www.beatport.com/track/x/1'))
    def test_untergenre_kommt_mit(self):
        t = [tr(1, 'Greg Downey', 'Invaders', 'Extended Mix', 'Trance (Main Floor)', 'Tech Trance', 140)]
        r = b.bewerte({'artist': 'Greg Downey', 'title': 'Invaders (extended mix)'}, t)
        self.assertEqual(r['styles'], ['Trance (Main Floor)', 'Tech Trance'])
    def test_passender_mix_gewinnt(self):
        t = [tr(1, 'Greg Downey', 'Invaders', 'Extended Mix', 'Trance (Main Floor)'),
             tr(2, 'Greg Downey', 'Invaders', 'Radio Edit', 'Mainstage')]
        self.assertEqual(b.bewerte({'artist': 'Greg Downey', 'title': 'Invaders (Extended Mix)'}, t)['styles'][0], 'Trance (Main Floor)')
    def test_verschiedene_genres_ohne_mixhinweis_widerspruch(self):
        t = [tr(1, 'Greg Downey', 'Invaders', 'Extended Mix', 'Trance (Main Floor)'),
             tr(2, 'Greg Downey', 'Invaders', 'Extended Mix', 'Mainstage')]
        self.assertEqual(b.bewerte({'artist': 'Greg Downey', 'title': 'Invaders'}, t)['status'], 'widerspruch')
    def test_fremder_titel_unklar(self):
        t = [tr(1, 'Pushing Boundaries', "Keep It Goin'", 'Matt Shrewd Remix', 'Jackin House')]
        self.assertEqual(b.bewerte({'artist': 'Perky Wires', 'title': "Keep It Goin' On"}, t)['status'], 'unklar')
    def test_ohne_treffer_unklar(self):
        self.assertEqual(b.bewerte({'artist': 'A', 'title': 'B'}, [])['status'], 'unklar')

if __name__ == '__main__':
    unittest.main()
