#!/bin/bash
# Check if AzuraCast has a "request next song" or "skip" API
echo "=== Station Backend Info ==="
curl -s "https://radio.yourparty.tech/api/station/1" -k \
  -H "X-API-Key: __ROTATED_SECRET__" \
  | jq '{backend, backend_config}'

echo ""
echo "=== Check if AutoDJ can be controlled ==="
curl -s "https://radio.yourparty.tech/api/station/1/queue" -k \
  -H "X-API-Key: __ROTATED_SECRET__" \
  | jq '.[0:3]'
