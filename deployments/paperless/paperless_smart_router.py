#!/usr/bin/env python3
"""
Paperless-ngx Smart Router v4
Läuft als PAPERLESS_POST_CONSUME_SCRIPT nach jedem eingelesenen Dokument.

Ablauf:
  1. OCR-Text von Paperless holen
  2. Lokaler KI-Dienst (Ollama auf OptiPlex, qwen2.5:3b) analysiert den Text:
     Person/Entität, Ablage-Kategorie, Absender, Betrag, Frist, Handlungsbedarf,
     Kurzzusammenfassung. Bei Ausfall: nahtloser Fallback auf Gemini Cloud.
  3. Correspondent/Document-Type/Tags in Paperless setzen (inkl.
     ablage:<kategorie>-Tag, den das host-seitige Filing-Skript liest)
  4. Bei Handlungsbedarf: Odoo-Aufgabe bei der richtigen Person anlegen

v3 → v4: Lokaler KI-Dienst Ollama (qwen2.5:3b auf OptiPlex 10.0.0.227) als primäre,
datenschutzkonforme Ingest-Pipeline ohne API-Limits/Kosten; nahtloser automatischer
Fallback auf Gemini Cloud bei Nicht-Erreichbarkeit.
"""

import os
import re
import sys
import json
import subprocess
import xmlrpc.client
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

DOC_ID = os.environ.get("DOCUMENT_ID")
DOC_FILENAME = os.environ.get("DOCUMENT_FILE_NAME", "")

PAPERLESS_URL = "http://localhost:8000/api"
PAPERLESS_API_TOKEN = os.environ.get("PAPERLESS_API_TOKEN", "")

ODOO_URL = os.environ.get("ODOO_URL", "http://10.1.0.112:8069")
if "10.1.0.140" in ODOO_URL:
    ODOO_URL = ODOO_URL.replace("10.1.0.140", "10.1.0.112")
ODOO_DB = os.environ.get("ODOO_DB", "FraWo_GbR")
ODOO_USER = os.environ.get("ODOO_USER", "wolf@frawo.tech")
ODOO_PASS = os.environ.get("ODOO_PASS", "")

# Zuerst StudioPC (schnell, nicht 24/7), dann OptiPlex (24/7). Die OptiPlex-KI braucht
# die Firewall-Regel "CT110 -> 11434" in cluster.fw (29.09.2026, Odoo #1645).
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.0.0.156:11434")
OLLAMA_URL_OPTIPLEX = os.environ.get("OLLAMA_URL_OPTIPLEX", "http://10.1.0.227:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.5-flash-lite"  # deutlich hoeheres Frei-Kontingent als 3.6-flash (dort nur 20/Tag)

# entity -> Odoo user_id (Aufgabe zugewiesen), partner_id (Kontakt-Verknüpfung
# falls vorhanden), project_id (Ziel-Projekt)
ENTITY_MAP = {
    "Wolf_Prinz":    {"user_id": 6,  "partner_id": 7,     "project_id": 32},
    "Franz_Bienert": {"user_id": 10, "partner_id": 16,    "project_id": 32},
    "Alois_Prinz":   {"user_id": 6,  "partner_id": 42,    "project_id": 58},
    "Heidi_Prinz":   {"user_id": 6,  "partner_id": 42,    "project_id": 58},
    "FraWo_GbR":     {"user_id": 6,  "partner_id": False, "project_id": 32},
}

# Kategorie-Kürzel, das Gemini/Ollama liefert -> Tag "ablage:<kürzel>". Das
# Kategorie-Kürzel steuert die Ablage in FOLDER_MAP (siehe unten).
VALID_CATEGORIES = {
    "finanzen", "vertraege", "amt_behoerden", "gesundheit",
    "wohnen", "arbeit", "projekte", "sonstiges",
}

VALID_DOCUMENT_TYPES = {
    "Rechnung", "Quittung", "Mahnung", "Vertrag", "Bescheid", "Kontoauszug",
    "Versicherungspolice", "Zeugnis", "Bewerbung", "Kündigung",
    "Antrag", "Angebot", "Sonstiges",
}
BELEG_TYPEN = ("Rechnung", "Quittung", "Kassenbeleg")

# Probelauf: ROUTER_PROBE=1 klassifiziert und zeigt die geplante Entscheidung, schreibt aber
# NICHTS (weder Paperless noch Drive noch Odoo). Aufruf siehe README.md.
PROBE = os.environ.get("ROUTER_PROBE") == "1"

# --- Qualitaetsregel fuer automatisch angelegte Odoo-Aufgaben (30.09.2026, Odoo #1585) ---
# Wolf: "eine schwachsinnige Aufgabe, aus der niemand schlau wird" (#1585: "Unbekannt — 0,00 €",
# entstanden, weil ALLE KI-Dienste ausgefallen waren; dazu wurde ein fremder Beleg angehaengt).
#   1. Eine Aufgabe entsteht NUR, wenn ein Mensch wirklich etwas tun muss (zahlen, antworten,
#      unterschreiben, Frist einhalten). Bezahlte Belege werden gebucht, nicht als Aufgabe abgelegt.
#   2. Der Titel sagt, was zu tun ist ("Rechnung bezahlen: Thomann GmbH"), ohne Betrag.
#   3. Erste Zeile der Beschreibung: Was · Warum · Bis wann · Wer.
#   4. Der Beleg haengt als PDF an der Aufgabe.
#   5. Wer die Regeln nicht erfuellen kann (KI ausgefallen, Absender unbekannt, keine Aktion),
#      legt KEINE Aufgabe an - lieber Buchung, Paperless-Schlagwort oder gar nichts.
AKTION_JE_TYP = {
    "Rechnung": "Rechnung bezahlen", "Quittung": "Beleg prüfen", "Mahnung": "Mahnung klären",
    "Vertrag": "Vertrag prüfen", "Bescheid": "Bescheid prüfen", "Kündigung": "Kündigung prüfen",
    "Antrag": "Antrag ausfüllen", "Angebot": "Angebot entscheiden", "Versicherungspolice": "Police prüfen",
}
KI_AUSFALL_TAG = "ki-ausfall-nachholen"

# Bezahlt erkennen (deutsch + englisch). 30.09.2026: GitHub-Quittung "We received payment ...
# Charged to PayPal account" rutschte durch, weil nur deutsche Formulierungen geprueft wurden.
BEZAHLT_MUSTER = re.compile(
    r"(?i)(zahlungsart\W{0,5}(ec|karte|bar|girocard|paypal|kredit|n26|visa|master)|ec-karte|kartenzahlung|"
    r"bar bezahlt|betrag erhalten|bereits bezahlt|zahlung erhalten|bezahlt am|\bpaid\b|n26 bank se\W+•|"
    r"we received payment|payment received|charged to|receipt for your payment|amount paid)")
# Von einem GbR-Konto bezahlt -> keine Auslage Wolf (Qonto, N26-Space "FraWo" ...5630 56).
GBR_KONTO_MUSTER = re.compile(r"(?i)(qonto|frawo space|5630\s?56)")
# Auslage Wolf nur mit AUSDRUECKLICHEM Zahlungsmittel im Beleg (Jarvis-Review #1585, 30.09.2026):
# "bezahlt", "Quittung" oder "payment received" beweisen nur, DASS bezahlt wurde - nicht, WER.
# Verlangt werden beide: ein konkretes Zahlungsmittel (Karte, PayPal, N26) UND Wolf als Zahler/Kaeufer.
ZAHLMITTEL_MUSTER = re.compile(
    r"(?i)(zahlungs(?:art|methode|mittel)\W{0,5}(ec|karte|girocard|paypal|kredit|n26|visa|master|debit)|"
    r"ec-karte|girocard|kartenzahlung|charged to (?:your )?(paypal|visa|mastercard|card)|"
    r"paypal account|n26 bank se)")
WOLF_ZAHLER_MUSTER = re.compile(r"(?i)(\bwolf(?:gang)?\s+(?:ferdinand\s+)?prinz\b|\bw\.prinz)")
# Journal fuer Auslagen Wolf: bucht die Zahlung direkt auf Konto 201100 "Verbindlichkeit Gesellschafter
# Wolf Prinz (Auslagen)" - die GbR schuldet Wolf den Betrag (Entscheidung Wolf 30.09.2026, #1585).
# NICHT BNK1: das buchte auf "Ausstehende Zahlungen", als haette die Firmenbank bezahlt.
AUSLAGE_JOURNAL_CODE = "AUSW"

# Eingangsrechnungen (Odoo #1645, 29.09.2026). Kleinunternehmer § 19 UStG: Einkauf wird
# BRUTTO gebucht, OHNE Steuer. Die Firma hat als Einkaufs-Standardsteuer "VSt 19%" hinterlegt -
# deshalb setzt der Router tax_ids ausdruecklich leer.
# Kostenart (von der KI) -> Kontonummer. Alles andere: Standardkonto des Einkaufsjournals
# (600000 Aufwand). Vorher nahm der Router das ERSTE Aufwandskonto = 443000 Skontoverlust.
KOSTENART_KONTO = {
    "ausruestung": "611000",    # Einkauf von Ausruestung
    "versicherung": "627000",
    "miete": "612000",
    "bankgebuehren": "620000",
    "sonstiges": None,
}
# Eine Bestellung kommt oft als mehrere Belege (Bestelluebersicht + Haendlerrechnungen).
# Die Bestellnummer ist das stabile Merkmal gegen Doppelbuchung (AGENTS.md Verbot 6).
BESTELLNR_MUSTER = [
    re.compile(r"\b\d{3}-\d{7}-\d{7}\b"),                                    # Amazon
    re.compile(r"(?i)bestell(?:ung|nummer|-nr\.?|nr\.?)\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{5,})"),
]

print(f"=== PAPERLESS SMART ROUTER v4 · Dokument #{DOC_ID} ({DOC_FILENAME}) ===")

if not DOC_ID:
    print("Fehler: Kein DOCUMENT_ID von Paperless übergeben.")
    sys.exit(0)

if not OLLAMA_URL and not GEMINI_API_KEY:
    print("Fehler: Weder OLLAMA_URL noch GEMINI_API_KEY gesetzt — Router kann nicht klassifizieren.")
    sys.exit(0)


def paperless_auth_header():
    return f"Token {PAPERLESS_API_TOKEN}"


def paperless_request(path, method="GET", body=None):
    url = f"{PAPERLESS_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", paperless_auth_header())
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"Paperless-API-Fehler {method} {path}: {e.code} {e.read()[:300]}")
        return None
    except Exception as e:
        print(f"Paperless-API-Fehler {method} {path}: {e}")
        return None


