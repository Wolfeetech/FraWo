#!/usr/bin/env python3
"""FraWo M1 – kleines UCG-Werkzeug fuer den Netz-Umzug.

Schluessel kommt aus /etc/frawo/unifi.env (FRAWO_UNIFI_KEY), nie aus diesem Skript.
"""
import json
import os
import ssl
import sys
import time
import urllib.request

ENV = os.environ.get("FRAWO_UNIFI_ENV", "/etc/frawo/unifi.env")
KEY = [line.split("=", 1)[1].strip().strip("\"'") for line in open(ENV)
       if line.startswith("FRAWO_UNIFI_KEY=")][0]
BASE = "https://10.1.0.1/proxy/network/api/s/default"
CTX = ssl._create_unverified_context()
GW_ID = "69ee24bcd950e39403fa0607"
NET = {
    "lan": "69d0ff7727ec024b992dcb6f",
    "server": "69d0ff9b27ec024b992dcb7f",
    "iot": "69d1001127ec024b992dcb88",
}
NET_NAME = {value: key for key, value in NET.items()}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        BASE + path, method=method, data=data,
        headers={"X-API-KEY": KEY, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, context=CTX, timeout=20) as response:
        result = json.load(response)
    if result.get("meta", {}).get("rc") != "ok":
        sys.exit(f"FEHLER {method} {path}: {result.get('meta')}")
    return result["data"]


def get_dev():
    return [device for device in call("GET", "/stat/device") if device.get("_id") == GW_ID][0]


def backup(outdir):
    os.makedirs(outdir, exist_ok=True)
    parts = {
        "device": "/stat/device", "user": "/rest/user", "networkconf": "/rest/networkconf",
        "firewallrule": "/rest/firewallrule", "firewallgroup": "/rest/firewallgroup",
        "routing": "/rest/routing",
    }
    for name, path in parts.items():
        data = call("GET", path)
        if not data:
            sys.exit(f"FEHLER: {name} ist leer – keine echte Sicherung")
        with open(f"{outdir}/{name}.json", "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=1)
        print(f"{name}: {len(data)} Eintraege gesichert")
    device = get_dev()
    if len(device.get("port_overrides", [])) != 4:
        sys.exit("FEHLER: port_overrides hat nicht 4 Eintraege – Sicherung verdaechtig")
    print("port_overrides:", json.dumps(device["port_overrides"]))


def ports():
    for port in get_dev().get("port_overrides", []):
        print(port["port_idx"], port.get("name", ""),
              NET_NAME.get(port.get("native_networkconf_id"), port.get("native_networkconf_id")),
              port.get("forward"))


def native(port, net, name=None):
    port = int(port)
    if port == 5:
        sys.exit("Port 5 ist WAN – wird nie angefasst")
    device = get_dev()
    overrides = device.get("port_overrides", [])
    if len(overrides) != 4:
        sys.exit(f"FEHLER: erwartet 4 Port-Sonderregeln, gefunden {len(overrides)} – Abbruch")
    matches = [entry for entry in overrides if entry["port_idx"] == port]
    if not matches:
        sys.exit(f"FEHLER: keine Sonderregel fuer Port {port}")
    matches[0]["native_networkconf_id"] = NET[net]
    if name:
        matches[0]["name"] = name
    call("PUT", f"/rest/device/{GW_ID}", {"port_overrides": overrides})
    for _ in range(10):
        device = get_dev()
        found = [entry for entry in device["port_overrides"] if entry["port_idx"] == port][0]
        if found.get("native_networkconf_id") == NET[net] and len(device["port_overrides"]) == 4:
            print(f"Port {port} -> {net} bestaetigt")
            return
        time.sleep(1)
    sys.exit(f"FEHLER: Port {port} zeigt nach dem Schreiben nicht {net}")


def reserve(mac, ip, net, name=None):
    mac = mac.lower()
    users = [user for user in call("GET", "/rest/user") if user.get("mac", "").lower() == mac]
    body = {"use_fixedip": True, "fixed_ip": ip, "network_id": NET[net]}
    if name:
        body["name"] = name
    if users:
        call("PUT", f"/rest/user/{users[0]['_id']}", body)
    else:
        body["mac"] = mac
        call("POST", "/rest/user", body)
    user = [user for user in call("GET", "/rest/user") if user.get("mac", "").lower() == mac][0]
    if user.get("fixed_ip") != ip or user.get("network_id") != NET[net]:
        sys.exit(f"FEHLER: Zuteilung {mac} nicht uebernommen: {user.get('fixed_ip')} {user.get('network_id')}")
    print(f"{mac} -> {ip} ({net}) bestaetigt")


def forget(mac):
    mac = mac.lower()
    call("POST", "/cmd/stamgr", {"cmd": "forget-sta", "macs": [mac]})
    for _ in range(10):
        remaining = [user for user in call("GET", "/rest/user") if user.get("mac", "").lower() == mac]
        if not remaining:
            print(f"{mac} vergessen")
            return
        time.sleep(1)
    sys.exit(f"FEHLER: {mac} noch vorhanden")


if __name__ == "__main__":
    command, arguments = sys.argv[1], sys.argv[2:]
    {"backup": backup, "native": native, "reserve": reserve, "ports": ports, "forget": forget}[command](*arguments)
