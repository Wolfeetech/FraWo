# -*- coding: utf-8 -*-
"""Duenner Client fuer die AzuraCast-REST-API (nur was die Kanal-Demokratie braucht).

Bewusst REST statt MariaDB-Direktzugriff: nach direkten DB-Aenderungen
muesste der Sender neu gestartet werden (NOW.md-Fallentabelle), ueber die
API benachrichtigt AzuraCast liquidsoap selbst.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import urllib3

from odoo import models

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

STATION_ID = 1
TIMEOUT = 10

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def _hhmm_zu_uhrzeit(wert):
    """AzuraCast-HHMM-Ganzzahl (z.B. 2130) -> (Stunde, Minute). Robust gegen
    None/kaputte Werte (dann 00:00)."""
    try:
        wert = int(wert or 0)
    except (TypeError, ValueError):
        wert = 0
    stunde = (wert // 100) % 24
    minute = wert % 100
    if minute > 59:
        minute = 59
    return stunde, minute


def _playlist_instanzen(playlist, montag):
    """Baut aus den ``schedule_items`` einer Playlist alle Wocheninstanzen
    fuer zwei Wochen: die Vorwoche und die Anzeige-Woche ab ``montag``
    (Montag..Sonntag). AzuraCasts ``days`` ist ISO: 1=Montag ... 7=Sonntag
    (an echten Daten verifiziert -- Playlist "01 Sunrise" mit days=[1,2,3,4,5]
    deckt sich mit der bekannten Mo-Fr-Sendezeit 06:00-08:30).

    Eine leere ``days``-Liste wird als "jeden Tag" behandelt (Vorgabe; unter
    21 echten AzuraCast-Playlists kam eine leere days-Liste kein einziges
    Mal vor, daher an echten Daten nicht bestaetigbar, nur per Fixture
    getestet).

    Die Vorwoche wird erzeugt, damit eine Sendung, die Sonntagnacht startet
    und erst Montagfrueh endet (real: "06 Deep Night" So 21:30-06:00), beim
    Wochenwechsel noch korrekt als "jetzt laufend" erkannt wird und nicht
    vom eigenen, erst spaeter beginnenden Montag-Fragment verdeckt bleibt.
    """
    name = playlist.get("name") or ""
    beschreibung = playlist.get("description") or ""
    instanzen = []
    for item in (playlist.get("schedule_items") or []):
        if not isinstance(item, dict):
            continue
        if item.get("start_time") is None or item.get("end_time") is None:
            continue  # defekter Eintrag ohne Pflichtfelder -- ueberspringen
        tage = item.get("days") or [1, 2, 3, 4, 5, 6, 7]
        start_stunde, start_minute = _hhmm_zu_uhrzeit(item.get("start_time"))
        end_stunde, end_minute = _hhmm_zu_uhrzeit(item.get("end_time"))
        ueber_mitternacht = (end_stunde, end_minute) <= (start_stunde, start_minute)
        for iso_tag in tage:
            try:
                iso_tag = int(iso_tag)
            except (TypeError, ValueError):
                continue
            if iso_tag < 1 or iso_tag > 7:
                continue
            basis_versatz = iso_tag - 1  # 0=Montag ... 6=Sonntag
            for wochen_versatz in (-7, 0):
                versatz = basis_versatz + wochen_versatz
                start_datum = montag + timedelta(days=versatz)
                start_dt = datetime(
                    start_datum.year, start_datum.month, start_datum.day,
                    start_stunde, start_minute, tzinfo=BERLIN_TZ,
                )
                end_datum = start_datum + timedelta(days=1 if ueber_mitternacht else 0)
                end_dt = datetime(
                    end_datum.year, end_datum.month, end_datum.day,
                    end_stunde, end_minute, tzinfo=BERLIN_TZ,
                )
                instanzen.append({
                    "name": name, "beschreibung": beschreibung,
                    "start_dt": start_dt, "end_dt": end_dt,
                })
    return instanzen


def _ist_teilmenge(klein, gross):
    """True, wenn der Zeitraum von ``klein`` vollstaendig in ``gross`` liegt
    (gleicher Sendungsname) und ``gross`` mindestens genauso weit reicht.

    Deckt zwei reale AzuraCast-Eigenheiten ab: (1) einzelne Playlists haben
    ueberlappende ``schedule_items`` -- "06 Deep Night" hat sowohl ein
    Mo-Do-21:00-06:00-Item als auch ein zusaetzliches Mo-Fr-00:00-06:00-Item,
    das die Naechte Di-Fr morgens doppelt abdeckt; (2) den Wochenwechsel
    So->Mo (siehe ``_playlist_instanzen``).
    """
    if klein is gross:
        return False
    if klein["name"] != gross["name"]:
        return False
    innerhalb = (gross["start_dt"] <= klein["start_dt"]) and (gross["end_dt"] >= klein["end_dt"])
    echt_kleiner = (gross["start_dt"] < klein["start_dt"]) or (gross["end_dt"] > klein["end_dt"])
    return innerhalb and echt_kleiner


def _schedule_vereinfachen(playlists, jetzt=None):
    """Baut aus GET /api/station/1/playlists (wiederkehrende Sendezeiten,
    nicht der kurzfristige Occurrence-Feed) eine volle Wochenansicht
    Montag..Sonntag: {name, beschreibung, start, ende, jetzt}.

    Nur aktivierte Playlists mit ``schedule_items`` (keine Jingles, keine
    leeren/deaktivierten Playlists). Ueberlappende schedule_items derselben
    Playlist werden zusammengefasst (siehe ``_ist_teilmenge``), sodass jede
    Sendung dem Tag ihres Beginns zugeordnet bleibt und ``jetzt`` bei
    Ueberlappung nur an einem Eintrag steht.

    ``jetzt`` ist ein Parameter (statt intern ``datetime.now()`` zu rufen),
    damit die Funktion fuer Tests deterministisch bleibt; ohne Angabe wird
    die echte aktuelle Zeit in Europe/Berlin verwendet. Ein naiver
    (tzlos-uebergebener) ``jetzt``-Wert wird als Europe/Berlin interpretiert.

    Reine Funktion ohne Odoo-Env -- model-frei und ohne Datenbank testbar.
    """
    if jetzt is None:
        jetzt = datetime.now(BERLIN_TZ)
    elif jetzt.tzinfo is None:
        jetzt = jetzt.replace(tzinfo=BERLIN_TZ)

    montag = jetzt.date() - timedelta(days=jetzt.weekday())
    sonntag = montag + timedelta(days=6)

    alle = []
    for pl in (playlists or []):
        if not isinstance(pl, dict):
            continue
        if not pl.get("is_enabled", True):
            continue
        if pl.get("is_jingle"):
            continue
        if not pl.get("schedule_items"):
            continue
        alle.extend(_playlist_instanzen(pl, montag))

    behalten = [
        eintrag for eintrag in alle
        if not any(_ist_teilmenge(eintrag, andere) for andere in alle)
    ]

    ausgabe = []
    for e in behalten:
        in_anzeige_woche = montag <= e["start_dt"].date() <= sonntag
        ist_jetzt = e["start_dt"] <= jetzt < e["end_dt"]
        # Ausserhalb der Anzeige-Woche nur behalten, wenn es der gerade
        # laufende Eintrag ist (Wochenwechsel-Randfall, siehe oben).
        if in_anzeige_woche or ist_jetzt:
            ausgabe.append((e, ist_jetzt))

    ausgabe.sort(key=lambda paar: paar[0]["start_dt"])

    return [
        {
            "name": e["name"],
            "beschreibung": e["beschreibung"],
            "start": e["start_dt"].isoformat(),
            "ende": e["end_dt"].isoformat(),
            "jetzt": ist_jetzt,
        }
        for e, ist_jetzt in ausgabe
    ]


class FrawoRadioAzuracast(models.AbstractModel):
    _name = "frawo.radio.azuracast"
    _description = "AzuraCast REST-Client (Playlisten-Gewichte)"

    def _api_config(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        base = (get_param("frawo_agent.azuracast_api_url", "") or "").rstrip("/")
        key = get_param("frawo_agent.azuracast_api_key", "") or ""
        return base, key

    def _headers(self):
        _, key = self._api_config()
        return {"X-API-Key": key}

    def list_playlists(self):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlists"
        resp = requests.get(url, headers=self._headers(), verify=False, timeout=TIMEOUT)
        if resp.status_code != 200:
            _logger.warning("AzuraCast-Playlisten nicht lesbar (HTTP %s)", resp.status_code)
            return []
        return resp.json()

    def get_weights(self, playlist_ids):
        wanted = set(playlist_ids)
        out = {}
        for pl in self.list_playlists():
            if pl.get("id") in wanted:
                out[pl["id"]] = pl.get("weight")
        return out

    def set_weight(self, playlist_id, weight):
        base, _ = self._api_config()
        url = f"{base}/api/station/{STATION_ID}/playlist/{playlist_id}"
        resp = requests.put(
            url, headers=self._headers(), json={"weight": weight},
            verify=False, timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            _logger.warning(
                "Gewicht fuer Playlist %s nicht gesetzt (HTTP %s)",
                playlist_id, resp.status_code,
            )
            return False
        return True
