#!/usr/bin/env bash
set -euo pipefail

echo "[media-devices] Detecting removable install-media candidates"
lsblk -S -o NAME,PATH,MODEL,VENDOR,SIZE,TRAN,SERIAL,HOTPLUG
echo
echo "[media-devices] Current recommendation"
echo "rpi_sd_candidate=/dev/mmcblk0"
echo "image_usb_target=/dev/sdd"
echo "favorites_usb_target=/dev/sdc"
echo "rpi_music_library_usb=attached_directly_to_radio_node"
echo "note=/dev/sdd is the dedicated boot-and-install stick even though it only fits one large Ubuntu image comfortably"
