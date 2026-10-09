#!/usr/bin/env python3
"""FraWo Home Assistant API CLI für Hermes & andere Agenten.

Liest Konfiguration aus ~/.hermes/.env oder ~/.ai-tools-shared/.env.
Enthält harte Sicherheitsprüfung für Shelly 10.4.0.11 (Regel 7).
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

# Gesperrte Entitäten & Muster gemäß Agenten-Protokoll (Regel 7 / Notabschaltungs-Verbot)
FORBIDDEN_PATTERNS = [
    "10.4.0.11",
    "e4:b0:63:d5:66:1c",
    "e4b063d5661c",
    "nie_remote_schalten",
    "it_netzwerk_strom",
    "outdoor_plug_s_gen3_it_netzwerk_strom",
]

def load_env():
    for p in [Path.home() / ".hermes" / ".env", Path.home() / ".ai-tools-shared" / ".env", Path("/home/hermes/.hermes/.env")]:
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    if k not in os.environ:
                        os.environ[k] = v

load_env()

HA_URL = os.environ.get("HOMEASSISTANT_URL") or os.environ.get("HASS_URL") or "http://10.1.0.40:8123"
HA_TOKEN = os.environ.get("HOMEASSISTANT_TOKEN") or os.environ.get("HASS_TOKEN")

if not HA_TOKEN:
    # Try HASS_API_KEY
    raw = os.environ.get("HASS_API_KEY")
    if raw:
        HA_TOKEN = f"Bearer {raw}"

if not HA_TOKEN:
    print("Fehler: HOMEASSISTANT_TOKEN weder in Umgebung noch in ~/.hermes/.env gefunden.", file=sys.stderr)
    sys.exit(1)

if not HA_TOKEN.startswith("Bearer "):
    HA_TOKEN = f"Bearer {HA_TOKEN}"

def request(endpoint, method="GET", data=None):
    url = f"{HA_URL.rstrip('/')}/api/{endpoint.lstrip('/')}"
    headers = {"Authorization": HA_TOKEN, "Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {err}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Verbindungsfehler zu {url}: {e}", file=sys.stderr)
        sys.exit(3)

def check_safety(target_text):
    low = target_text.lower()
    for pat in FORBIDDEN_PATTERNS:
        if pat in low:
            print("❌ SICHERHEITSBLOCKADE: Shelly 10.4.0.11 (IT/Netzwerk-Strom) darf NIEMALS geschaltet werden!", file=sys.stderr)
            print("Verstoß gegen FraWo Agenten-Protokoll Regel 7 / Notfall-Richtlinie.", file=sys.stderr)
            sys.exit(99)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Verwendung: hass-api <Befehl> [Optionen]")
        print("Befehle:")
        print("  status                  Prüft Verbindung und API-Status")
        print("  states [filter]         Listet Entitäten (optional gefiltert nach Text/Domain)")
        print("  state <entity_id>       Zeigt Zustand und Attribute einer Entität")
        print("  call <domain> <service> [json_payload]  Ruft einen Dienst auf (z.B. light turn_on)")
        print("  services                Listet verfügbare Dienste auf")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        res = request("/")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif cmd == "states":
        filt = sys.argv[2].lower() if len(sys.argv) > 2 else None
        res = request("/states")
        out = []
        for s in res:
            eid = s.get("entity_id", "")
            fname = s.get("attributes", {}).get("friendly_name", "")
            state = s.get("state", "")
            if not filt or filt in eid.lower() or filt in fname.lower():
                out.append({"entity_id": eid, "state": state, "name": fname})
        print(json.dumps(out, indent=2, ensure_ascii=False))

    elif cmd == "state":
        if len(sys.argv) < 3:
            print("Fehler: entity_id fehlt.", file=sys.stderr); sys.exit(1)
        eid = sys.argv[2]
        res = request(f"/states/{eid}")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif cmd == "services":
        res = request("/services")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif cmd == "call":
        if len(sys.argv) < 4:
            print("Fehler: domain und service erforderlich (z.B. light turn_on).", file=sys.stderr); sys.exit(1)
        domain = sys.argv[2]
        service = sys.argv[3]
        payload = {}
        if len(sys.argv) > 4:
            try:
                payload = json.loads(sys.argv[4])
            except Exception as e:
                print(f"Ungültiges JSON-Payload: {e}", file=sys.stderr); sys.exit(1)

        # Harte Sicherheitsprüfung
        check_safety(f"{domain}.{service} {json.dumps(payload)}")

        res = request(f"/services/{domain}/{service}", method="POST", data=payload)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        print(f"Unbekannter Befehl: {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
