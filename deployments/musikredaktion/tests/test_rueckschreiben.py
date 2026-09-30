import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rueckschreiben as r

KATALOG = [
    {'id': 1, 'artist': 'A', 'title': 'Song'},
    {'id': 2, 'artist': 'Boris Brejcha', 'title': 'Bells Of Eternity'},
    {'id': 3, 'artist': 'Boris Brejcha', 'title': 'Bells Of Eternity'},  # echte Dublette im Katalog
]


class TestZuordnen(unittest.TestCase):
    def test_eindeutig_gibt_id(self):
        self.assertEqual(r.zuordnen('A|Song', KATALOG), 1)

    def test_zwei_kandidaten_gibt_none(self):
        self.assertIsNone(r.zuordnen('Boris Brejcha|Bells Of Eternity', KATALOG))

    def test_kein_treffer_gibt_none(self):
        self.assertIsNone(r.zuordnen('Unbekannt|Nichts', KATALOG))

    def test_feat_und_mix_werden_normalisiert(self):
        self.assertEqual(r.zuordnen('A feat. X|Song (Original Mix)', KATALOG), 1)

    def test_kaputter_track_id_ohne_trennzeichen(self):
        self.assertIsNone(r.zuordnen('KeinTrennzeichen', KATALOG))

    def test_leerer_track_id(self):
        self.assertIsNone(r.zuordnen('', KATALOG))
        self.assertIsNone(r.zuordnen('|', KATALOG))


class TestAuswerten(unittest.TestCase):
    def test_energie_mittelwert_gerundet(self):
        zeilen = [{'art': 'energie', 'wert': 3}, {'art': 'energie', 'wert': 4}]
        self.assertEqual(r.auswerten(zeilen)['energie'], 4)  # 3.5 -> 4 (kaufmaennisch)

    def test_energie_mittelwert_ohne_rundungsbedarf(self):
        zeilen = [{'art': 'energie', 'wert': 2}, {'art': 'energie', 'wert': 2}, {'art': 'energie', 'wert': 5}]
        self.assertEqual(r.auswerten(zeilen)['energie'], 3)  # 3.0 exakt

    def test_ohne_energie_urteile_ist_energie_none(self):
        zeilen = [{'art': 'passt', 'wert': 1, 'sendung': '06 Deep Night'}]
        self.assertIsNone(r.auswerten(zeilen)['energie'])

    def test_passt_0_sammelt_sendung(self):
        zeilen = [{'art': 'passt', 'wert': 0, 'sendung': '06 Deep Night'},
                  {'art': 'passt', 'wert': 1, 'sendung': '03 Lunch Groove'}]
        self.assertEqual(r.auswerten(zeilen)['passt_nicht'], ['06 Deep Night'])

    def test_passt_0_mehrfach_ohne_duplikat_sortiert(self):
        zeilen = [{'art': 'passt', 'wert': 0, 'sendung': '06 Deep Night'},
                  {'art': 'passt', 'wert': 0, 'sendung': '06 Deep Night'},
                  {'art': 'passt', 'wert': 0, 'sendung': '01 Sunrise'}]
        self.assertEqual(r.auswerten(zeilen)['passt_nicht'], ['01 Sunrise', '06 Deep Night'])

    def test_passt_1_wird_nicht_aufgenommen(self):
        zeilen = [{'art': 'passt', 'wert': 1, 'sendung': '06 Deep Night'}]
        self.assertEqual(r.auswerten(zeilen)['passt_nicht'], [])


class TestMergePasstNicht(unittest.TestCase):
    def test_leerer_bestand(self):
        self.assertEqual(r.merge_passt_nicht('', ['06 Deep Night']), '06 Deep Night')

    def test_haengt_neue_an(self):
        self.assertEqual(r.merge_passt_nicht('01 Sunrise', ['06 Deep Night']), '01 Sunrise, 06 Deep Night')

    def test_kein_duplikat(self):
        self.assertEqual(r.merge_passt_nicht('01 Sunrise, 06 Deep Night', ['06 Deep Night']),
                          '01 Sunrise, 06 Deep Night')

    def test_none_bestand_wie_leer(self):
        self.assertEqual(r.merge_passt_nicht(None, ['06 Deep Night']), '06 Deep Night')


