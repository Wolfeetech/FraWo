#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy New FraWo Homepage - Veranstaltungstechnik
=================================================
Komplette Homepage mit:
- Korrektem Inhalt (Veranstaltungstechnik, keine IT)
- kabaus-Layout + NTS-Minimal + FraWo CI
- 4 Service Cards (Licht&Ton, Verleih, Stage, Sonderbau)
"""

import os
import sys
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_RPC_URL', os.getenv('ODOO_URL', 'http://10.4.0.22:8069'))
ODOO_DB = os.getenv('ODOO_RPC_DB', os.getenv('ODOO_DB', 'FraWo_GbR'))
ODOO_USER = os.getenv('ODOO_RPC_USER', os.getenv('ODOO_USER'))
ODOO_SECRET = os.getenv('ODOO_RPC_API_KEY')

if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_SECRET]):
    raise SystemExit("Missing ODOO_RPC_URL/ODOO_RPC_DB/ODOO_RPC_USER/ODOO_RPC_API_KEY")


# New Homepage HTML (without <odoo> wrapper - that's added by Odoo)
HOMEPAGE_HTML = """<t t-call="website.layout">
    <div id="wrap" class="oe_structure">

<!-- Skip to Content (Accessibility) -->
<a href="#main-content" class="skip-to-content">Zum Hauptinhalt springen</a>

<!-- Schema.org LocalBusiness Markup -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "FraWo GbR",
  "image": "https://www.frawo-tech.de/web/image/993/hero-bodensee.jpg",
  "url": "https://www.frawo-tech.de",
  "telephone": "+49-8389-9209870",
  "email": "info@frawo-tech.de",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Rothkreuz 14",
    "addressLocality": "Weissensberg",
    "postalCode": "88138",
    "addressCountry": "DE"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "47.5833",
    "longitude": "9.7833"
  },
  "description": "Veranstaltungstechnik Bodensee. PA-Systeme, Licht, Ton.",
  "areaServed": "Bodensee",
  "priceRange": "€€",
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Services",
    "itemListElement": [
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Licht &amp; Ton"}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Verleih"}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Stage Service"}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Sonderbauten"}}
    ]
  }
}
</script>

<!-- Hero Section -->
<section class="fw-hero" id="main-content" aria-label="Hauptbereich" style="padding: 80px 0 60px !important;">
  <div class="container">
    <div class="row align-items-center g-5">
      <div class="col-lg-6">
        <div class="fw-eyebrow">Bodensee</div>
        <h1 class="fw-h1">Licht &amp; Ton<br/>für dein Event</h1>
        <p class="fw-lead">
          Vereine. Feiern. Festivals.<br/>
          <strong>Bodensee-Region.</strong>
        </p>
        <div class="d-flex flex-wrap gap-3">
          <a class="fw-btn-primary btn" href="/contactus" aria-label="Jetzt Veranstaltungstechnik anfragen">Jetzt anfragen</a>
          <a class="fw-btn-ghost btn" href="#services" aria-label="Zu unseren Leistungen springen">Unsere Leistungen</a>
        </div>
        <p class="fw-trust-line">
          ✓ IHK-Fachkraft Veranstaltungstechnik
          ✓ Zimmermanngeselle
          ✓ Bodensee-Region
        </p>
      </div>
      <div class="col-lg-6">
        <div class="fw-img-wrapper">
          <picture>
            <source srcset="/web/image/1003/hero-bodensee.webp" type="image/webp"/>
            <img src="/web/image/993/hero-bodensee.jpg" alt="FraWo Veranstaltungstechnik - PA-Anlage und Lichttechnik am Bodensee Beach Event mit Bühnenaufbau"/>
          </picture>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Services Grid -->
