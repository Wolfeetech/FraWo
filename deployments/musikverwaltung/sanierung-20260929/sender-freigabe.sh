#!/bin/sh
# 🤖 [Claude] 29.09.2026 — Odoo #1263/#1090: eigene Samba-Freigabe [sender] fuer AzuraCast (CT120).
# Zeigt dieselbe Platte wie [music], blendet aber Arbeits-/Altbereiche aus, NUR LESEN.
# [music] (Wolfs Laufwerk M:) bleibt unveraendert. Rueckweg: smb.conf.bak-20260929-sender zurueckkopieren.
set -e
pct exec 120 -- cp -a /etc/samba/smb.conf /etc/samba/smb.conf.bak-20260929-sender
pct exec 120 -- sh -c 'grep -q "^\[sender\]" /etc/samba/smb.conf || cat >> /etc/samba/smb.conf <<EOF

[sender]
	comment = FraWo Funk: nur Bibliothek und Sendungen (AzuraCast), nur lesen - Odoo #1263
	path = /mnt/music
	read only = yes
	valid users = wolf
	hosts allow = 10.1.0.38
	hosts deny = 0.0.0.0/0
	veto files = /_Dokumente/Inbox/_STAGING_RAW/Quarantine/MusicBrainz_Input/Curated_Playlists.bak-20260914/
EOF'
pct exec 120 -- testparm -s --section-name=sender 2>/dev/null
pct exec 120 -- smbcontrol all reload-config
echo "Freigabe [sender] aktiv."