def get_or_create(endpoint, name):
    """Liefert die ID eines Correspondent/DocumentType/Tag anhand des Namens,
    legt ihn bei Bedarf an."""
    if not name:
        return None
    found = paperless_request(f"/{endpoint}/?name__iexact={urllib.parse.quote(name)}")
    if found and found.get("results"):
        return found["results"][0]["id"]
    created = paperless_request(f"/{endpoint}/", method="POST", body={"name": name})
    return created["id"] if created else None


def get_paperless_document(doc_id):
    return paperless_request(f"/documents/{doc_id}/")


doc_data = get_paperless_document(DOC_ID)
if not doc_data:
    sys.exit(1)

content = (doc_data.get("content") or "")[:5000]  # Erste 5000 Zeichen genügen für Header/Metadaten und beschleunigen CPU-Inferenz
title = doc_data.get("title", DOC_FILENAME)

# 22.08.2026: Dateien ohne (oder mit kaum) OCR-Text -- typischerweise
# Fotos ohne Text, die die vorgelagerte Triage faelschlich als "Dokument"
# statt "Foto" einsortiert hat -- nicht wie ein normales Dokument
# durchlaufen lassen. Sonst bekommen sie einen erfundenen Titel/Absender
# und moeglicherweise eine Odoo-Aufgabe, obwohl nichts Verwertbares im
# Bild erkannt wurde. Stattdessen klar markieren, damit von Hand geprueft
# werden kann, ob es doch ein Dokumentenfoto ist.
if len(content.strip()) < 20:
    print(f"OCR-Text zu kurz/leer ({len(content.strip())} Zeichen) — "
          f"vermutlich Foto ohne Text, wird nur markiert statt klassifiziert.")
    review_tag_id = get_or_create("tags", "ocr-leer-pruefen")
    tag_ids = [t for t in [review_tag_id] if t]
    paperless_request(f"/documents/{DOC_ID}/", method="PATCH",
                       body={"tags": tag_ids} if tag_ids else {})
    print("=== SMART ROUTER v4 FERTIG (uebersprungen, kein OCR-Text) ===")
    sys.exit(0)


