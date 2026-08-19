import xmlrpc.client
import os
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

home_html = """<?xml version="1.0"?>
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'homepage'"/>
        
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&amp;display=swap" rel="stylesheet"/>
        
        <style>
            :root {
                --tech-primary: #3b82f6;
                --tech-accent: #60a5fa;
                --funk-primary: #10B981;
                --funk-accent: #34d399;
                --dark-bg: #030712;
            }
            
            body, html {
                margin: 0; padding: 0;
                font-family: 'Outfit', sans-serif;
                background-color: var(--dark-bg);
                color: #fff;
                overflow-x: hidden;
            }
            
            /* Dynamic Background Setup */
            .fw-hero-section {
                position: relative;
                width: 100%;
                min-height: calc(100vh - 72px);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                padding: 40px 20px;
            }

            /* Animated Gradient Mesh */
            .fw-mesh-bg {
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: 
                    radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.15), transparent 40%),
                    radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.15), transparent 40%),
                    radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.1), transparent 50%);
                filter: blur(40px);
                z-index: 0;
                animation: mesh-move 15s ease-in-out infinite alternate;
            }

            @keyframes mesh-move {
                0% { transform: scale(1) translate(0, 0); }
                50% { transform: scale(1.1) translate(2%, 3%); }
                100% { transform: scale(1) translate(-2%, -2%); }
            }

            /* Navigation/Auth Bar embedded in Hero */
            .fw-auth-nav {
                position: absolute;
                top: 30px;
                right: 40px;
                z-index: 10;
                display: flex;
                gap: 15px;
            }
            
            .fw-auth-btn {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #fff;
                padding: 10px 24px;
                border-radius: 50px;
                font-weight: 600;
                font-size: 0.9rem;
                text-decoration: none;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .fw-auth-btn:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                color: #fff;
            }

            .fw-auth-btn.primary {
                background: linear-gradient(135deg, var(--tech-primary), #2563eb);
                border: none;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            }
            
            .fw-auth-btn.primary:hover {
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
                background: linear-gradient(135deg, #60a5fa, var(--tech-primary));
            }

            /* Split Content Container */
            .fw-split-container {
                position: relative;
                z-index: 2;
                display: flex;
                flex-direction: row;
                width: 100%;
                max-width: 1400px;
                gap: 30px;
                margin-top: 40px;
            }

            @media (max-width: 991px) {
                .fw-split-container {
                    flex-direction: column;
                    margin-top: 80px;
                }
                .fw-auth-nav {
                    top: 20px;
                    right: 20px;
                    width: 100%;
                    justify-content: center;
                    padding-right: 40px;
                }
            }

            /* Glassmorphism Cards */
            .fw-card {
                flex: 1;
                background: rgba(15, 23, 42, 0.4);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 24px;
                padding: 60px 40px;
                text-align: center;
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                cursor: pointer;
            }

            .fw-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 3px;
                background: transparent;
                transition: all 0.5s ease;
            }

            .fw-card-tech::before { background: linear-gradient(90deg, transparent, var(--tech-primary), transparent); opacity: 0; }
            .fw-card-funk::before { background: linear-gradient(90deg, transparent, var(--funk-primary), transparent); opacity: 0; }

            .fw-card:hover {
                transform: translateY(-10px);
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .fw-card-tech:hover {
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 40px rgba(59, 130, 246, 0.1);
            }
            .fw-card-tech:hover::before { opacity: 1; }

            .fw-card-funk:hover {
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 40px rgba(16, 185, 129, 0.1);
            }
            .fw-card-funk:hover::before { opacity: 1; }

            /* Card Content Typography */
            .fw-card-title {
                font-size: 3.5rem;
                font-weight: 900;
                margin-bottom: 20px;
                letter-spacing: -1px;
                line-height: 1.1;
                background: #fff;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .fw-card-tech .fw-card-title { background: linear-gradient(135deg, #fff, var(--tech-accent)); -webkit-background-clip: text; }
            .fw-card-funk .fw-card-title { background: linear-gradient(135deg, #fff, var(--funk-accent)); -webkit-background-clip: text; }

            .fw-card-desc {
                font-size: 1.1rem;
                font-weight: 300;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 40px;
                line-height: 1.6;
            }

            /* Action Buttons inside Cards */
            .fw-action-btn {
                display: inline-block;
                padding: 16px 40px;
                border-radius: 50px;
                font-size: 1rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                text-decoration: none;
                position: relative;
                overflow: hidden;
                z-index: 1;
                transition: color 0.4s ease;
            }

            .fw-action-btn::after {
                content: '';
                position: absolute;
                bottom: 0; left: 0; right: 0; top: 0;
                z-index: -1;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .btn-tech {
                color: #fff;
                background: transparent;
                border: 2px solid var(--tech-primary);
            }
            .btn-tech::after {
                background: var(--tech-primary);
                transform: scaleY(0);
                transform-origin: bottom;
            }
            .btn-tech:hover::after { transform: scaleY(1); }
            .btn-tech:hover { color: #fff; }

            .btn-funk {
                color: #000;
                background: var(--funk-primary);
                border: 2px solid var(--funk-primary);
                box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2);
            }
            .btn-funk::after {
                background: #fff;
                transform: scaleX(0);
                transform-origin: left;
            }
            .btn-funk:hover::after { transform: scaleX(1); }
            .btn-funk:hover { color: var(--funk-primary); border-color: #fff; box-shadow: 0 15px 30px rgba(255,255,255,0.2); }

            /* Reveal Animations */
            .reveal {
                opacity: 0;
                transform: translateY(30px);
                animation: revealUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            .delay-1 { animation-delay: 0.2s; }
            .delay-2 { animation-delay: 0.4s; }

            @keyframes revealUp {
                to { opacity: 1; transform: translateY(0); }
            }
            
        </style>

        <div id="wrap" class="oe_structure oe_empty">
            <div class="fw-hero-section">
                <!-- Dynamic Mesh Background -->
                <div class="fw-mesh-bg"></div>

                <!-- Registration / Login Navigation -->
                <div class="fw-auth-nav reveal">
                    <a href="/web/login" class="fw-auth-btn">
                        <i class="fa fa-user-circle-o"></i> Login
                    </a>
                    <a href="/web/signup" class="fw-auth-btn primary">
                        Community Joinen
                    </a>
                </div>

                <!-- Split Cards -->
                <div class="fw-split-container">
                    
                    <!-- TECH CARD -->
                    <div class="fw-card fw-card-tech reveal delay-1" onclick="window.location.href='/contactus'">
                        <h2 class="fw-card-title">FRAWO TECH</h2>
                        <p class="fw-card-desc">
                            Maßgeschneiderte IT-Lösungen, High-End Infrastructure und smarte Automatisierung für dein Business. <br/>
                            Zuverlässig. Skalierbar. Professionell.
                        </p>
                        <a href="/contactus" class="fw-action-btn btn-tech">Business Solutions</a>
                    </div>
                    
                    <!-- FUNK CARD -->
                    <div class="fw-card fw-card-funk reveal delay-2" onclick="window.location.href='/frawo-funk'">
                        <h2 class="fw-card-title">FRAWO FUNK</h2>
                        <p class="fw-card-desc">
                            Premium Electronic Music Broadcast. <br/>
                            Tauche ein in feinsten Sound, Live-Sets und eine exklusive Community rund um die Uhr.
                        </p>
                        <a href="/frawo-funk" class="fw-action-btn btn-funk">Listen Live</a>
                    </div>

                </div>
            </div>
        </div>
        
        <script>
            // 3D Tilt Effect for Desktop
            document.addEventListener("DOMContentLoaded", function() {
                if (window.innerWidth > 991) {
                    const cards = document.querySelectorAll('.fw-card');
                    
                    cards.forEach(card => {
                        card.addEventListener('mousemove', e => {
                            const rect = card.getBoundingClientRect();
                            const x = e.clientX - rect.left;
                            const y = e.clientY - rect.top;
                            
                            const centerX = rect.width / 2;
                            const centerY = rect.height / 2;
                            
                            const rotateX = ((y - centerY) / centerY) * -5;
                            const rotateY = ((x - centerX) / centerX) * 5;
                            
                            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
                        });
                        
                        card.addEventListener('mouseleave', () => {
                            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
                            card.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                        });
                        
                        card.addEventListener('mouseenter', () => {
                            card.style.transition = 'none';
                        });
                    });
                }
            });
        </script>
    </t>
</t>"""

existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search_read', [[('key', '=', 'website.homepage')]], {'fields': ['id']})
if existing_view:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0]['id'], {'arch': home_html}])
    print("SUCCESS: Deployed V2 Glassmorphism Split Hero to Homepage.")
else:
    print("ERROR: View 'website.homepage' not found!")
