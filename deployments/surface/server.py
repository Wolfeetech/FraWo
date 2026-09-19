#!/usr/bin/env python3
"""
FraWo Surface Go Portal Server (Port 17827)
Serves frawo_anker_hub.html and provides live telemetry (/api/telemetry)
for weather, Shelly power, system status, and focus tasks for Wolf & Franz.
"""

import http.server
import json
import os
import socket
import threading
import time
import urllib.request
import urllib.error

PORT = 17827
BIND_HOST = "127.0.0.1"
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Thread-safe global cache for telemetry
telemetry_data = {
    "timestamp": 0,
    "weather": {
        "temp": 18.0,
        "apparent_temp": 18.0,
        "code": 0,
        "code_text": "Klar",
        "icon": "☀️",
        "precipitation": 0.0,
        "wind_speed": 5.0,
        "humidity": 65,
    },
    "power": {
        "server_watts": 131.0,
        "server_total_kwh": 511.2,
        "screen_watts": 88.0,
        "screen_state": True,
    },
    "system": {
        "ha_online": True,
        "gateway_online": True,
        "anker_online": True,
        "internet_online": True,
    },
    "focus_franz": [
        {"id": 1406, "title": "Werkstatt arbeitsfähig machen", "sub": "Führungsschiene, Absaugung & Messmikrofon"},
        {"id": 1421, "title": "PSA & Arbeitskleidung", "sub": "Größen Wolf & Franz (42/43, M/S) erfasst"},
        {"id": 1411, "title": "Verleihanlagen & Messung", "sub": "Messung vor Kistenpacken (#1051)"}
    ],
    "focus_wolf": [
        {"id": 1359, "title": "Bar-Abrechnung", "sub": "174,57 € bar an Christiane übergeben"},
        {"id": 1219, "title": "Pixel 9 Pro Displayfehler", "sub": "Google/Back Market Garantie vorziehen (0 €)"},
        {"id": 1430, "title": "Finom GbR-Konto", "sub": "Kontoeröffnung zum Jahreswechsel"}
    ],
    "upcoming_events": [
        {"title": "Leichte Liebe Open Air", "loc": "Bregenz, Beach Bar", "task_id": 1057},
        {"title": "Closing Wasserburg", "loc": "Wasserburg", "task_id": 1059},
        {"title": "Eishalle Einlassshow", "loc": "Lindau Eishalle", "task_id": 1356}
    ]
}
telemetry_lock = threading.Lock()

def weather_code_to_text(code):
    if code == 0:
        return "Klar / Sonnig", "☀️"
    elif code in [1, 2]:
        return "Leicht bewölkt", "🌤️"
    elif code == 3:
        return "Bedeckt", "☁️"
    elif code in [45, 48]:
        return "Nebel", "🌫️"
    elif code in [51, 53, 55]:
        return "Leichter Niesel", "🌦️"
    elif code in [61, 63, 65]:
        return "Regen", "🌧️"
    elif code in [71, 73, 75]:
        return "Schneefall", "🌨️"
    elif code in [80, 81, 82]:
        return "Regenschauer", "🌧️"
    elif code in [95, 96, 99]:
        return "Gewitter", "⛈️"
    return "Bewölkt", "⛅"

