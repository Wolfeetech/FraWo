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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# HTML content for the page
page_html = """<?xml version="1.0"?>
<t name="FraWo Funk" t-name="website.frawo_radio_page">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
            <section class="s_cover pt96 pb96" style="background-color: #0f0f0f; color: #ffffff; min-height: 80vh;">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-lg-8">
                            <h1 style="font-size: 6rem; font-weight: 900; letter-spacing: -3px; text-transform: uppercase; margin-bottom: 0;">FRAWO</h1>
                            <h1 style="font-size: 6rem; font-weight: 900; letter-spacing: -3px; text-transform: uppercase; color: #10B981; margin-top: -20px;">FUNK</h1>
                            <p class="lead mt-4" style="font-size: 1.5rem; font-weight: 400; color: #8B5CF6; text-transform: uppercase; letter-spacing: 2px;">Broadcasting from the Underground.</p>
                            
                            <div class="mt-5" style="display: flex; align-items: center; gap: 30px;">
                                <button id="play-button" style="background: #10B981; color: #0f0f0f; border: none; width: 100px; height: 100px; border-radius: 50%; font-size: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.2s;">
                                    ▶
                                </button>
                                <div>
                                    <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #8B5CF6; font-weight: bold; margin-bottom: 5px;">Now Playing</div>
                                    <div id="now-playing-title" style="font-size: 28px; font-weight: 700; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Live Stream</div>
                                </div>
                            </div>
                            
                            <audio id="radio-audio" preload="none">
                                <source src="https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3" type="audio/mpeg"/>
                            </audio>
                        </div>
                        
                        <div class="col-lg-4 mt-5 mt-lg-0">
                            <!-- Minimalist Grid / Schedule -->
                            <div style="border-left: 3px solid #1a1a1a; padding-left: 30px; height: 100%;">
                                <h3 style="font-weight: 800; text-transform: uppercase; font-size: 20px; margin-bottom: 30px; letter-spacing: 1px;">Schedule</h3>
                                <ul style="list-style: none; padding: 0; margin: 0;">
                                    <li style="margin-bottom: 25px;">
                                        <div style="color: #10B981; font-weight: bold; font-size: 14px; margin-bottom: 5px;">24 / 7</div>
                                        <div style="font-weight: 700; font-size: 18px; text-transform: uppercase;">Auto-DJ Rotation</div>
                                        <div style="color: #666; font-size: 14px; margin-top: 5px;">Mixed genres</div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var audio = document.getElementById('radio-audio');
                    var btn = document.getElementById('play-button');
                    var isPlaying = false;
                    
                    btn.addEventListener('click', function() {
                        if(isPlaying) {
                            audio.pause();
                            btn.innerHTML = '▶';
                            isPlaying = false;
                        } else {
                            audio.play();
                            btn.innerHTML = '⏸';
                            isPlaying = true;
                        }
                    });
                });
            </script>
        </div>
    </t>
</t>"""

# Check if view exists
existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website.frawo_radio_page')]])

if existing_view:
    view_id = existing_view[0]
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [view_id, {'arch': page_html}])
    print(f"Updated existing view {view_id}")
else:
    view_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
        'name': 'FraWo Funk Page',
        'type': 'qweb',
        'key': 'website.frawo_radio_page',
        'arch': page_html,
    }])
    print(f"Created new view {view_id}")

# Create or update the website.page
existing_page = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search', [[('url', '=', '/radio')]])
if existing_page:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'write', [existing_page[0], {'view_id': view_id, 'is_published': True}])
    print(f"Updated existing page /radio")
else:
    page_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'create', [{
        'name': 'FraWo Funk',
        'url': '/radio',
        'view_id': view_id,
        'is_published': True,
    }])
    print(f"Created new page /radio with ID {page_id}")

