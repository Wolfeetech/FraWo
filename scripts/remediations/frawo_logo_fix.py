# -*- coding: utf-8 -*-
# FraWo Logo Fix — Mix-Blend-Mode für transparentes Aussehen

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

# CSS Update - Logo mit mix-blend-mode
css_update = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --fw-forest: #064e3b;
  --fw-uv: #a855f7;
  --fw-bg: #0a0a0a;
  --fw-surface: #121212;
  --fw-border: #1a1a1a;
  --fw-text: #e0e0e0;
  --fw-text-dim: #888888;
  --fw-text-dimmer: #555555;
}

body, #wrap, header, footer, .navbar {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background: var(--fw-bg) !important;
  color: var(--fw-text) !important;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
}

header#top, .o_header_standard, .o_header_affixed, .navbar, .navbar-light {
  background-color: var(--fw-bg) !important;
  background: var(--fw-bg) !important;
  border-bottom: 1px solid var(--fw-border) !important;
}

.nav-link, .navbar-light .navbar-nav .nav-link {
  color: var(--fw-text-dim) !important;
  font-weight: 400 !important;
  font-size: 0.9rem !important;
}

.nav-link:hover {
  color: var(--fw-text) !important;
}

/* LOGO FIX - Mix-Blend-Mode */
.fw-logo-img, img[alt*="logo"], img[src*="logo"], .navbar-brand img {
  height: 32px !important;
  width: auto !important;
  filter: none !important;
  mix-blend-mode: screen !important;
  opacity: 0.9 !important;
}

footer, .o_footer {
  background-color: var(--fw-surface) !important;
  color: var(--fw-text-dim) !important;
  padding: 2rem 0 !important;
  border-top: 1px solid var(--fw-border) !important;
}

.o_footer .o_footer_copyright {
  display: none !important;
}
</style>"""

print("Updating CSS with Logo Fix (mix-blend-mode)...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': css_update}])
print("Logo Fix applied!")
