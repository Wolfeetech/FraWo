#!/bin/bash
# Paperless-ngx POST_CONSUME_SCRIPT
# Laeuft nach jedem verarbeiteten Dokument im Container (VM 330).
# Laedt das Originaldokument via Paperless API in Nextcloud/Archiv hoch.
# Mount: /usr/local/bin/paperless-to-nc.sh:ro im webserver Container
#
# Umgebungsvariablen (von Paperless gesetzt):
#   DOCUMENT_ID, DOCUMENT_TITLE, DOCUMENT_CORRESPONDENT, DOCUMENT_CREATED

NC_USER="frawoadmin"
NC_PASS="NC-Frawo-2026!"
NC_BASE="http://10.4.0.21/remote.php/dav/files/${NC_USER}"
LOG="/var/log/paperless-to-nc.log"
API_TOKEN="4ca7affa0948fe3a73bb224c60fe1090d1c00b08"

YEAR=$(echo "$DOCUMENT_CREATED" | cut -c1-4)
CORRESPONDENT="${DOCUMENT_CORRESPONDENT:-Unbekannt}"
SAFE_CORR=$(echo "$CORRESPONDENT" | sed 's/[^a-zA-Z0-9_äöüÄÖÜß -]//g')
ARCHIVE_PATH="Dokumente/Archiv/${SAFE_CORR}/${YEAR}"
FILENAME="${DOCUMENT_CREATED}_${DOCUMENT_TITLE}.pdf"
SAFE_FILENAME=$(echo "$FILENAME" | sed 's/[^a-zA-Z0-9_äöüÄÖÜß .-]//g')

echo "$(date): Doc #${DOCUMENT_ID}: ${DOCUMENT_TITLE} -> ${ARCHIVE_PATH}" >> $LOG

# Zielordner anlegen (MKCOL ist idempotent)
curl -s -o /dev/null -u "${NC_USER}:${NC_PASS}" -X MKCOL "${NC_BASE}/Dokumente/Archiv" 2>/dev/null
curl -s -o /dev/null -u "${NC_USER}:${NC_PASS}" -X MKCOL "${NC_BASE}/Dokumente/Archiv/${SAFE_CORR}" 2>/dev/null
curl -s -o /dev/null -u "${NC_USER}:${NC_PASS}" -X MKCOL "${NC_BASE}/${ARCHIVE_PATH}" 2>/dev/null

# Dokument von Paperless API laden und nach NC hochladen
curl -s -H "Authorization: Token ${API_TOKEN}" \
    "http://localhost:8000/api/documents/${DOCUMENT_ID}/download/" \
    -o /tmp/pl_doc_${DOCUMENT_ID}.pdf

if [ -f /tmp/pl_doc_${DOCUMENT_ID}.pdf ] && [ -s /tmp/pl_doc_${DOCUMENT_ID}.pdf ]; then
    CODE=$(curl -s -o /dev/null -w '%{http_code}' \
        -u "${NC_USER}:${NC_PASS}" \
        -T /tmp/pl_doc_${DOCUMENT_ID}.pdf \
        "${NC_BASE}/${ARCHIVE_PATH}/${SAFE_FILENAME}")
    echo "$(date): Upload ${SAFE_FILENAME} -> HTTP ${CODE}" >> $LOG
    rm -f /tmp/pl_doc_${DOCUMENT_ID}.pdf
else
    echo "$(date): Download fehlgeschlagen fuer Doc #${DOCUMENT_ID}" >> $LOG
fi
