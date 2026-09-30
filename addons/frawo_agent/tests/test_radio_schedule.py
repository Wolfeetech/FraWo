# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.frawo_agent.models.radio_azuracast import _schedule_vereinfachen


@tagged("post_install", "-at_install", "frawo_agent")
class TestScheduleVereinfachen(TransactionCase):
    """Model-freie Hilfsfunktion, reale Fixtures aus einem echten Abruf von
    GET https://10.1.0.38/api/station/1/schedule (30.09.2026, aus CT140).

    Beobachtung beim echten Abruf: AzuraCast liefert fuer eine Sendung, die
    ueber Mitternacht laeuft (z.B. 21:00-06:00), manchmal zwei Eintraege mit
    unterschiedlicher id -- einen ab dem echten Beginn (21:00) und einen
    zweiten, der bei 00:00 des Folgetags nochmal beginnt und denselben
    Zeitraum bis zum Ende doppelt abdeckt. Beide koennen is_now=true haben,
    wenn "jetzt" in der Ueberlappung liegt. _schedule_vereinfachen muss das
    auf einen Eintrag zusammenfassen (den mit dem fruehesten Start =
    Beginn-Tag) und darf danach nur noch genau ein jetzt=true im Ergebnis haben.
    """

    def _peak_time_voll(self, jetzt):
        return {
            "id": 111, "type": "playlist",
            "name": "07 Peak Time Club", "title": "07 Peak Time Club",
            "description": "Playlist: 07 Peak Time Club",
            "start_timestamp": 1790110800,
            "start": "2026-10-02T21:00:00+02:00",
            "end_timestamp": 1790128800,
            "end": "2026-10-03T02:00:00+02:00",
            "is_now": jetzt,
        }

    def _peak_time_dublette(self, jetzt):
        # Von AzuraCast zusaetzlich gelieferter Eintrag: beginnt erst um
        # Mitternacht, deckt aber denselben Rest-Zeitraum nochmal ab.
        return {
            "id": 127, "type": "playlist",
            "name": "07 Peak Time Club", "title": "07 Peak Time Club",
            "description": "Playlist: 07 Peak Time Club",
            "start_timestamp": 1790121600,
            "start": "2026-10-03T00:00:00+02:00",
            "end_timestamp": 1790128800,
            "end": "2026-10-03T02:00:00+02:00",
            "is_now": jetzt,
        }

    def _sunrise(self):
        return {
            "id": 100, "type": "playlist",
            "name": "01 Sunrise", "title": "01 Sunrise",
            "description": "Playlist: 01 Sunrise",
            "start_timestamp": 1790143200,
            "start": "2026-10-03T06:00:00+02:00",
            "end_timestamp": 1790152200,
            "end": "2026-10-03T08:30:00+02:00",
            "is_now": False,
        }

    def _jingle(self):
        return {
            "id": 999, "type": "jingle",
            "name": "Station ID", "title": "Station ID",
            "description": "Jingle: Station ID",
            "start_timestamp": 1790110000,
            "start": "2026-10-02T20:59:00+02:00",
            "end_timestamp": 1790110060,
            "end": "2026-10-02T21:00:00+02:00",
            "is_now": False,
        }

    def test_leere_liste_ergibt_leere_liste(self):
        self.assertEqual(_schedule_vereinfachen([]), [])

    def test_none_eingabe_ergibt_leere_liste(self):
        self.assertEqual(_schedule_vereinfachen(None), [])

    def test_nur_sendungen_playlists_keine_jingles(self):
        out = _schedule_vereinfachen([self._jingle(), self._sunrise()])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "01 Sunrise")

    def test_felder_werden_korrekt_gemappt(self):
        out = _schedule_vereinfachen([self._sunrise()])
        self.assertEqual(out[0], {
            "name": "01 Sunrise",
            "beschreibung": "Playlist: 01 Sunrise",
            "start": "2026-10-03T06:00:00+02:00",
            "ende": "2026-10-03T08:30:00+02:00",
            "jetzt": False,
        })

    def test_ueber_mitternacht_wird_dem_beginn_tag_zugeordnet(self):
        # 21:00 Freitag -> 02:00 Samstag: muss unter Freitag (dem Beginn-Tag)
        # erscheinen, also mit dem Freitag-Start im Ergebnis stehen.
        out = _schedule_vereinfachen([self._peak_time_voll(False)])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["start"], "2026-10-02T21:00:00+02:00")
        from datetime import datetime
        beginn = datetime.fromisoformat(out[0]["start"])
        self.assertEqual(beginn.weekday(), 4)  # Freitag

    def test_dubletten_ueber_mitternacht_werden_zusammengefasst(self):
        out = _schedule_vereinfachen([
            self._peak_time_voll(False),
            self._peak_time_dublette(False),
        ])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["start"], "2026-10-02T21:00:00+02:00")
        self.assertEqual(out[0]["ende"], "2026-10-03T02:00:00+02:00")

    def test_jetzt_genau_bei_einem_eintrag_gesetzt(self):
        # Realer Fall: beide ueberlappenden Rohdaten-Eintraege kommen mit
        # is_now=true zurueck, weil "jetzt" in der Ueberlappung liegt.
        out = _schedule_vereinfachen([
            self._peak_time_voll(True),
            self._peak_time_dublette(True),
            self._sunrise(),
        ])
        jetzt_eintraege = [e for e in out if e["jetzt"]]
        self.assertEqual(len(jetzt_eintraege), 1)
        self.assertEqual(jetzt_eintraege[0]["name"], "07 Peak Time Club")

    def test_ergebnis_chronologisch_sortiert(self):
        out = _schedule_vereinfachen([
            self._sunrise(),
            self._peak_time_voll(False),
        ])
        self.assertEqual([e["name"] for e in out],
                          ["07 Peak Time Club", "01 Sunrise"])
