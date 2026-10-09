---
name: homeassistant
description: Home Assistant Steuerung und Statusabfragen für FraWo Hausautomation (Rothkreuz, 10.1.0.40:8123)
---

# Home Assistant Integration (FraWo)

**Host:** `http://10.1.0.40:8123` (VM 210 auf anker-pve)  
**Authentifizierung:** Long-Lived Access Token in `~/.hermes/.env` (`HOMEASSISTANT_TOKEN`)  
**MCP Server:** `homeassistant` (SSE: `http://10.1.0.40:8123/mcp_server/sse`)  
**CLI Tool:** `hass-api` (`/usr/local/bin/hass-api`)  

---

## ⛔ ROTE LINIE: Shelly 10.4.0.11 NIEMALS schalten!

Gemäß **FraWo Agenten-Protokoll Regel 7** (Verbote):
> Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c, `switch.shelly_outdoor_plug_s_gen3_it_netzwerk_strom_kritisch_nie_remote_schalten`) darf **NIEMALS** remote geschaltet werden! Er versorgt die IT-/Netzwerkinfrastruktur mit Strom.

Das Skript `hass-api` blockiert jeden Versuch hart mit Exit-Code 99.

---

## Verwendung per CLI (`hass-api`)

```bash
# 1. API-Status prüfen
hass-api status

# 2. Entitäten suchen / filtern
hass-api states light
hass-api states temperature
hass-api states switch

# 3. Einzelnen Zustand & Attribute abfragen
hass-api state sensor.wohnzimmer_temperatur

# 4. Dienst aufrufen (Service Call)
hass-api call light turn_on '{"entity_id": "light.garten"}'
hass-api call switch turn_off '{"entity_id": "switch.steckdose_1"}'
```

---

## Verwendung per Python

```python
import os, json, urllib.request

HA_URL = os.environ.get("HOMEASSISTANT_URL", "http://10.1.0.40:8123")
HA_TOKEN = os.environ.get("HOMEASSISTANT_TOKEN")

req = urllib.request.Request(
    f"{HA_URL}/api/states",
    headers={"Authorization": HA_TOKEN, "Content-Type": "application/json"}
)
states = json.loads(urllib.request.urlopen(req).read().decode())
```
