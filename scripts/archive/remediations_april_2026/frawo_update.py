# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# ─────────────────────────────────────────────────────────────────────────────
# HOMEPAGE (View 3644)
# ─────────────────────────────────────────────────────────────────────────────
home_arch = """<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">

      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&amp;display=swap');
        :root{
          --fw-bg:#0d1117;
          --fw-card:#161b22;
          --fw-border:#30363d;
          --fw-acc:#a855f7;
          --fw-acc-rgb:168,85,247;
          --fw-forest:#064e3b;
          --fw-forest-dark:#052e16;
          --fw-ink:#0f172a;
          --fw-soft:#64748b;
          --fw-white:#ffffff;
        }

        /* ── Base ── */
        body { font-family: 'Poppins', sans-serif !important; }

        /* ── Hero ── */
        .fw-hero{
          padding: 110px 0 90px;
          background: linear-gradient(135deg, #0d1117 0%, #111827 55%, #0d1117 100%);
          position: relative;
          overflow: hidden;
        }
        .fw-hero::before{
          content:'';
          position:absolute;
          top:-20%;right:-10%;
          width:55rem;height:55rem;
          border-radius:50%;
          background:radial-gradient(circle, rgba(168,85,247,.22) 0%, transparent 70%);
          pointer-events:none;
        }
        .fw-hero::after{
          content:'';
          position:absolute;
          bottom:-25%;left:-8%;
          width:40rem;height:40rem;
          border-radius:50%;
          background:radial-gradient(circle, rgba(6,78,59,.35) 0%, transparent 70%);
          pointer-events:none;
        }
        .fw-eyebrow{
          font-size:.78rem;
          font-weight:700;
          letter-spacing:.25em;
          text-transform:uppercase;
          color:#a855f7;
        }
        .fw-h1{
          font-size:clamp(2.8rem,6vw,5rem);
          font-weight:900;
          line-height:1.0;
          background:linear-gradient(135deg,#ffffff 0%,#d8b4fe 100%);
          -webkit-background-clip:text;
          -webkit-text-fill-color:transparent;
          background-clip:text;
        }
        .fw-lead{
          color:#94a3b8;
          font-size:1.15rem;
          line-height:1.7;
          max-width:38rem;
        }
        .fw-chip{
          display:inline-flex;align-items:center;gap:.5rem;
          padding:.55rem 1rem;border-radius:999px;
          border:1px solid #30363d;background:rgba(255,255,255,.05);
          color:#c4b5fd;font-size:.88rem;font-weight:600;
        }
        .fw-chip::before{
          content:'';width:.45rem;height:.45rem;border-radius:50%;
          background:#a855f7;flex-shrink:0;
        }
        .fw-btn-primary{
          background:linear-gradient(135deg,#7c3aed,#a855f7) !important;
          border:none !important;border-radius:12px !important;
          padding:14px 32px !important;font-weight:700 !important;
          color:#fff !important;transition:.25s ease !important;
          box-shadow:0 4px 20px rgba(168,85,247,.35) !important;
        }
        .fw-btn-primary:hover{
          transform:translateY(-2px) !important;
          box-shadow:0 8px 28px rgba(168,85,247,.5) !important;
        }
        .fw-btn-outline{
          background:transparent !important;
          border:2px solid #30363d !important;border-radius:12px !important;
          padding:12px 30px !important;font-weight:600 !important;
          color:#e2e8f0 !important;transition:.25s ease !important;
        }
        .fw-btn-outline:hover{
          border-color:#a855f7 !important;color:#c4b5fd !important;
        }

        /* ── Photo Stack ── */
        .fw-photo-stack{display:grid;grid-template-columns:1.2fr .8fr;gap:1.2rem;align-items:stretch;}
        .fw-photo-main{border-radius:1.5rem;overflow:hidden;
          box-shadow:0 32px 64px rgba(0,0,0,.6),0 0 0 1px rgba(168,85,247,.15);}
        .fw-photo-main img,.fw-photo-card img{width:100%;height:100%;object-fit:cover;display:block;}
        .fw-photo-side{display:grid;grid-template-rows:1fr 1fr;gap:1.2rem;}
        .fw-photo-card{border-radius:1.1rem;overflow:hidden;
          box-shadow:0 20px 40px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.07);}

        /* ── Section spacers ── */
        .fw-section{padding:80px 0;}
        .fw-section-sm{padding:50px 0;}

        /* ── Glass Cards ── */
        .fw-card{
          height:100%;border-radius:1.4rem;
          background:rgba(22,27,34,.85);
          border:1px solid rgba(255,255,255,.07);
          padding:2.2rem;
          backdrop-filter:blur(12px);
          transition:.3s ease;
        }
        .fw-card:hover{
          border-color:rgba(168,85,247,.4);
          transform:translateY(-6px);
          box-shadow:0 20px 48px rgba(168,85,247,.12);
        }
        .fw-num{
          font-size:2.2rem;font-weight:900;
          background:linear-gradient(135deg,#a855f7,#7c3aed);
          -webkit-background-clip:text;
          -webkit-text-fill-color:transparent;
          background-clip:text;
          line-height:1;margin-bottom:.8rem;
        }
        .fw-card h3{color:#f1f5f9;font-weight:800;margin-bottom:.8rem;}
        .fw-card p{color:#94a3b8;margin:0;}
        .fw-card ul{color:#94a3b8;padding-left:0;list-style:none;margin:0;}
        .fw-card ul li{padding:.35rem 0;display:flex;align-items:baseline;gap:.55rem;}
        .fw-card ul li::before{content:'•';color:#a855f7;flex-shrink:0;}

        /* ── Band: Dark Green ── */
        .fw-band{
          background:linear-gradient(135deg,#052e16 0%,#064e3b 100%);
          border-radius:1.8rem;padding:3rem;
          border:1px solid rgba(167,243,208,.1);
        }
        .fw-band-kicker{color:#a7f3d0;letter-spacing:.2em;text-transform:uppercase;font-weight:700;font-size:.75rem;}
        .fw-band h2{color:#f0fdf4;font-weight:900;}
        .fw-band p{color:#bbf7d0;}
        .fw-step{display:grid;grid-template-columns:auto 1fr;gap:1.2rem;align-items:start;}
        .fw-step-no{
          width:2.4rem;height:2.4rem;border-radius:999px;
          background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.2);
          display:flex;align-items:center;justify-content:center;
          font-weight:800;color:#a7f3d0;font-size:.9rem;flex-shrink:0;
        }
        .fw-step div{color:#dcfce7;}
        .fw-step strong{color:#f0fdf4;}

        /* ── Proof block ── */
        .fw-proof{
          border-radius:1.6rem;
          background:rgba(22,27,34,.7);
          border:1px solid rgba(255,255,255,.07);
          padding:2rem;
        }
        .fw-proof h3{color:#f1f5f9;font-weight:800;}
        .fw-proof ul{color:#94a3b8;padding-left:0;list-style:none;margin:0;}
        .fw-proof ul li{padding:.4rem 0;display:flex;gap:.6rem;align-items:baseline;}
        .fw-proof ul li::before{content:'→';color:#a855f7;flex-shrink:0;}
        .fw-proof strong{color:#e2e8f0;}
        .fw-gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;}
        .fw-gallery img{width:100%;height:11rem;object-fit:cover;border-radius:1rem;
          box-shadow:0 12px 32px rgba(0,0,0,.5);}

        /* ── CTA Card ── */
        .fw-cta-card{
          border-radius:1.6rem;
          background:rgba(22,27,34,.85);
          border:1px solid rgba(168,85,247,.2);
          padding:2.5rem;
          backdrop-filter:blur(12px);
        }
        .fw-cta-card h3{color:#f1f5f9;font-weight:800;}
        .fw-cta-card p{color:#94a3b8;}

        /* ── Responsiv ── */
        @media(max-width:991px){
          .fw-photo-stack{grid-template-columns:1fr;}
          .fw-photo-side{grid-template-columns:1fr 1fr;grid-template-rows:none;}
          .fw-gallery{grid-template-columns:1fr;}
          .fw-gallery img{height:16rem;}
          .fw-band{padding:1.8rem;}
        }
        @media(max-width:767px){
          .fw-hero{padding:80px 0 60px;}
          .fw-photo-side{grid-template-columns:1fr;}
        }
      </style>

      <!-- ─── HERO ──────────────────────────────────── -->
      <section class="fw-hero">
        <div class="container position-relative" style="z-index:1;">
          <div class="row align-items-center g-5">
            <div class="col-lg-6">
              <div class="fw-eyebrow mb-3">FraWo Hybrid Solutions</div>
              <h1 class="fw-h1 mb-4">Technik für Events &amp;<br/>High-End Home.</h1>
              <p class="fw-lead mb-5">
                Professionalität auf der Bühne, Leidenschaft für den Klang zu Hause.
                FraWo verbindet Event-Präzision mit audiophilen Setups und intelligenter Automation.
              </p>
              <div class="d-flex flex-wrap gap-3 mb-4">
                <a class="fw-btn-primary btn btn-lg" href="mailto:info@frawo-tech.de?subject=Projektanfrage%20FraWo">Projekt anfragen</a>
                <a class="fw-btn-outline btn btn-lg" href="/contactus">Kontakt</a>
              </div>
              <div class="d-flex flex-wrap gap-2">
                <span class="fw-chip">Event &amp; Live</span>
                <span class="fw-chip">Home Cinema &amp; HiFi</span>
                <span class="fw-chip">Smart Living</span>
              </div>
            </div>
            <div class="col-lg-6">
              <div class="fw-photo-stack">
                <div class="fw-photo-main"><img src="/web/image/1803" alt="FraWo Eventmotiv"/></div>
                <div class="fw-photo-side">
                  <div class="fw-photo-card"><img src="/web/image/1798" alt="Detail 1"/></div>
                  <div class="fw-photo-card"><img src="/web/image/1801" alt="Detail 2"/></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ─── SERVICE CARDS ─────────────────────────── -->
      <section class="fw-section" style="background:#0d1117;">
        <div class="container">
          <div class="row g-4">
            <div class="col-lg-4 d-flex">
              <div class="fw-card">
                <div class="fw-num">01</div>
                <h3>Event &amp; Live</h3>
                <p class="mb-3">Professionelle Ton-, Licht- und Zuspieltechnik. Betriebssicher, präzise, live-erprobt.</p>
                <ul>
                  <li>Ton- &amp; Lichttechnik</li>
                  <li>Medienzuspielung</li>
                  <li>Ablaufsteuerung</li>
                </ul>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="fw-card">
                <div class="fw-num">02</div>
                <h3>High-End Audio</h3>
                <p class="mb-3">Individuelle Heimkino- und HiFi-Konzepte mit audiophiler Präzision.</p>
                <ul>
                  <li>Heimkino &amp; HiFi</li>
                  <li>Schallpegelmessung</li>
                  <li>Akustik-Optimierung</li>
                </ul>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="fw-card">
                <div class="fw-num">03</div>
                <h3>Smart Living</h3>
                <p class="mb-3">Garten- und Architekturbeleuchtung sowie intelligente Hausautomation.</p>
                <ul>
                  <li>Lichtkonzepte Outdoor</li>
                  <li>Architekturlicht</li>
                  <li>Smart Home Integration</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ─── BAND: Wie wir arbeiten ────────────────── -->
      <section class="fw-section-sm" style="background:#0d1117;">
        <div class="container">
          <div class="fw-band">
            <div class="row g-4 align-items-start">
              <div class="col-lg-5">
                <div class="fw-band-kicker mb-3">Arbeitsweise</div>
                <h2 class="display-6 mb-3">Kein BlaBla. Ein sauberer Betriebsweg.</h2>
                <p>FraWo arbeitet wie ein verantwortlicher Technikpartner: kurz im Briefing, klar in den Entscheidungen, präsent im entscheidenden Moment.</p>
              </div>
              <div class="col-lg-7">
                <div class="d-grid gap-3">
                  <div class="fw-step"><div class="fw-step-no">01</div><div><strong>Briefing:</strong> Ziel, Konzept und Budget werden ohne Umwege festgelegt.</div></div>
                  <div class="fw-step"><div class="fw-step-no">02</div><div><strong>Planung:</strong> Systemdesign und Materialauswahl vor dem ersten Handgriff.</div></div>
                  <div class="fw-step"><div class="fw-step-no">03</div><div><strong>Umsetzung:</strong> Installation und Einmessung vor Ort – mit höchster Präzision.</div></div>
                  <div class="fw-step"><div class="fw-step-no">04</div><div><strong>Übergabe:</strong> Das System läuft auf Knopfdruck oder das Event startet reibungslos.</div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ─── PROOF / GALLERY ───────────────────────── -->
      <section class="fw-section" style="background:#0d1117;">
        <div class="container">
          <div class="row g-5 align-items-center">
            <div class="col-lg-5">
              <div class="fw-eyebrow mb-3">Positionierung</div>
              <h2 class="display-6 mb-3" style="color:#f1f5f9;font-weight:900;">Bereit für echte Präzision?</h2>
              <p style="color:#94a3b8;" class="mb-3">
                Ein herausragendes Event oder ein High-End Heimkino haben eines gemeinsam:
                kompromisslose Technik und Erfahrung.
              </p>
              <p style="color:#94a3b8;" class="mb-0">
                Egal ob gewerbliches Projekt oder exklusive Privatinstallation –
                am schnellsten startet der Prozess per Mail.
              </p>
            </div>
            <div class="col-lg-7">
              <div class="fw-proof">
                <div class="row g-4 align-items-center">
                  <div class="col-lg-7">
                    <h3 class="h3 mb-3">Klar definierte Services</h3>
                    <ul>
                      <li><strong>Eventbetreuung:</strong> Signalweg, Zuspielung und Live-Sicherheit.</li>
                      <li><strong>HiFi &amp; Akustik:</strong> Einmessung, Schallpegel und Beratung.</li>
                      <li><strong>Lichtkonzepte:</strong> Architekturlicht und Garten-Illumination.</li>
                      <li><strong>Smart Home:</strong> Mediensteuerung ohne Komplexität.</li>
                    </ul>
                  </div>
                  <div class="col-lg-5">
                    <div class="fw-gallery">
                      <img src="/web/image/1797" alt="FraWo Galerie 1"/>
                      <img src="/web/image/1805" alt="FraWo Galerie 2"/>
                      <img src="/web/image/1806" alt="FraWo Galerie 3"/>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ─── CTA ───────────────────────────────────── -->
      <section class="fw-section-sm" style="background:#0d1117;">
        <div class="container">
          <div class="row g-5 align-items-center">
            <div class="col-lg-6">
              <div class="fw-eyebrow mb-3">Kontakt</div>
              <h2 class="display-6 mb-3" style="color:#f1f5f9;font-weight:900;">Wenn es konkret werden soll – direkt melden.</h2>
              <p style="color:#94a3b8;" class="mb-0">Am schnellsten per Mail. Für die schnelle Rückfrage ist das Telefon da.</p>
            </div>
            <div class="col-lg-6">
              <div class="fw-cta-card">
                <h3 class="mb-3">Projektstart</h3>
                <p class="mb-4">Egal ob Eventanfrage oder audiophiles Heim-Projekt – eine kurze Mail reicht.</p>
                <div class="d-flex flex-wrap gap-3">
                  <a class="fw-btn-primary btn" href="mailto:info@frawo-tech.de?subject=Projektanfrage%20FraWo">info@frawo-tech.de</a>
                  <a class="fw-btn-outline btn" href="tel:+4915155243164">+49 151 55 24 31 64</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </t>
</t>"""

