"""Tests fuer radio_titel_putzen.py - Beispiele echt aus der Bibliothek (04.10.2026)."""
import unittest

from radio_titel_putzen import (putze_titel, putze_kuenstler, braucht_nacharbeit,
                                 aus_dateiname, putze_album, entwirre_sampler)


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

    def test_ein_durchgang_reicht(self):
        alt = '00 - Faithless Sound System - 27-02-2010'
        self.t(alt, '27-02-2010', 'Faithless Sound System')
        self.assertEqual(putze_titel(putze_titel(alt, 'Faithless Sound System'), 'Faithless Sound System'), '27-02-2010')

    def test_webadresse_im_titel(self):
        self.t('Be Strong (Extended Mix) www.djsoundtop.com', 'Be Strong (Extended Mix)')
        self.t('Lambo (Original Mix) www.electronicfresh.com', 'Lambo')
        self.t('Helicopter (Extended Mix) heydj.pro', 'Helicopter (Extended Mix)')
        self.t('Track djsoundtop.com', 'Track')
        self.t('Mr. Fingers', 'Mr. Fingers')
        self.t('Version 2.0', 'Version 2.0')

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


class TestAusDateiname(unittest.TestCase):
    def test_titel_fehlt_kuenstler_passt(self):
        self.assertEqual(aus_dateiname('Kolsch - All Week (Extended Version)', 'Kolsch', ''),
                         ('Kolsch', 'All Week (Extended Version)'))
        self.assertEqual(aus_dateiname('Antdot, ARYMÉ - Romance (Extended Mix)', 'Antdot, ARYMÉ', ''),
                         ('Antdot, ARYMÉ', 'Romance (Extended Mix)'))

    def test_titel_fehlt_kuenstler_passt_nicht(self):
        self.assertIsNone(aus_dateiname('Cheise - Grant - Malt Brun (Cheise Edit)', 'Somebody', ''))

    def test_kuenstler_fehlt_eindeutiger_name(self):
        self.assertEqual(aus_dateiname('Maze DJ - Morning Magic (Extended Version)', '', ''),
                         ('Maze DJ', 'Morning Magic (Extended Version)'))
        self.assertEqual(aus_dateiname('Low Steppa - Turbo Groover', '', ''), ('Low Steppa', 'Turbo Groover'))

    def test_various_artists_ist_kein_kuenstler(self):
        self.assertIsNone(aus_dateiname('Various Artists - Sugar Baby Love (DJ Edit)', '', 'Sugar Baby Love (DJ Edit)'))
        self.assertIsNone(aus_dateiname('VA - Track', '', ''))

    def test_kuenstler_fehlt_unklar(self):
        self.assertIsNone(aus_dateiname('01 Better Days', '', ''))
        self.assertIsNone(aus_dateiname('A - B - C', '', ''))
        self.assertIsNone(aus_dateiname('03 - Lo', '', ''))

    def test_nichts_zu_tun(self):
        self.assertIsNone(aus_dateiname('Kolsch - All Week', 'Kolsch', 'All Week'))


class TestAlbum(unittest.TestCase):
    def test_haendler_listen_fallen_weg(self):
        for a in ('Beatport 100 Afro House 2024 August', 'BP Weekend Picks 2025 Week 26',
                  'Beatport Weekend Picks Week 16 (2025)', 'Beatport New Releases',
                  'Beatport Top 100 Tech House July 2023 FLAC', 'Beatport Best New Hype Deep House August 2024',
                  'Exclusives Only', 'Traxsource Top 100'):
            self.assertEqual(putze_album(a), '', a)

    def test_echte_alben_bleiben(self):
        for a in ('Grand 12-Inches 13', 'Planet Love', 'Weekends #33', 'Top of the Pops',
                  'Dekmantel Ten A Decade of Dekmantel Festival', 'Balloonerism'):
            self.assertEqual(putze_album(a), a, a)


