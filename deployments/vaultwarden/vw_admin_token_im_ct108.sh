#!/bin/bash
# Vaultwarden: neues Admin-Token setzen und altes agent@-Konto loeschen (Odoo #1931). Laeuft in CT108.
# Neues Token kommt per stdin, wird nie ausgegeben.
set -euo pipefail
read -r TOKEN
cd /opt/vaultwarden
command -v argon2 >/dev/null || apt-get install -y -qq argon2 >/dev/null 2>&1
HASH=$(printf '%s' "$TOKEN" | argon2 "$(openssl rand -base64 32)" -e -id -k 65540 -t 3 -p 4)
case "$HASH" in '$argon2id$'*) ;; *) echo "ABBRUCH: Hash ungueltig"; exit 1;; esac
cp -p docker-compose.yml docker-compose.yml.bak-20261006
cp -p .env .env.bak-20261006
ESC=$(printf '%s' "$HASH" | sed 's/\$/$$/g')
python3 - "$ESC" <<'PY'
import sys, re
p = '/opt/vaultwarden/docker-compose.yml'
s = open(p).read()
s2, n = re.subn(r'(\n\s*- ADMIN_TOKEN=).*', lambda m: m.group(1) + sys.argv[1], s)
assert n == 1, n
open(p, 'w').write(s2)
PY
# Klartext-Token aus .env entfernen (wurde nicht benutzt, Compose setzt den Hash)
sed -i 's/^ADMIN_TOKEN=.*/# ADMIN_TOKEN entfernt 06.10.2026 (#1931) - gilt nur der Hash in docker-compose.yml/' .env
docker compose up -d 2>&1 | tail -1 || docker-compose up -d 2>&1 | tail -1
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/alive 2>/dev/null | grep -q 200 && break; sleep 2; done
PORT=$(docker port vaultwarden 80/tcp 2>/dev/null | head -1 | sed 's/.*://'); PORT=${PORT:-80}
J=/tmp/vwadmin.jar; rm -f $J
curl -s -c $J -o /dev/null -w 'admin-login %{http_code}\n' --data-urlencode "token=$TOKEN" "http://127.0.0.1:$PORT/admin"
UUID=$(curl -s -b $J "http://127.0.0.1:$PORT/admin/users" | python3 -c "import sys,json; print([u['id'] for u in json.load(sys.stdin) if u['email']=='agent@frawo.tech'][0])")
curl -s -b $J -X POST -o /dev/null -w 'agent@ geloescht: %{http_code}\n' "http://127.0.0.1:$PORT/admin/users/$UUID/delete"
curl -s -b $J "http://127.0.0.1:$PORT/admin/users" | python3 -c "import sys,json; print('agent@ noch da:', any(u['email']=='agent@frawo.tech' for u in json.load(sys.stdin)))"
rm -f $J
