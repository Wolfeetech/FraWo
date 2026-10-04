"""Tests fuer radio_titel_putzen.py - Beispiele echt aus der Bibliothek (04.10.2026)."""
import unittest

from radio_titel_putzen import putze_titel, putze_kuenstler, braucht_nacharbeit


class TestTitel(unittest.TestCase):
    def t(self, alt, neu, kuenstler=''):
        self.assertEqual(putze_titel(alt, kuenstler), neu)

    def test_original_mix_faellt_weg(self):
        self.t("'96 (Original Mix)", "'96")
        self.t('10+1 (Orginal Mix)', '10+1')

    def test_andere_versionen_bleiben(self):
        self.t('45th Street (Extended Mix)', '45th Street (Extended Mix)')
        self.t('Bring The Funk Back (Radio Edit)', 'Bring The Funk Back (Radio Edit)')
        self.t("'68 (Hot X Intervamp remix)", "'68 (Hot X Intervamp Remix)")

    def test_bpm_am_ende(self):
        self.t('2 Ice (Original Mix) 130', '2 Ice')
        self.t('Enne (Br) (Original Mix) 131', 'Enne (Br)')
        self.t('All Day (Radio Edit) 127', 'All Day (Radio Edit)')

    def test_zahl_im_titel_bleibt(self):
        self.t('2 Ice', '2 Ice')
        self.t('Area 51', 'Area 51')
        self.t('Track 101', 'Track 101')
        self.t('45th Street', '45th Street')

    def test_doppelte_leerzeichen(self):
        self.t('2 My People  (Original Mix)', '2 My People')

    def test_doppelung_mit_semikolon(self):
        self.t('Alternative Reality; Alternative Reality', 'Alternative Reality')
        self.t("'68 (Hot X Intervamp remix); Don't Touch Orig", "'68 (Hot X Intervamp Remix)")

    def test_feat(self):
        self.t('Ambifoco feat. Verico (Original Mix)', 'Ambifoco (feat. Verico)')
        self.t('Song ft. Someone', 'Song (feat. Someone)')
        self.t('Song (feat. Someone)', 'Song (feat. Someone)')
        self.t('Song (Extended Mix) feat. X', 'Song (feat. X) (Extended Mix)')

    def test_tracknummer_vorne(self):
        self.t('01 - Opening', 'Opening')
        self.t('00 Breathe', 'Breathe')
        self.t('2 Ice', '2 Ice')

    def test_rip_vermerke_und_endung(self):
        self.t('Now Is The Time [VINYL RIP]', 'Now Is The Time')
        self.t('RA.843 Nosedrip.mp3', 'RA.843 Nosedrip')
        self.t('Track [Free Download]', 'Track')
        self.t('Track [Remastered]', 'Track [Remastered]')

    def test_kuenstler_im_titel(self):
        self.t('Nicholas - Now Is The Time', 'Now Is The Time', 'Nicholas')
        self.t('Other Guy - Now Is The Time', 'Other Guy - Now Is The Time', 'Nicholas')

    def test_unterstriche(self):
        self.t('now_is_the_time', 'now is the time')

    def test_versionsklammer_einheitlich_gross(self):
        self.t('We Are the Young (club version)', 'We Are the Young (Club Version)')
        self.t('Power of One (extended mix)', 'Power of One (Extended Mix)')
        self.t('Shadow Dancing (special disco version)', 'Shadow Dancing (Special Disco Version)')
        self.t('Rhythm Is a Dancer (12″ mix)', 'Rhythm Is a Dancer (12″ Mix)')
        self.t('Joris (Ita) (Excit Remix) 130', 'Joris (Ita) (Excit Remix)')

    def test_unveraendert_wenn_sauber(self):
        self.t('Moments in Love (Liebrand Mix)', 'Moments in Love (Liebrand Mix)')


class TestKuenstler(unittest.TestCase):
    def test_semikolon_erster_wert_ist_anzeige(self):
        # Mehrfachwert-Tag: erst Anzeige-Kuenstler, dann Einzelkuenstler
        self.assertEqual(putze_kuenstler('Damon Jee & Darlyn Vlys; Damon Jee; Darlyn Vlys'), 'Damon Jee & Darlyn Vlys')
        self.assertEqual(putze_kuenstler('Anima Sound System; Santos'), 'Anima Sound System')

    def test_schraegstrich_bleibt(self):
        self.assertEqual(putze_kuenstler('Man/ipulate'), 'Man/ipulate')

    def test_doppelung(self):
        self.assertEqual(putze_kuenstler('Toman; Toman'), 'Toman')


class TestNacharbeit(unittest.TestCase):
    def test_codes_und_leer(self):
        self.assertTrue(braucht_nacharbeit('$R8EZCC2', 'X'))
        self.assertTrue(braucht_nacharbeit('', 'X'))
        self.assertTrue(braucht_nacharbeit('Song', ''))
        self.assertFalse(braucht_nacharbeit('Song', 'Artist'))

    def test_kuenstler_noch_im_titel(self):
        self.assertTrue(braucht_nacharbeit('HUGEL,GROSSOMODDO - Andalucia', 'X'))

    def test_kauderwelsch(self):
        self.assertTrue(braucht_nacharbeit('@@0@@20711278@@Vinyl(2) - Other.wav134522D_10000_261C_100_0', 'X'))
        self.assertTrue(braucht_nacharbeit('16356956_Sunday Visitor_(A Visit From The Min', 'X'))
        self.assertFalse(braucht_nacharbeit('1989', 'X'))
        self.assertFalse(braucht_nacharbeit('ALIVE', 'X'))


if __name__ == '__main__':
    unittest.main()
