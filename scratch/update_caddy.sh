#!/bin/bash
SED_CMD="/header_down -X-Frame-Options/a \\    header_down +Content-Security-Policy \"frame-ancestors 'self' ha.hs27.internal\""
sed -i "$SED_CMD" /opt/homeserver2027/stacks/toolbox-network/Caddyfile
docker exec toolbox-network-caddy-1 caddy reload --config /etc/caddy/Caddyfile