def build_classification_prompt(text, title_str):
    return f"""Du bist der digitale Assistent der FraWo GbR.
Analysiere das folgende eingescannte Dokument aufmerksam. Erkenne selbstständig neue oder bestehende Absender, erfasse den Sachverhalt und den richtigen Empfänger (Wolf_Prinz, Franz_Bienert, FraWo_GbR, Alois_Prinz, Heidi_Prinz).

Titel: {title_str}
Text (OCR, ggf. unvollständig):
---
{text}
---

Antworte NUR mit einem gültigen JSON-Objekt im folgenden Format:
{{
  "entity": "Wolf_Prinz" | "Franz_Bienert" | "Alois_Prinz" | "Heidi_Prinz" | "FraWo_GbR",
  "category": "finanzen" | "vertraege" | "amt_behoerden" | "gesundheit" | "wohnen" | "arbeit" | "projekte" | "sonstiges",
  "document_type": "Rechnung" | "Quittung" | "Mahnung" | "Vertrag" | "Bescheid" | "Kontoauszug" | "Versicherungspolice" | "Zeugnis" | "Bewerbung" | "Kündigung" | "Antrag" | "Angebot" | "Sonstiges",
  "vendor": "<Absender/Firma/Behörde, präzise und vollständig>",
  "document_date": "<Datum AUF dem Dokument selbst, YYYY-MM-DD, oder null wenn nicht erkennbar>",
  "clean_title": "<kurzer, sauberer Titel nach dem Muster 'Dokumenttyp Absender Datum', z.B. 'Rechnung Thomann GmbH 2026-08-15', OHNE Dateiendung. Ist kein Datum erkennbar: Datum im Titel weglassen>",
  "amount": <Gesamtbetrag in der Waehrung des Belegs, 0.0 wenn kein Betrag>,
  "waehrung": "<ISO-Code der Waehrung des Betrags, z.B. EUR oder USD>",
  "bezahlt": true | false,
  "aktion": "<was ein Mensch jetzt tun muss, 2-4 Woerter mit Verb, z.B. 'Rechnung bezahlen', 'Brief beantworten', oder null>",
  "bestellnummer": "<Bestell- oder Auftragsnummer des Händlers, z.B. Amazon 028-5051623-4280329, oder null>",
  "kostenart": "ausruestung" | "versicherung" | "miete" | "bankgebuehren" | "sonstiges",
  "positionen": [{{"text": "<Artikelbezeichnung wie auf dem Beleg>", "betrag": <Bruttobetrag dieser Zeile in Euro>}}],
  "due_date": "<Fristdatum YYYY-MM-DD oder null>",
  "requires_action": true | false,
  "summary": "<ein präziser deutscher Satz, der den Sachverhalt auf den Punkt bringt>"
}}

Kategorien: finanzen=Rechnungen/Bank/Versicherung, vertraege=Verträge,
amt_behoerden=Ämter/Finanzamt/Bescheide, gesundheit=Arzt/Krankenkasse,
wohnen=Miete/Nebenkosten/Haus, arbeit=Job/Gewerbe/Ausbildung,
projekte=laufende Vorhaben, sonstiges=alles andere.
positionen: jede Artikelzeile einer Rechnung mit ihrem Bruttobetrag (inkl. MwSt),
Versand als eigene Zeile; MwSt/USt NIE als eigene Zeile; leere Liste, wenn es keine Rechnung ist.
kostenart: ausruestung = Technik, Kabel, Werkzeug, Geräte (zum Anfassen); Software, Abos, Online-Dienste = sonstiges; sonst passend oder sonstiges.
Quittung = Zahlungsbestaetigung/Kassenbon/Receipt ueber einen schon bezahlten Kauf oder ein Abo.
bezahlt=true, wenn der Beleg zeigt, dass schon bezahlt wurde (Karte, PayPal, bar, "paid", "payment received").
requires_action=true nur bei echtem Handlungsbedarf (zahlen, antworten,
unterschreiben, Frist einhalten). Ist eine Rechnung bereits bezahlt oder handelt es sich um ein reines Infoschreiben: false."""


def parse_json_flexible(raw_text):
    text = (raw_text or "").strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return json.loads(text)


def call_ollama(text, title_str, basis=None, timeout=120):
    prompt = build_classification_prompt(text, title_str)
    url = f"{(basis or OLLAMA_URL).rstrip('/')}/api/generate"
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = json.loads(r.read().decode("utf-8"))
        res_text = raw.get("response", "")
        return parse_json_flexible(res_text)


def call_gemini(text, title_str):
    prompt = build_classification_prompt(text, title_str)
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read().decode("utf-8"))
    raw_text = resp["candidates"][0]["content"]["parts"][0]["text"]
    return parse_json_flexible(raw_text)


