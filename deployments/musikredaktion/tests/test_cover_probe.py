import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cover_probe as cp


class TestGruppieren(unittest.TestCase):
    def test_zaehlt_dateien_und_eindeutige_alben(self):
        eintraege = [
            {'hash': 'h1', 'album': 'Album A'},
            {'hash': 'h1', 'album': 'Album A'},  # zweiter Titel desselben Albums
            {'hash': 'h1', 'album': 'Album B'},
        ]
        g = cp.gruppieren(eintraege)
        self.assertEqual(g['h1']['anzahl_dateien'], 3)
        self.assertEqual(g['h1']['alben'], {'Album A', 'Album B'})  # Album A nur einmal

    def test_ohne_bild_wird_ignoriert(self):
        eintraege = [{'hash': '', 'album': 'X'}, {'hash': None, 'album': 'Y'}]
        self.assertEqual(cp.gruppieren(eintraege), {})

    def test_leeres_album_wird_als_unbekannt_gezaehlt(self):
        eintraege = [{'hash': 'h1', 'album': ''}, {'hash': 'h1', 'album': None}]
        g = cp.gruppieren(eintraege)
        self.assertEqual(g['h1']['alben'], {'(unbekannt)'})

    def test_mehrere_hashes_getrennt(self):
        eintraege = [{'hash': 'h1', 'album': 'A'}, {'hash': 'h2', 'album': 'B'}]
        g = cp.gruppieren(eintraege)
        self.assertEqual(set(g.keys()), {'h1', 'h2'})


class TestKandidatenBestimmen(unittest.TestCase):
    def _eintraege(self, hash_alben):
        """hash_alben: {hash: [album, album, ...]} -> eine Zeile je Eintrag."""
        out = []
        for h, alben in hash_alben.items():
            for i, album in enumerate(alben):
                out.append({'item_id': len(out), 'pfad': '/x/%s-%d' % (h, i), 'artist': 'A',
                            'album': album, 'title': 'T', 'hash': h, 'mime': 'image/jpeg',
                            'groesse_bytes': 100, 'breite': 500, 'hoehe': 500})
        return out

    def test_unter_schwelle_kein_kandidat(self):
        eintraege = self._eintraege({'h1': ['Alb1', 'Alb2', 'Alb3']})  # 3 Alben, Schwelle 5
        self.assertEqual(cp.kandidaten_bestimmen(eintraege, schwelle_alben=5), [])

    def test_ab_schwelle_ist_kandidat(self):
        eintraege = self._eintraege({'h1': ['A1', 'A2', 'A3', 'A4', 'A5']})
        k = cp.kandidaten_bestimmen(eintraege, schwelle_alben=5)
        self.assertEqual(len(k), 5)
        self.assertEqual(k[0]['albenzahl'], 5)
        self.assertFalse(k[0]['ocr_bestaetigt'])
        self.assertIn('Verdacht', k[0]['grund'])

    def test_ohne_bild_nie_kandidat_auch_nicht_bei_vielen_zeilen(self):
        eintraege = [{'item_id': i, 'pfad': '/x/%d' % i, 'artist': 'A', 'album': 'Alb%d' % i,
                      'title': 'T', 'hash': '', 'mime': '', 'groesse': 0, 'breite': None, 'hoehe': None}
                     for i in range(10)]
        self.assertEqual(cp.kandidaten_bestimmen(eintraege, schwelle_alben=5), [])

    def test_ocr_bestaetigung_aendert_grund_text(self):
        eintraege = self._eintraege({'h1': ['A1', 'A2', 'A3', 'A4', 'A5']})
        k = cp.kandidaten_bestimmen(eintraege, schwelle_alben=5, ocr={'h1': 'www.djsoundtop.com Exclusive'})
        self.assertTrue(all(x['ocr_bestaetigt'] for x in k))
        self.assertIn('bestätigt', k[0]['grund'])

    def test_mehrere_hashes_nur_der_haeufige_wird_kandidat(self):
        eintraege = self._eintraege({
            'h_selten': ['A1', 'A2'],                       # unter Schwelle
            'h_haeufig': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6'],
        })
        k = cp.kandidaten_bestimmen(eintraege, schwelle_alben=5)
        self.assertEqual({x['hash'] for x in k}, {'h_haeufig'})