def check_tcp_port(host, port, timeout=1.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def fetch_json(url, timeout=2.5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FraWo-Touchboard/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass
    return None

def telemetry_poller():
    """Background thread polling weather and device status every 25 seconds."""
    while True:
        try:
            # 1. Weather (Open-Meteo Lindau/Bodensee: 47.58°N, 9.72°E)
            w_url = (
                "https://api.open-meteo.com/v1/forecast?"
                "latitude=47.58&longitude=9.72&"
                "current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
            )
            w_data = fetch_json(w_url, timeout=3.5)
            
            # 2. Shelly 10.4.0.11 (IT- & Werkstatt-Stromkreis - READ ONLY!)
            s11_data = fetch_json("http://10.4.0.11/rpc/Switch.GetStatus?id=0", timeout=2.0)
            
            # 3. Shelly 10.4.0.10 (TV & StudioPC-Bildschirm)
            s10_data = fetch_json("http://10.4.0.10/rpc/Switch.GetStatus?id=0", timeout=2.0)
            
            # 4. Connectivity checks
            ha_ok = check_tcp_port("10.1.0.40", 8123, timeout=1.5)
            gw_ok = check_tcp_port("10.4.0.1", 53, timeout=1.0) or check_tcp_port("10.1.0.1", 443, timeout=1.0)
            anker_ok = check_tcp_port("10.1.0.92", 22, timeout=1.0)
            inet_ok = check_tcp_port("1.1.1.1", 53, timeout=1.5)

            # 5. Odoo Live Telemetry (Focus Franz, Focus Wolf, Upcoming Events, Hours)
            odoo_info = query_odoo_hubs()
            
            with telemetry_lock:
                telemetry_data["timestamp"] = int(time.time())
                
                if w_data and "current" in w_data:
                    c = w_data["current"]
                    code = c.get("weather_code", 0)
                    desc, icon = weather_code_to_text(code)
                    telemetry_data["weather"] = {
                        "temp": round(c.get("temperature_2m", 18.0), 1),
                        "apparent_temp": round(c.get("apparent_temperature", 18.0), 1),
                        "code": code,
                        "code_text": desc,
                        "icon": icon,
                        "precipitation": c.get("precipitation", 0.0),
                        "wind_speed": round(c.get("wind_speed_10m", 0.0), 1),
                        "humidity": c.get("relative_humidity_2m", 60),
                    }
                
                if s11_data:
                    telemetry_data["power"]["server_watts"] = round(s11_data.get("apower", 0.0), 1)
                    aenergy = s11_data.get("aenergy", {})
                    telemetry_data["power"]["server_total_kwh"] = round(aenergy.get("total", 0.0) / 1000.0, 1)
                    
                if s10_data:
                    telemetry_data["power"]["screen_watts"] = round(s10_data.get("apower", 0.0), 1)
                    telemetry_data["power"]["screen_state"] = bool(s10_data.get("output", True))
                
                telemetry_data["system"]["ha_online"] = ha_ok
                telemetry_data["system"]["gateway_online"] = gw_ok
                telemetry_data["system"]["anker_online"] = anker_ok
                telemetry_data["system"]["internet_online"] = inet_ok

                if odoo_info:
                    telemetry_data["focus_franz"] = odoo_info.get("focus_franz", [])
                    telemetry_data["hubs"] = odoo_info.get("hubs", {})
                    telemetry_data["focus_wolf"] = odoo_info.get("hubs", {}).get("anker", [])
                    telemetry_data["upcoming_events"] = odoo_info.get("upcoming_events", [])
                    telemetry_data["open_questions"] = odoo_info.get("open_questions", [])
                
        except Exception as e:
            pass
        
        time.sleep(25)

# Odoo XML-RPC Helpers
import xmlrpc.client
from urllib.parse import urlparse, parse_qs

ODOO_URL = os.environ.get("ODOO_RPC_URL", "http://10.1.0.112:8069")
ODOO_DB = os.environ.get("ODOO_RPC_DB", "FraWo_GbR")
ODOO_USER = os.environ.get("ODOO_RPC_USER", "agent@frawo.tech")
ODOO_PASS = os.environ.get("ODOO_RPC_PASSWORD", "JarvisAgent2026!FraWo")

def get_odoo_models():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return uid, models

def query_odoo_hubs():
    """Direct XML-RPC query to Odoo for all 4 hubs and open questions."""
    try:
        import datetime, re
        uid, models = get_odoo_models()
        now_dt = datetime.datetime.now()
        two_days_future = (now_dt + datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

        # 1. Franz tasks (strictly actionable tasks assigned to Franz, excluding future event dates)
        raw_franz = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
            [[('active', '=', True), ('user_ids', 'in', [10]), ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes'])]],
            {'fields': ['id', 'name', 'project_id', 'stage_id', 'description', 'date_deadline'], 'limit': 10, 'order': 'stage_id desc, write_date desc'}
        )
        focus_franz = []
        for t in raw_franz:
            pid = t['project_id'][0] if t.get('project_id') else 0
            dl = t.get('date_deadline')
            stage_name = t['stage_id'][1] if t.get('stage_id') else ''
            if pid == 104 and dl and str(dl) > two_days_future and 'In Arbeit' not in stage_name:
                continue
            clean_desc = re.sub(r'<[^>]+>', ' ', t.get('description') or '').strip()
            clean_desc = re.sub(r'\s+', ' ', clean_desc)[:110]
            focus_franz.append({
                "id": t['id'],
                "title": t['name'],
                "sub": clean_desc or stage_name,
                "stage": stage_name,
                "project": t['project_id'][1] if t.get('project_id') else ''
            })
            if len(focus_franz) >= 4:
                break

        # 2. Hub-specific Wolf tasks
        def fetch_tasks(domain, limit=4):
            recs = models.execute_kw(
                ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
                [domain],
                {'fields': ['id', 'name', 'project_id', 'stage_id', 'description', 'date_deadline'], 'limit': limit, 'order': 'stage_id desc, write_date desc'}
            )
            res = []
            for t in recs:
                clean_desc = re.sub(r'<[^>]+>', ' ', t.get('description') or '').strip()
                clean_desc = re.sub(r'\s+', ' ', clean_desc)[:110]
                stage_name = t['stage_id'][1] if t.get('stage_id') else ''
                res.append({
                    "id": t['id'],
                    "title": t['name'],
                    "sub": clean_desc or stage_name,
                    "stage": stage_name,
                    "project": t['project_id'][1] if t.get('project_id') else '',
                    "date": str(t.get('date_deadline') or '')[:10]
                })
            return res

        hubs_data = {
            "anker": fetch_tasks([
                ('active', '=', True),
                ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes']),
                '|', ('tag_ids', 'in', [154]), ('project_id', 'in', [105, 107])
            ]),
            "villa": fetch_tasks([
                ('active', '=', True),
                ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes']),
                '|', ('tag_ids', 'in', [155]), ('project_id', 'in', [159, 160, 161, 162, 163, 110])
            ]),
            "stockenweiler": fetch_tasks([
                ('active', '=', True),
                ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes']),
                '|', ('tag_ids', 'in', [156]), ('project_id', 'in', [106])
            ]),
            "jobs": fetch_tasks([
                ('active', '=', True),
                ('project_id', '=', 104),
                ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen'])
            ], limit=6)
        }

        # 3. Upcoming events (Project 10)
        upcoming_recs = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
            [[('active', '=', True), ('project_id', '=', 104), ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen'])]],
            {'fields': ['id', 'name', 'date_deadline', 'stage_id'], 'limit': 6, 'order': 'date_deadline asc nulls last, id asc'}
        )
        upcoming_events = []
        for ev in upcoming_recs:
            dl = ev.get('date_deadline')
            dt_str = dl[8:10] + '.' + dl[5:7] + '.' if dl and len(dl) >= 10 else ''
            upcoming_events.append({
                "id": ev['id'],
                "title": ev['name'],
                "date": dt_str,
                "stage": ev['stage_id'][1] if ev.get('stage_id') else ''
            })

        # 4. Open questions (Tag 153 '🙋 braucht Wolf')
        q_recs = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
            [[('active', '=', True), ('tag_ids', 'in', [153]), ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen'])]],
            {'fields': ['id', 'name', 'project_id', 'stage_id', 'description'], 'limit': 8, 'order': 'priority desc, write_date desc'}
        )
        open_questions = []
        for qt in q_recs:
            desc = qt.get('description') or ''
            q_text = ""
            if "Offene Fragen" in desc or "Offene Frage" in desc:
                m = re.search(r'(?:<b>\s*Offene Fragen?:\s*</b>|<h3>\s*Offene Fragen?.*?</h3>)(.*?)(?:<h[1-4]>|<p><b>Fertig|$)', desc, re.DOTALL | re.IGNORECASE)
                if m:
                    q_text = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
            if not q_text:
                q_text = re.sub(r'<[^>]+>', ' ', desc).strip()[:180]
            open_questions.append({
                "id": qt['id'],
                "title": qt['name'],
                "project": qt['project_id'][1] if qt.get('project_id') else '',
                "question": q_text,
                "stage": qt['stage_id'][1] if qt.get('stage_id') else ''
            })

        return {
            "focus_franz": focus_franz,
            "hubs": hubs_data,
            "upcoming_events": upcoming_events,
            "open_questions": open_questions
        }
    except Exception as e:
        print(f"query_odoo_hubs error: {e}")
        return None

def call_ollama(prompt, model="frawo-mitarbeiter-fast:latest", timeout=8.0):
    """Call local Ollama on OptiPlex to refine answers."""
    try:
        url = "http://10.1.0.227:11434/api/generate"
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "top_p": 0.9}
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                res_data = json.loads(resp.read().decode("utf-8"))
                return res_data.get("response", "").strip()
    except Exception as e:
        print(f"Ollama call failed: {e}")
    return None

class PortalRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/telemetry":
            qs = parse_qs(parsed.query)
            hub = qs.get("hub", ["anker"])[0]

            with telemetry_lock:
                resp_dict = dict(telemetry_data)
                if "hubs" in resp_dict and hub in resp_dict["hubs"]:
                    resp_dict["focus_wolf"] = resp_dict["hubs"][hub]
                resp_dict["hub"] = hub
                payload = json.dumps(resp_dict).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
            return

        elif parsed.path == "/api/questions":
            # Direct questions list
            hub_odoo = fetch_json("https://frawo.tech/frawo/touch/api/summary", timeout=3.0)
            questions = []
            if hub_odoo and hub_odoo.get("open_questions"):
                questions = hub_odoo["open_questions"]
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "questions": questions}).encode("utf-8"))
            return
            
        elif parsed.path == "/api/screen_toggle":
            # Toggle only living room screen Shelly 10.4.0.10 (NEVER 10.4.0.11!)
            res = fetch_json("http://10.4.0.10/rpc/Switch.Toggle?id=0", timeout=2.0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": res is not None, "result": res}).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/ollama/refine":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                question = data.get("question", "")
                raw_answer = data.get("answer", "")
                
                prompt = (
                    "Du bist der KI-Assistent im FraWo-Betrieb. "
                    "Formuliere die folgende stichpunktartige Antwort von Wolf Prinz zu einer offenen Frage "
                    "in eine präzise, sachliche, kurze Antwort (1-2 Sätze) für den Odoo-Chatter um. "
                    "Regel: Nur Fakten, keine Floskeln, kein 'Hallo/Tschüss'.\n\n"
                    f"Frage: {question}\n"
                    f"Wolfs Notiz: {raw_answer}\n\n"
                    "Formulierte Antwort:"
                )
                refined = call_ollama(prompt) or raw_answer
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "refined": refined}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        elif parsed.path == "/api/task/answer":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                task_id = int(data.get("task_id", 0))
                raw_answer = data.get("answer", "").strip()
                use_ollama = bool(data.get("use_ollama", False))
                question = data.get("question", "")
                
                if not task_id or not raw_answer:
                    raise ValueError("task_id und answer sind erforderlich")

                final_answer = raw_answer
                if use_ollama:
                    prompt = (
                        "Du bist der KI-Assistent im FraWo-Betrieb. "
                        "Formuliere die Antwort von Wolf Prinz zu einer offenen Frage "
                        "in eine präzise, sachliche, kurze Antwort (1-2 Sätze) für den Odoo-Chatter um. "
                        "Regel: Nur Fakten, keine Floskeln.\n\n"
                        f"Frage: {question}\n"
                        f"Wolfs Notiz: {raw_answer}\n\n"
                        "Formulierte Antwort:"
                    )
                    refined = call_ollama(prompt)
                    if refined:
                        final_answer = refined

                # Post to Odoo
                uid, models = get_odoo_models()
                
                # 1. Post chatter message
                chatter_body = f"<p><b>Antwort von Wolf (via FraWo Hub):</b><br>{final_answer}</p>"
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASS,
                    'project.task', 'message_post',
                    [[task_id]],
                    {
                        'body': chatter_body,
                        'message_type': 'comment',
                        'subtype_xmlid': 'mail.mt_comment'
                    }
                )

                # 2. Update tags: remove 153 ('🙋 braucht Wolf'), add 160 ('✅ beantwortet')
                task_data = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASS,
                    'project.task', 'read',
                    [[task_id]],
                    {'fields': ['tag_ids']}
                )
                current_tags = task_data[0].get('tag_ids', []) if task_data else []
                new_tags = [t for t in current_tags if t != 153]
                if 160 not in new_tags:
                    new_tags.append(160)

                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASS,
                    'project.task', 'write',
                    [[task_id], {'tag_ids': [(6, 0, new_tags)]}]
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "task_id": task_id,
                    "answer": final_answer,
                    "message": "Erfolgreich in Odoo erfasst & Tag '✅ beantwortet' gesetzt."
                }).encode("utf-8"))
                return

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        super().do_POST()

    def log_message(self, format, *args):
        # Suppress routine log spam on touchboard
        pass

def main():
    t = threading.Thread(target=telemetry_poller, daemon=True)
    t.start()
    
    server_address = (BIND_HOST, PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, PortalRequestHandler)
    print(f"FraWo Anker Hub Server listening on http://{BIND_HOST}:{PORT} (serving {DIRECTORY})")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