def sanitize_classification(result, title_str):
    if not isinstance(result, dict):
        result = {}
    if result.get("entity") not in ENTITY_MAP:
        result["entity"] = "FraWo_GbR"
    if result.get("category") not in VALID_CATEGORIES:
        result["category"] = "sonstiges"
    if result.get("document_type") not in VALID_DOCUMENT_TYPES:
        result["document_type"] = "Sonstiges"
    if not result.get("clean_title"):
        result["clean_title"] = title_str
    else:
        cleaned = re.sub(r"\s+null\s*$", "", str(result["clean_title"]), flags=re.IGNORECASE).strip()
        result["clean_title"] = cleaned or title_str
    if result.get("document_date"):
        try:
            datetime.strptime(str(result["document_date"]), "%Y-%m-%d")
        except ValueError:
            result["document_date"] = None
    try:
        result["amount"] = float(result.get("amount") or 0)
    except (TypeError, ValueError):
        result["amount"] = 0.0
    if result.get("due_date"):
        try:
            datetime.strptime(str(result["due_date"]), "%Y-%m-%d")
        except ValueError:
            result["due_date"] = None
    if "requires_action" not in result:
        result["requires_action"] = False
    if not result.get("vendor"):
        result["vendor"] = "Unbekannt"
    if not result.get("summary"):
        result["summary"] = f"Dokument: {title_str}"
    if result.get("kostenart") not in KOSTENART_KONTO:
        result["kostenart"] = "sonstiges"
    pos, steuer = [], 0.0
    for p in result.get("positionen") or []:
        try:
            text, betrag = str(p.get("text") or "").strip(), round(float(p.get("betrag") or 0), 2)
        except (AttributeError, TypeError, ValueError):
            continue
        # Steuer ist nie eine Artikelzeile (29.09.2026: ReTech "MwSt.-Betrag 3,18" als eigene Position).
        # Bei genau einer Artikelzeile wird der Steuerbetrag in sie eingerechnet (brutto, § 19).
        if re.search(r"(?i)\b(mwst|ust|umsatzsteuer|mehrwertsteuer|vorsteuer)\b", text):
            steuer += betrag
            continue
        if text and betrag > 0:
            pos.append({"text": text[:200], "betrag": betrag})
    if steuer and len(pos) == 1:
        pos[0]["betrag"] = round(pos[0]["betrag"] + steuer, 2)
    result["positionen"] = pos
    # Sichtbar schon bezahlte Belege brauchen keine Aufgabe fuer Wolf (29.09.2026: smartRepair, EC-Karte;
    # 30.09.2026: GitHub-Quittung auf Englisch, #1585). Eine Quittung ist per Definition bezahlt.
    # Amazon-Rechnungen sind immer schon bezahlt (Versand erst nach Zahlung), nennen aber die
    # Zahlungsart nicht (#1585: Paperless #230 Cable Matters) -> bezahlt, aber keine Auslage ohne Zahlungsquelle.
    amazon = bool(re.search(r"(?i)amazon", content or "") and BESTELLNR_MUSTER[0].search(content or ""))
    result["bezahlt"] = bool(result.get("bezahlt") is True or result["document_type"] == "Quittung"
                             or (result["document_type"] == "Rechnung" and (amazon or BEZAHLT_MUSTER.search(content or ""))))
    if result["bezahlt"] and result["document_type"] in BELEG_TYPEN:
        result["requires_action"] = False
    w = str(result.get("waehrung") or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", w):
        w = "EUR"
    # Die KI liest "$34.00 USD" gern als Euro - der Belegtext entscheidet, wenn er eindeutig ist.
    if w == "EUR" and re.search(r"\bUSD\b|\$\s?\d", content or "") and not re.search(r"€|\bEUR\b", content or ""):
        w = "USD"
    result["waehrung"] = w
    aktion = str(result.get("aktion") or "").strip()
    result["aktion"] = aktion if aktion and aktion.lower() not in ("null", "none", "keine") else None
    bn = result.get("bestellnummer")
    result["bestellnummer"] = str(bn).strip() if bn and str(bn).strip().lower() not in ("null", "none") else None
    return result


def classify_document(text, title_str):
    # 1. Lokale KI: zuerst StudioPC (schnell, aber nicht 24/7), dann OptiPlex (24/7, ~6 Token/s,
    #    daher lange Wartezeit). Reihenfolge seit 29.09.2026, Odoo #1645/#1517.
    for basis, frist in ((OLLAMA_URL, 120), (OLLAMA_URL_OPTIPLEX, 360)):
        if not basis:
            continue
        try:
            print(f"Klassifiziere lokal mit Ollama ({OLLAMA_MODEL} @ {basis}, max. {frist}s)...")
            res = call_ollama(text, title_str, basis, frist)
            if isinstance(res, dict) and (res.get("entity") or res.get("vendor") or res.get("document_type")):
                print(f"Erfolgreich lokal durch Ollama @ {basis} klassifiziert.")
                return sanitize_classification(res, title_str)
        except Exception as e:
            print(f"Warnung: Ollama @ {basis} fehlgeschlagen ({e}). Nächster Weg...")

    # 2. Cloud-Fallback (Gemini)
    if GEMINI_API_KEY:
        try:
            print(f"Klassifiziere mit Gemini Cloud ({GEMINI_MODEL})...")
            res = call_gemini(text, title_str)
            if isinstance(res, dict):
                print("Erfolgreich durch Gemini Cloud klassifiziert.")
                return sanitize_classification(res, title_str)
        except Exception as e:
            print(f"Warnung: Gemini-Aufruf fehlgeschlagen ({e}).")

    # 3. Alle KI-Dienste ausgefallen. Frueher entstand hier eine Aufgabe "Unbekannt — 0,00 €"
    #    (#1585, 24.09.2026: StudioPC aus + Gemini 503). Jetzt: keine Aufgabe, keine Buchung -
    #    nur das Paperless-Schlagwort KI_AUSFALL_TAG; nachholen per Neulauf (README.md).
    print("Alle KI-Dienste fehlgeschlagen — keine Auswertung, Dokument wird zum Nachholen markiert.")
    return None


def ezb_kurs(waehrung, datum):
    """EZB-Referenzkurs (1 EUR = x Waehrung) am Belegdatum bzw. letzten Bankarbeitstag davor."""
    ende = datum or datetime.now().strftime("%Y-%m-%d")
    start = (datetime.strptime(ende, "%Y-%m-%d") - timedelta(days=10)).strftime("%Y-%m-%d")
    url = (f"https://data-api.ecb.europa.eu/service/data/EXR/D.{waehrung}.EUR.SP00.A"
           f"?startPeriod={start}&endPeriod={ende}&format=csvdata")
    with urllib.request.urlopen(url, timeout=20) as r:
        zeilen = r.read().decode("utf-8").strip().splitlines()
    kopf = zeilen[0].split(",")
    letzte = zeilen[-1].split(",")
    return letzte[kopf.index("TIME_PERIOD")], float(letzte[kopf.index("OBS_VALUE")])


def in_euro_umrechnen(info):
    """Fremdwaehrung -> EUR nach EZB-Kurs; Originalbetrag bleibt im Zeilentext sichtbar.
    Klappt die Umrechnung nicht, wird NICHT gebucht (info['umrechnung_fehlt'])."""
    w = info.get("waehrung") or "EUR"
    if w == "EUR" or not info.get("amount"):
        return info
    try:
        kurstag, kurs = ezb_kurs(w, info.get("document_date"))
    except Exception as e:
        print(f"EZB-Kurs {w} nicht abrufbar ({e}) — keine automatische Buchung.")
        info["umrechnung_fehlt"] = True
        return info
    fmt = lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    info["amount_original"] = info["amount"]
    info["amount"] = round(info["amount"] / kurs, 2)
    pos = [{"text": f"{p['text']} ({fmt(p['betrag'])} {w})"[:200], "betrag": round(p["betrag"] / kurs, 2)}
           for p in info.get("positionen") or []]
    # Rundungsdifferenz in die letzte Zeile, damit die Zeilen exakt den Gesamtbetrag ergeben.
    if pos and abs(sum(p["betrag"] for p in pos) - info["amount"]) <= 0.05:
        pos[-1]["betrag"] = round(pos[-1]["betrag"] + info["amount"] - sum(p["betrag"] for p in pos), 2)
    info["positionen"] = pos
    info["kurs_hinweis"] = (f"{fmt(info['amount_original'])} {w} = {fmt(info['amount'])} € "
                            f"(EZB-Referenzkurs {kurstag}: 1 EUR = {kurs} {w})")
    print(f"Umgerechnet: {info['kurs_hinweis']}")
    return info


classification = classify_document(content, title)
if classification is None:
    if PROBE:
        print("PROBE: KI ausgefallen -> Plan: nur Paperless-Schlagwort, keine Aufgabe, keine Buchung.")
        sys.exit(0)
    tag_id = get_or_create("tags", KI_AUSFALL_TAG)
    if tag_id:
        alt = [t for t in (doc_data.get("tags") or [])]
        paperless_request(f"/documents/{DOC_ID}/", method="PATCH", body={"tags": sorted(set(alt + [tag_id]))})
    print(f"=== SMART ROUTER v4 FERTIG (KI ausgefallen, Schlagwort '{KI_AUSFALL_TAG}' gesetzt) ===")
    sys.exit(0)
classification = in_euro_umrechnen(classification)
print("Klassifikation:")
print(json.dumps(classification, indent=2, ensure_ascii=False))


def ist_gbr_beleg(info):
    # "Wolfeetech" = GitHub-Organisation der GbR (github.com/Wolfeetech/FraWo), #1585.
    return info.get("entity") == "FraWo_GbR" or bool(re.search(r"(?i)frawo|wolfeetech", content or ""))


def als_rechnung_buchen(info):
    return (info.get("document_type") in BELEG_TYPEN and float(info.get("amount") or 0) > 0
            and info.get("entity") in ("FraWo_GbR", "Wolf_Prinz") and not info.get("umrechnung_fehlt"))


def auslage_nachweis(info):
    """Liefert (ist_auslage, Grund). Auslage Wolf = bezahlter GbR-Beleg, den Wolf nachweislich mit
    eigenem Zahlungsmittel bezahlt hat -> FraWo schuldet ihm den Betrag (Wolf_Einkauf_JJJJ_NN,
    Zahlung im Journal AUSLAGE_JOURNAL_CODE). Fehlt der Nachweis, bleibt die Rechnung Entwurf."""
    text = content or ""
    if not info.get("bezahlt"):
        return False, "Beleg nicht als bezahlt erkannt"
    if not ist_gbr_beleg(info):
        return False, "kein GbR-Beleg"
    if GBR_KONTO_MUSTER.search(text):
        return False, "von einem GbR-Konto bezahlt"
    zm = ZAHLMITTEL_MUSTER.search(text)
    if not zm:
        return False, "kein ausdrückliches Zahlungsmittel im Beleg (Quittung/„bezahlt“ allein reicht nicht)"
    if not WOLF_ZAHLER_MUSTER.search(text):
        return False, f"Zahlungsmittel „{zm.group(0)}“ ohne Wolf als Zahler im Beleg"
    return True, f"Zahlungsmittel „{zm.group(0)}“, Zahler Wolf"


def als_auslage_wolf(info):
    return auslage_nachweis(info)[0]


def aufgabe_pruefen(info):
    """Qualitaetsregel (siehe oben). Liefert (erlaubt, Grund)."""
    if info.get("bezahlt") and info.get("document_type") in BELEG_TYPEN:
        return False, "Beleg ist bezahlt — wird gebucht, keine Aufgabe"
    if info.get("umrechnung_fehlt"):
        return True, "Fremdwährung ohne Kurs — Mensch muss buchen"
    if not (info.get("requires_action") or info.get("action_required")):
        return False, "kein Handlungsbedarf"
    if not info.get("vendor") or info["vendor"] == "Unbekannt":
        return False, "Absender unbekannt — daraus wird niemand schlau"
    if not (info.get("aktion") or AKTION_JE_TYP.get(info.get("document_type"))):
        return False, "keine konkrete Aktion erkennbar"
    return True, "Handlungsbedarf"


if PROBE:
    ok, grund = aufgabe_pruefen(classification)
    print("PROBE-Plan (nichts wird geschrieben):")
    ausl_ok, ausl_grund = auslage_nachweis(classification)
    print(f"  Rechnung buchen: {als_rechnung_buchen(classification)}"
          f" · als bezahlte Auslage Wolf (Journal {AUSLAGE_JOURNAL_CODE}): "
          f"{als_rechnung_buchen(classification) and ausl_ok} ({ausl_grund})")
    print(f"  Odoo-Aufgabe: {'ja' if ok else 'nein'} ({grund})")
    sys.exit(0)

# --- Paperless-Metadaten setzen (Correspondent, Dokumenttyp, Tags, Titel) ---
correspondent_id = get_or_create("correspondents", classification["vendor"])
document_type_id = get_or_create("document_types", classification["document_type"])
entity_tag_id = get_or_create("tags", classification["entity"].replace("_", " "))
category_tag_id = get_or_create("tags", classification["category"])

patch_body = {"title": classification["clean_title"]}
if correspondent_id:
    patch_body["correspondent"] = correspondent_id
if document_type_id:
    patch_body["document_type"] = document_type_id
tag_ids = [t for t in (entity_tag_id, category_tag_id) if t]
if tag_ids:
    patch_body["tags"] = tag_ids
if classification.get("document_date"):
    patch_body["created"] = f"{classification['document_date']}T00:00:00Z"

paperless_request(f"/documents/{DOC_ID}/", method="PATCH", body=patch_body)
print(f"Paperless-Metadaten gesetzt: {patch_body}")


# --- Ablage zurück nach Google Drive (bestehende Ordnerstruktur) ---
FOLDER_MAP = {
    "finanzen": "10_Finanzen & Versicherung",
    "vertraege": "20_Verträge",
    "amt_behoerden": "30_Amt & Behörden ",
    "gesundheit": "40_Gesundheit",
    "wohnen": "50_Wohnen",
    "arbeit": "60_Arbeit und Gewebe",
    "projekte": "70_Projekte",
    "sonstiges": "99_Archiv",
}


def safe_filename(text, fallback):
    cleaned = "".join(c for c in (text or "") if c not in '/\\:*?"<>|').strip()
    return cleaned or fallback


def file_to_drive(doc, classification, doc_id):
    # Über die API laden statt Pfade zu erraten: Paperless legt fuer
    # Text-Dateien keine "archived"-Version an (kein OCR noetig), fuer
    # Scans schon — der Download-Endpunkt liefert in beiden Faellen die
    # richtige, beste verfuegbare Version.
    archived_name = doc.get("archived_file_name") or doc.get("original_file_name") or ""
    ext = os.path.splitext(archived_name)[1] or ".pdf"
    target_folder = FOLDER_MAP.get(classification["category"], "99_Archiv")
    doc_title = classification.get("clean_title") or doc.get("title") or title
    target_name = safe_filename(doc_title, f"dokument_{doc_id}") + ext

    req = urllib.request.Request(f"{PAPERLESS_URL}/documents/{doc_id}/download/")
    req.add_header("Authorization", paperless_auth_header())
    tmp_path = f"/tmp/gdrive_filing_{doc_id}{ext}"
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(tmp_path, "wb") as out:
            out.write(r.read())
    except Exception as e:
        print(f"Download fuer Drive-Ablage fehlgeschlagen: {e}")
        return False

    try:
        result = subprocess.run(
            [
                "rclone", "--config", "/etc/rclone/rclone.conf",
                "copyto", tmp_path, f"gdrive:{target_folder}/{target_name}",
            ],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            print(f"rclone-Fehler bei der Drive-Ablage: {result.stderr[:400]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"rclone Timeout (>180s) bei Drive-Ablage fuer {target_name}")
        return False
    except Exception as e:
        print(f"Unerwarteter Fehler bei Drive-Ablage: {e}")
        return False
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    print(f"In Drive abgelegt: {target_folder}/{target_name}")
    return True


if file_to_drive(doc_data, classification, DOC_ID):
    done_tag_id = get_or_create("tags", "gdrive-abgelegt")
    if done_tag_id:
        existing_tags = patch_body.get("tags", [])
        paperless_request(f"/documents/{DOC_ID}/", method="PATCH",
                           body={"tags": existing_tags + [done_tag_id]})


PROJECT_TASK_MODEL_ID = 522  # ir.model-ID von project.task
TODO_ACTIVITY_TYPE_ID = 4    # mail.activity.type "To-Do"


def upsert_todo_activity(models, uid, task_id, user_id, due_date, summary):
    """Legt eine To-Do-Aktivitaet auf der Aufgabe an (oder zieht die Frist
    einer schon vorhandenen nach) -- damit taucht das in der persoenlichen
    To-do-Liste auf, nicht nur auf dem Projekt-Board."""
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'mail.activity', 'search',
        [[
            ['res_model_id', '=', PROJECT_TASK_MODEL_ID],
            ['res_id', '=', task_id],
            ['activity_type_id', '=', TODO_ACTIVITY_TYPE_ID],
        ]],
        {'limit': 1},
    )
    if existing:
        models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'mail.activity', 'write',
                           [existing, {'date_deadline': due_date, 'summary': summary}])
    else:
        models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'mail.activity', 'create', [{
            'res_model_id': PROJECT_TASK_MODEL_ID,
            'res_id': task_id,
            'activity_type_id': TODO_ACTIVITY_TYPE_ID,
            'user_id': user_id,
            'date_deadline': due_date,
            'summary': summary,
        }])