# ─────────────────────────────────────────────────────────────────────────────
# CONTACT PAGE (View 3637)
# ─────────────────────────────────────────────────────────────────────────────
contact_arch = """<t name="Contact Us" t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&amp;display=swap');
        body{font-family:'Poppins',sans-serif !important;}
        .fw-contact-hero{
          padding:110px 0 90px;
          background:linear-gradient(135deg,#0d1117 0%,#111827 55%,#0d1117 100%);
          position:relative;overflow:hidden;
        }
        .fw-contact-hero::before{
          content:'';position:absolute;top:-10%;right:-10%;
          width:50rem;height:50rem;border-radius:50%;
          background:radial-gradient(circle,rgba(168,85,247,.2) 0%,transparent 70%);
        }
        .fw-eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:#c4b5fd;}
        .fw-ch1{
          font-size:clamp(2.5rem,5vw,4.2rem);font-weight:900;line-height:1.0;
          background:linear-gradient(135deg,#fff 0%,#d8b4fe 100%);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        }
        .fw-contact-img{border-radius:1.5rem;overflow:hidden;
          box-shadow:0 32px 64px rgba(0,0,0,.6),0 0 0 1px rgba(168,85,247,.15);}
        .fw-contact-img img{width:100%;height:100%;min-height:22rem;object-fit:cover;}
        .fw-contact-section{padding:80px 0;background:#0d1117;}
        .fw-info-card{
          height:100%;border-radius:1.4rem;
          background:rgba(22,27,34,.85);border:1px solid rgba(255,255,255,.07);
          padding:2rem;transition:.3s ease;
        }
        .fw-info-card:hover{border-color:rgba(168,85,247,.35);transform:translateY(-4px);}
        .fw-info-card h3{color:#f1f5f9;font-weight:800;}
        .fw-info-card p{color:#94a3b8;margin:0;}
        .fw-info-card a{color:#c4b5fd;}
        .fw-btn-p{
          background:linear-gradient(135deg,#7c3aed,#a855f7) !important;
          border:none !important;border-radius:12px !important;
          padding:14px 32px !important;font-weight:700 !important;
          color:#fff !important;box-shadow:0 4px 20px rgba(168,85,247,.35) !important;
          transition:.25s ease !important;
        }
        .fw-btn-p:hover{transform:translateY(-2px) !important;box-shadow:0 8px 28px rgba(168,85,247,.5) !important;}
        .fw-btn-o{
          background:transparent !important;
          border:2px solid #30363d !important;border-radius:12px !important;
          padding:12px 30px !important;font-weight:600 !important;color:#e2e8f0 !important;
          transition:.25s ease !important;
        }
        .fw-btn-o:hover{border-color:#a855f7 !important;color:#c4b5fd !important;}
        @media(max-width:991px){.fw-contact-hero{padding:80px 0 60px;}}
      </style>

      <section class="fw-contact-hero">
        <div class="container position-relative" style="z-index:1;">
          <div class="row align-items-center g-5">
            <div class="col-lg-7">
              <div class="fw-eyebrow mb-3">Kontakt</div>
              <h1 class="fw-ch1 mb-4">Projektstart ohne Umwege.</h1>
              <p style="color:#94a3b8;font-size:1.1rem;line-height:1.7;max-width:38rem;" class="mb-5">
                Egal ob Event-Anfrage, High-End Heimkino oder Smart-Living-Projekt.
                FraWo antwortet lieber konkret als künstlich aufgeblasen.
              </p>
              <div class="d-flex flex-wrap gap-3">
                <a class="fw-btn-p btn btn-lg" href="mailto:info@frawo-tech.de?subject=Projektanfrage%20FraWo">info@frawo-tech.de</a>
                <a class="fw-btn-o btn btn-lg" href="tel:+4915155243164">+49 151 55 24 31 64</a>
              </div>
            </div>
            <div class="col-lg-5">
              <div class="fw-contact-img"><img src="/web/image/1803" alt="FraWo Kontakt"/></div>
            </div>
          </div>
        </div>
      </section>

      <section class="fw-contact-section">
        <div class="container">
          <div class="row g-4">
            <div class="col-lg-4 d-flex">
              <div class="fw-info-card">
                <h3 class="h4 mb-3">E-Mail</h3>
                <p class="mb-3">Schnellster Weg für Anfragen, Termine und erste Eckdaten.</p>
                <p><a href="mailto:info@frawo-tech.de">info@frawo-tech.de</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="fw-info-card">
                <h3 class="h4 mb-3">Telefon</h3>
                <p class="mb-3">Wenn etwas schnell geklärt werden muss oder der Termin näher rückt.</p>
                <p><a href="tel:+4915155243164">+49 151 55 24 31 64</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="fw-info-card">
                <h3 class="h4 mb-3">Standort</h3>
                <p class="mb-3">FraWo arbeitet von Weißensberg aus und betreut Einsätze in der gesamten Bodenseeregion.</p>
                <p>Rothkreuz 14<br/>88138 Weißensberg</p>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </t>
</t>"""

# ─────────────────────────────────────────────────────────────────────────────
# CSS in custom_code_head (minimal global override)
# ─────────────────────────────────────────────────────────────────────────────
global_css = """<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap');
  body, #wrap { font-family: 'Poppins', sans-serif !important; }
</style>"""

# Write to Odoo
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3644], {'arch_db': home_arch}])
print("Homepage updated.")

models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3637], {'arch_db': contact_arch}])
print("Contact page updated.")

models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': global_css}])
print("Global CSS updated.")

print("All done!")
