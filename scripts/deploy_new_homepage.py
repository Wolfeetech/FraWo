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

<!-- Hero Section -->
<section class="fw-hero">
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
          <a class="fw-btn-primary btn" href="/contactus">Jetzt anfragen</a>
          <a class="fw-btn-ghost btn" href="#services">Unsere Leistungen</a>
        </div>
        <p class="fw-trust-line">
          ✓ IHK-Fachkraft Veranstaltungstechnik
          ✓ Zimmermanngeselle
          ✓ Bodensee-Region
        </p>
      </div>
      <div class="col-lg-6">
        <div class="fw-img-wrapper">
          <img src="/web/image/993/hero-bodensee.jpg" alt="Beach Event Bodensee - FraWo Veranstaltungstechnik"/>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Services Grid -->
<section class="fw-services" id="services">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Leistungen</div>
      <h2 class="fw-h2">Was wir machen</h2>
    </div>

    <div class="row g-4">

      <!-- Service 1: Licht &amp; Ton -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-img" style="background-image: linear-gradient(rgba(10,10,10,0.85), rgba(10,10,10,0.85)), url('/web/image/1000/mikrofon-ton.jpg'); background-size: cover; background-position: center;">
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
          <a href="/contactus" class="fw-service-link">Anfragen →</a>
        </div>
      </div>

      <!-- Service 2: Verleih -->
      <div class="col-lg-6">
        <div class="fw-service-card fw-service-card-img" style="background-image: linear-gradient(rgba(10,10,10,0.85), rgba(10,10,10,0.85)), url('/web/image/999/fussballdart.jpg'); background-size: cover; background-position: center;">
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
          <a href="/contactus" class="fw-service-link">Zum Verleih →</a>
        </div>
      </div>

      <!-- Service 3: Stage Service -->
      <div class="col-lg-6">
        <div class="fw-service-card">
          <div class="fw-service-icon">🎪</div>
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
          <a href="/contactus" class="fw-service-link">Anfragen →</a>
        </div>
      </div>

      <!-- Service 4: Sonderbauten -->
      <div class="col-lg-6">
        <div class="fw-service-card">
          <div class="fw-service-icon">🔨</div>
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
          <a href="/contactus" class="fw-service-link">Projekt anfragen →</a>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Referenzen -->
<section class="fw-referenzen">
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
<section class="fw-projects">
  <div class="container">
    <div class="fw-section-header">
      <div class="fw-eyebrow">Unsere Projekte</div>
      <h2 class="fw-h2">Was wir gebaut haben</h2>
    </div>

    <div class="row g-1">
      <div class="col-lg-4">
        <div class="fw-project-card">
          <img src="/web/image/997/rave-on-sup.jpg" alt="Rave on SUP"/>
          <div class="fw-project-overlay">
            <h3 class="fw-h3">Rave on SUP</h3>
            <p>Lautsprecher auf Fischerboot</p>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="fw-project-card">
          <img src="/web/image/996/sonderbau-holz.jpg" alt="Holzkonstruktion"/>
          <div class="fw-project-overlay">
            <h3 class="fw-h3">Sonderbau</h3>
            <p>Custom Holzkonstruktion</p>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="fw-project-card">
          <img src="/web/image/995/service-stage.jpg" alt="Live Stage"/>
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
<section class="fw-about">
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
        <a href="/contactus" class="fw-btn-primary btn mt-3">Kontakt aufnehmen</a>
      </div>
      <div class="col-lg-6">
        <div class="fw-img-wrapper">
          <img src="/web/image/998/buehne-traverse.jpg" alt="FraWo Bühnenaufbau"/>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Radio -->
<section class="fw-radio-cta">
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
<section class="fw-cta">
  <div class="container">
    <div class="row">
      <div class="col-lg-8 offset-lg-2 text-center">
        <h2 class="fw-h2">Event geplant?</h2>
        <p class="fw-lead">
          Kostenlose Beratung. Bodensee-Region.
        </p>
        <a href="/contactus" class="fw-btn-primary btn">Anfrage senden</a>
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
