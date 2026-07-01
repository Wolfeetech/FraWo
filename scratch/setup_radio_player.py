import xmlrpc.client
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find website.layout ID
res = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.model.data', 'search_read', [[('module', '=', 'website'), ('name', '=', 'layout')]], {'fields': ['res_id']})
if not res:
    print("Could not find website.layout")
    sys.exit(1)
layout_id = res[0]['res_id']

# Create a QWeb view that injects the radio player into the website layout
player_html = """<data name="FraWo Radio Player" inherit_id="website.layout">
    <xpath expr="//div[@id='wrapwrap']" position="inside">
        <div id="frawo-radio-player" style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #1a1a1a; color: #fff; padding: 10px 20px; z-index: 9999; display: flex; align-items: center; justify-content: space-between; border-top: 2px solid #8B5CF6;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="/web/image/website/1/logo" alt="FraWo Logo" style="height: 40px; filter: grayscale(100%) brightness(200%);" />
                <div>
                    <h5 style="margin: 0; font-size: 16px; font-weight: bold; color: #10B981;">FraWo Funk</h5>
                    <span style="font-size: 12px; opacity: 0.8;">Live Stream</span>
                </div>
            </div>
            <audio id="frawo-audio" controls="controls" preload="none" style="height: 40px;">
                <source src="https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3" type="audio/mpeg" />
                Dein Browser unterstützt kein Audio.
            </audio>
        </div>
    </xpath>
</data>"""

# Check if view already exists
existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website.frawo_radio_player')]])
if existing:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing, {'arch': player_html}])
    print(f"Updated Radio Player view with ID: {existing[0]}")
else:
    view_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
        'name': 'frawo.radio.player',
        'type': 'qweb',
        'arch': player_html,
        'inherit_id': layout_id,
        'active': True,
        'customize_show': True,
        'key': 'website.frawo_radio_player'
    }])
    print(f"Created Radio Player view with ID: {view_id}")
