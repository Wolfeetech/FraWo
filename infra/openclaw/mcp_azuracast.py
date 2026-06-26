#!/usr/bin/env python3
"""Minimal AzuraCast MCP server for OpenClaw/ServAssi."""
import json, os, sys
import urllib.request, urllib.error

BASE_URL = os.environ.get("AZURACAST_URL", "http://10.1.0.38")
API_KEY  = os.environ.get("AZURACAST_API_KEY", "")
STATION  = os.environ.get("AZURACAST_STATION_ID", "1")

def az_request(method, path, body=None):
    url = f"{BASE_URL}/api/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
          headers={"X-API-Key": API_KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode()}

TOOLS = [
    {"name": "az_station_status",  "description": "Aktuellen Station-Status, Now-Playing und Stream-Info abrufen.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "az_list_playlists",  "description": "Alle Playlists der Station auflisten.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "az_list_media",      "description": "Mediendateien auflisten (max 100, optional nach Playlist filtern).", "inputSchema": {"type": "object", "properties": {"playlist_id": {"type": "integer", "description": "Nur Dateien dieser Playlist (optional)"}, "limit": {"type": "integer", "default": 50}}}},
    {"name": "az_assign_playlist", "description": "Mediendatei(en) einer Playlist zuweisen.", "inputSchema": {"type": "object", "required": ["file_ids", "playlist_id"], "properties": {"file_ids": {"type": "array", "items": {"type": "integer"}}, "playlist_id": {"type": "integer"}}}},
    {"name": "az_create_playlist", "description": "Neue Playlist anlegen.", "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}, "weight": {"type": "integer", "default": 3}}}},
    {"name": "az_skip_song",       "description": "Aktuellen Song überspringen, nächsten spielen.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "az_restart_station", "description": "Radio-Station neu starten (liquidsoap).", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "az_search_media",    "description": "Mediendateien nach Stichwort suchen.", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}}}},
]

def call_tool(name, args):
    sid = STATION
    if name == "az_station_status":
        return az_request("GET", f"station/{sid}/nowplaying")
    if name == "az_list_playlists":
        return az_request("GET", f"station/{sid}/playlists")
    if name == "az_list_media":
        pl = args.get("playlist_id")
        limit = args.get("limit", 50)
        path = f"station/{sid}/files?per_page={limit}"
        if pl:
            path += f"&playlist={pl}"
        return az_request("GET", path)
    if name == "az_assign_playlist":
        return az_request("PUT", f"station/{sid}/files/batch",
                          {"do": "playlist", "playlists": [args["playlist_id"]], "files": args["file_ids"]})
    if name == "az_create_playlist":
        return az_request("POST", f"station/{sid}/playlists",
                          {"name": args["name"], "type": "default", "weight": args.get("weight", 3), "is_enabled": True})
    if name == "az_skip_song":
        return az_request("POST", f"station/{sid}/backend/skip")
    if name == "az_restart_station":
        return az_request("POST", f"station/{sid}/restart")
    if name == "az_search_media":
        return az_request("GET", f"station/{sid}/files?per_page=50&search={urllib.parse.quote(args['query'])}")
    return {"error": "unknown tool"}

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def main():
    import urllib.parse
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = msg.get("id")
        method = msg.get("method", "")
        if method == "initialize":
            send({"jsonrpc":"2.0","id":mid,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"azuracast","version":"1.0"}}})
        elif method == "tools/list":
            send({"jsonrpc":"2.0","id":mid,"result":{"tools":TOOLS}})
        elif method == "tools/call":
            p = msg.get("params", {})
            result = call_tool(p.get("name",""), p.get("arguments",{}))
            send({"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":json.dumps(result, ensure_ascii=False, indent=2)}]}})
        elif method == "notifications/initialized":
            pass
        else:
            if mid is not None:
                send({"jsonrpc":"2.0","id":mid,"error":{"code":-32601,"message":"Method not found"}})

if __name__ == "__main__":
    main()