class TestNacharbeit(unittest.TestCase):
    def test_codes_und_leer(self):
        self.assertTrue(braucht_nacharbeit('$R8EZCC2', 'X'))
        self.assertTrue(braucht_nacharbeit('', 'X'))
        self.assertTrue(braucht_nacharbeit('Song', ''))
        self.assertFalse(braucht_nacharbeit('Song', 'Artist'))

    def test_version_bindestrich_ist_erlaubt(self):
        self.assertFalse(braucht_nacharbeit('Calma - Extended', 'Eli Fola, Canetis'))
        self.assertFalse(braucht_nacharbeit('Kula - Bassfinder & Faceoff Remix', 'Ladour, David Hopperman'))

    def test_kuenstler_noch_im_titel(self):
        self.assertTrue(braucht_nacharbeit('HUGEL,GROSSOMODDO - Andalucia', 'X'))

    def test_kauderwelsch(self):
        self.assertTrue(braucht_nacharbeit('@@0@@20711278@@Vinyl(2) - Other.wav134522D_10000_261C_100_0', 'X'))
        self.assertTrue(braucht_nacharbeit('16356956_Sunday Visitor_(A Visit From The Min', 'X'))
        self.assertFalse(braucht_nacharbeit('1989', 'X'))
        self.assertFalse(braucht_nacharbeit('ALIVE', 'X'))


class TestSamplerImport(unittest.TestCase):
    """Beatport-Sampler vom 07.10.2026: Tracknummer landete im Kuenstlerfeld,
    der Sampler-Name im Titel. 44 Faelle gleichzeitig auf Sendung.
    Muster: '<Sampler> - <Kuenstler> - <Titel>' bei Kuenstler = reine Zahl."""

    def test_sampler_wird_entwirrt(self):
        self.assertEqual(
            entwirre_sampler('37', 'Beatport 100 Afro House 2024 August - Sterio T,NkOstA LED,TomyV - Uwrongo'),
            ('Sterio T, NkOstA LED, TomyV', 'Uwrongo', 'Beatport 100 Afro House 2024 August'),
        )
        self.assertEqual(
            entwirre_sampler('28', 'Beatport 100 Afro House 2024 August - Hypaphonik - Funa Wena'),
            ('Hypaphonik', 'Funa Wena', 'Beatport 100 Afro House 2024 August'),
        )

    def test_beatport_sampler_im_artistfeld_wird_entwirrt(self):
        self.assertEqual(
            entwirre_sampler('Beatport Best New Hype Deep House August 2024', 'You Got Me - Karter (Original Mix)'),
            ('Karter', 'You Got Me', 'Beatport Best New Hype Deep House August 2024'),
        )
        self.assertEqual(
            entwirre_sampler('Beatport Best New Hype Deep House August 2024', 'Capi Scuri - DJ Rocca (Manuel Costela Remix)'),
            ('DJ Rocca', 'Capi Scuri (Manuel Costela Remix)', 'Beatport Best New Hype Deep House August 2024'),
        )

    def test_fuehrender_bindestrich_ohne_sampler(self):
        self.assertEqual(
            entwirre_sampler('36', '- Pierre Johnson,Oscar Mbo - Ukuphila'),
            ('Pierre Johnson, Oscar Mbo', 'Ukuphila', ''),
        )

    def test_version_am_ende_bleibt_am_titel(self):
        self.assertEqual(
            entwirre_sampler('45', 'Beatport 100 Afro House 2024 August - Eli Fola,Canetis - Calma - Extended'),
            ('Eli Fola, Canetis', 'Calma - Extended', 'Beatport 100 Afro House 2024 August'),
        )

    def test_echter_kuenstler_wird_nicht_angetastet(self):
        self.assertIsNone(entwirre_sampler('Hypaphonik', 'Funa Wena'))
        self.assertIsNone(entwirre_sampler('Daft Punk', 'Around the World - Radio Edit'))

    def test_zahl_als_kuenstler_ohne_muster_bleibt_nacharbeit(self):
        self.assertIsNone(entwirre_sampler('37', 'Uwrongo'))
        self.assertTrue(braucht_nacharbeit('Uwrongo', '37'))

    def test_nach_dem_entwirren_ist_es_sendertauglich(self):
        k, t, _ = entwirre_sampler('37', 'Beatport 100 Afro House 2024 August - Sterio T,NkOstA LED,TomyV - Uwrongo')
        self.assertFalse(braucht_nacharbeit(t, k))


if __name__ == '__main__':
    unittest.main()
