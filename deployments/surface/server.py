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
            odoo_data = fetch_json("https://frawo.tech/frawo/touch/api/summary", timeout=4.0)
            
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

    def do_GET(self):
        if self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with telemetry_lock:
                payload = json.dumps(telemetry_data).encode("utf-8")
            self.wfile.write(payload)
            return
            
        elif self.path == "/api/screen_toggle":
            # Toggle only living room screen Shelly 10.4.0.10 (NEVER 10.4.0.11!)
            res = fetch_json("http://10.4.0.10/rpc/Switch.Toggle?id=0", timeout=2.0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": res is not None, "result": res}).encode("utf-8"))
            return

        super().do_GET()

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
