import xmlrpc.client
import os
import re
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Read original arch
with open("C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo\\scratch\\radio_arch.html", "r", encoding="utf-8") as f:
    arch = f.read()

# Apply patches
# 1. Add playsinline to audio
arch = arch.replace('<audio id="audio-stream" crossorigin="anonymous"', '<audio id="audio-stream" crossorigin="anonymous" playsinline="playsinline"')

# 2. Modify JS to detect Safari and disable Web Audio API for it
old_js = """
                let isPlaying = false;
                let useFallback = false;
"""
new_js = """
                let isPlaying = false;
                const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
                let useFallback = isSafari;
"""
arch = arch.replace(old_js, new_js)

old_init = """
                function initAudio() {
                    if (!audioCtx) {
"""
new_init = """
                function initAudio() {
                    if (isSafari) {
                        useFallback = true;
                        return; // Safari has a bug with WebAudio routing live streams, so skip it to ensure audio plays
                    }
                    if (!audioCtx) {
"""
arch = arch.replace(old_init, new_init)

# Now update the view in Odoo
pages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[('url', '=', '/frawo-funk')]], {'fields': ['view_id']})
if pages:
    view_id = pages[0]['view_id'][0]
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [view_id, {'arch': arch}])
    print("SUCCESS: Patched FraWo Funk page for Safari compatibility!")
else:
    print("Error: Could not find page")
