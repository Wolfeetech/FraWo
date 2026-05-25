#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
import re
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def fix_tasks_pass2():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Hole alle Tasks für Pass 2...")
    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[]], {'fields': ['id', 'name']})

    updated = 0
    for t in tasks:
        orig_name = t['name']
        
        # Strip all emojis to get the pure clean name
        clean_name = orig_name.replace('🤖', '').replace('🐺', '').replace('🛠️', '').strip(' -:')
        text_lower = clean_name.lower()
        
        target_emoji = '🤖' # IT default
        
        # Wolf: Technik, Signal, Kabel, Audio, Verträge, Finanzen
        if any(x in text_lower for x in ['patch', 'verkabel', 'signal', 'audio', 'sound', 'mixer', 'dj', 'auftritt', 'schallplatten', 'stream', 'obs', 'finanzamt', 'notar', 'gbr', 'vollmacht', 'quonto']):
            target_emoji = '🐺'
        # Franz: Handwerk, Grobes, Studiobau, Sanitär, Möbel
        elif any(x in text_lower for x in ['bau', 'holz', 'wand', 'handwerk', 'grob', 'schrank', 'badewanne', 'klo', 'küche', 'abfluss', 'growbox', 'studio', 'vermieter', 'toilette']):
            target_emoji = '🛠️'
            
        final_name = f"{target_emoji} {clean_name}"
        
        if final_name != orig_name:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], {'name': final_name}])
            print(f"Korrektur: {orig_name} -> {final_name}")
            updated += 1
            
    print(f"\n[OK] {updated} Aufgaben final nach korrekter Rolle umsortiert.")

fix_tasks_pass2()
