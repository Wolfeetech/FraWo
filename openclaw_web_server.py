#!/usr/bin/env python3
import os
import sys
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Configuration
PORT = 5555
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "frawo-pro:latest"

class OpenClawAPIHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "online",
                "model": OLLAMA_MODEL,
                "backend": "ollama"
            }).encode())
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except:
            data = {}

        if parsed.path == "/api/chat":
            self.handle_chat(data)
        else:
            self.send_error(404)

    def handle_chat(self, data):
        message = data.get("message", "")
        print(f"Chat Request: {message}")
        
        try:
            import urllib.request
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": message,
                "stream": False
            }
            
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/generate",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                resp_data = json.loads(response.read().decode())
                ai_response = resp_data.get('response', 'Keine Antwort erhalten.')
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": ai_response,
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())
            
        except Exception as e:
            print(f"Error in chat: {e}")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": f"⚠️ Ollama nicht erreichbar: {e}",
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())

def run():
    print(f"Starting OpenClaw API on port {PORT} (Ollama: {OLLAMA_MODEL})...")
    server = HTTPServer(('0.0.0.0', PORT), OpenClawAPIHandler)
    server.serve_forever()

if __name__ == "__main__":
    run()
