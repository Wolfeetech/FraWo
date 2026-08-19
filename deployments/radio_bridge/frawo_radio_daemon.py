#!/usr/bin/env python3
import os
import subprocess
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.parser import BytesParser

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 8888
BEARER_TOKEN = os.environ.get("FRAWO_BRIDGE_TOKEN", "")
RADIO_INBOX = "/mnt/music_hdd/Inbox/Radio"
CURATE_SCRIPT = "/usr/local/bin/curate_radio.py"
LOCK_FILE = "/tmp/frawo_curate.lock"
LOG_FILE = "/tmp/frawo_curate.log"

def is_pid_running(pid):
    if pid <= 0:
        return False
    try:
        # Reap zombie if it is our child
        try:
            reaped_pid, status = os.waitpid(pid, os.WNOHANG)
            if reaped_pid == pid:
                return False
        except ChildProcessError:
            # Not our child or already reaped
            pass
            
        os.kill(pid, 0)
        
        # Check if it is a zombie (defunct) via /proc
        try:
            with open(f"/proc/{pid}/status", "r") as f:
                for line in f:
                    if line.startswith("State:"):
                        if "Z (zombie)" in line or "zombie" in line.lower():
                            return False
                        break
        except Exception:
            pass
            
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # If we don't have permission but it exists, it is running
        return True
    except OSError:
        return False

class RadioBridgeHandler(BaseHTTPRequestHandler):

    def _send_response(self, status_code, data, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        if content_type == "application/json":
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.wfile.write(data)

    def do_OPTIONS(self):
        # CORS preflight
        self._send_response(200, {})

    def _verify_auth(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            return False
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header.split(" ", 1)[1].strip()
        return token == BEARER_TOKEN

    def _check_curation_status(self):
        if not os.path.exists(LOCK_FILE):
            return False, 0
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            if is_pid_running(pid):
                return True, pid
            else:
                # PID is not running, clean up lock file
                os.remove(LOCK_FILE)
                return False, 0
        except Exception:
            # If reading lockfile fails, assume not running
            return False, 0

    def do_GET(self):
        if not self._verify_auth():
            self._send_response(401, {"status": "error", "message": "Unauthorized"})
            return

        if self.path == "/status":
            is_running, pid = self._check_curation_status()
            
            # List files in Inbox/Radio
            inbox_files = []
            if os.path.exists(RADIO_INBOX):
                try:
                    for f in os.listdir(RADIO_INBOX):
                        if f not in [".", ".."]:
                            full_path = os.path.join(RADIO_INBOX, f)
                            if os.path.isfile(full_path):
                                size = os.path.getsize(full_path)
                                inbox_files.append({"name": f, "size": size})
                except Exception as e:
                    self._send_response(500, {"status": "error", "message": f"Failed to read inbox: {str(e)}"})
                    return
            
            # Read logs if they exist
            logs = ""
            if os.path.exists(LOG_FILE):
                try:
                    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as lf:
                        logs = lf.read()
                except Exception as e:
                    logs = f"Error reading log file: {str(e)}"

            self._send_response(200, {
                "status": "success",
                "curation_running": is_running,
                "curation_pid": pid,
                "inbox_files": inbox_files,
                "logs": logs
            })
        else:
            self._send_response(404, {"status": "error", "message": "Not Found"})

    def do_POST(self):
        if not self._verify_auth():
            self._send_response(401, {"status": "error", "message": "Unauthorized"})
            return

        if self.path == "/curate":
            is_running, pid = self._check_curation_status()
            if is_running:
                self._send_response(409, {"status": "error", "message": f"Curation already running under PID {pid}"})
                return

            try:
                # Clear log file and start curation in background
                with open(LOG_FILE, "w", encoding="utf-8") as lf:
                    lf.write("--- Curation Pipeline started via API ---\n")
                
                # Open log file for subprocess output redirect
                lf_out = open(LOG_FILE, "a", encoding="utf-8")
                proc = subprocess.Popen(
                    ["python3", CURATE_SCRIPT], 
                    stdout=lf_out, 
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
                
                # Write PID to lock file
                with open(LOCK_FILE, "w") as f:
                    f.write(str(proc.pid))
                
                self._send_response(200, {
                    "status": "success",
                    "message": "Curation started in background.",
                    "pid": proc.pid
                })
            except Exception as e:
                self._send_response(500, {"status": "error", "message": str(e)})

        elif self.path == "/delete":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_response(400, {"status": "error", "message": "Missing payload"})
                return
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
                filename = body.get("filename")
                if not filename:
                    self._send_response(400, {"status": "error", "message": "Missing filename parameter"})
                    return
                # Clean filename to avoid path traversal
                filename = os.path.basename(filename)
                target_path = os.path.join(RADIO_INBOX, filename)
                if os.path.exists(target_path) and os.path.isfile(target_path):
                    os.remove(target_path)
                    self._send_response(200, {"status": "success", "message": f"File '{filename}' deleted successfully."})
                else:
                    self._send_response(404, {"status": "error", "message": f"File '{filename}' not found."})
            except Exception as e:
                self._send_response(500, {"status": "error", "message": str(e)})

        elif self.path == "/upload":
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                self._send_response(400, {"status": "error", "message": "Content-Type must be multipart/form-data"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    self._send_response(400, {"status": "error", "message": "Empty body"})
                    return

                # Read body bytes
                body_bytes = self.rfile.read(content_length)

                # Parse bytes as message
                headers_str = f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
                msg = BytesParser().parsebytes(headers_str + body_bytes)

                if not msg.is_multipart():
                    self._send_response(400, {"status": "error", "message": "Request must be multipart"})
                    return

                uploaded_files = []
                os.makedirs(RADIO_INBOX, exist_ok=True)

                for part in msg.walk():
                    filename = part.get_filename()
                    if filename:
                        # Clean filename
                        filename = os.path.basename(filename)
                        dest_path = os.path.join(RADIO_INBOX, filename)
                        
                        # Save file payload
                        with open(dest_path, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        
                        uploaded_files.append(filename)

                self._send_response(200, {
                    "status": "success",
                    "message": f"Successfully uploaded {len(uploaded_files)} files.",
                    "files": uploaded_files
                })
            except Exception as e:
                self._send_response(500, {"status": "error", "message": str(e)})
        else:
            self._send_response(404, {"status": "error", "message": "Not Found"})

def run_server():
    server_address = (LISTEN_IP, LISTEN_PORT)
    httpd = HTTPServer(server_address, RadioBridgeHandler)
    print(f"Starting FraWo Radio Bridge Daemon on {LISTEN_IP}:{LISTEN_PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Stopping daemon...")

if __name__ == "__main__":
    run_server()
