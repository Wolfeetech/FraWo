import xmlrpc.client
import sys
import subprocess
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from odoo_env import resolve_connection


DEFAULT_URL = 'http://10.1.0.22:8069'
DEFAULT_DB = 'FraWo_Live'
DEFAULT_USER = 'admin'
DEFAULT_SSH_TARGET = '10.1.0.22'


def sql_escape(value: str) -> str:
    return value.replace("'", "''")

def orchestrate():
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    ssh_target = os.getenv("ODOO_SSH_TARGET", DEFAULT_SSH_TARGET)
    print(f'Attempting Odoo Authentication at {settings.url}...')
    try:
        common = xmlrpc.client.ServerProxy(f'{settings.url}/xmlrpc/2/common')
        uid = common.authenticate(settings.db, settings.user, settings.secret, {})
        if not uid:
            print('Authentication failed. Forcing password reset via psql...')
            pwd_reset = (
                f"UPDATE res_users SET password='{sql_escape(settings.secret)}' "
                f"WHERE login='{sql_escape(settings.user)}';"
            )
            subprocess.run(
                [
                    'ssh',
                    '-o',
                    'StrictHostKeyChecking=no',
                    ssh_target,
                    f'docker exec -i odoo_db_1 psql -U odoo -d {settings.db} -c "{pwd_reset}"',
                ],
                check=True,
            )
            uid = common.authenticate(settings.db, settings.user, settings.secret, {})
            if not uid:
                 print('CRITICAL: Authentication failed even after SQL reset.')
                 return
        
        print(f'Authenticated as {settings.user} (UID: {uid})')
        models = xmlrpc.client.ServerProxy(f'{settings.url}/xmlrpc/2/object')

        # 1. Update Company Information
        print('Updating Company Branding...')
        company_ids = models.execute_kw(settings.db, uid, settings.secret, 'res.company', 'search', [[['name', 'ilike', 'FraWo']]])
        if company_ids:
             models.execute_kw(settings.db, uid, settings.secret, 'res.company', 'write', [company_ids, {
                 'name': 'FraWo GbR',
                 'email': 'info@frawo-tech.de',
                 'website': 'https://frawo-tech.de'
             }])

        # 2. Inject Homepage Content
        print('Infecting Professional Architecture...')
        HOMEPAGE_ARCH = '''<?xml version="1.0"?>
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
            <section class="s_text_block pb80 pt80" style="background:#090b0a; color:white; min-height:80vh; display:flex; align-items:center;">
                <div class="container">
                    <h1 style="font-size:clamp(3rem, 6vw, 5rem); color:#b0ff00; font-family:sans-serif; font-weight:bold; line-height:1.1; margin-bottom:20px;">
                        Planung, Betrieb,<br/>digitale Begleitung.
                    </h1>
                    <p style="font-size:1.4rem; opacity:0.8; max-width:600px; line-height:1.6;">
                        FraWo GbR - Wir sorgen dafür, dass Veranstaltungstechnik und IT-Infrastruktur am Abend einfach funktionieren.
                    </p>
                    <a href="/contactus" style="display:inline-block; margin-top:40px; padding:20px 48px; background:#b0ff00; color:black; font-weight:bold; text-decoration:none; border-radius:4px;">Projekt anreissen</a>
                </div>
            </section>
        </div>
    </t>
</t>'''
        
        # Target ALL homepage views
        view_ids = models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
        for vid in view_ids:
            models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'write', [[vid], {'arch_db': HOMEPAGE_ARCH}])
            print(f'Successfully updated View ID: {vid}')

        # 3. Inject Ultra-Dark CSS
        DARK_CSS = '<style>body { background:#090b0a !important; color:white !important; } .navbar { background:#0a0c0b !important; border-bottom:1px solid rgba(255,255,255,0.1) !important; }</style>'
        css_ids = models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'search', [[['key', '=', 'website.user_custom_css']]])
        for cid in css_ids:
             models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'write', [[cid], {'arch': DARK_CSS}])
             print(f'Successfully updated CSS ID: {cid}')

        print('\nSUCCESS: Master Orchestration Complete.')

    except Exception as e:
        print(f'FAILED: {str(e)}')

if __name__ == '__main__':
    orchestrate()
