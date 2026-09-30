# -*- coding: utf-8 -*-
from datetime import datetime
from zoneinfo import ZoneInfo

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.frawo_agent.models.radio_azuracast import _schedule_vereinfachen

BERLIN = ZoneInfo("Europe/Berlin")


def _jetzt(jahr, monat, tag, stunde, minute=0):
    return datetime(jahr, monat, tag, stunde, minute, tzinfo=BERLIN)


def _item(start_time, end_time, days):
    return {
        "start_time": start_time, "end_time": end_time, "days": days,
        "start_date": None, "end_date": None, "loop_once": False,
    }


def _playlist(name, items, description="", is_enabled=True, is_jingle=False):
    return {
        "name": name, "description": description,
        "is_enabled": is_enabled, "is_jingle": is_jingle,
        "schedule_items": items,
    }


@tagged("post_install", "-at_install", "frawo_agent")
class TestScheduleVereinfachen(TransactionCase):
    """Model-freie Hilfsfunktion. Eingabeform und Zahlenkonventionen (days:
    1=Montag...7=Sonntag, start_time/end_time als HHMM-Ganzzahl) an einem
    echten Abruf von GET https://10.1.0.38/api/station/1/playlists (30.09.2026,
    ueber CT140, Header X-API-Key) verifiziert -- u.a. Playlist "01 Sunrise"
    mit schedule_items days=[1,2,3,4,5] start_time=600 end_time=830 deckt sich
    exakt mit der bekannten Sendezeit 06:00-08:30 Mo-Fr. Unter allen 21 echten
    Playlists kam keine einzige mit leerer days-Liste vor (Test 'jeden Tag'
    unten daher nur per Fixture, nicht an echten Daten bestaetigbar).
    """

    # -- Grundfaelle -----------------------------------------------------

    def test_leere_liste_ergibt_leere_liste(self):
        self.assertEqual(_schedule_vereinfachen([]), [])

    def test_none_eingabe_ergibt_leere_liste(self):
        self.assertEqual(_schedule_vereinfachen(None), [])

    def test_beschreibung_kommt_aus_playlist_description(self):
        pl = _playlist("01 Sunrise", [_item(600, 830, [1])], description="Ambient und organisch.")
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 7))
        self.assertEqual(out[0]["beschreibung"], "Ambient und organisch.")

    def test_description_none_wird_leerstring(self):
        # Real beobachtet: Playlist "⭐ Best of the Week" hat description=null.
        pl = _playlist("⭐ Best of the Week", [_item(1800, 2000, [7])], description=None)
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 10, 4, 19))
        self.assertEqual(out[0]["beschreibung"], "")

    # -- Filter: nur aktivierte Sendungen mit schedule_items --------------

    def test_deaktivierte_playlist_faellt_weg(self):
        pl = _playlist("Alt-Kanal", [_item(600, 800, [1])], is_enabled=False)
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 7))
        self.assertEqual(out, [])

    def test_jingle_playlist_faellt_weg(self):
        pl = _playlist("Station IDs", [_item(0, 2359, [1, 2, 3, 4, 5, 6, 7])], is_jingle=True)
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 7))
        self.assertEqual(out, [])

    def test_playlist_ohne_schedule_items_faellt_weg(self):
        pl = _playlist("Ohne Zeiten", [])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 7))
        self.assertEqual(out, [])

    # -- Robustheit: kaputte/leere Eintraege --------------------------------

    def test_defekte_eintraege_werden_uebersprungen_ohne_absturz(self):
        rohliste = [
            None,
            {"name": "Ohne Items-Key", "is_enabled": True, "description": ""},
            _playlist("Kaputte Items", [None, {}, {"start_time": 600}]),
            _playlist("Gemischte Tage", [_item(1000, 1100, ["x", None, 3])]),
        ]
        out = _schedule_vereinfachen(rohliste, jetzt=_jetzt(2026, 9, 30, 10, 30))
        # Nur der gueltige Tag (3 = Mittwoch) in "Gemischte Tage" ergibt einen Eintrag.
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "Gemischte Tage")
        self.assertTrue(out[0]["jetzt"])

    # -- Ueber Mitternacht: Beginn-Tag + jetzt -----------------------------

    def test_ueber_mitternacht_21_bis_06_dem_beginn_tag_zugeordnet(self):
        pl = _playlist("06 Deep Night", [_item(2100, 600, [1])])  # Montag 21:00-06:00
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 23))  # Mo 23:00
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["start"], "2026-09-28T21:00:00+02:00")
        self.assertEqual(out[0]["ende"], "2026-09-29T06:00:00+02:00")
        self.assertTrue(out[0]["jetzt"])
        beginn = datetime.fromisoformat(out[0]["start"])
        self.assertEqual(beginn.weekday(), 0)  # Montag

    def test_ueber_mitternacht_samstag_22_bis_02(self):
        pl = _playlist("07 Peak Time Club", [_item(2200, 200, [6])])  # Samstag 22:00-02:00
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 10, 3, 23, 30))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["start"], "2026-10-03T22:00:00+02:00")
        self.assertEqual(out[0]["ende"], "2026-10-04T02:00:00+02:00")
        self.assertTrue(out[0]["jetzt"])

    def test_freitag_21_bis_02_unterscheidet_sich_von_samstag(self):
        pl = _playlist("07 Peak Time Club", [
            _item(2100, 200, [5]),  # Freitag 21:00-02:00
            _item(2200, 200, [6]),  # Samstag 22:00-02:00
        ])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 10, 2, 22))  # Fr 22:00
        # Beide Eintraege sind real und ueberlappen sich nicht (Fr endet Sa 02:00,
        # Sa startet erst 22:00) -- beide muessen erscheinen, nur der Freitag ist "jetzt".
        self.assertEqual(len(out), 2)
        jetzt_eintraege = [e for e in out if e["jetzt"]]
        self.assertEqual(len(jetzt_eintraege), 1)
        self.assertEqual(jetzt_eintraege[0]["start"], "2026-10-02T21:00:00+02:00")

    # -- jetzt genau einmal -------------------------------------------------

    def test_jetzt_genau_einmal_bei_voller_abdeckung(self):
        pl = _playlist("Tagesprogramm", [
            _item(600, 1800, [3]),   # Mittwoch 06:00-18:00
            _item(1800, 600, [3]),   # Mittwoch 18:00-06:00 (naechster Tag)
        ])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 30, 12))
        jetzt_eintraege = [e for e in out if e["jetzt"]]
        self.assertEqual(len(jetzt_eintraege), 1)
        self.assertEqual(jetzt_eintraege[0]["start"], "2026-09-30T06:00:00+02:00")

    # -- Ueberlappende schedule_items derselben Playlist (real beobachtet) --

    def test_ueberlappende_schedule_items_werden_zusammengefasst(self):
        # Reale Konfiguration von "06 Deep Night": ein Mo-Do-21:00-06:00-Item
        # UND ein zusaetzliches Mo-Fr-00:00-06:00-Item, das Di-Fr morgens
        # doppelt abdeckt.
        pl = _playlist("06 Deep Night", [
            _item(2100, 600, [1, 2, 3, 4]),
            _item(0, 600, [1, 2, 3, 4, 5]),
        ])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 29, 2))  # Di 02:00
        # Dienstagmorgen ist Teil der Montagnacht-Sendung, keine eigene
        # Dienstag-00:00-Karte.
        dienstag_karten = [e for e in out if e["start"].startswith("2026-09-29T00:00")]
        self.assertEqual(dienstag_karten, [])
        jetzt_eintraege = [e for e in out if e["jetzt"]]
        self.assertEqual(len(jetzt_eintraege), 1)
        self.assertEqual(jetzt_eintraege[0]["start"], "2026-09-28T21:00:00+02:00")

    # -- Wochenwechsel Sonntag -> Montag -------------------------------------

    def test_wochenwechsel_sonntagnacht_bleibt_montagfrueh_jetzt(self):
        # Sonntag 21:30-06:00 (real: "06 Deep Night" So) + ein Montag-Fragment
        # 00:00-06:00, das (wie bei "06 Deep Night" real) denselben Zeitraum
        # nochmal ueberlappt.
        pl = _playlist("06 Deep Night", [
            _item(2130, 600, [7]),
            _item(0, 600, [1, 2, 3, 4, 5]),
        ])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 2))  # Mo 02:00
        jetzt_eintraege = [e for e in out if e["jetzt"]]
        self.assertEqual(len(jetzt_eintraege), 1)
        # Der laufende Eintrag stammt vom Sonntag-Beginn (Vorwoche), nicht vom
        # Montag-Fragment.
        beginn = datetime.fromisoformat(jetzt_eintraege[0]["start"])
        self.assertEqual(beginn.weekday(), 6)  # Sonntag
        self.assertEqual(jetzt_eintraege[0]["ende"], "2026-09-28T06:00:00+02:00")

    # -- Leere Tage-Liste = "jeden Tag" (Vorgabe, an Fixture getestet) ------

    def test_leere_tage_liste_bedeutet_jeden_tag(self):
        pl = _playlist("Nonstop-Kanal", [_item(1000, 1100, [])])
        out = _schedule_vereinfachen([pl], jetzt=_jetzt(2026, 9, 28, 7))
        self.assertEqual(len(out), 7)
        wochentage = sorted(datetime.fromisoformat(e["start"]).weekday() for e in out)
        self.assertEqual(wochentage, [0, 1, 2, 3, 4, 5, 6])

    # -- Volle Woche ----------------------------------------------------------

    def test_volle_woche_deckt_alle_sieben_tage_ab(self):
        playlists = [
            _playlist("01 Sunrise", [
                _item(600, 830, [1, 2, 3, 4, 5]),
                _item(600, 930, [6]),
                _item(600, 1000, [7]),
            ]),
            _playlist("06 Deep Night", [
                _item(2100, 600, [1, 2, 3, 4]),
                _item(0, 600, [1, 2, 3, 4, 5]),
                _item(200, 600, [6]),
                _item(200, 600, [7]),
                _item(2130, 600, [7]),
            ]),
            _playlist("07 Peak Time Club", [
                _item(2100, 200, [5]),
                _item(2200, 200, [6]),
            ]),
        ]
        out = _schedule_vereinfachen(playlists, jetzt=_jetzt(2026, 9, 30, 12))
        wochentage = set(datetime.fromisoformat(e["start"]).weekday() for e in out)
        self.assertEqual(wochentage, {0, 1, 2, 3, 4, 5, 6})
