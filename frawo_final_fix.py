# -*- coding: utf-8 -*-
import xmlrpc.client
import subprocess

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def sql_update_arch(view_id, arch):
    # Mapping for psql injection
    mapping = {
        'ä': "' || chr(228) || '",
        'ö': "' || chr(246) || '",
        'ü': "' || chr(252) || '",
        'ß': "' || chr(223) || '",
        'Ä': "' || chr(196) || '",
        'Ö': "' || chr(214) || '",
        'Ü': "' || chr(220) || '",
        '–': "' || chr(150) || '",
        '…': "' || chr(133) || '"
    }
    
    escaped_arch = arch.replace("'", "''")
    for char, psql_chr in mapping.items():
        escaped_arch = escaped_arch.replace(char, psql_chr)
    
    sql = f"UPDATE ir_ui_view SET arch_db = '{escaped_arch}' WHERE id = {view_id};"
    cmd = ["docker", "exec", "-e", "PGPASSWORD=odoo_db_pass_final_v1", "odoo_db_1", "psql", "-U", "odoo", "-d", "FraWo_GbR", "-c", sql]
    subprocess.run(cmd, check=True)

# HOMEPAGE
home_arch = """<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&amp;display=swap');
        :root{ --fw-bg:#0d1117; --fw-acc:#a855f7; --fw-acc-rgb:168,85,247; --fw-forest:#064e3b; }
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
              <p class="fw-lead mb-5">Präzise Lichtplanung, erstklassige Akustik-Konzepte und intelligente Automation. FraWo erschafft audiovisuelle Erlebnisse für anspruchsvolle Privatprojekte – von der Gartenillumination bis zum Heimkino.</p>
              <div class="d-flex flex-wrap gap-3">
                <a class="fw-btn-primary btn btn-lg" href="/contactus">Beratungsgespräch anfragen</a>
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
      <section id="services" style="padding: 100px 0; background:#0d1117;">
        <div class="container">
          <div class="row g-4">
            <div class="col-md-4"><div class="fw-card"><div class="fw-num">01</div><h3 style="color:#fff;">Heimkino &amp; HiFi</h3><p>Maßgeschneiderte Klangwelten und visuelle Erlebnisse. Wir planen und installieren Ihr individuelles High-End Setup.</p></div></div>
            <div class="col-md-4"><div class="fw-card"><div class="fw-num">02</div><h3 style="color:#fff;">Smart Living</h3><p>Intelligente Hausautomation und Beleuchtungssteuerung. Komfort und Sicherheit, einfach bedienbar integriert.</p></div></div>
            <div class="col-md-4"><div class="fw-card"><div class="fw-num">03</div><h3 style="color:#fff;">Akustik &amp; Licht</h3><p>Präzise Schallpegelmessung und ästhetische Lichtkonzepte für Architektur sowie Garten- &amp; Außenanlagen.</p></div></div>
          </div>
        </div>
      </section>
      <section style="padding: 60px 0; background:#0d1117;">
        <div class="container">
          <div class="fw-band">
            <div class="row align-items-center">
              <div class="col-lg-7">
                <h2 style="color:#fff; font-weight:800;">Technik, die sich unsichtbar macht.</h2>
                <p style="color:#a7f3d0; font-size:1.1rem;">Wir sorgen dafür, dass die Komplexität im Hintergrund bleibt, damit Sie nur das Ergebnis genießen.</p>
              </div>
              <div class="col-lg-5 text-lg-end"><a class="btn btn-light btn-lg" style="border-radius:12px; font-weight:700; color:#064e3b;" href="/contactus">Jetzt Kontakt aufnehmen</a></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""

# CONTACT
contact_arch = """<t name="Contact Us" t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <style>
        body { font-family: 'Poppins', sans-serif !important; background: #0d1117; color: #fff; }
        .fw-contact-hero { padding: 100px 0; background: #0d1117; }
        .fw-card { border-radius:1.2rem; background:rgba(22,27,34,.8); border:1px solid rgba(255,255,255,.07); padding:2rem; }
      </style>
      <section class="fw-contact-hero">
        <div class="container">
          <div class="row g-5">
            <div class="col-lg-6">
              <h1 style="font-weight:900; background:linear-gradient(135deg,#fff,#d8b4fe); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">Projektstart B2C.</h1>
              <p style="color:#94a3b8; font-size:1.1rem;">Für Ihr Heimkino-Projekt, Akustik-Messungen oder moderne Lichtplanung – wir freuen uns auf Ihre Anfrage.</p>
            </div>
            <div class="col-lg-6">
               <div class="fw-card">
                 <h3 style="color:#fff;">Kontaktformular</h3><p>Wir melden uns umgehend bei Ihnen.</p>
                 <hr style="border-color:rgba(255,255,255,.1);"/><p style="color:#fff;">Rothkreuz 14, 88138 Weißensberg</p>
               </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""

sql_update_arch(3644, home_arch)
sql_update_arch(3637, contact_arch)

# GLOBAL CSS - Specificity overkill to kill the white header
global_css = """<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap');
  :root { --fw-bg: #0d1117; }
  body, #wrap, header, footer, .navbar, .o_header_standard { font-family: 'Poppins', sans-serif !important; }
  header#top, .o_header_standard, .o_header_affixed, .navbar, .navbar-light { background-color: #0d1117 !important; background: #0d1117 !important; color: white !important; }
  footer, .o_footer { background-color: #0d1117 !important; color: #94a3b8 !important; }
  .nav-link, .navbar-light .navbar-nav .nav-link { color: #94a3b8 !important; }
  .nav-link:hover { color: #a855f7 !important; }
  .navbar-brand { color: white !important; font-weight: 800 !important; }
  /* Fix logo area white bar */
  .o_header_logo_area, .o_header_standard { border-bottom: 1px solid #30363d; }
</style>"""

models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': global_css, 'name': 'FraWo'}])

# Fix Footer
v_data = models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [[3632]], {'fields': ['arch_db']})
f_arch = v_data[0]['arch_db']
f_arch = f_arch.replace('Weissensberg', 'Weißensberg')
sql_update_arch(3632, f_arch)
print("Final Fix pushed.")
