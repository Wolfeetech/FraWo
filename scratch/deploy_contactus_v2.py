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

new_arch = """<t t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure oe_empty">
      <style>
        :root {
          --fw-bg: #030303;
          --fw-surface: rgba(20, 20, 20, 0.6);
          --fw-tech-blue: #3b82f6;
          --fw-tech-glow: rgba(59, 130, 246, 0.5);
          --fw-text: #ffffff;
          --fw-text-2: #a1a1aa;
        }
        body {
          background-color: var(--fw-bg);
          color: var(--fw-text);
          font-family: 'Inter', sans-serif;
        }
        .mesh-bg {
          position: fixed;
          top: 0; left: 0; width: 100vw; height: 100vh;
          z-index: -1;
          background: 
            radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.15), transparent 40%),
            radial-gradient(circle at 85% 30%, rgba(59, 130, 246, 0.1), transparent 40%);
        }
        .glass-card {
          background: var(--fw-surface);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 1.5rem;
          padding: 2.5rem;
          box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .fw-input {
          background: rgba(0,0,0,0.3) !important;
          border: 1px solid rgba(59, 130, 246, 0.3) !important;
          color: white !important;
          border-radius: 0.75rem !important;
          padding: 0.8rem 1rem !important;
        }
        .fw-input:focus {
          border-color: var(--fw-tech-blue) !important;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
        }
        .fw-label {
          color: var(--fw-tech-blue);
          font-weight: 600;
          margin-bottom: 0.5rem;
        }
        .fw-btn-tech {
          background: linear-gradient(135deg, #2563eb, #3b82f6);
          color: white;
          border: none;
          border-radius: 0.75rem;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        .fw-btn-tech:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px -10px var(--fw-tech-glow);
          color: white;
        }
      </style>

      <div class="mesh-bg"></div>

      <section style="padding: 100px 0 60px 0; text-align: center; position: relative;">
        <div class="container">
          <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(59, 130, 246, 0.1); padding: 0.5rem 1rem; border-radius: 2rem; border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 2rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
            <span style="color: #3b82f6; font-weight: 600; font-size: 0.9rem; letter-spacing: 1px;">FRAWO TECH</span>
          </div>
          <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem;">
            Start dein <span style="background: linear-gradient(135deg, #60a5fa, #2563eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Projekt</span>.
          </h1>
          <p style="font-size: 1.25rem; color: var(--fw-text-2); max-width: 600px; margin: 0 auto;">
            Ob Smart Home, Heimkino oder Event-Technik am Bodensee. Erzähl uns von deiner Idee – wir kümmern uns um die Technik.
          </p>
        </div>
      </section>

      <section style="padding-bottom: 100px;">
        <div class="container">
          <div class="row g-5">
            
            <div class="col-lg-7">
              <div class="glass-card">
                <h3 style="font-weight: 700; margin-bottom: 2rem; display: flex; align-items: center; gap: 10px;">
                  <i class="fa fa-envelope" style="color: var(--fw-tech-blue);"></i> Projektanfrage
                </h3>
                
                <form id="contact-form" action="/website/form/" method="post" enctype="multipart/form-data">
                  <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
                  <input type="hidden" name="model_name" value="crm.lead"/>
                  <input type="hidden" name="success_page" value="/contactus-thank-you"/>
                  
                  <div class="row g-3">
                    <div class="col-md-6 mb-3">
                      <label for="contact_name" class="fw-label">Dein Name *</label>
                      <input type="text" class="form-control fw-input" id="contact_name" name="contact_name" required="required"/>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="email_from" class="fw-label">Deine E-Mail *</label>
                      <input type="email" class="form-control fw-input" id="email_from" name="email_from" required="required"/>
                    </div>
                  </div>

                  <div class="mb-3">
                    <label for="phone" class="fw-label">Telefon (optional)</label>
                    <input type="tel" class="form-control fw-input" id="phone" name="phone"/>
                  </div>

                  <div class="mb-3">
                    <label for="name" class="fw-label">Was planst du? *</label>
                    <select class="form-select fw-input" id="name" name="name" required="required">
                      <option value="" style="background: #111;">Bitte wählen...</option>
                      <option value="Event-Technik" style="background: #111;">Event-Technik (FOH, Licht, Streaming)</option>
                      <option value="Equipment-Verleih" style="background: #111;">Equipment-Verleih (Lautsprecher, Licht, Drohne)</option>
                      <option value="Smart Home" style="background: #111;">Smart Home (Home Assistant, Hue, Shelly)</option>
                      <option value="Heimkino" style="background: #111;">Heimkino &amp; Akustik</option>
                      <option value="Innenausbau" style="background: #111;">Innenausbau (Möbel, Racks, Akustikpanels)</option>
                      <option value="Studio Interesse" style="background: #111;">Studio Rothkreuz (Interesse)</option>
                      <option value="Sonstiges" style="background: #111;">Sonstiges</option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label for="timeline" class="fw-label">Wann soll's fertig sein? *</label>
                    <input type="text" class="form-control fw-input" id="timeline" name="timeline" placeholder="z.B. 'Juli 2026' oder 'flexibel'" required="required"/>
                  </div>

                  <div class="mb-4">
                    <label for="description" class="fw-label">Beschreibe dein Projekt *</label>
                    <textarea class="form-control fw-input" id="description" name="description" rows="5" required="required" placeholder="Was willst du machen? Was ist die größte Sorge? Hast du schon Hardware?"></textarea>
                  </div>

                  <div class="mb-4 form-check">
                    <input class="form-check-input" type="checkbox" id="privacy" name="privacy" required="required" style="background: rgba(0,0,0,0.3); border-color: rgba(59,130,246,0.3);"/>
                    <label class="form-check-label" for="privacy" style="color: var(--fw-text-2); font-size: 0.9rem;">
                      Ich habe die <a href="/datenschutz" target="_blank" style="color: var(--fw-tech-blue); text-decoration: none;">Datenschutzerklärung</a> gelesen und stimme der Verarbeitung zu. *
                    </label>
                  </div>

                  <button type="submit" class="btn fw-btn-tech w-100 py-3" style="font-size: 1.1rem;">
                    Anfrage senden <i class="fa fa-paper-plane ms-2"></i>
                  </button>
                </form>
              </div>
            </div>

            <div class="col-lg-5">
              <div class="glass-card mb-4" style="background: rgba(59, 130, 246, 0.05);">
                <h4 style="font-weight: 700; margin-bottom: 1rem;"><i class="fa fa-info-circle" style="color: var(--fw-tech-blue);"></i> Was du schreiben solltest</h4>
                <ul style="color: var(--fw-text-2); line-height: 1.6; margin-bottom: 0; padding-left: 1.2rem;">
                  <li class="mb-2"><strong>Was willst du machen?</strong> (Event, Smart Home, etc.)</li>
                  <li class="mb-2"><strong>Wann?</strong> (Zeitrahmen, Flexibilität)</li>
                  <li class="mb-2"><strong>Größte Sorge?</strong> (Budget, Technik, Zeitdruck)</li>
                  <li><strong>Hardware?</strong> (Vorhanden oder nicht?)</li>
                </ul>
                <div style="margin-top: 1rem; font-size: 0.9rem; color: #60a5fa;">
                  <i class="fa fa-clock-o"></i> Typische Antwortzeit: 2 Werktage.
                </div>
              </div>

              <div class="glass-card mb-4">
                <h4 style="font-weight: 700; margin-bottom: 1rem;"><i class="fa fa-calendar-check-o" style="color: var(--fw-tech-blue);"></i> Verfügbarkeit 2026</h4>
                <p style="color: var(--fw-text-2); margin-bottom: 0; line-height: 1.6;">
                  Wir haben aktuell <strong>begrenzte Kapazitäten</strong>. Für größere Projekte bitte rechtzeitig anfragen!
                </p>
              </div>

              <div class="glass-card" style="padding: 0; overflow: hidden;">
                <div style="padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                  <h4 style="font-weight: 700; margin: 0;"><i class="fa fa-map-marker" style="color: var(--fw-tech-blue);"></i> Bodensee-Region</h4>
                  <p style="color: var(--fw-text-2); font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 0;">Weißensberg (Lindau/Bregenz). Wir arbeiten regional und deutschlandweit.</p>
                </div>
                <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=9.6,47.55,9.75,47.62&amp;layer=mapnik&amp;marker=47.585,9.675" width="100%" height="250" style="border:0; display:block;" allowfullscreen="" loading="lazy"></iframe>
              </div>
            </div>

          </div>
        </div>
      </section>

      <script>
      document.addEventListener('DOMContentLoaded', function() {
          var form = document.getElementById('contact-form');
          if (form) {
              form.addEventListener('submit', function(event) {
                  event.preventDefault();
                  var timelineInput = document.getElementById('timeline');
                  var interestInput = document.getElementById('name');
                  var descInput = document.getElementById('description');
                  var privacyInput = document.getElementById('privacy');
                  
                  if (timelineInput &amp;&amp; interestInput &amp;&amp; descInput) {
                      var timeline = timelineInput.value;
                      var interest = interestInput.value;
                      var originalDesc = descInput.value;
                      
                      descInput.value = "[Zeitrahmen: " + timeline + "] [Interesse: " + interest + "]\\n\\nBeschreibung:\\n" + originalDesc;
                      
                      timelineInput.removeAttribute('name');
                      if (privacyInput) privacyInput.removeAttribute('name');
                      
                      HTMLFormElement.prototype.submit.call(form);
                  }
              });
          }
      });
      </script>
    </div>
  </t>
</t>"""

pages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[('url', '=', '/contactus')]], {'fields': ['view_id']})
if pages:
    view_id = pages[0]['view_id'][0]
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [view_id, {'arch': new_arch}])
    print("SUCCESS: Deployed new V2 Contact Page")
else:
    print("Error: /contactus page not found")
