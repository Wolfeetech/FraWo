import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

home_html = """<?xml version="1.0"?>
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'homepage'"/>
        
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&amp;display=swap" rel="stylesheet"/>
        
        <style>
            .fw-split-wrapper {
                font-family: 'Outfit', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #000;
            }
            .fw-split-container {
                display: flex;
                flex-direction: row;
                height: calc(100vh - 72px); /* Assuming standard Odoo header height */
                min-height: 600px;
                width: 100%;
                overflow: hidden;
            }
            @media (max-width: 991px) {
                .fw-split-container {
                    flex-direction: column;
                    height: auto;
                }
            }
            
            .fw-split-panel {
                flex: 1;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: flex 0.7s cubic-bezier(0.25, 1, 0.5, 1);
                overflow: hidden;
                cursor: default;
            }
            
            /* Responsive Hover only on Desktop */
            @media (min-width: 992px) {
                .fw-split-container:hover .fw-split-panel {
                    flex: 0.8; /* Shrink non-hovered slightly */
                }
                .fw-split-container .fw-split-panel:hover {
                    flex: 1.4; /* Grow hovered significantly */
                }
            }
            
            @media (max-width: 991px) {
                .fw-split-panel {
                    min-height: 50vh;
                }
            }
            
            .fw-split-panel::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.5);
                transition: background 0.7s ease;
                z-index: 1;
            }
            .fw-split-panel:hover::before {
                background: rgba(0,0,0,0.1);
            }
            
            .fw-panel-tech {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            }
            
            .fw-panel-funk {
                background: linear-gradient(135deg, #050505 0%, #111827 100%);
            }
            /* Add a subtle glow behind the Funk side */
            .fw-panel-funk::after {
                content: '';
                position: absolute;
                top: 50%; left: 50%;
                width: 600px; height: 600px;
                background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, rgba(139,92,246,0.05) 50%, rgba(0,0,0,0) 70%);
                transform: translate(-50%, -50%);
                z-index: 0;
                pointer-events: none;
            }
            
            .fw-content {
                position: relative;
                z-index: 2;
                text-align: center;
                padding: 40px;
                color: #fff;
                transition: transform 0.7s cubic-bezier(0.25, 1, 0.5, 1);
            }
            .fw-split-panel:hover .fw-content {
                transform: scale(1.05);
            }
            
            .fw-title {
                font-size: 4rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 15px;
                line-height: 1;
            }
            @media (max-width: 768px) {
                .fw-title { font-size: 3rem; }
            }
            
            .fw-subtitle {
                font-size: 1.2rem;
                font-weight: 300;
                letter-spacing: 1px;
                margin-bottom: 40px;
                color: rgba(255,255,255,0.7);
            }
            
            .fw-btn {
                display: inline-block;
                padding: 15px 40px;
                font-size: 14px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-decoration: none;
                border-radius: 30px;
                transition: all 0.3s ease;
            }
            
            .fw-btn-tech {
                background: transparent;
                color: #fff;
                border: 2px solid #3b82f6;
            }
            .fw-btn-tech:hover {
                background: #3b82f6;
                box-shadow: 0 10px 20px rgba(59,130,246,0.3);
                color: #fff;
            }
            
            .fw-btn-funk {
                background: linear-gradient(135deg, #10B981, #059669);
                color: #fff;
                border: none;
                box-shadow: 0 10px 20px rgba(16,185,129,0.3);
            }
            .fw-btn-funk:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 30px rgba(16,185,129,0.5);
                color: #fff;
            }
            
            /* Logo Elements */
            .tech-accent { color: #3b82f6; }
            .funk-accent { color: #10B981; }
            
        </style>

        <div id="wrap" class="oe_structure oe_empty">
            <div class="fw-split-wrapper">
                <div class="fw-split-container">
                    
                    <!-- LEFT PANEL: B2B TECH -->
                    <div class="fw-split-panel fw-panel-tech">
                        <div class="fw-content">
                            <h1 class="fw-title">FRAWO <span class="tech-accent">TECH</span></h1>
                            <p class="fw-subtitle">IT-Consulting • Infrastructure • AI Solutions</p>
                            <a href="/contactus" class="fw-btn fw-btn-tech">Explore Solutions</a>
                        </div>
                    </div>
                    
                    <!-- RIGHT PANEL: B2C FUNK -->
                    <div class="fw-split-panel fw-panel-funk">
                        <div class="fw-content">
                            <h1 class="fw-title">FRAWO <span class="funk-accent">FUNK</span></h1>
                            <p class="fw-subtitle">Underground Electronic Broadcast • Community</p>
                            <a href="/frawo-funk" class="fw-btn fw-btn-funk">Listen Live</a>
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>
    </t>
</t>"""

existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search_read', [[('key', '=', 'website.homepage')]], {'fields': ['id']})
if existing_view:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0]['id'], {'arch': home_html}])
    print("SUCCESS: Deployed B2B/B2C Split Hero to Homepage.")
else:
    print("ERROR: View 'website.homepage' not found!")