class TestPlanErstellen(unittest.TestCase):
    def test_eindeutiger_titel_wird_verplant(self):
        export = [{'track_id': 'A|Song', 'art': 'energie', 'wert': 5, 'sendung': ''}]
        zuordnungen, offen = r.plan_erstellen(export, KATALOG)
        self.assertEqual(len(zuordnungen), 1)
        self.assertEqual(zuordnungen[0], {'item_id': 1, 'track_id': 'A|Song', 'energie': 5, 'passt_nicht': []})
        self.assertEqual(offen, [])

    def test_mehrdeutiger_titel_nicht_verplant_sondern_offen(self):
        # Review-Fokus: gleicher Artist+Titel mehrfach im Katalog -> nichts schreiben, in Liste aufnehmen.
        export = [{'track_id': 'Boris Brejcha|Bells Of Eternity', 'art': 'energie', 'wert': 3, 'sendung': ''}]
        zuordnungen, offen = r.plan_erstellen(export, KATALOG)
        self.assertEqual(zuordnungen, [])
        self.assertEqual(len(offen), 1)
        self.assertEqual(offen[0]['track_id'], 'Boris Brejcha|Bells Of Eternity')
        self.assertEqual(offen[0]['grund'], 'mehrdeutig')
        self.assertEqual(offen[0]['anzahl_urteile'], 1)

    def test_unbekannter_titel_offen_mit_kein_treffer(self):
        export = [{'track_id': 'Unbekannt|Nichts', 'art': 'energie', 'wert': 3, 'sendung': ''}]
        _, offen = r.plan_erstellen(export, KATALOG)
        self.assertEqual(offen[0]['grund'], 'kein_treffer')

    def test_mehrere_urteile_je_track_werden_gruppiert(self):
        export = [
            {'track_id': 'A|Song', 'art': 'energie', 'wert': 4, 'sendung': ''},
            {'track_id': 'A|Song', 'art': 'energie', 'wert': 2, 'sendung': ''},
            {'track_id': 'A|Song', 'art': 'passt', 'wert': 0, 'sendung': '06 Deep Night'},
        ]
        zuordnungen, offen = r.plan_erstellen(export, KATALOG)
        self.assertEqual(len(zuordnungen), 1)
        self.assertEqual(zuordnungen[0]['energie'], 3)
        self.assertEqual(zuordnungen[0]['passt_nicht'], ['06 Deep Night'])
        self.assertEqual(offen, [])


class TestCsvSchreiben(unittest.TestCase):
    def test_schreibt_semikolon_csv(self):
        import csv, tempfile
        offen = [{'track_id': 'A|Song', 'grund': 'mehrdeutig', 'anzahl_urteile': 2}]
        with tempfile.TemporaryDirectory() as tmp:
            pfad = os.path.join(tmp, 'unterordner', 'offen.csv')
            r.csv_schreiben(offen, pfad)
            with open(pfad, encoding='utf-8') as f:
                zeilen = list(csv.reader(f, delimiter=';'))
        self.assertEqual(zeilen[0], ['track_id', 'grund', 'anzahl_urteile'])
        self.assertEqual(zeilen[1], ['A|Song', 'mehrdeutig', '2'])


class TestTokenLesen(unittest.TestCase):
    def test_liest_wert_hinter_gleichheitszeichen(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            pfad = os.path.join(tmp, 'odoo.env')
            with open(pfad, 'w', encoding='utf-8') as f:
                f.write('ODOO_EXPORT_TOKEN=geheim123\n')
            self.assertEqual(r.token_lesen(pfad), 'geheim123')


class TestSichern(unittest.TestCase):
    def test_kopiert_db_mit_datum_im_namen(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            quelle = os.path.join(tmp, 'musik.db')
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('inhalt')
            ziel = r.sichern(quelle, datum='2026-09-30')
            self.assertEqual(ziel, quelle + '.vor-rueckschreiben-2026-09-30')
            self.assertTrue(os.path.exists(ziel))
            with open(ziel, encoding='utf-8') as f:
                self.assertEqual(f.read(), 'inhalt')


if __name__ == '__main__':
    unittest.main()