<section class="fw-services" id="services" aria-label="Unsere Leistungen" style="padding: 40px 0 !important;">
  <div class="container">
    <div class="fw-section-header" style="margin-bottom: 25px !important;">
      <div class="fw-eyebrow">Leistungen</div>
      <h2 class="fw-h2">Unsere Expertise</h2>
    </div>

    <div class="row g-4">

      <!-- Service 1: Licht &amp; Ton -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/1000/mikrofon-ton.jpg');">
          <h3 class="fw-h3">Licht &amp; Ton</h3>
          <p class="fw-service-desc">
            PA-Systeme. Lichttechnik. Vor-Ort-Betreuung.
          </p>
          <ul class="fw-service-list">
            <li>PA-Systeme</li>
            <li>Moving Heads</li>
            <li>Technische Betreuung</li>
            <li>Subunternehmer</li>
          </ul>
          <a href="/contactus" class="fw-service-link" aria-label="Licht und Ton Service anfragen">Anfragen →</a>
        </div>
      </div>

      <!-- Service 2: Verleih -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/999/fussballdart.jpg')">
          <h3 class="fw-h3">Verleih</h3>
          <p class="fw-service-desc">
            Equipment-Verleih. Tageweise oder Wochenende.
          </p>
          <ul class="fw-service-list">
            <li>Fußballdart (3×5m)</li>
            <li>PA-Systeme</li>
            <li>Moving Heads</li>
            <li>Tages-/Wochenmiete</li>
          </ul>
          <a href="/contactus" class="fw-service-link" aria-label="Equipment-Verleih anfragen">Zum Verleih →</a>
        </div>
      </div>

      <!-- Service 3: Stage Service -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/995/service-stage.jpg')">
          <h3 class="fw-h3">Stage Service</h3>
          <p class="fw-service-desc">
            Aufbau. Betreuung. Backline.
          </p>
          <ul class="fw-service-list">
            <li>Crew</li>
            <li>Event-Betreuung</li>
            <li>Backline</li>
            <li>Open Air</li>
          </ul>
          <a href="/contactus" class="fw-service-link" aria-label="Stage Service anfragen">Anfragen →</a>
        </div>
      </div>

      <!-- Service 4: Sonderbauten -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/996/sonderbau-holz.jpg')">
          <h3 class="fw-h3">Sonderbauten</h3>
          <p class="fw-service-desc">
            Holzbau trifft Veranstaltungstechnik.
          </p>
          <ul class="fw-service-list">
            <li>Custom Stages</li>
            <li>Holzkonstruktionen</li>
            <li>Zimmermann + Technik</li>
            <li>Individuelle Projekte</li>
          </ul>
          <a href="/contactus" class="fw-service-link" aria-label="Sonderbau-Projekt anfragen">Projekt anfragen →</a>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Referenzen -->
<section class="fw-referenzen" aria-label="Referenzen">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Referenzen</div>
      <h2 class="fw-h2">Unsere Kunden</h2>
    </div>

    <div class="row g-4">
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>L.H. Veranstaltungstechnik</strong>
          <p>Subunternehmer</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>Baas TV</strong>
          <p>Technische Unterstützung</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>Club Vaudeville e.V.</strong>
          <p>Veranstaltungstechnik</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>Inselhalle Lindau</strong>
          <p>Event Support</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>KuMoP e.V.</strong>
          <p>Bühnenaufbau &amp; Technik</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>LaGo e.V.</strong>
          <p>Veranstaltungsunterstützung</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>Spring Spring Hooray</strong>
          <p>Wasserburg (Open Air)</p>
        </div>
      </div>
      <div class="col-lg-3 col-6">
        <div class="fw-ref-item">
          <strong>Leichte Liebe</strong>
          <p>Bregenz (Open Air)</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Projekte -->
<section class="fw-projects" aria-label="Projekte" style="padding: 40px 0 !important;">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Portfolio</div>
      <h2 class="fw-h2">Ausgewählte Projekte</h2>
    </div>

    <div class="row g-1">
      <div class="col-lg-4">
        <div class="fw-project-card">
          <picture>
            <source srcset="/web/image/1006/rave-on-sup.webp" type="image/webp"/>
            <img loading="lazy" src="/web/image/997/rave-on-sup.jpg" alt="Rave on SUP Bodensee - Schwimmende PA-Anlage auf Fischerboot für Open-Air Event"/>
          </picture>
          <div class="fw-project-overlay">
            <h3 class="fw-h3">Rave on SUP</h3>
            <p>Lautsprecher auf Fischerboot</p>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="fw-project-card">
          <picture>
            <source srcset="/web/image/1005/sonderbau-holz.webp" type="image/webp"/>
            <img loading="lazy" src="/web/image/996/sonderbau-holz.jpg" alt="Sonderbau Holzkonstruktion - Zimmermann Franz Bienert Holzbühne mit Dekoration"/>
          </picture>
          <div class="fw-project-overlay">
            <h3 class="fw-h3">Sonderbau</h3>
            <p>Open Air Bühne (Jun. 2024)</p>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="fw-project-card">
          <picture>
            <source srcset="/web/image/1004/service-stage.webp" type="image/webp"/>
            <img loading="lazy" src="/web/image/995/service-stage.jpg" alt="Live Stage FOH - Wolfgang Prinz am Front of House Mischpult bei Konzert"/>
          </picture>
          <div class="fw-project-overlay">
            <h3 class="fw-h3">Live Stage</h3>
            <p>Backstage Tech-Betreuung</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Über Uns -->
