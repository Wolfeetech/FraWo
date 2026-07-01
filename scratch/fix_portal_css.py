#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def fix_portal_css():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Suche Portal Frontend Layout...")
    portal_layout = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'portal.frontend_layout')]])
    if not portal_layout:
        print("Fehler: portal.frontend_layout nicht gefunden!")
        return

    existing_fix = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'portal.frawo_dark_mode_fix')]])
    if existing_fix:
        print("CSS Fix existiert bereits! Lösche den alten Fix...")
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'unlink', [existing_fix])

    css = """<?xml version="1.0"?>
    <data>
        <xpath expr="//head" position="inside">
            <style>
                /* Zwinge den Haupt-Portal-Bereich hell zu sein */
                .o_portal_wrap {
                    background-color: #f8f9fa !important;
                    color: #212529 !important;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                }
                .o_portal_page_content, .o_portal_sidebar {
                    background-color: #ffffff !important;
                    color: #212529 !important;
                    padding: 20px;
                    border-radius: 8px;
                }
                /* Überschriften im Portal */
                .o_portal_wrap h1, .o_portal_wrap h2, .o_portal_wrap h3, .o_portal_wrap h4, .o_portal_wrap h5, .o_portal_wrap h6 {
                    color: #212529 !important;
                }
                /* Tabellen und Listen im Portal */
                .o_portal_wrap table, .o_portal_wrap th, .o_portal_wrap td, .o_portal_wrap li, .o_portal_wrap span, .o_portal_wrap p, .o_portal_wrap div {
                    color: #212529 !important;
                }
                /* Bewahre Button Farben (primär) */
                .o_portal_wrap a:not(.btn) {
                    color: #0d6efd !important;
                }
                /* Überschreibe dunkle Odoo Klassen, falls sie greifen */
                .text-bg-dark, .bg-dark {
                    background-color: #ffffff !important;
                    color: #212529 !important;
                }
            </style>
        </xpath>
    </data>
    """
    print("Füge neues CSS in Odoo ein...")
    new_view_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
        'name': 'FraWo Portal Dark Mode Fix',
        'key': 'portal.frawo_dark_mode_fix',
        'type': 'qweb',
        'inherit_id': portal_layout[0],
        'arch': css,
        'active': True,
    }])
    print(f"[OK] Portal CSS Fix erfolgreich angewendet! (View ID: {new_view_id})")

fix_portal_css()
