import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cover_ersatz as ce

try:
    import mutagen
    import mutagen.id3
    import mutagen.flac
    MUTAGEN_VERFUEGBAR = True
except ImportError:
    MUTAGEN_VERFUEGBAR = False

try:
    from PIL import Image
    # 1x1 Pixel Dummy PNG & JPEG
    img = Image.new('RGB', (10, 10), color='red')
    buf_png = io.BytesIO()
    img.save(buf_png, format='PNG')
    DUMMY_PNG = buf_png.getvalue()

    buf_jpg = io.BytesIO()
    img.save(buf_jpg, format='JPEG')
    DUMMY_JPG = buf_jpg.getvalue()
except ImportError:
    DUMMY_PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 120
    DUMMY_JPG = b'\xff\xd8\xff\xe0' + b'\x00' * 120


class TestBildValidierung(unittest.TestCase):
    def test_gueltiges_png(self):
        gueltig, mime = ce.ist_gueltiges_bild(DUMMY_PNG)
        self.assertTrue(gueltig)
        self.assertEqual(mime, 'image/png')

    def test_gueltiges_jpeg(self):
        gueltig, mime = ce.ist_gueltiges_bild(DUMMY_JPG)
        self.assertTrue(gueltig)
        self.assertEqual(mime, 'image/jpeg')

    def test_ungueltige_bytes(self):
        gueltig, mime = ce.ist_gueltiges_bild(b'<html>404 Not Found</html>')
        self.assertFalse(gueltig)
        self.assertEqual(mime, '')

    def test_zu_kurze_bytes(self):
        gueltig, mime = ce.ist_gueltiges_bild(b'\xff\xd8\xff')
        self.assertFalse(gueltig)


class TestBackup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sichere_original_bild(self):
        h = ce.bild_hash(DUMMY_PNG)
        pfad = ce.sichere_original_bild(DUMMY_PNG, backup_dir=self.tmp)
        self.assertTrue(os.path.exists(pfad))
        self.assertIn(h, pfad)
        with open(pfad, 'rb') as f:
            self.assertEqual(f.read(), DUMMY_PNG)


