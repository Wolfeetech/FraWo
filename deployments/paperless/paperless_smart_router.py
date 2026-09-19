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

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.0.0.227:11434")
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
    "Rechnung", "Mahnung", "Vertrag", "Bescheid", "Kontoauszug",
    "Versicherungspolice", "Zeugnis", "Bewerbung", "Kündigung",
    "Antrag", "Angebot", "Sonstiges",
}

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
  "document_type": "Rechnung" | "Mahnung" | "Vertrag" | "Bescheid" | "Kontoauszug" | "Versicherungspolice" | "Zeugnis" | "Bewerbung" | "Kündigung" | "Antrag" | "Angebot" | "Sonstiges",
  "vendor": "<Absender/Firma/Behörde, präzise und vollständig>",
  "document_date": "<Datum AUF dem Dokument selbst, YYYY-MM-DD, oder null wenn nicht erkennbar>",
  "clean_title": "<kurzer, sauberer Titel nach dem Muster 'Dokumenttyp Absender Datum', z.B. 'Rechnung Thomann GmbH 2026-08-15', OHNE Dateiendung. Ist kein Datum erkennbar: Datum im Titel weglassen>",
  "amount": <Zahl in Euro oder 0.0 falls keine Zahlungsaufforderung>,
  "due_date": "<Fristdatum YYYY-MM-DD oder null>",
  "requires_action": true | false,
  "summary": "<ein präziser deutscher Satz, der den Sachverhalt auf den Punkt bringt>"
}}

Kategorien: finanzen=Rechnungen/Bank/Versicherung, vertraege=Verträge,
amt_behoerden=Ämter/Finanzamt/Bescheide, gesundheit=Arzt/Krankenkasse,
wohnen=Miete/Nebenkosten/Haus, arbeit=Job/Gewerbe/Ausbildung,
projekte=laufende Vorhaben, sonstiges=alles andere.
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


def call_ollama(text, title_str):
    prompt = build_classification_prompt(text, title_str)
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
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
    return result


def classify_document(text, title_str):
    # 1. Lokaler KI-Dienst (Ollama auf OptiPlex)
    if OLLAMA_URL:
        try:
            print(f"Klassifiziere primär lokal mit Ollama ({OLLAMA_MODEL} @ {OLLAMA_URL})...")
            res = call_ollama(text, title_str)
            if isinstance(res, dict) and (res.get("entity") or res.get("vendor") or res.get("document_type")):
                print("Erfolgreich lokal durch Ollama klassifiziert.")
                return sanitize_classification(res, title_str)
        except Exception as e:
            print(f"Warnung: Lokaler Ollama-Aufruf fehlgeschlagen ({e}). Wechsle auf Fallback...")

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

    # 3. Sicherer Notfall-Fallback
    print("Alle KI-Dienste fehlgeschlagen — nutze sichere Fallback-Werte.")
    return sanitize_classification({
        "entity": "FraWo_GbR", "category": "sonstiges", "document_type": "Sonstiges",
        "vendor": "Unbekannt", "document_date": None, "clean_title": title_str,
        "amount": 0.0, "due_date": None, "requires_action": True,
        "summary": f"Automatische Auswertung fehlgeschlagen für: {title_str}",
    }, title_str)


classification = classify_document(content, title)
print("Klassifikation:")
print(json.dumps(classification, indent=2, ensure_ascii=False))

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
        due_date = info.get("due_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        doc_link = f'<a href="http://10.1.0.100:8000/documents/{doc_id}/details">Paperless-Dokument #{doc_id} ansehen</a>'

        # Erst pruefen, ob zu diesem Absender + dieser Person schon eine
        # OFFENE Aufgabe existiert (gleicher Fall/Vorgang) -- dann dort
        # anhaengen statt eine weitere, isolierte Aufgabe anzulegen.
        open_stage_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task.type', 'search',
            [[['name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen', 'Erledigt', 'Abgebrochen']]]],
        )
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
            [[
                ['project_id', '=', mapping["project_id"]],
                ['stage_id', 'in', open_stage_ids],
                ['name', 'ilike', f"[{info['entity']}] {info['vendor']}"],
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
            task_name = f"📄 [{info['entity']}] {info['vendor']} — {doc_title}"
            description = f"""<p><b>Automatischer Paperless-Import #{doc_id}</b></p>
<p>{info['summary']}</p>
<p><b>Absender:</b> {info['vendor']}<br/>
<b>Betrag:</b> {info['amount']:.2f} €<br/>
<b>Frist:</b> {due_date}</p>
<p>{doc_link}</p>"""

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
        if info.get("document_type") in ["Rechnung", "Kassenbeleg"] and info.get("amount", 0) > 0 and info.get("entity") == "FraWo_GbR":
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
            ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_count',
            [[['ref', 'ilike', ref_pattern]]]
        )
        if existing > 0:
            print(f"Lieferantenrechnung für Paperless #{doc_id} existiert bereits ({existing}x) — überspringe Duplikat.")
            return None
        
        # 1. Partner suchen oder anlegen
        partners = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'search_read',
                                     [[['name', 'ilike', vendor_name]]], {'fields': ['id', 'name'], 'limit': 1})
        if partners:
            partner_id = partners[0]['id']
        else:
            partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'create',
                                           [{'name': vendor_name, 'supplier_rank': 1}])

        # 2. Aufwandskonto suchen
        expense_accs = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.account', 'search_read',
                                         [[['account_type', '=', 'expense']]], {'fields': ['id'], 'limit': 1})
        account_id = expense_accs[0]['id'] if expense_accs else False

        inv_date = info.get("document_date") or datetime.now().strftime("%Y-%m-%d")
        due_date = info.get("due_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner_id,
            'invoice_date': inv_date,
            'invoice_date_due': due_date,
            'ref': f"Paperless #{doc_id}: {doc_title[:40]}",
            'invoice_line_ids': [
                (0, 0, {
                    'name': info.get("summary") or doc_title,
                    'price_unit': amount,
                    'quantity': 1,
                    'account_id': account_id
                })
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
        return bill_id
    except Exception as e:
        print(f"Warnung: Automatische Lieferantenrechnung fehlgeschlagen: {e}")
        return None


# 1. Automatische Lieferantenrechnung in Odoo Finanzen
if classification.get("document_type") in ["Rechnung", "Kassenbeleg", "Quittung"] and float(classification.get("amount") or 0.0) > 0 and classification.get("entity") in ["FraWo_GbR", "Wolf_Prinz"]:
    pdf_bytes = None
    try:
        pdf_req = urllib.request.Request(f"{PAPERLESS_URL}/documents/{DOC_ID}/download/")
        pdf_req.add_header("Authorization", paperless_auth_header())
        with urllib.request.urlopen(pdf_req, timeout=30) as r:
            pdf_bytes = r.read()
    except Exception as att_err:
        print(f"Hinweis: PDF fuer Rechnungsanhang konnte nicht geladen werden: {att_err}")
    create_odoo_vendor_bill(info=classification, doc_id=DOC_ID, doc_title=title, pdf_bytes=pdf_bytes)

# 2. Odoo-Aufgabe bei Handlungsbedarf
if classification.get("requires_action") or classification.get("action_required"):
    create_odoo_task(classification, DOC_ID, title)
else:
    print("Kein Handlungsbedarf erkannt — keine Odoo-Aufgabe.")

print("=== SMART ROUTER v4 FERTIG ===")
