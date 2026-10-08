#!/usr/bin/env python3
"""
FraWo Task-Strukturierer & Wünsche-Führer (Ollama-Mehrwert)
==========================================================
Zweck:
  Nimmt Freitext/Sprachnotizen von Wolf entgegen, analysiert und zerlegt
  sie mit lokalem Ollama (GPU StudioPC bevorzugt, Fallback OptiPlex 24/7),
  prüft Duplikate in Odoo und erstellt/führt sauber formatierte Odoo-Tasks
  gemäß den FraWo-Projektregeln (AGENTS.md).

Aufruf:
  python frawo_task_structurer.py "Mein Wunsch..."
  python frawo_task_structurer.py --create "Mein Wunsch..."  (Sofort anlegen)
  python frawo_task_structurer.py                           (Interaktiver Dialog)
"""

import sys
import os
import json
import re
import time
import urllib.request
import urllib.error
import xmlrpc.client
from pathlib import Path

# UTF-8 Setup
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

# ── Odoo-Verbindung & Konfiguration ───────────────────────────────────────────
_env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip()
            if k not in os.environ or os.environ[k].startswith("${"):
                os.environ[k] = v

def _clean_val(val):
    if not val or (isinstance(val, str) and val.startswith("${") and val.endswith("}")):
        return None
    return val

ODOO_URL = _clean_val(os.environ.get("ODOO_RPC_URL")) or _clean_val(os.environ.get("ODOO_URL")) or "http://10.1.0.112:8069"
if not ODOO_URL.startswith("http://") and not ODOO_URL.startswith("https://"):
    ODOO_URL = f"http://{ODOO_URL}"
ODOO_DB = _clean_val(os.environ.get("ODOO_RPC_DB")) or _clean_val(os.environ.get("ODOO_DB_GBR")) or "FraWo_GbR"
ODOO_USER = _clean_val(os.environ.get("ODOO_RPC_USER")) or _clean_val(os.environ.get("ODOO_USER")) or "agent@frawo.tech"
ODOO_PASS = (_clean_val(os.environ.get("ODOO_RPC_PASSWORD"))
             or _clean_val(os.environ.get("ODOO_PASSWORD")) or "JarvisAgent2026!FraWo")

# Ollama-Endpunkte Kaskade (StudioPC GPU lokal & LAN, Fallback OptiPlex 24/7 CPU)
OLLAMA_ENDPOINTS = [
    ("http://127.0.0.1:11434", "frawo-mitarbeiter:latest", "StudioPC GPU (lokal)"),
    ("http://10.0.0.156:11434", "frawo-mitarbeiter:latest", "StudioPC GPU (LAN 10.0.0.156)"),
    ("http://10.1.0.227:11434", "frawo-mitarbeiter-fast:latest", "OptiPlex 7050 CPU 24/7"),
]

PROJECT_MAP = {
    160: {"name": "🔧 20 · Werkstatt & Lautsprecherbau", "icon": "🔧", "keywords": ["werkstatt", "lautsprecher", "gehäuse", "holz", "leimen", "lackieren", "löten", "fräsen", "chassis", "subwoofer"]},
    104: {"name": "💼 10 · Aufträge & Events", "icon": "💼", "keywords": ["event", "veranstaltung", "kunde", "gig", "hochzeit", "party", "verleih", "pa-anlage", "tontechnik vor ort"]},
    110: {"name": "🎨 70 · Marke & Website", "icon": "🎨", "keywords": ["website", "web", "marke", "design", "frawo.tech", "flyer", "logo", "text", "seo"]},
    159: {"name": "🎬 30 · Studio Villa (Rothkreuz 14)", "icon": "🎬", "keywords": ["studio", "tonstudio", "regie", "aufnahme", "akustik", "mikrofon", "villa", "rothkreuz"]},
    161: {"name": "📻 40 · Radio FraWo Funk", "icon": "📻", "keywords": ["radio", "azuracast", "stream", "sendung", "moderation", "playlist", "track", "jingle"]},
    105: {"name": "🛠️ 50 · IT & Infrastruktur", "icon": "🛠️", "keywords": ["server", "proxmox", "odoo", "netzwerk", "docker", "backup", "ct150", "ct160", "ct140", "ollama", "wifi", "lan", "vpn"]},
    162: {"name": "🪴 80 · GrowBox — Testmodell Indoor Gardening", "icon": "🪴", "keywords": ["growbox", "pflanzen", "garten", "sensoren", "licht", "belüftung", "bewässerung"]},
    163: {"name": "💶 60 · Business, Recht & Finanzen", "icon": "💶", "keywords": ["rechnung", "steuer", "finanzamt", "vertrag", "bank", "konto", "buchhaltung", "geld", "kosten"]},
    106: {"name": "🏡 90 · Familie & Immobilien (Stockenweiler)", "icon": "🏡", "keywords": ["stockenweiler", "haus", "grundstück", "familie", "eltern", "umbau", "gartenarbeit"]},
    107: {"name": "🔒 99 · Wolf: Privat & Beruf (Inselhalle)", "icon": "🔒", "keywords": ["inselhalle", "dienstplan", "arbeitszeit", "privat", "arzt", "führerschein", "persönlich"]},
    32:  {"name": "📥 Eingang / Inbox", "icon": "📥", "keywords": ["inbox", "sonstiges", "unklar"]}
}

