# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://10.1.0.22:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def update_view(view_id, arch):
    models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[view_id], {'arch_db': arch}])

# ─── HOMEPAGE (3644) ───
# Use XML NCRs for all German characters to avoid encoding corruption
# ä: &#xe4;  ö: &#xf6;  ü: &#xfc;  ß: &#xdf;  –: &#x2013;  
home_arch = """<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&amp;display=swap');
        :root{
          --fw-bg:#0d1117;
          --fw-acc:#a855f7;
          --fw-acc-rgb:168,85,247;
          --fw-forest:#064e3b;
        }
        body { font-family: 'Poppins', sans-serif !important; background: #0d1117; color: #fff; }
        .fw-hero{ padding: 110px 0 90px; background: linear-gradient(135deg, #0d1117 0%, #111827 55%, #0d1117 100%); position: relative; overflow: hidden; }
        .fw-eyebrow{ font-size:.78rem; font-weight:700; letter-spacing:.25em; text-transform:uppercase; color:#a855f7; }
        .fw-h1{ font-size:clamp(2.5rem,6vw,4.5rem); font-weight:900; line-height:1.0; background:linear-gradient(135deg,#ffffff 0%,#d8b4fe 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
        .fw-lead{ color:#94a3b8; font-size:1.1rem; line-height:1.7; max-width:38rem; }
        .fw-btn-primary{ background:linear-gradient(135deg,#7c3aed,#a855f7) !important; border:none !important; border-radius:12px !important; padding:14px 32px !important; font-weight:700 !important; color:#fff !important; }
        .fw-card{ height:100%; border-radius:1.4rem; background:rgba(22,27,34,.85); border:1px solid rgba(255,255,255,.07); padding:2.2rem; backdrop-filter:blur(12px); transition:.3s ease; }
        .fw-card:hover{ border-color:rgba(168,85,247,.4); transform:translateY(-6px); }
        .fw-num{ font-size:2rem; font-weight:900; color:#a855f7; margin-bottom:.8rem; }
        .fw-band{ background:linear-gradient(135deg,#052e16 0%,#064e3b 100%); border-radius:1.8rem; padding:3rem; border:1px solid rgba(167,243,208,.1); }
      </style>

      <section class="fw-hero">
        <div class="container position-relative" style="z-index:1;">
          <div class="row align-items-center g-5">
            <div class="col-lg-6">
              <div class="fw-eyebrow mb-3">FraWo High-End Solutions</div>
              <h1 class="fw-h1 mb-4">High-End Home &amp;<br/>Audiophile Systeme.</h1>
              <p class="fw-lead mb-5">
                Pr&#xe4;zise Lichtplanung, erstklassige Akustik-Konzepte und intelligente Automation. 
                FraWo erschafft audiovisuelle Erlebnisse f&#xfc;r anspruchsvolle Privatprojekte &#x2013; von der Gartenillumination bis zum Heimkino.
              </p>
              <div class="d-flex flex-wrap gap-3">
                <a class="fw-btn-primary btn btn-lg" href="/contactus">Beratungsgespr&#xe4;ch anfragen</a>
                <a class="btn btn-outline-light btn-lg" style="border-radius:12px; font-weight:600;" href="#services">Services entdecken</a>
              </div>
            </div>
            <div class="col-lg-6">
              <div style="border-radius:1.5rem; overflow:hidden; box-shadow:0 30px 60px rgba(0,0,0,.5); border:1px solid rgba(168,85,247,.2);">
                <img src="/web/image/1803" style="width:100%; height:auto; display:block;" alt="Home Cinema Detail"/>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="services" class="fw-section" style="padding: 100px 0; background:#0d1117;">
        <div class="container">
          <div class="row g-4">
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">01</div>
                <h3 style="color:#fff;">Heimkino &amp; HiFi</h3>
                <p>Ma&#xdf;geschneiderte Klangwelten und visuelle Erlebnisse. Wir planen und installieren Ihr individuelles High-End Setup.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">02</div>
                <h3 style="color:#fff;">Smart Living</h3>
                <p>Intelligente Hausautomation und Beleuchtungssteuerung. Komfort und Sicherheit, einfach bedienbar integriert.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">03</div>
                <h3 style="color:#fff;">Akustik &amp; Licht</h3>
                <p>Pr&#xe4;zise Schallpegelmessung und &#xe4;sthetische Lichtkonzepte f&#xfc;r Architektur sowie Garten- &amp; Au&#xdf;enanlagen.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="fw-section" style="padding: 60px 0; background:#0d1117;">
        <div class="container">
          <div class="fw-band">
            <div class="row align-items-center">
              <div class="col-lg-7">
                <h2 style="color:#fff; font-weight:800;">Technik, die sich unsichtbar macht.</h2>
                <p style="color:#a7f3d0; font-size:1.1rem;">Wir sorgen daf&#xfc;r, dass die Komplexit&#xe4;t im Hintergrund bleibt, damit Sie nur das Ergebnis genie&#xdf;en.</p>
              </div>
              <div class="col-lg-5 text-lg-end">
                <a class="btn btn-light btn-lg" style="border-radius:12px; font-weight:700; color:#064e3b;" href="/contactus">Jetzt Kontakt aufnehmen</a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""

# ─── CONTACT PAGE (3637) ───
contact_arch = """<t name="Contact Us" t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <style>
        body { font-family: 'Poppins', sans-serif !important; background: #0d1117; color: #fff; }
        .fw-contact-hero { padding: 100px 0; background: linear-gradient(135deg, #0d1117 0%, #111827 100%); }
        .fw-card { border-radius:1.2rem; background:rgba(22,27,34,.8); border:1px solid rgba(255,255,255,.07); padding:2rem; }
      </style>
      <section class="fw-contact-hero">
        <div class="container">
          <div class="row g-5">
            <div class="col-lg-6">
              <h1 style="font-weight:900; background:linear-gradient(135deg,#fff,#d8b4fe); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">Projektstart B2C.</h1>
              <p style="color:#94a3b8; font-size:1.1rem;">F&#xfc;r Ihr Heimkino-Projekt, Akustik-Messungen oder moderne Lichtplanung &#x2013; wir freuen uns auf Ihre Anfrage.</p>
              <div class="mt-5">
                <div class="fw-card mb-3">
                  <h4 style="color:#fff;">E-Mail Anfrage</h4>
                  <a href="mailto:info@frawo-tech.de" style="color:#a855f7; font-weight:600; font-size:1.2rem; text-decoration:none;">info@frawo-tech.de</a>
                </div>
                <div class="fw-card">
                  <h4 style="color:#fff;">Telefonischer Kontakt</h4>
                  <a href="tel:+4915155243164" style="color:#a855f7; font-weight:600; font-size:1.2rem; text-decoration:none;">+49 151 55 24 31 64</a>
                </div>
              </div>
            </div>
            <div class="col-lg-6">
               <div class="fw-card" style="background:#161b22; border-color:#a855f7;">
                 <h3 style="color:#fff; margin-bottom:1.5rem;">Senden Sie uns eine Nachricht</h3>
                 <p style="color:#94a3b8;">Wir antworten in der Regel innerhalb von 24 Stunden auf Ihre Anfrage.</p>
                 <hr style="border-color:rgba(255,255,255,.1);"/>
                 <p style="color:#fff;">Rothkreuz 14<br/>88138 Wei&#xdf;ensberg</p>
               </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""

# ─── GLOBAL BRANDING & FIXES ───
global_css = """<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap');
  body, #wrap { font-family: 'Poppins', sans-serif !important; }
  header#top, footer { background-color: #0d1117 !important; border-color: #30363d !important; }
  header#top .navbar, footer { color: #fff !important; }
  header#top .nav-link, footer a { color: #94a3b8 !important; }
  header#top .nav-link:hover, footer a:hover { color: #a855f7 !important; }
</style>"""

# Push updates
update_view(3644, home_arch)
print("Homepage updated (NCR fix).")

update_view(3637, contact_arch)
print("Contact page updated (NCR fix).")

models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': global_css}])
print("Global CSS updated.")

print("All NCR-protected updates complete!")