<section class="fw-about" aria-label="Über uns" style="padding: 40px 0 !important;">
  <div class="container">
    <div class="row align-items-center g-5">
      <div class="col-lg-6">
        <div class="fw-eyebrow">Über FraWo</div>
        <h2 class="fw-h2">Wolf + Franz</h2>
        <p class="fw-lead">
          <strong>Wolfgang Prinz</strong><br/>IHK-Fachkraft Veranstaltungstechnik
        </p>
        <p class="fw-lead">
          <strong>Franz Bienert</strong><br/>Zimmermanngeselle
        </p>
        <p class="fw-body">
          Bodensee. Lokal. Zuverlässig.
        </p>
        <a href="/contactus" class="fw-btn-primary btn mt-3" aria-label="Kontakt zu FraWo Veranstaltungstechnik aufnehmen">Kontakt aufnehmen</a>
      </div>
      <div class="col-lg-6">
        <div class="row g-3">
          <div class="col-6">
            <div class="fw-img-wrapper">
              <picture>
                <source srcset="/web/image/1004/service-stage.webp" type="image/webp"/>
                <img loading="lazy" src="/web/image/995/service-stage.jpg" alt="Wolfgang Prinz am Front of House Mischpult - FraWo Stage Service"/>
              </picture>
            </div>
          </div>
          <div class="col-6">
            <div class="fw-img-wrapper">
              <picture>
                <source srcset="/web/image/1007/buehne-traverse.webp" type="image/webp"/>
                <img loading="lazy" src="/web/image/998/buehne-traverse.jpg" alt="Franz Bienert bei Bühnenaufbau - FraWo Sonderbauten und Holzkonstruktion"/>
              </picture>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Radio -->
<section class="fw-radio-cta" aria-label="Radio" style="padding: 40px 0 !important;">
  <div class="container">
    <div class="row">
      <div class="col-lg-8 offset-lg-2 text-center">
        <div class="fw-eyebrow">FraWo Funk</div>
        <h2 class="fw-h2">Community Radio</h2>
        <p class="fw-lead">
          Online-Radio. Community. Musikförderung.
        </p>
        <a href="https://funk.frawo-tech.de" class="fw-btn-ghost btn mt-3">Zu FraWo Funk →</a>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="fw-cta" aria-label="Kontakt" style="padding: 40px 0 !important;">
  <div class="container">
    <div class="row">
      <div class="col-lg-8 offset-lg-2 text-center">
        <h2 class="fw-h2">Event geplant?</h2>
        <p class="fw-lead">
          Kostenlose Beratung. Bodensee-Region.
        </p>
        <a href="/contactus" class="fw-btn-primary btn" aria-label="Veranstaltungstechnik-Anfrage senden">Anfrage senden</a>
      </div>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="fw-footer" style="background: #0a0a0a; border-top: 1px solid #1a1a1a; padding: 3rem 0 2rem 0; color: #888;">
  <div class="container">
    <div class="row g-4">
      <div class="col-md-4">
        <h5 style="color: #e8e8e8; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">FraWo GbR</h5>
        <p style="font-size: 0.875rem; line-height: 1.6; color: #707070;">
          Veranstaltungstechnik &amp; Sonderbauten<br/>
          Bodensee-Region
        </p>
      </div>
      <div class="col-md-4">
        <h5 style="color: #e8e8e8; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">Rechtliches</h5>
        <ul style="list-style: none; padding: 0; margin: 0;">
          <li style="margin-bottom: 0.5rem;"><a href="/impressum" style="color: #707070; text-decoration: none; font-size: 0.875rem; transition: color 0.2s;">Impressum</a></li>
          <li style="margin-bottom: 0.5rem;"><a href="/datenschutz" style="color: #707070; text-decoration: none; font-size: 0.875rem; transition: color 0.2s;">Datenschutz</a></li>
        </ul>
      </div>
      <div class="col-md-4">
        <h5 style="color: #e8e8e8; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">Kontakt</h5>
        <p style="font-size: 0.875rem; line-height: 1.6; color: #707070;">
          <a href="mailto:info@frawo-tech.de" style="color: #707070; text-decoration: none;">info@frawo-tech.de</a>
        </p>
      </div>
    </div>
    <div class="row" style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #1a1a1a;">
      <div class="col-12 text-center">
        <p style="font-size: 0.8rem; color: #555; margin: 0;">
          © 2026 FraWo GbR. State-of-the-Art Media &amp; Event.
        </p>
      </div>
    </div>
  </div>
</footer>

<!-- FINAL OVERRIDE - Must be last to override Odoo's compiled CSS -->
<style>
/* MAXIMUM SPECIFICITY - Override Bootstrap and Odoo Frontend CSS */
.fw-services .row.g-4,
section.fw-services .row.g-4 {
  display: grid !important;
  grid-template-columns: repeat(2, 1fr) !important;
  gap: 1px !important;
  background: #1a1a1a !important;
  border: 1px solid #1a1a1a !important;
  margin: 0 !important;
}

