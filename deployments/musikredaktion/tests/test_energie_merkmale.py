import json, os, subprocess, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import energie_merkmale as e

FIX = os.path.join(os.path.dirname(__file__), 'fixtures', 'essentia_beispiel.json')

class TestMerkmale(unittest.TestCase):
    def test_felder_vorhanden_und_plausibel(self):
        with open(FIX, encoding='utf-8') as f:
            m = e.merkmale(json.load(f))
        self.assertTrue(60 <= m['bpm'] <= 200)
        self.assertEqual(m['tonart'], 'D minor')
        self.assertTrue(0 <= m['lautheit'] <= 1)
        for k in ('tanzbarkeit', 'anschlagdichte', 'dynamik', 'tonart_sicherheit'):
            self.assertIsInstance(m[k], float)

class TestMesse(unittest.TestCase):
    def test_defekte_datei_liefert_fehler_statt_abbruch(self):
        lauf = mock.Mock(returncode=1, stderr=b'Error: cannot decode')
        with mock.patch('subprocess.run', return_value=lauf):
            self.assertIn('fehler', e.messe(b'/tmp/kaputt.flac', '/bin/false'))
    def test_zeitueberschreitung_liefert_fehler(self):
        with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('x', 1)):
            self.assertEqual(e.messe(b'/tmp/lang.wav', '/bin/false')['fehler'], 'zeitueberschreitung')

if __name__ == '__main__':
    unittest.main()
