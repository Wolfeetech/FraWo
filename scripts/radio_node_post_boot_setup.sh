#!/usr/bin/env bash
# radio_node_post_boot_setup.sh
# Einmalig nach cloud-init auf dem Pi ausführen via:
#   ssh wolf@<tailscale-ip> 'bash -s' < scripts/radio_node_post_boot_setup.sh
set -euo pipefail

AZURACAST_ROOT=/var/azuracast
SWAP_FILE=/swapfile
DOCKER_SCRIPT_URL="https://raw.githubusercontent.com/AzuraCast/AzuraCast/main/docker.sh"

log() { echo "[$(date +%H:%M:%S)] $*"; }

# --- Swap (Pi 4 2GB braucht Swap für AzuraCast) ---
if [ ! -f "$SWAP_FILE" ]; then
  log "Swap anlegen (2 GB)..."
  sudo fallocate -l 2G "$SWAP_FILE"
  sudo chmod 600 "$SWAP_FILE"
  sudo mkswap "$SWAP_FILE"
  sudo swapon "$SWAP_FILE"
  echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
fi

# --- Docker Compose sicherstellen ---
if ! docker compose version &>/dev/null; then
  log "Docker Compose installieren..."
  sudo mkdir -p /usr/libexec/docker/cli-plugins
  sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-aarch64" \
    -o /usr/libexec/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose
fi

# --- Docker daemon tunen (weniger Overhead) ---
sudo mkdir -p /etc/docker
echo '{"userland-proxy": false}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker

# --- AzuraCast installieren ---
sudo mkdir -p "$AZURACAST_ROOT"
if [ ! -f "$AZURACAST_ROOT/docker-compose.yml" ]; then
  log "AzuraCast docker.sh herunterladen..."
  sudo curl -fsSL "$DOCKER_SCRIPT_URL" -o "$AZURACAST_ROOT/docker.sh"
  sudo chmod +x "$AZURACAST_ROOT/docker.sh"

  log "AzuraCast Stable-Release setzen..."
  cd "$AZURACAST_ROOT"
  sudo ./docker.sh setup-release stable

  log "AzuraCast installieren (unattended)..."
  cd "$AZURACAST_ROOT"
  yes '' | sudo ./docker.sh install
  log "AzuraCast Installation abgeschlossen."
else
  log "AzuraCast bereits installiert — überspringe."
fi

# --- Live-Capture Verzeichnisse ---
sudo mkdir -p /srv/radio-library/recordings
sudo chown wolf:wolf /srv/radio-library/recordings

# --- ffmpeg installieren ---
sudo apt-get install -y ffmpeg

# --- Systemd Service: Live Capture → AzuraCast + lokale Aufnahme ---
sudo tee /etc/systemd/system/radio-live-capture.service > /dev/null << 'EOF'
[Unit]
Description=Radio Live Capture (USB Audio → AzuraCast + Recording)
After=network.target docker.service azuracast.service
Wants=docker.service

[Service]
Type=simple
User=wolf
EnvironmentFile=/etc/radio-live-capture.env
ExecStartPre=/bin/sh -c 'until curl -sf http://localhost/ > /dev/null 2>&1; do sleep 5; done'
ExecStart=/usr/local/bin/radio-live-capture.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# --- Umgebungsvariablen (Source-Password nach AzuraCast-Setup eintragen) ---
if [ ! -f /etc/radio-live-capture.env ]; then
sudo tee /etc/radio-live-capture.env > /dev/null << 'EOF'
# USB Audio device — prüfen mit: arecord -l
AUDIO_DEVICE=hw:1,0
# Samplerate und Kanäle des Interfaces
AUDIO_RATE=44100
AUDIO_CHANNELS=2
# AzuraCast Icecast Source-Password (aus AzuraCast Web UI → Station → Broadcasting)
ICECAST_SOURCE_PASSWORD=REPLACE_AFTER_AZURACAST_SETUP
# AzuraCast Mount-Point für Live-Input
ICECAST_MOUNT=/live
# Stream-Bitrate in kbps
STREAM_BITRATE=192
# Lokales Recording-Verzeichnis
RECORDING_DIR=/srv/radio-library/recordings
EOF
fi

# --- Capture-Script ---
sudo tee /usr/local/bin/radio-live-capture.sh > /dev/null << 'SCRIPT'
#!/usr/bin/env bash
source /etc/radio-live-capture.env
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RECORDING_FILE="${RECORDING_DIR}/${TIMESTAMP}_live.mp3"

exec ffmpeg -hide_banner -loglevel warning \
  -f alsa -channels "$AUDIO_CHANNELS" -sample_rate "$AUDIO_RATE" -i "$AUDIO_DEVICE" \
  -filter:a "loudnorm=I=-16:LRA=11:TP=-1.5" \
  -map 0 -acodec libmp3lame -ab "${STREAM_BITRATE}k" -ar "$AUDIO_RATE" \
    -f mp3 "icecast://source:${ICECAST_SOURCE_PASSWORD}@localhost:8000${ICECAST_MOUNT}" \
  -map 0 -acodec libmp3lame -ab 320k -ar "$AUDIO_RATE" \
    "$RECORDING_FILE"
SCRIPT
sudo chmod +x /usr/local/bin/radio-live-capture.sh

sudo systemctl daemon-reload
# Service noch NICHT enablen — erst nach AzuraCast-Setup und Password eintragen
log "Live-Capture Service registriert (noch nicht gestartet — erst nach AzuraCast-Setup)."

# --- USB Audio Device anzeigen ---
log "Erkannte Audio-Devices:"
arecord -l 2>/dev/null || echo "  (keine ALSA-Devices — USB Interface eingesteckt?)"

log ""
log "=== FERTIG ==="
log "Nächste Schritte:"
log "  1. AzuraCast Web UI öffnen: http://$(tailscale ip -4 2>/dev/null || echo '<tailscale-ip>')/"
log "  2. Station 'frawo-funk' einrichten, Live-Broadcasting aktivieren"
log "  3. Source-Password aus AzuraCast in /etc/radio-live-capture.env eintragen"
log "  4. sudo systemctl enable --now radio-live-capture"