.fw-services .col-lg-6,
section.fw-services .col-lg-6 {
  padding: 0 !important;
  max-width: none !important;
  flex: none !important;
}

.fw-services .fw-service-card,
section.fw-services .fw-service-card {
  padding: 0.75rem 1rem !important;
  min-height: 200px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 0.3rem !important;
}

.fw-service-card .fw-h3,
.fw-service-card h3.fw-h3 {
  margin: 0 0 0.3rem 0 !important;
  font-size: 0.75rem !important;
}

.fw-service-card .fw-service-desc,
.fw-service-card p.fw-service-desc {
  margin: 0 0 0.3rem 0 !important;
  font-size: 0.85rem !important;
}

.fw-service-card .fw-service-list,
.fw-service-card ul.fw-service-list {
  margin: 0 0 0.5rem 0 !important;
  padding: 0 !important;
  list-style: none !important;
}

.fw-service-card .fw-service-list li,
.fw-service-card ul li {
  padding: 0.08rem 0 0.08rem 1rem !important;
  margin: 0 !important;
  font-size: 0.8rem !important;
  line-height: 1.3 !important;
}

/* Referenzen ultra-compact */
.fw-referenzen .row.g-4,
section.fw-referenzen .row.g-4 {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 1px !important;
  background: #1a1a1a !important;
  border: 1px solid #1a1a1a !important;
  margin: 0 !important;
}

.fw-referenzen .col-lg-3,
.fw-referenzen .col-6,
section.fw-referenzen .col-lg-3,
section.fw-referenzen .col-6 {
  padding: 0 !important;
  max-width: none !important;
  flex: none !important;
}

.fw-referenzen .fw-ref-item,
section.fw-referenzen .fw-ref-item {
  padding: 0.75rem 0.5rem !important;
  min-height: 90px !important;
  background: #0a0a0a !important;
}

.fw-ref-item strong {
  font-size: 0.7rem !important;
  margin: 0 !important;
}

.fw-ref-item p {
  font-size: 0.65rem !important;
  margin: 0 !important;
}

/* Section spacing */
section.fw-services,
section.fw-referenzen,
section.fw-projects,
section.fw-about,
section.fw-radio-cta,
section.fw-cta {
  padding: 40px 0 !important;
}

section.fw-hero {
  padding: 80px 0 60px !important;
}

.fw-section-header {
  margin-bottom: 25px !important;
}

/* Mobile override */
@media (max-width: 991px) {
  .fw-services .row.g-4 {
    grid-template-columns: 1fr !important;
  }
  .fw-referenzen .row.g-4 {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

/* Added fixes for premium design */
.container {
  margin-left: auto !important;
  margin-right: auto !important;
}
a.fw-btn-primary.btn {
  background: #9d4edd !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 4px !important;
  padding: 14px 28px !important;
  display: inline-block !important;
  text-decoration: none !important;
  font-weight: 600 !important;
}
a.fw-btn-ghost.btn {
  background: transparent !important;
  border: 2px solid #9d4edd !important;
  border-radius: 4px !important;
  padding: 14px 28px !important;
  color: #ffffff !important;
  display: inline-block !important;
  text-decoration: none !important;
  font-weight: 600 !important;
}
.fw-img-wrapper {
  position: relative !important;
}
.fw-img-wrapper::after {
  content: '' !important;
  position: absolute !important;
  bottom: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 40% !important;
  background: linear-gradient(to top, #0a0a0a, transparent) !important;
  pointer-events: none !important;
}
.fw-about .fw-img-wrapper {
  max-height: 400px !important;
}
</style>

    </div>
</t>"""


def deploy_homepage():
    """Deploy new homepage to Odoo"""
    print("[*] Connecting to Odoo...")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_SECRET, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        return 1

    print(f"[OK] Auth OK (UID:{uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Find homepage
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_SECRET,
        'website.page', 'search_read',
        [[['url', '=', '/']]],
        {'fields': ['id', 'name', 'view_id']}
    )

    if not pages:
        print("[FAIL] Homepage not found!")
        return 1

    homepage = pages[0]
    view_id = homepage['view_id'][0]

    print(f"[*] Updating Homepage (Page ID:{homepage['id']}, View ID:{view_id})...")

    # Update view arch
    models.execute_kw(
        ODOO_DB, uid, ODOO_SECRET,
        'ir.ui.view', 'write',
        [[view_id], {'arch': HOMEPAGE_HTML}]
    )

    print("[OK] Homepage deployed!")
    print(f"\n[*] Live at: https://www.frawo-tech.de/")

    return 0


if __name__ == "__main__":
    sys.exit(deploy_homepage())