class TestPfadeEntdoppeln(unittest.TestCase):
    def test_zwei_zeilen_gleicher_pfad_werden_eine(self):
        eintraege = [
            {'pfad': '/x/a.mp3', 'album': '', 'hash': 'h1'},
            {'pfad': '/x/a.mp3', 'album': 'Echtes Album', 'hash': 'h1'},
        ]
        out = cp.pfade_entdoppeln(eintraege)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['album'], 'Echtes Album')  # das vollere Feld gewinnt

    def test_erste_zeile_behalten_wenn_beide_album_haben(self):
        eintraege = [
            {'pfad': '/x/a.mp3', 'album': 'Zuerst', 'hash': 'h1'},
            {'pfad': '/x/a.mp3', 'album': 'Zweitens', 'hash': 'h1'},
        ]
        out = cp.pfade_entdoppeln(eintraege)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['album'], 'Zuerst')

    def test_unterschiedliche_pfade_bleiben_beide(self):
        eintraege = [{'pfad': '/x/a.mp3', 'album': 'A'}, {'pfad': '/x/b.mp3', 'album': 'B'}]
        self.assertEqual(len(cp.pfade_entdoppeln(eintraege)), 2)

    def test_reihenfolge_bleibt_erhalten(self):
        eintraege = [{'pfad': '/x/b.mp3', 'album': 'B'}, {'pfad': '/x/a.mp3', 'album': 'A'}]
        out = cp.pfade_entdoppeln(eintraege)
        self.assertEqual([e['pfad'] for e in out], ['/x/b.mp3', '/x/a.mp3'])


class TestOcrVerdaechtig(unittest.TestCase):
    def test_bekannte_werbequelle_erkannt(self):
        self.assertTrue(cp.ocr_verdaechtig('Download more at www.djsoundtop.com Exclusive'))

    def test_generisches_werbewort_erkannt(self):
        self.assertTrue(cp.ocr_verdaechtig('PROMO ONLY - not for resale'))

    def test_harmloser_text_nicht_verdaechtig(self):
        self.assertFalse(cp.ocr_verdaechtig('Boris Brejcha Live in Berlin'))

    def test_leerer_text_nicht_verdaechtig(self):
        self.assertFalse(cp.ocr_verdaechtig(''))
        self.assertFalse(cp.ocr_verdaechtig(None))

    def test_gross_kleinschreibung_egal(self):
        self.assertTrue(cp.ocr_verdaechtig('MUZHOUSEBEAT.COM'))


class TestBildUrlSuchen(unittest.TestCase):
    def test_findet_url_in_verschachteltem_dict(self):
        objekt = {'release': {'image': {'uri': 'https://img.example.com/cover.jpg'}}}
        self.assertEqual(cp.bild_url_suchen(objekt), 'https://img.example.com/cover.jpg')

    def test_discogs_artige_struktur(self):
        objekt = {'results': [{'cover_image': 'https://discogs.example/abc.png', 'title': 'X - Y'}]}
        self.assertEqual(cp.bild_url_suchen(objekt), 'https://discogs.example/abc.png')

    def test_ohne_bild_leerer_string(self):
        self.assertEqual(cp.bild_url_suchen({'name': 'kein Bild hier'}), '')
        self.assertEqual(cp.bild_url_suchen([]), '')
        self.assertEqual(cp.bild_url_suchen(None), '')

    def test_platzhalter_werden_ersetzt(self):
        objekt = {'image': {'dynamic_uri': 'https://img.example.com/{w}x{h}/cover.jpg'}}
        self.assertEqual(cp.bild_url_suchen(objekt), 'https://img.example.com/500x500/cover.jpg')

    def test_text_ohne_bildendung_wird_nicht_als_url_genommen(self):
        objekt = {'uri': '/release/12345'}
        self.assertEqual(cp.bild_url_suchen(objekt), '')


class TestCsvRundtrip(unittest.TestCase):
    # Regressionstest: ein Feld im Eintrags-Dict hieß 'groesse' statt
    # 'groesse_bytes' (CSV_FELDER) -- csv_schreiben schrieb dadurch beim
    # echten Lauf 10.669x eine leere Größe, ohne dass irgendwo ein Fehler
    # auftrat (csv.DictWriter füllt fehlende Felder einfach mit '').
    def test_alle_felder_kommen_in_der_csv_an(self):
        zeile = {'pfad': '/x/a.mp3', 'hash': 'h1', 'grund': 'Testgrund', 'albenzahl': 7,
                  'ocr_bestaetigt': True, 'artist': 'A', 'title': 'T', 'album': 'Alb',
                  'breite': 500, 'hoehe': 500, 'groesse_bytes': 12345, 'mime': 'image/jpeg',
                  'ersatzquelle': ''}
        with tempfile.TemporaryDirectory() as d:
            pfad = os.path.join(d, 'kandidaten.csv')
            cp.csv_schreiben([zeile], pfad=pfad)
            zurueck = cp.csv_lesen(pfad=pfad)
        self.assertEqual(len(zurueck), 1)
        self.assertEqual(zurueck[0]['groesse_bytes'], '12345')
        self.assertEqual(zurueck[0]['breite'], '500')
        self.assertEqual(zurueck[0]['grund'], 'Testgrund')

    def test_fehlendes_feld_wird_leer_statt_fehler(self):
        with tempfile.TemporaryDirectory() as d:
            pfad = os.path.join(d, 'kandidaten.csv')
            cp.csv_schreiben([{'pfad': '/x/a.mp3'}], pfad=pfad)
            zurueck = cp.csv_lesen(pfad=pfad)
        self.assertEqual(zurueck[0]['groesse_bytes'], '')


if __name__ == '__main__':
    unittest.main()
