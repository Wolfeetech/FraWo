import os, sqlite3, sys, tempfile, unittest
from unittest import mock
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


class TestDbSichern(unittest.TestCase):
    def test_kopiert_db_mit_datum_im_namen_und_gleichem_inhalt(self):
        # Minor-Fix: sqlite3-Online-Backup-API statt shutil.copy2 -> Inhalt
        # ueber eine echte sqlite-Abfrage pruefen, nicht per Byte-Vergleich.
        with tempfile.TemporaryDirectory() as tmp:
            quelle = os.path.join(tmp, 'musik.db')
            c = sqlite3.connect(quelle)
            c.execute('create table items (id integer, titel text)')
            c.execute('insert into items values (1, "Testtitel")')
            c.commit()
            c.close()
            ziel = r.db_sichern(quelle, datum='2026-09-30')
            self.assertEqual(ziel, quelle + '.vor-rueckschreiben-2026-09-30')
            self.assertTrue(os.path.exists(ziel))
            z = sqlite3.connect(ziel)
            zeile = z.execute('select id, titel from items').fetchone()
            z.close()
            self.assertEqual(zeile, (1, 'Testtitel'))


class _FakeItem:
    """Minimales, beets-freies Double für item.get/Attributzugriff/store()."""
    def __init__(self, **felder):
        object.__setattr__(self, '_werte', dict(felder))
        object.__setattr__(self, 'gespeichert', 0)

    def get(self, key, default=None):
        return self._werte.get(key, default)

    def __setattr__(self, name, value):
        self._werte[name] = value

    def __getattr__(self, name):
        try:
            return self._werte[name]
        except KeyError:
            raise AttributeError(name)

    def store(self):
        object.__setattr__(self, 'gespeichert', self.gespeichert + 1)


class _FakeLib:
    def __init__(self, items_by_id):
        self._items = items_by_id

    def get_item(self, item_id):
        return self._items.get(item_id)


class TestMacherSpeichern(unittest.TestCase):
    def test_schreibt_und_zaehlt_bei_aenderung(self):
        item = _FakeItem()
        speichern = r._macher_speichern(_FakeLib({1: item}), '2026-10-01')
        self.assertTrue(speichern(1, 4, ['06 Deep Night']))
        self.assertEqual(item.gespeichert, 1)
        self.assertEqual(item.get('energie'), 4)
        self.assertEqual(item.get('quelle_energie'), 'Redaktion 2026-10-01')
        self.assertEqual(item.get('passt_nicht'), '06 Deep Night')

    def test_keine_aenderung_kein_store_und_zaehlt_nicht(self):
        # Wichtig-Befund 2: nur speichern/zaehlen, wenn sich etwas aendert.
        item = _FakeItem(energie='4', quelle_energie='Redaktion 2026-10-01', passt_nicht='')
        speichern = r._macher_speichern(_FakeLib({1: item}), '2026-10-01')
        self.assertFalse(speichern(1, 4, []))
        self.assertEqual(item.gespeichert, 0)

    def test_nur_passt_1_urteile_lassen_energie_unveraendert(self):
        item = _FakeItem(energie='3', quelle_energie='Redaktion 2026-09-20', passt_nicht='')
        speichern = r._macher_speichern(_FakeLib({1: item}), '2026-10-01')
        self.assertFalse(speichern(1, None, []))
        self.assertEqual(item.gespeichert, 0)
        self.assertEqual(item.get('energie'), '3')

    def test_passt_nicht_wird_gesetzt_nicht_gemergt(self):
        # Controller-Entscheidung: SETZEN, nicht mergen.
        item = _FakeItem(passt_nicht='06 Deep Night')
        speichern = r._macher_speichern(_FakeLib({1: item}), '2026-10-01')
        self.assertTrue(speichern(1, None, ['01 Sunrise']))
        self.assertEqual(item.get('passt_nicht'), '01 Sunrise')  # ersetzt, nicht angehaengt

    def test_passt_nicht_wird_bei_leerer_liste_geleert(self):
        item = _FakeItem(passt_nicht='06 Deep Night')
        speichern = r._macher_speichern(_FakeLib({1: item}), '2026-10-01')
        self.assertTrue(speichern(1, None, []))
        self.assertEqual(item.get('passt_nicht'), '')

    def test_item_verschwunden_gibt_none(self):
        speichern = r._macher_speichern(_FakeLib({}), '2026-10-01')
        self.assertIsNone(speichern(999, 4, []))


