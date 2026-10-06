#!/usr/bin/env bash
# Technik-Dateien aus dem Paperless-Parkordner in Nextcloud 80_Technik einsortieren (Odoo #1927).
# Laeuft auf dem OptiPlex-Host. Quelle bleibt unveraendert (CT110:/opt/paperless/nicht-dokumente-20261006).
# Ziel: Nextcloud-Benutzer wolf, Ordner 80_Technik (VM300, Docker nextcloud_app_1), danach files:scan.
set -euo pipefail
S=/root/technik-20261006
rm -rf "$S"; mkdir -p "$S/park" "$S/80_Technik"
pct exec 110 -- tar cf - -C /opt/paperless nicht-dokumente-20261006 | tar xf - -C "$S/park"
P="$S/park/nicht-dokumente-20261006"; T="$S/80_Technik"
mkdir -p "$T/Ton/dB-Technologies" "$T/Ton/DSP" "$T/Licht/Fixtures" "$T/Licht/Showfiles" \
         "$T/IT/Server & Scripts" "$T/IT/System & Diagnostics" "$T/IT/Rack" "$T/IT/Doku" \
         "$T/Software/Installer" "$T/Software/KI-Modelle" "$T/Projekte & Konfigurationen" "$T/Webseiten"
# Ton
cp -p "$P"/Gallery_Gallery_AURORA-NET_*.zip "$P"/Gallery_Gallery_DBTECHNOLOGIES-NETWORK_*.zip "$P/VioTowerLR.dvac" "$T/Ton/dB-Technologies/"
cp -p "$P/AuroraNet_2026.3.0.exe/AuroraNet release notes.pdf" "$T/Ton/dB-Technologies/AuroraNet 2026.3 Release Notes.pdf"
cp -p "$P/10356350-Bilder-omnitronic-dxo-26-pro-systemcontroller.zip" "$T/Ton/DSP/"
cp -rp "$P/448459_the_t.racks_dsp_4x4_mini_firmware_1.07_-_pc_editor_1.05" "$T/Ton/DSP/t.racks DSP 4x4 Mini Firmware 1.07 + Editor 1.05"
# Licht: vier identische Kopien (md5 gleich) -> eine
cp -p "$P/beamZ-Panther-35-150459.qxf" "$T/Licht/Fixtures/beamZ-Panther-35.qxf"
# IT
cp -p "$P/Server & Scripts/"* "$T/IT/Server & Scripts/"
cp -p "$P/System & Diagnostics/"* "$T/IT/System & Diagnostics/"
cp -p "$P/IKEA+Kallax+10+inch+Rack+7U.zip" "$T/IT/Rack/IKEA Kallax 10 Zoll Rack 7HE.zip"
cp -p "$P/Readme.md" "$T/IT/Doku/Home Assistant Systemdoku (alt).md"
# Software
cp -p "$P/TouchDesignerWebInstaller.2025.33230.exe" "$T/Software/Installer/"
cp -p "$P/ggml-base.bin" "$T/Software/KI-Modelle/whisper-ggml-base.bin"
# Projekte, Webseiten
cp -p "$P/Projekte & Konfigurationen/"* "$T/Projekte & Konfigurationen/"
cp -rp "$P/gbr-website" "$T/Webseiten/gbr-website"
echo "Einsortiert: $(find "$T" -type f | wc -l) Dateien, $(du -sh "$T" | cut -f1)"
find "$T" -type f | sed "s#^$S/##" | sort

# Nach Nextcloud uebertragen
rsync -a --delete "$T/" root@10.1.0.21:/root/80_Technik/
ssh root@10.1.0.21 'set -e
D=/var/www/html/data/wolf/files/80_Technik
docker exec nextcloud_app_1 test ! -e "$D" || { echo "ABBRUCH: $D existiert schon"; exit 1; }
docker cp /root/80_Technik nextcloud_app_1:"$D"
docker exec nextcloud_app_1 chown -R www-data:www-data "$D"
docker exec -u www-data nextcloud_app_1 php occ files:scan --path="wolf/files/80_Technik" | tail -4
rm -rf /root/80_Technik'
echo FERTIG
