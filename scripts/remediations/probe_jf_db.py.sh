set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
pct exec 100 -- bash -lc 'cat > /tmp/jf_probe.py <<"PY"
import sqlite3
conn = sqlite3.connect("/srv/jellyfin/config/data/jellyfin.db")
cur = conn.cursor()
print(cur.execute("SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name").fetchall())
print(cur.execute("SELECT sql FROM sqlite_master WHERE type=\'table\' AND name=\'Users\'").fetchone()[0])
print(cur.execute("PRAGMA table_info(Users)").fetchall())
print(cur.execute("SELECT * FROM Users").fetchall())
PY
python3 /tmp/jf_probe.py
rm -f /tmp/jf_probe.py'
SSH