@unittest.skipUnless(MUTAGEN_VERFUEGBAR, "mutagen wird für MP3/FLAC Tests benötigt")
class TestCoverOperationen(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _erstelle_dummy_mp3(self):
        pfad = os.path.join(self.tmp, 'test.mp3')
        # Minimaler MP3 Frame
        with open(pfad, 'wb') as f:
            f.write(b'\xff\xfb\x90\x00' + b'\x00' * 1000)
        id3 = mutagen.id3.ID3()
        id3.save(pfad)
        return pfad

    def _erstelle_dummy_flac(self):
        pfad = os.path.join(self.tmp, 'test.flac')
        # Minimaler FLAC Header mit gueltiger Sample-Rate (44100 Hz, 16 Bit, 2 Kanäle)
        with open(pfad, 'wb') as f:
            f.write(b'fLaC\x80\x00\x00\x22\x10\x00\x10\x00\x00\x00\x00\x00\x00\x00\x0a\xc4\x42\xf0' + b'\x00' * 20)
        return pfad

    def test_mp3_cover_setzen_und_entfernen(self):
        mp3 = self._erstelle_dummy_mp3()
        # Vorher: kein Bild
        self.assertIsNone(ce.eingebettetes_bild(mp3))

        # Setzen
        ce.ersetze_cover(mp3, DUMMY_PNG, 'image/png')
        bild = ce.eingebettetes_bild(mp3)
        self.assertIsNotNone(bild)
        self.assertEqual(bild[0], DUMMY_PNG)
        self.assertEqual(bild[1], 'image/png')

        # Entfernen
        ce.entferne_cover(mp3)
        self.assertIsNone(ce.eingebettetes_bild(mp3))

    def test_flac_cover_setzen_und_entfernen(self):
        flac = self._erstelle_dummy_flac()
        self.assertIsNone(ce.eingebettetes_bild(flac))

        # Setzen
        ce.ersetze_cover(flac, DUMMY_JPG, 'image/jpeg')
        bild = ce.eingebettetes_bild(flac)
        self.assertIsNotNone(bild)
        self.assertEqual(bild[0], DUMMY_JPG)
        self.assertEqual(bild[1], 'image/jpeg')

        # Entfernen
        ce.entferne_cover(flac)
        self.assertIsNone(ce.eingebettetes_bild(flac))

    def test_putze_datei_tags(self):
        mp3 = self._erstelle_dummy_mp3()
        id3 = mutagen.id3.ID3(mp3)
        # Werbe-Link und sauberer Tag
        id3.add(mutagen.id3.WXXX(encoding=3, desc='Website', url='https://djsoundtop.com'))
        id3.add(mutagen.id3.COMM(encoding=3, lang='eng', desc='', text='Exclusive on www.djsoundtop.com'))
        id3.add(mutagen.id3.TIT2(encoding=3, text='Sauberer Track Titel'))
        id3.save(mp3)

        entfernt = ce.putze_datei_tags(mp3)
        self.assertTrue(len(entfernt) >= 2)

        # Verifikation: Werbe-Tags weg, Titel bleibt
        nachher = mutagen.id3.ID3(mp3)
        self.assertEqual(str(nachher['TIT2']), 'Sauberer Track Titel')
        self.assertFalse(any(k.startswith('W') for k in nachher.keys()))
        self.assertFalse(any('djsoundtop' in str(v) for v in nachher.values()))


@unittest.skipUnless(MUTAGEN_VERFUEGBAR, "mutagen wird benötigt")
class TestBearbeiteKandidat(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.tmp, 'backups')
        self.cache_dir = os.path.join(self.tmp, 'cache')
        self.log_pfad = os.path.join(self.tmp, 'aenderungen.jsonl')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _erstelle_mp3_mit_bild(self, bild_daten, mime='image/png'):
        pfad = os.path.join(self.tmp, f"track_{time.time()}.mp3")
        with open(pfad, 'wb') as f:
            f.write(b'\xff\xfb\x90\x00' + b'\x00' * 1000)
        id3 = mutagen.id3.ID3()
        id3.add(mutagen.id3.APIC(encoding=3, mime=mime, type=3, desc='Cover', data=bild_daten))
        id3.save(pfad)
        return pfad

    def test_dry_run_aendert_nichts(self):
        mp3 = self._erstelle_mp3_mit_bild(DUMMY_PNG)
        original_hash = ce.bild_hash(DUMMY_PNG)
        kandidat = {
            'pfad': mp3,
            'ersatzquelle': 'https://example.com/cover.jpg',
            'ocr_bestaetigt': False
        }

        res = ce.bearbeite_kandidat(kandidat, anwenden=False,
                                    backup_dir=self.backup_dir,
                                    cache_dir=self.cache_dir,
                                    log_pfad=self.log_pfad)

        self.assertEqual(res['status'], 'dry_run_ersetzen')
        # Datei unverändert
        self.assertEqual(ce.bild_hash(ce.eingebettetes_bild(mp3)[0]), original_hash)
        # Kein Log und kein Backup geschrieben
        self.assertFalse(os.path.exists(self.log_pfad))
        self.assertFalse(os.path.exists(self.backup_dir))

    @mock.patch('cover_ersatz.lade_bild_aus_url')
    def test_live_ersetzen_erfolgreich(self, mock_lade):
        mock_lade.return_value = (DUMMY_JPG, 'image/jpeg')
        mp3 = self._erstelle_mp3_mit_bild(DUMMY_PNG)

        kandidat = {
            'pfad': mp3,
            'ersatzquelle': 'https://example.com/cover.jpg',
            'ocr_bestaetigt': True
        }

        res = ce.bearbeite_kandidat(kandidat, anwenden=True,
                                    backup_dir=self.backup_dir,
                                    cache_dir=self.cache_dir,
                                    log_pfad=self.log_pfad)

        self.assertEqual(res['status'], 'ersetzt')
        # Bild in Datei ist jetzt das neue JPG
        aktuell = ce.eingebettetes_bild(mp3)
        self.assertEqual(aktuell[0], DUMMY_JPG)
        # Backup des alten PNGs existiert
        self.assertTrue(os.path.exists(os.path.join(self.backup_dir, f"{ce.bild_hash(DUMMY_PNG)}.png")))
        # Logfile geschrieben
        self.assertTrue(os.path.exists(self.log_pfad))
        with open(self.log_pfad, 'r', encoding='utf-8') as f:
            eintrag = json.loads(f.readline())
            self.assertEqual(eintrag['aktion'], 'ersetzt')
            self.assertEqual(eintrag['pfad'], mp3)

    def test_live_entfernen_wenn_ohne_ersatz(self):
        mp3 = self._erstelle_mp3_mit_bild(DUMMY_PNG)

        kandidat = {
            'pfad': mp3,
            'ersatzquelle': '',
            'ocr_bestaetigt': True
        }

        res = ce.bearbeite_kandidat(kandidat, anwenden=True,
                                    entfernen_wenn_ohne_ersatz=True,
                                    backup_dir=self.backup_dir,
                                    cache_dir=self.cache_dir,
                                    log_pfad=self.log_pfad)

        self.assertEqual(res['status'], 'entfernt')
        self.assertIsNone(ce.eingebettetes_bild(mp3))
        # Backup existiert
        self.assertTrue(os.path.exists(os.path.join(self.backup_dir, f"{ce.bild_hash(DUMMY_PNG)}.png")))


if __name__ == '__main__':
    unittest.main()
