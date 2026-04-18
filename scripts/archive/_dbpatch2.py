import sys
import subprocess
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_db_password

db_password = resolve_db_password()

sql = "UPDATE ir_ui_view SET arch_db = replace(replace(replace(replace(replace(replace(replace(arch_db::text, '&uuml;', '\\xc3\\xbc'), '&auml;', '\\xc3\\xa4'), '&ouml;', '\\xc3\\xb6'), '&Uuml;', '\\xc3\\x9c'), '&Auml;', '\\xc3\\x84'), '&Ouml;', '\\xc3\\x96'), '&szlig;', '\\xc3\\x9f')::xml WHERE id IN (3644, 3637);"
r = subprocess.run(["docker", "exec", "-e", f"PGPASSWORD={db_password}", "odoo_db_1", "psql", "-U", "odoo", "-d", "FraWo_GbR", "-c", sql], capture_output=True, text=True)
print("out:", r.stdout)
print("err:", r.stderr[:300])