# --- Odoo-Aufgabe bei Handlungsbedarf ---
def create_odoo_task(info, doc_id, doc_title):
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        if not uid:
            print("Odoo-Login fehlgeschlagen.")
            return None
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # Loop-Schutz (Task #1008): Eigene FraWo/Odoo-Mails erzeugen nie rekursive Aufgaben
        vendor_lower = (info.get("vendor") or "").lower()
        summary_lower = (info.get("summary") or "").lower()
        if any(x in vendor_lower or x in summary_lower for x in ["info@frawo.tech", "noreply@frawo", "odoo-bot", "tagesbericht", "servassi"]):
            print(f"Loop-Schutz: Absender/Inhalt '{info.get('vendor')}' ist intern/automatisiert -> keine Odoo-Aufgabe erzeugen.")
            return None

        mapping = ENTITY_MAP[info["entity"]]
        frist_vom_beleg = bool(info.get("due_date"))
        due_date = info.get("due_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        if info.get("umrechnung_fehlt"):
            aktion = f"Beleg in {info.get('waehrung')} buchen"
        else:
            aktion = info.get("aktion") or AKTION_JE_TYP.get(info.get("document_type")) or "Dokument bearbeiten"
        wer = {"Franz_Bienert": "Franz"}.get(info["entity"], "Wolf")
        betrag = f" · Betrag {info['amount']:.2f} €".replace(".", ",") if info.get("amount") else ""

        doc_link = f'<a href="http://10.1.0.100:8000/documents/{doc_id}/details">Paperless-Dokument #{doc_id} ansehen</a>'

        # Erst pruefen, ob zu diesem Absender + dieser Person schon eine OFFENE Aufgabe aus dem
        # Router existiert (gleicher Vorgang) -- dann dort anhaengen. aufgabe_pruefen() hat
        # "Unbekannt" schon ausgeschlossen; frueher sammelten sich unter "Unbekannt" fremde
        # Belege in einer Aufgabe (#1585: GitHub-Quittung + Amazon-Rechnung).
        open_stage_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task.type', 'search',
            [[['name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen', 'Erledigt', 'Abgebrochen']]]],
        )
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
            [[
                ['project_id', '=', mapping["project_id"]],
                ['stage_id', 'in', open_stage_ids],
                ['name', 'ilike', info['vendor']],
                ['description', 'ilike', 'Paperless-Import'],
            ]],
            {'fields': ['id', 'name'], 'limit': 1},
        )

        if existing:
            task_id = existing[0]['id']
            note = f"""<p><b>Weiteres Dokument zum selben Absender (#{doc_id}):</b> {doc_title}</p>
<p>{info['summary']}</p>
<p><b>Betrag:</b> {info['amount']:.2f} € · <b>Frist:</b> {due_date}</p>
<p>{doc_link}</p>"""
            models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'project.task', 'message_post',
                               [[task_id]], {'body': note})
            # Fristen nachziehen, falls die neue naeher/dringlicher ist.
            models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'project.task', 'write',
                               [[task_id], {'date_deadline': due_date}])
            upsert_todo_activity(models, uid, task_id, mapping["user_id"], due_date,
                                  f"{info['vendor']}: {doc_title}")
            print(f"An bestehende Aufgabe #{task_id} angehaengt statt Duplikat (Dokument #{doc_id}).")
        else:
            # Titel = was zu tun ist (ohne Betrag). Erste Zeile = Was · Warum · Bis · Wer.
            task_name = f"📄 {aktion}: {info['vendor']}"[:120]
            frist_text = datetime.strptime(due_date, "%Y-%m-%d").strftime("%d.%m.%Y") + (
                "" if frist_vom_beleg else " (keine Frist auf dem Beleg, +14 Tage)")
            description = f"""<p><b>Was:</b> {aktion} · <b>Warum:</b> {info['summary']} · <b>Bis:</b> {frist_text} · <b>Wer:</b> {wer}</p>
<p>Absender {info['vendor']}{betrag} · Beleg hängt an · {doc_link}</p>
<p><i>Automatischer Paperless-Import #{doc_id}</i></p>"""

            task_vals = {
                'name': task_name,
                'project_id': mapping["project_id"],
                'user_ids': [(4, mapping["user_id"])],
                'date_deadline': due_date,
                'description': description,
            }
            if mapping["partner_id"]:
                task_vals['partner_id'] = mapping["partner_id"]

            task_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'project.task', 'create', [task_vals])
            upsert_todo_activity(models, uid, task_id, mapping["user_id"], due_date,
                                  f"{info['vendor']}: {doc_title}")
            print(f"Odoo-Aufgabe #{task_id} angelegt für {info['entity']} (Dokument #{doc_id}).")

        # PDF direkt als Anhang an die Odoo-Aufgabe haengen fuer In-App Vorschau
        pdf_bytes = None
        try:
            pdf_req = urllib.request.Request(f"{PAPERLESS_URL}/documents/{doc_id}/download/")
            pdf_req.add_header("Authorization", paperless_auth_header())
            with urllib.request.urlopen(pdf_req, timeout=30) as r:
                pdf_bytes = r.read()
            import base64
            att_vals = {
                'name': f"{safe_filename(doc_title, 'dokument')}.pdf",
                'datas': base64.b64encode(pdf_bytes).decode('ascii'),
                'res_model': 'project.task',
                'res_id': task_id,
                'mimetype': 'application/pdf',
            }
            att_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create', [att_vals])
            print(f"PDF #{att_id} direkt als Anhang an Odoo-Aufgabe #{task_id} gehaengt.")
        except Exception as att_err:
            print(f"Warnung: PDF-Anhang an Odoo fehlgeschlagen: {att_err}")

        # Wenn es eine Rechnung/Ausgabe fuer die GbR ist -> automatisch Lieferantenrechnung in Odoo Finanzen anlegen!
        # Sperre gegen doppelte Buchung: derselbe doc_id darf nie zwei account.move erzeugen,
        # z.B. wenn Paperless dasselbe Dokument nach einem Retry/Reprocessing erneut konsumiert.
        if als_rechnung_buchen(info) and info.get("entity") == "FraWo_GbR":
            already_billed = models.execute_kw(
                ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_count',
                [[['ref', 'ilike', f"Paperless #{doc_id}:"]]],
            )
            if already_billed:
                print(f"Lieferantenrechnung fuer Dokument #{doc_id} existiert bereits ({already_billed}x) - ueberspringe, keine doppelte Buchung.")
            else:
                create_odoo_vendor_bill(info=info, doc_id=doc_id, doc_title=doc_title, pdf_bytes=pdf_bytes, models=models, uid=uid)

        return task_id
    except Exception as e:
        print(f"Fehler beim Anlegen der Odoo-Aufgabe: {e}")
        return None


