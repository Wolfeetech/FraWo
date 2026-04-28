# -*- coding: utf-8 -*-
# FraWo v3.1 Hotfix — Force Update CSS and Content

import sys
import xmlrpc.client
import subprocess
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection, resolve_db_password

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
db_password = resolve_db_password()
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def sql_update_arch(view_id, arch):
    mapping = {
        'ä': "' || chr(228) || '",
        'ö': "' || chr(246) || '",
        'ü': "' || chr(252) || '",
        'ß': "' || chr(223) || '",
        'Ä': "' || chr(196) || '",
        'Ö': "' || chr(214) || '",
        'Ü': "' || chr(220) || '",
        '–': "' || chr(150) || '",
        '…': "' || chr(133) || '"
    }

    escaped_arch = arch.replace("'", "''")
    for char, psql_chr in mapping.items():
        escaped_arch = escaped_arch.replace(char, psql_chr)

    sql = f"UPDATE ir_ui_view SET arch_db = '{escaped_arch}' WHERE id = {view_id};"
    cmd = ["docker", "exec", "-e", f"PGPASSWORD={db_password}", "odoo_db_1", "psql", "-U", "odoo", "-d", db, "-c", sql]
    subprocess.run(cmd, check=True)

# GLOBAL CSS with GREEN + UV COLORS (NO MORE ORANGE!)
global_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --fw-forest: #064e3b;
  --fw-forest-dark: #052e16;
  --fw-forest-light: #14532d;
  --fw-uv: #a855f7;
  --fw-uv-light: #c084fc;
  --fw-uv-glow: rgba(168, 85, 247, 0.35);
  --fw-bg: #0a0a0a;
  --fw-surface: #141414;
  --fw-text: #f0f0ee;
  --fw-text-2: #a0a09e;
  --fw-text-3: #6b7280;
  --fw-mint: #a7f3d0;
  --fw-mint-pale: #f0fdf4;
}

body, #wrap, header, footer, .navbar {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  background: var(--fw-bg) !important;
  color: var(--fw-text) !important;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Outfit', 'Inter', sans-serif !important;
  font-weight: 800 !important;
}

/* Nuclear Header/Footer Fix */
header#top, .o_header_standard, .o_header_affixed, .navbar, .navbar-light {
  background-color: var(--fw-bg) !important;
  background: var(--fw-bg) !important;
  border-bottom: 1px solid #1a1a1a !important;
}

footer, .o_footer {
  background-color: var(--fw-forest) !important;
  color: var(--fw-mint-pale) !important;
  padding: 3rem 0 !important;
}

.nav-link, .navbar-light .navbar-nav .nav-link {
  color: var(--fw-text-2) !important;
  font-weight: 500 !important;
  transition: color 0.2s ease !important;
}

.nav-link:hover {
  color: var(--fw-uv) !important;
}

.navbar-brand {
  color: var(--fw-text) !important;
  font-weight: 800 !important;
}

/* Logo Fix - NO FILTER! */
.fw-logo-img, img[alt*="logo"], img[src*="logo"] {
  height: 42px !important;
  width: auto !important;
  filter: none !important;
}

/* Remove Odoo Branding */
.o_footer .o_footer_copyright {
  display: none !important;
}
</style>"""

print("Updating global CSS...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': global_css, 'name': 'FraWo'}])
print("Global CSS updated with Green + UV colors!")
print("Hotfix completed!")
