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

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')


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
<section class="fw-hero" id="main-content" aria-label="Hauptbereich">
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
<section class="fw-services" id="services" aria-label="Unsere Leistungen">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Leistungen</div>
      <h2 class="fw-h2">Was wir machen</h2>
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
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/999/fussballdart.jpg');">
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
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/995/service-stage.jpg');">
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
        <div class="fw-service-card fw-service-card-bg" style="background-image: linear-gradient(rgba(10,10,10,0.88), rgba(10,10,10,0.88)), url('/web/image/996/sonderbau-holz.jpg');">
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
      <h2 class="fw-h2">Wir haben gearbeitet für</h2>
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
<section class="fw-projects" aria-label="Projekte">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Unsere Projekte</div>
      <h2 class="fw-h2">Was wir gebaut haben</h2>
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
            <p>Custom Holzkonstruktion</p>
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
<section class="fw-about" aria-label="Über uns">
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
<section class="fw-radio-cta" aria-label="Radio">
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
<section class="fw-cta" aria-label="Kontakt">
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

    </div>
</t>"""


def deploy_homepage():
    """Deploy new homepage to Odoo"""
    print("[*] Connecting to Odoo...")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        return 1

    print(f"[OK] Auth OK (UID:{uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Find homepage
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
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
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.ui.view', 'write',
        [[view_id], {'arch': HOMEPAGE_HTML}]
    )

    print("[OK] Homepage deployed!")
    print(f"\n[*] Live at: https://www.frawo-tech.de/")

    return 0


if __name__ == "__main__":
    sys.exit(deploy_homepage())
