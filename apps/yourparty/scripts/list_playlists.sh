#!/bin/bash
curl -s "https://radio.yourparty.tech/api/station/1/playlists" -k \
  -H "X-API-Key: __ROTATED_SECRET__" \
  | jq '.[] | {id, name, is_enabled, type}'