class TestLauf(unittest.TestCase):
    EXPORT = [{'track_id': 'A|Song', 'art': 'energie', 'wert': 5, 'sendung': ''}]

    def test_sichern_laeuft_vor_jedem_speichern(self):
        reihenfolge = []
        sichern = mock.Mock(side_effect=lambda: reihenfolge.append('sichern'))
        speichern = mock.Mock(side_effect=lambda *a: (reihenfolge.append('speichern'), True)[1])
        csv_schreiben = mock.Mock()
        r.lauf(self.EXPORT, KATALOG, sichern, csv_schreiben, speichern, probe=False)
        self.assertEqual(reihenfolge, ['sichern', 'speichern'])

    def test_probe_ruft_weder_sichern_noch_speichern_noch_csv(self):
        sichern, speichern, csv_schreiben = mock.Mock(), mock.Mock(), mock.Mock()
        ergebnis = r.lauf(self.EXPORT, KATALOG, sichern, csv_schreiben, speichern, probe=True)
        sichern.assert_not_called()
        speichern.assert_not_called()
        csv_schreiben.assert_not_called()
        self.assertEqual(len(ergebnis['zuordnungen']), 1)

    def test_sichern_laeuft_auch_ohne_zuordnungen(self):
        # Sicherung vor dem Lauf, nicht nur vor tatsaechlichen Treffern.
        sichern, speichern, csv_schreiben = mock.Mock(), mock.Mock(), mock.Mock()
        r.lauf([], KATALOG, sichern, csv_schreiben, speichern, probe=False)
        sichern.assert_called_once()
        speichern.assert_not_called()
        csv_schreiben.assert_not_called()

    def test_speichern_false_zaehlt_nicht_als_geschrieben(self):
        sichern, csv_schreiben = mock.Mock(), mock.Mock()
        speichern = mock.Mock(return_value=False)
        ergebnis = r.lauf(self.EXPORT, KATALOG, sichern, csv_schreiben, speichern, probe=False)
        self.assertEqual(ergebnis['geschrieben'], 0)
        csv_schreiben.assert_not_called()  # nichts offen, nichts verschwunden

    def test_verschwundenes_item_landet_in_offen_csv_statt_stillem_ueberspringen(self):
        sichern, csv_schreiben = mock.Mock(), mock.Mock()
        speichern = mock.Mock(return_value=None)
        ergebnis = r.lauf(self.EXPORT, KATALOG, sichern, csv_schreiben, speichern, probe=False)
        self.assertEqual(ergebnis['geschrieben'], 0)
        self.assertTrue(any(o['grund'] == 'item_verschwunden' for o in ergebnis['offen']))
        csv_schreiben.assert_called_once()
        offen_arg = csv_schreiben.call_args[0][0]
        self.assertTrue(any(o['grund'] == 'item_verschwunden' for o in offen_arg))

    def test_mehrdeutige_und_unbekannte_landen_ebenfalls_in_csv(self):
        export = [{'track_id': 'Boris Brejcha|Bells Of Eternity', 'art': 'energie', 'wert': 3, 'sendung': ''}]
        sichern, speichern, csv_schreiben = mock.Mock(), mock.Mock(), mock.Mock()
        ergebnis = r.lauf(export, KATALOG, sichern, csv_schreiben, speichern, probe=False)
        speichern.assert_not_called()
        csv_schreiben.assert_called_once_with(ergebnis['offen'])


if __name__ == '__main__':
    unittest.main()
