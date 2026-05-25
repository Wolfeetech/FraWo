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

def fix_tasks():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Hole alle Tasks...")
    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[]], {'fields': ['id', 'name', 'stage_id', 'state']})

    updated_count = 0
    done_count = 0

    for t in tasks:
        orig_name = t['name']
        new_name = orig_name
        
        text_lower = orig_name.lower()
        
        # Determine strict role based on keywords
        target_emoji = '🤖' # Default IT/Agent
        
        # Franz Keywords
        if any(x in text_lower for x in ['growbox', 'studio', 'vermieter', 'bauen', 'holz', 'wand', 'handwerk', 'franz']):
            target_emoji = '🛠️'
        # Wolf Keywords
        elif any(x in text_lower for x in ['dj', 'audio', 'kabel', 'patch', 'signal', 'auftritt', 'sound', 'mixer', 'wolfmix', 'wolf']):
            target_emoji = '🐺'
            
        # Remove old text tags and brackets completely if they are AGENT/WOLF/FRANZ
        new_name = re.sub(r'\[.*?agent.*?\]', '', new_name, flags=re.IGNORECASE)
        new_name = re.sub(r'\[.*?wolf.*?\]', '', new_name, flags=re.IGNORECASE)
        new_name = re.sub(r'\[.*?franz.*?\]', '', new_name, flags=re.IGNORECASE)
        
        # Remove all existing role emojis to avoid duplicates
        new_name = new_name.replace('🤖', '').replace('🐺', '').replace('🛠️', '').replace('👤', '').replace('👷‍♂️', '').replace('✅', '')
        
        # Clean up double spaces and leading/trailing dashes or spaces
        new_name = re.sub(r'\s+', ' ', new_name).strip(' -:[]')
        
        # Add new emoji
        new_name = f"{target_emoji} {new_name}"
        
        update_vals = {}
        if new_name != orig_name:
            update_vals['name'] = new_name
            
        # Hard-Set State to Done if in Erledigt stage
        stage_name = t['stage_id'][1] if t.get('stage_id') else ''
        if 'Erledigt' in stage_name or 'Done' in stage_name:
            if t.get('state') != '1_done':
                update_vals['state'] = '1_done'
                done_count += 1
                
        if update_vals:
            try:
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], update_vals])
                print(f"Update [{t['id']}]: {orig_name} -> {update_vals}")
                updated_count += 1
            except Exception as e:
                # If state doesn't exist or is invalid, try updating only the name
                if 'state' in update_vals:
                    del update_vals['state']
                    if update_vals:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], update_vals])
                        print(f"Update (ohne State) [{t['id']}]: {orig_name} -> {update_vals}")
                        updated_count += 1

    print(f"\n[OK] {updated_count} Aufgaben wurden bereinigt und {done_count} Aufgaben hart auf 'Erledigt' gesetzt!")

fix_tasks()