def create_odoo_vendor_bill(info, doc_id, doc_title, pdf_bytes=None, models=None, uid=None):
    try:
        if not models or not uid:
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
            if not uid:
                print("Odoo-Login fehlgeschlagen für Lieferantenrechnung.")
                return None
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        vendor_name = info.get("vendor") or "Unbekannter Lieferant"
        amount = float(info.get("amount") or 0.0)
        if amount <= 0:
            return None

        # Duplikatschutz: Pruefen ob Beleg mit gleicher Paperless-ID schon existiert
        ref_pattern = f"Paperless #{doc_id}:"
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read',
            [[['ref', 'ilike', ref_pattern], ['state', '!=', 'cancel']]], {'fields': ['id', 'name', 'state', 'payment_state']}
        )
        if existing:
            e0 = existing[0]
            print(f"Lieferantenrechnung für Paperless #{doc_id} existiert bereits ({len(existing)}x, #{e0['id']} "
                  f"{e0['name']}: {e0['state']}/{e0['payment_state']}) — keine zweite Rechnung.")
            # Neulauf nach Teilfehler: die Auslage-Schritte pruefen selbst, was schon erledigt ist.
            if len(existing) == 1 and als_auslage_wolf(info):
                als_auslage_bezahlen(models, uid, e0['id'], info.get("document_date") or datetime.now().strftime("%Y-%m-%d"),
                                     vendor_name, doc_title, info)
            return e0['id']

        # 0. Dieselbe Bestellung schon gebucht? Dann Beleg anhaengen statt neue Rechnung (#1645).
        bestellnr = None
        for muster in BESTELLNR_MUSTER:
            m = muster.search(content or "")
            if m:
                bestellnr = m.group(1) if m.groups() else m.group(0)
                break
        bestellnr = bestellnr or info.get("bestellnummer")
        if bestellnr:
            vorhanden = models.execute_kw(
                ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read',
                [[['move_type', '=', 'in_invoice'], ['ref', 'ilike', bestellnr]]],
                {'fields': ['id', 'ref', 'state'], 'limit': 1})
            if vorhanden:
                ziel = vorhanden[0]
                if ziel['state'] == 'draft':
                    models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'write',
                                      [[ziel['id']], {'ref': f"Paperless #{doc_id}: {ziel['ref'] or ''}"[:250]}])
                if pdf_bytes:
                    import base64
                    models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create', [{
                        'name': f"Beleg_{safe_filename(doc_title, 'beleg')}.pdf",
                        'datas': base64.b64encode(pdf_bytes).decode('ascii'),
                        'res_model': 'account.move', 'res_id': ziel['id'], 'mimetype': 'application/pdf'}])
                models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'message_post', [[ziel['id']]], {
                    'body': f"🤖 Paperless-Router: Beleg Paperless #{doc_id} gehört zu Bestellung {bestellnr} "
                            f"und wurde angehängt — keine zweite Rechnung angelegt. Betrag laut Beleg: {amount:.2f} €. "
                            f"Bitte Positionen prüfen.",
                    'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note'})
                print(f"Bestellung {bestellnr} bereits als Rechnung #{ziel['id']} gebucht — Beleg angehängt, keine Dublette.")
                return ziel['id']

        # 0b. Derselbe Beleg nochmal hochgeladen (neue Paperless-Nummer, gleicher Inhalt)?
        #     Stabiles Merkmal: Lieferant + Rechnungsdatum + Betrag (29.09.2026: smartRepair doppelt).
        inv_datum = info.get("document_date")
        if inv_datum:
            gleich = models.execute_kw(
                ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read',
                [[['move_type', '=', 'in_invoice'], ['state', '!=', 'cancel'],
                  ['partner_id.name', 'ilike', vendor_name[:25]], ['invoice_date', '=', inv_datum],
                  ['amount_total', '>=', amount - 0.005], ['amount_total', '<=', amount + 0.005]]],
                {'fields': ['id', 'name'], 'limit': 1})
            if gleich:
                models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'message_post', [[gleich[0]['id']]], {
                    'body': f"🤖 Paperless-Router: Paperless #{doc_id} ist derselbe Beleg (Lieferant, Datum, Betrag {amount:.2f} € gleich) "
                            f"— keine zweite Rechnung angelegt.",
                    'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note'})
                print(f"Gleicher Beleg schon als Rechnung #{gleich[0]['id']} vorhanden — keine Dublette.")
                return gleich[0]['id']

        # 1. Partner suchen oder anlegen
        partners = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'search_read',
                                     [[['name', 'ilike', vendor_name]]], {'fields': ['id', 'name'], 'limit': 1})
        if partners:
            partner_id = partners[0]['id']
        else:
            partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'create',
                                           [{'name': vendor_name, 'supplier_rank': 1}])

        # 2. Aufwandskonto: nach Kostenart, sonst Standardkonto des Einkaufsjournals.
        account_id = False
        code = KOSTENART_KONTO.get(info.get("kostenart"))
        if code:
            acc = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.account', 'search_read',
                                    [[['code', '=', code]]], {'fields': ['id'], 'limit': 1})
            account_id = acc[0]['id'] if acc else False
        if not account_id:
            jr = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.journal', 'search_read',
                                   [[['type', '=', 'purchase']]], {'fields': ['default_account_id'], 'limit': 1})
            account_id = jr[0]['default_account_id'][0] if jr and jr[0]['default_account_id'] else False

        inv_date = info.get("document_date") or datetime.now().strftime("%Y-%m-%d")
        due_date = info.get("due_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # 3. Zeilen: Artikelzeilen nur, wenn ihre Summe exakt zum Gesamtbetrag passt -
        #    sonst eine Zeile mit dem Belegtitel (kein KI-Satz). Steuer immer leer (§ 19).
        positionen = info.get("positionen") or []
        if positionen and abs(sum(p["betrag"] for p in positionen) - amount) <= 0.05:
            zeilen = [(p["text"], p["betrag"]) for p in positionen]
        else:
            zeilen = [(doc_title, amount)]
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner_id,
            'invoice_date': inv_date,
            'invoice_date_due': due_date,
            'ref': f"Paperless #{doc_id}: {(bestellnr + ' ') if bestellnr else ''}{doc_title[:40]}",
            'narration': info.get("kurs_hinweis") or False,
            'invoice_line_ids': [
                (0, 0, {'name': text, 'price_unit': betrag, 'quantity': 1,
                        'account_id': account_id, 'tax_ids': [(6, 0, [])]})
                for text, betrag in zeilen
            ]
        }
        bill_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'create', [bill_vals])
        print(f"Odoo Lieferantenrechnung #{bill_id} für {vendor_name} ({amount:.2f} €) angelegt.")

        if pdf_bytes:
            import base64
            att_vals = {
                'name': f"Beleg_{safe_filename(doc_title, 'beleg')}.pdf",
                'datas': base64.b64encode(pdf_bytes).decode('ascii'),
                'res_model': 'account.move',
                'res_id': bill_id,
                'mimetype': 'application/pdf',
            }
            models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create', [att_vals])
        if als_auslage_wolf(info):
            als_auslage_bezahlen(models, uid, bill_id, inv_date, vendor_name, doc_title, info)
        return bill_id
    except Exception as e:
        print(f"Warnung: Automatische Lieferantenrechnung fehlgeschlagen: {e}")
        return None


