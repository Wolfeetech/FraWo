# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Global CSS for Header/Footer Persistence
css_head = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap');
  body, #wrap { font-family: 'Poppins', sans-serif !important; }
  /* Nuclear Dark Mode Fix */
  .o_header_standard, .o_header_affixed, #top, footer { background-color: #0d1117 !important; border-color: #30363d !important; }
  .navbar-light .navbar-nav .nav-link, .navbar-light .navbar-brand { color: #fff !important; }
  .navbar-light .navbar-nav .nav-link:hover { color: #a855f7 !important; }
  /* Fix for text over background images */
  section.s_cover h1, section.s_cover p { color: #fff !important; }
</style>
"""

models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': css_head}])
print("Global CSS updated.")