USER_MAP = {
    "wolf": 7,
    "franz": 8,
}

STAGE_IDEE = 316
STAGE_BACKLOG = 1
STAGE_NAECHSTES = 2

# ── Odoo XML-RPC Client ───────────────────────────────────────────────────────
class OdooClient:
    def __init__(self):
        self.common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
        self.uid = self.common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        if not self.uid:
            raise RuntimeError(f"Odoo Login fehlgeschlagen ({ODOO_USER}@{ODOO_DB})")
        self.models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def execute(self, model, method, *args, **kwargs):
        return self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASS, model, method, list(args), kwargs or {})

    def find_similar_tasks(self, project_id, title_keywords):
        """Sucht offene Aufgaben im selben Projekt mit ähnlichen Begriffen zur Duplikatvermeidung."""
        domain = [
            ("project_id", "=", project_id),
            ("stage_id", "not in", [6, 35]),
            ("active", "=", True)
        ]
        tasks = self.execute("project.task", "search_read", domain, fields=["id", "name", "stage_id"])
        matches = []
        words = set([w.lower() for w in re.findall(r"\w{4,}", title_keywords)])
        for t in tasks:
            t_words = set([w.lower() for w in re.findall(r"\w{4,}", t["name"])])
            common = words.intersection(t_words)
            if common:
                matches.append((t, len(common), list(common)))
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:3]]

    def create_task(self, name, project_id, description_html, stage_id=STAGE_NAECHSTES, priority="1", user_ids=None):
        vals = {
            "name": name,
            "project_id": project_id,
            "description": description_html,
            "stage_id": stage_id,
            "priority": str(priority),
        }
        if user_ids:
            vals["user_ids"] = [(6, 0, user_ids)]
        task_id = self.execute("project.task", "create", [vals])
        return task_id

