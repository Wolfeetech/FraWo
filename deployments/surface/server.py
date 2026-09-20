#!/usr/bin/env python3
"""
FraWo Surface Go Portal Server (Port 17827)
Serves frawo_anker_hub.html and provides live telemetry (/api/telemetry)
for weather, Shelly power, system status, and focus tasks for Wolf & Franz.
Also proxies /api/radio/* and /cockpit to Odoo CT140 (10.1.0.112:8069).
"""

import http.server
import json
import os
import socket
import threading
import time
import urllib.request
import urllib.error
import urllib.parse

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
    # Messwerte starten leer (None), nicht mit erfundenen Zahlen: ein Standardwert,
    # der wie eine Messung aussieht, ist schlimmer als gar keine Anzeige.
    "power": {
        "server_watts": None,
        "server_total_kwh": None,
        "screen_watts": None,
        "screen_state": None,
    },
    "system": {
        "ha_online": None,
        "gateway_online": None,
        "anker_online": None,
        "internet_online": None,
    },
    # Aufgaben NIE fest eintippen: eine Kopie ist eine zweite Wahrheit und laeuft
    # ab der ersten Sekunde auseinander (AGENTS.md, Rote Linie 6). Leer heisst hier
    # "noch nichts von Odoo geholt" - die Seite zeigt das als Hinweis an.
    "focus_franz": [],
    "focus_wolf": [],
    "upcoming_events": [],
    "open_questions": [],
    "today_hours": 0.0,
    # Alter der Odoo-Daten: 0 = noch nie erfolgreich geholt. Die Seite blendet
    # eine Warnung ein, sobald das aelter als zwei Minuten ist.
    "odoo_ok": False,
    "odoo_ts": 0,
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

ODOO_SUMMARY_URL = "http://10.1.0.112:8069/frawo/touch/api/summary"
ODOO_CACHE_TTL = 20.0
_odoo_cache = {}
_odoo_cache_lock = threading.Lock()


def get_odoo_summary(hub):
    """Aufgaben fuer EINEN Hub aus Odoo holen, kurz zwischengespeichert.

    Der Hub-Name muss mitgereicht werden - sonst liefert Odoo immer 'anker'
    und der Umschalter auf der Seite wirkt nicht.
    Rueckgabe: (daten_oder_None, alter_in_sekunden).
    """
    hub = hub if hub in ("anker", "villa", "jobs", "stockenweiler") else "anker"
    now = time.time()
    with _odoo_cache_lock:
        cached = _odoo_cache.get(hub)
    if cached and (now - cached[0]) < ODOO_CACHE_TTL:
        return cached[1], now - cached[0]

    data = fetch_json(f"{ODOO_SUMMARY_URL}?hub={hub}", timeout=4.0)
    if data and data.get("success"):
        with _odoo_cache_lock:
            _odoo_cache[hub] = (now, data)
        return data, 0.0

    # Fehlgeschlagen: den letzten bekannten Stand zurueckgeben, aber MIT Alter,
    # damit die Seite ihn als veraltet kennzeichnen kann statt ihn als frisch zu zeigen.
    if cached:
        return cached[1], now - cached[0]
    return None, None


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

            # 5. Odoo Live-Aufgaben: haelt den Zwischenspeicher fuer den Standard-Hub warm.
            #    Die Seite fragt ihren eigenen Hub selbst an (get_odoo_summary).
            get_odoo_summary("anker")

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

                if odoo_data and odoo_data.get("success"):
                    if "focus_franz" in odoo_data and odoo_data["focus_franz"]:
                        telemetry_data["focus_franz"] = odoo_data["focus_franz"]
                    if "focus_wolf" in odoo_data and odoo_data["focus_wolf"]:
                        telemetry_data["focus_wolf"] = odoo_data["focus_wolf"]
                    if "upcoming_events" in odoo_data and odoo_data["upcoming_events"]:
                        telemetry_data["upcoming_events"] = odoo_data["upcoming_events"]
                    if "today_hours" in odoo_data:
                        telemetry_data["today_hours"] = odoo_data["today_hours"]
                
        except Exception as e:
            pass
        
        time.sleep(25)

class PortalRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        # Pfad und Abfrageteil trennen: "/api/telemetry?hub=villa" ist derselbe
        # Endpunkt wie "/api/telemetry". Ein exakter Zeichenkettenvergleich hat hier
        # jede Anfrage mit Hub-Angabe in den Datei-Server laufen lassen -> 404,
        # und die Seite blieb dauerhaft auf ihrem Anfangsstand stehen.
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if route == "/api/telemetry":
            hub = (query.get("hub") or ["anker"])[0]
            if hub not in ("anker", "villa", "jobs", "stockenweiler"):
                hub = "anker"
            odoo_data, odoo_age = get_odoo_summary(hub)

            with telemetry_lock:
                payload = dict(telemetry_data)

            payload["hub"] = hub
            payload["timestamp"] = int(time.time())
            if odoo_data:
                for key in ("focus_franz", "focus_wolf", "upcoming_events",
                            "open_questions", "today_hours"):
                    if key in odoo_data:
                        payload[key] = odoo_data[key]
                payload["odoo_ok"] = odoo_age is not None and odoo_age < ODOO_CACHE_TTL * 3
                payload["odoo_age"] = round(odoo_age, 1) if odoo_age is not None else None
            else:
                # Odoo nicht erreichbar und nichts im Zwischenspeicher: lieber leer
                # anzeigen als einen alten Stand, der wie der aktuelle aussieht.
                payload["focus_franz"] = []
                payload["focus_wolf"] = []
                payload["upcoming_events"] = []
                payload["open_questions"] = []
                payload["odoo_ok"] = False
                payload["odoo_age"] = None

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        elif route == "/api/screen_toggle":
            # Toggle only living room screen Shelly 10.4.0.10 (NEVER 10.4.0.11!)
            res = fetch_json("http://10.4.0.10/rpc/Switch.Toggle?id=0", timeout=2.0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": res is not None, "result": res}).encode("utf-8"))
            return

        elif self.path.startswith("/api/radio/") or self.path.startswith("/frawo/touch/api/radio/"):
            try:
                odoo_path = self.path if self.path.startswith("/frawo/touch/") else self.path.replace("/api/radio/", "/frawo/touch/api/radio/")
                target_url = f"http://10.1.0.112:8069{odoo_path}"
                req = urllib.request.Request(target_url, headers={"User-Agent": "FraWo-Surface-Kiosk"})
                with urllib.request.urlopen(req, timeout=6.0) as resp:
                    content = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(content)
                    return
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": f"Proxy error: {e}"}).encode("utf-8"))
                return

        elif route == "/cockpit" or self.path.startswith("/frawo/touch/"):
            try:
                target_url = f"http://10.1.0.112:8069{self.path}" if self.path.startswith("/frawo/") else "http://10.1.0.112:8069/frawo/touch/cockpit"
                req = urllib.request.Request(target_url, headers={"User-Agent": "FraWo-Surface-Kiosk"})
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    content = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.end_headers()
                    self.wfile.write(content)
                    return
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Proxy error: {e}".encode("utf-8"))
                return

        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/radio/") or self.path.startswith("/frawo/touch/api/radio/"):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b""
                odoo_path = self.path if self.path.startswith("/frawo/touch/") else self.path.replace("/api/radio/", "/frawo/touch/api/radio/")
                target_url = f"http://10.1.0.112:8069{odoo_path}"
                req = urllib.request.Request(
                    target_url,
                    data=body,
                    headers={
                        "User-Agent": "FraWo-Surface-Kiosk",
                        "Content-Type": self.headers.get("Content-Type", "application/json")
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=6.0) as resp:
                    content = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(content)
                    return
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": f"Proxy error: {e}"}).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()

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