def als_auslage_bezahlen(models, uid, bill_id, datum, vendor_name, doc_title, info):
    """Bezahlte GbR-Rechnung, die Wolf nachweislich privat bezahlt hat (auslage_nachweis):
    Nummer Wolf_Einkauf_JJJJ_NN vergeben, buchen und im Journal "Auslagen Wolf" (AUSLAGE_JOURNAL_CODE)
    bezahlen. Die Zahlung bucht direkt auf Konto 201100 "Verbindlichkeit Gesellschafter Wolf Prinz" -
    die GbR schuldet Wolf den Betrag, bis sie ihn erstattet (Entscheidung Wolf 30.09.2026, #1585).

    Idempotent (Jarvis-Review #1585): Jeder XML-RPC-Aufruf ist eine eigene Transaktion, ein Fehler
    mittendrin laesst sich nicht zurueckrollen. Deshalb vor jedem Schritt den Ist-Zustand lesen,
    nach jedem Schritt state/payment_state nachpruefen; ein Neulauf setzt dort fort, wo es haengt.
    Fehlermeldungen nennen den tatsaechlichen Zustand der Rechnung."""
    def rpc(model, method, args, kw=None):
        try:
            return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, method, args, kw or {})
        except xmlrpc.client.Fault as f:
            if "cannot marshal None" in str(f):   # Methode lief, lieferte nur None zurueck
                return None
            raise

    def lesen():
        r = rpc('account.move', 'read', [[bill_id], ['name', 'state', 'payment_state', 'move_type', 'amount_residual']])
        return r[0] if r else None

    stand = None
    try:
        journal = rpc('account.journal', 'search_read', [[['code', '=', AUSLAGE_JOURNAL_CODE]]], {'fields': ['id', 'name'], 'limit': 1})
        if not journal:
            print(f"Warnung: Journal {AUSLAGE_JOURNAL_CODE} fehlt — Auslage für Rechnung #{bill_id} nicht bezahlt.")
            return
        journal_id = journal[0]['id']

        stand = lesen()
        if not stand or stand['move_type'] != 'in_invoice':
            print(f"Warnung: Rechnung #{bill_id} nicht gefunden oder keine Eingangsrechnung ({stand}) — nichts gebucht.")
            return
        if stand['state'] == 'cancel':
            print(f"Rechnung #{bill_id} ({stand['name']}) ist storniert — keine Auslage-Zahlung.")
            return

        # Schritt 1: Nummer Wolf_Einkauf_JJJJ_NN (nur im Entwurf, und nur wenn noch keine vergeben ist)
        if stand['state'] == 'draft' and not str(stand['name'] or '').startswith('Wolf_Einkauf_'):
            jahr = str(datum)[:4]
            namen = rpc('account.move', 'search_read', [[['name', '=like', f'Wolf_Einkauf_{jahr}_%']]], {'fields': ['name']})
            nummern = [int(n['name'].rsplit('_', 1)[1]) for n in namen if n['name'].rsplit('_', 1)[1].isdigit()]
            nr = f"Wolf_Einkauf_{jahr}_{(max(nummern) + 1) if nummern else 1:02d}"
            rpc('account.move', 'write', [[bill_id], {'name': nr, 'invoice_date_due': datum}])
            stand = lesen()
            if stand['name'] != nr:
                raise RuntimeError(f"Nummer {nr} nicht gesetzt")
        nr = stand['name']

        # Schritt 2: buchen
        if stand['state'] == 'draft':
            rpc('account.move', 'action_post', [[bill_id]])
            stand = lesen()
            if stand['state'] != 'posted':
                raise RuntimeError("Buchen fehlgeschlagen")

        # Schritt 3: bezahlen ueber "Auslagen Wolf" - nur, was noch offen ist
        memo = f"Auslage Wolf Prinz - {vendor_name[:40]} {datetime.strptime(datum, '%Y-%m-%d').strftime('%d.%m.%Y')} ({nr})"
        neu_bezahlt = False
        if stand['payment_state'] in ('paid', 'in_payment', 'reversed'):
            print(f"Rechnung #{bill_id} ({nr}) ist schon {stand['payment_state']} — keine weitere Zahlung.")
        else:
            ctx = {'context': {'active_model': 'account.move', 'active_ids': [bill_id]}}
            wiz = rpc('account.payment.register', 'create',
                      [{'journal_id': journal_id, 'payment_date': datum, 'communication': memo}], ctx)
            rpc('account.payment.register', 'action_create_payments', [[wiz]], ctx)
            stand = lesen()
            if stand['payment_state'] not in ('paid', 'in_payment'):
                raise RuntimeError("Zahlung über Auslagen Wolf nicht wirksam")
            neu_bezahlt = True

        if neu_bezahlt:
            nachweis = auslage_nachweis(info)[1]
            rpc('account.move', 'message_post', [[bill_id]], {
                'body': f"🤖 Paperless-Router: Beleg ist bezahlt ({nachweis}) → als <b>Auslage Wolf</b> gebucht, "
                        f"Zahlung im Journal „{journal[0]['name']}“ = Verbindlichkeit der GbR gegenüber Wolf ({memo}). "
                        f"{info.get('kurs_hinweis') or ''} Kleinunternehmer: brutto ohne Vorsteuer.",
                'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note'})
        print(f"Auslage Wolf: Rechnung #{bill_id} = {stand['name']}, {stand['state']}/{stand['payment_state']} ({memo}).")
    except Exception as e:
        try:
            ist = lesen()
            ist_text = f"{ist['name']}: {ist['state']}/{ist['payment_state']}, offen {ist['amount_residual']:.2f} €" if ist else "nicht lesbar"
        except Exception as e2:
            ist_text = f"Zustand nicht lesbar ({e2})"
        print(f"Warnung: Auslage-Buchung für Rechnung #{bill_id} fehlgeschlagen ({e}). "
              f"Tatsächlicher Zustand: {ist_text}. Neulauf setzt dort fort (README).")


# 1. Automatische Lieferantenrechnung in Odoo Finanzen
if als_rechnung_buchen(classification):
    pdf_bytes = None
    try:
        pdf_req = urllib.request.Request(f"{PAPERLESS_URL}/documents/{DOC_ID}/download/")
        pdf_req.add_header("Authorization", paperless_auth_header())
        with urllib.request.urlopen(pdf_req, timeout=30) as r:
            pdf_bytes = r.read()
    except Exception as att_err:
        print(f"Hinweis: PDF fuer Rechnungsanhang konnte nicht geladen werden: {att_err}")
    create_odoo_vendor_bill(info=classification, doc_id=DOC_ID, doc_title=title, pdf_bytes=pdf_bytes)

# 2. Odoo-Aufgabe nur, wenn die Qualitaetsregel erfuellt ist (siehe AUFGABE-Regel oben)
aufgabe_ok, aufgabe_grund = aufgabe_pruefen(classification)
if aufgabe_ok:
    create_odoo_task(classification, DOC_ID, title)
else:
    print(f"Keine Odoo-Aufgabe: {aufgabe_grund}.")

print("=== SMART ROUTER v4 FERTIG ===")