# ── Ollama Orchestrierung ────────────────────────────────────────────────────
def call_ollama(prompt: str, system_prompt: str) -> dict:
    endpoints = OLLAMA_ENDPOINTS
    last_err = None
    for url, model, desc in endpoints:
        try:
            req = urllib.request.Request(f"{url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status != 200:
                    continue
            
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 1000
                }
            }).encode("utf-8")
            
            t0 = time.time()
            api_req = urllib.request.Request(
                f"{url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(api_req, timeout=90) as api_resp:
                res_data = json.loads(api_resp.read().decode("utf-8"))
                duration = time.time() - t0
                tok_s = res_data.get("eval_count", 0) / (res_data.get("eval_duration", 1) / 1e9)
                return {
                    "node": desc,
                    "model": model,
                    "duration": duration,
                    "tok_s": tok_s,
                    "response": json.loads(res_data.get("response", "{}"))
                }
        except Exception as e:
            last_err = e
            continue
            
    raise RuntimeError(f"Kein Ollama-Knoten erreichbar: {last_err}")

SYSTEM_INSTRUCTION = """Du bist der FraWo Aufgaben-Strukturierer.
Deine Aufgabe ist es, gesprochene oder formlose Wünsche/Notizen von Wolf Prinz in professionelle, saubere Odoo-Projektaufgaben zu strukturieren.

Regeln nach AGENTS.md:
1. Keine Riesen-Mischaufgaben: Wenn Wolf mehrere unabhängige Dinge erwähnt (z. B. Gehäuse leimen UND Buchsen bestellen), zerlege sie in separate, eigenständige Aufgaben!
2. Titel-Format:
   - Kurz, prägnant, mit passendem Projekt-Icon am Anfang.
   - Handlungsverb verwenden.
   - NIEMALS Preise oder Geldbeträge im Titel!
   - Beispiel: "🔧 Subwoofer-Gehäuse leimen und lackieren" oder "💼 Speakon-Buchsen bei Thomann bestellen"
3. Projekt-Zuordnung (genau eine project_id aus dieser Liste):
   160: Werkstatt & Lautsprecherbau (Gehäuse, Löten, Holz, Audio-Hardware, Franz)
   104: Aufträge & Events (Mietanfragen, Event-Planung, Gigs, Kabel packen vor Ort)
   110: Marke & Website (frawo.tech, CI, Design, Text)
   159: Studio Villa (Rothkreuz 14, Regie, Recording, Akustik)
   161: Radio FraWo Funk (Sendungen, AzuraCast, Musik)
   105: IT & Infrastruktur (Server, Proxmox, Odoo, Netzwerk, Docker, Shelly)
   162: GrowBox — Indoor Gardening (Sensoren, Steuerung, Pflanzen)
   163: Business, Recht & Finanzen (Rechnungen, Buchhaltung, Steuern, Verträge)
   106: Familie & Immobilien (Stockenweiler)
   107: Wolf: Privat & Beruf (Inselhalle, persönliche Termine)
   32: Eingang / Inbox (nur wenn völlig unklar)
4. Beschreibung:
   Formatieren mit:
   - Was: [Konkrete Aufgabe]
   - Warum: [Zweck / Hintergrund]
   - Bis wann: [Frist falls genannt oder 'Offen']
   - Wer: [Wolf / Franz / Agent]
   - Fertig, wenn: [Klares Akzeptanzkriterium / Definition of Done]
5. Dringlichkeit:
   - stage: "naechstes" (für dringende, anstehende Aufgaben) oder "backlog" (für später) oder "idee" (für vage Einfälle)
   - priority: "0" (Normal), "1" (Wichtig), "2" (Sehr dringend)

Antworte IMMER im folgenden JSON-Schema:
{
  "tasks": [
    {
      "title": "Icon + Titel",
      "project_id": 160,
      "project_name": "Name des Projekts",
      "stage": "naechstes" oder "backlog" oder "idee",
      "priority": "1",
      "assigned_to": "Wolf" oder "Franz",
      "was": "...",
      "warum": "...",
      "bis_wann": "...",
      "wer": "...",
      "fertig_wenn": "..."
    }
  ]
}
"""

def process_wish(freitext: str, auto_create: bool = False, dry_run: bool = False):
    print("=" * 72)
    print("🚀 FraWo Task-Strukturierer — Eingabe:")
    print(f"   \"{freitext}\"")
    print("=" * 72)
    
    # 1. Ollama aufrufen
    print("▶ Lokales KI-Modell (Ollama) analysiert...")
    res = call_ollama(freitext, SYSTEM_INSTRUCTION)
    print(f"✔ Modell: {res['model']} auf {res['node']} in {res['duration']:.2f}s ({res['tok_s']:.1f} tok/s)\n")
    
    tasks_data = res["response"].get("tasks", [])
    if not tasks_data:
        print("❌ Keine Aufgaben im Modell-Ergebnis gefunden.")
        return []

    print(f"📋 Gefundene Aufgabe(n): {len(tasks_data)}\n")
    
    odoo = OdooClient()
    prepared = []
    
    for i, t in enumerate(tasks_data, 1):
        pid = t.get("project_id", 32)
        pname = PROJECT_MAP.get(pid, {}).get("name", t.get("project_name", "Eingang"))
        title = t.get("title", "Unbenannte Aufgabe")
        stage_str = t.get("stage", "naechstes")
        stage_id = STAGE_NAECHSTES if stage_str == "naechstes" else (STAGE_IDEE if stage_str == "idee" else STAGE_BACKLOG)
        priority = t.get("priority", "1")
        
        desc_html = f"""<p><b>Was:</b> {t.get('was', '')}</p>
<p><b>Warum:</b> {t.get('warum', '')}</p>
<p><b>Bis wann:</b> {t.get('bis_wann', 'Offen')}</p>
<p><b>Wer:</b> {t.get('wer', 'Wolf')}</p>
<hr>
<p><b>Fertig, wenn (Definition of Done):</b><br>{t.get('fertig_wenn', '')}</p>
<p style="color:#888; font-size:85%">🤖 Automatisch strukturiert via Ollama ({res['model']}) am {time.strftime('%d.%m.%Y %H:%M')}</p>
"""
        similar = odoo.find_similar_tasks(pid, title + " " + t.get("was", ""))
        
        print(f"[{i}/{len(tasks_data)}] {title}")
        print(f"      Projekt:    {pname} (ID {pid})")
        print(f"      Stufe:      {'📥 Als Nächstes' if stage_id == STAGE_NAECHSTES else ('💡 Idee' if stage_id == STAGE_IDEE else '📋 Backlog')}")
        print(f"      Zuweisung:  {t.get('assigned_to', 'Wolf')}")
        print(f"      DoD:        {t.get('fertig_wenn', '')}")
        
        if similar:
            print("      ⚠️ ÄHNLICHE OFFENE TASKS:")
            for s in similar:
                print(f"         -> #{s['id']}: {s['name']} ({s['stage_id'][1]})")
        else:
            print("      ✔ Keine offenen Duplikate gefunden.")
        print()
        
        prepared.append({
            "title": title,
            "project_id": pid,
            "desc_html": desc_html,
            "stage_id": stage_id,
            "priority": priority,
            "assigned_to": t.get("assigned_to", "Wolf")
        })

    if dry_run:
        print("ℹ️ [Dry-Run Modus: Keine Anlage in Odoo]")
        return prepared

    # Nachfrage oder Direktanlage
    should_create = auto_create
    if not auto_create:
        try:
            choice = input(f"Sollen diese {len(prepared)} Aufgabe(n) jetzt in Odoo angelegt werden? [J/n]: ").strip().lower()
            should_create = (choice in ("", "j", "ja", "y", "yes"))
        except (EOFError, KeyboardInterrupt):
            should_create = False

    if should_create:
        print("\n🚀 Lege Aufgaben in Odoo an...")
        for p in prepared:
            assigned_name = str(p["assigned_to"]).lower()
            u_ids = [USER_MAP["wolf"]] if "wolf" in assigned_name else ([USER_MAP["franz"]] if "franz" in assigned_name else [USER_MAP["wolf"]])
            new_id = odoo.create_task(p["title"], p["project_id"], p["desc_html"], p["stage_id"], p["priority"], u_ids)
            if isinstance(new_id, list):
                new_id = new_id[0]
            print(f"✔ Task #{new_id} angelegt: {p['title']}")
            print(f"  Link: {ODOO_URL}/web#id={new_id}&model=project.task&view_type=form")
        print("\n✨ Fertig! Das Aufgaben-Chaos ist erfolgreich geordnet.")
    else:
        print("\nAbgebrochen. Nichts in Odoo gespeichert.")
        
    return prepared

if __name__ == "__main__":
    args = sys.argv[1:]
    is_auto = "--create" in args
    is_dry = "--dry-run" in args
    
    clean_args = [a for a in args if not a.startswith("--")]
    
    if clean_args:
        text = " ".join(clean_args)
    else:
        print("=" * 72)
        print("🎤 FraWo Wünsche- & Aufgaben-Eingabe (Ollama Assistent)")
        print("Tippe oder diktiere deine Gedanken / Notizen ein (Enter zum Absenden):")
        print("=" * 72)
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
            
    if text:
        process_wish(text, auto_create=is_auto, dry_run=is_dry)
    else:
        print("Kein Text eingegeben.")
