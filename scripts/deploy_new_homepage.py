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


# New Homepage HTML
HOMEPAGE_HTML = """<odoo>
    <template id="website.homepage" name="Homepage">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">

<!-- Hero Section -->
<section class="fw-hero">
  <div class="container">
    <div class="row align-items-center g-5">
      <div class="col-lg-6">
        <div class="fw-eyebrow">Veranstaltungstechnik Bodensee</div>
        <h1 class="fw-h1">Licht &amp; Ton<br/>für kleine Events</h1>
        <p class="fw-lead">
          Veranstaltungstechniker + Zimmermann.<br/>
          Vom Bodensee. Für Events, Vereine, private Feiern.<br/>
          <strong>Ehrlich. Pragmatisch. Lokal.</strong>
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
          <img src="/web/image/932/hero-bodensee.jpg" alt="Veranstaltungstechnik am Bodensee" loading="lazy"/>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Services Grid (4 Cards - kabaus-Stil) -->
<section class="fw-services" id="services">
  <div class="container">
    <div class="row mb-5">
      <div class="col-lg-8 offset-lg-2 text-center">
        <div class="fw-eyebrow">Unsere Leistungen</div>
        <h2 class="fw-h2">Was wir anbieten</h2>
        <p class="fw-lead">Veranstaltungstechnik für kleine bis mittlere Events. Ehrlich: Wir haben kaum professionelle Ausrüstung – aber für kleine Events reicht's!</p>
      </div>
    </div>

    <div class="row g-4">

      <!-- Service 1: Licht &amp; Ton -->
      <div class="col-lg-6">
        <div class="fw-service-card">
          <div class="fw-service-icon">🎭</div>
          <h3 class="fw-h3">Licht &amp; Ton</h3>
          <p class="fw-service-desc">
            PA-Sets, Moving Heads, technische Betreuung für kleine Events.
            Ideal für Vereine, private Feiern, Community-Events.
          </p>
          <ul class="fw-service-list">
            <li>Mehrere kleine PA-Systeme</li>
            <li>Moving Heads (einige vorhanden)</li>
            <li>Technische Betreuung vor Ort</li>
            <li>B2B / Subunternehmer-Service</li>
          </ul>
          <a href="/contactus" class="fw-service-link">Anfragen →</a>
        </div>
      </div>

      <!-- Service 2: Verleih -->
      <div class="col-lg-6">
        <div class="fw-service-card">
          <div class="fw-service-icon">⚽</div>
          <h3 class="fw-h3">Equipment Verleih</h3>
          <p class="fw-service-desc">
            Fußballdart (3×5m), PA-Sets, Lichttechnik.
            Perfekt für Firmenevents, Stadtfeste, Vereinsfeiern.
          </p>
          <ul class="fw-service-list">
            <li>Aufblasbares Fußballdart (3m × 5m × 3m)</li>
            <li>PA-Sets (kleine bis mittlere Größe)</li>
            <li>Moving Heads für Club-Atmosphäre</li>
            <li>Ideal für private Vermieter &amp; Vereine</li>
          </ul>
          <a href="/contactus" class="fw-service-link">Zum Verleih →</a>
        </div>
      </div>

      <!-- Service 3: Stage Service -->
      <div class="col-lg-6">
        <div class="fw-service-card">
          <div class="fw-service-icon">🎪</div>
          <h3 class="fw-h3">Open Air / Stage Service</h3>
          <p class="fw-service-desc">
            Aufbau, technische Betreuung, Backline.
            Als Subunternehmer oder direkt.
          </p>
          <ul class="fw-service-list">
            <li>Aufbauhelfer (Crew)</li>
            <li>Technische Betreuung während Event</li>
            <li>Backline-Management</li>
            <li>Licht, Ton, Medien (je nach Setup)</li>
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
            Custom Stages, kreative Lösungen.
            Zimmermann + Veranstaltungstechnik = Einzigartige Kombi!
          </p>
          <ul class="fw-service-list">
            <li>Custom Stage Builds (KuMoP e.V.)</li>
            <li>Kreative Installationen (Rave on SUP)</li>
            <li>Zimmermann-Know-how trifft Event-Technik</li>
            <li>Individuelle Projekte möglich</li>
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
    <div class="row mb-5">
      <div class="col-lg-8 offset-lg-2 text-center">
        <div class="fw-eyebrow">Unsere Referenzen</div>
        <h2 class="fw-h2">Wir haben gearbeitet für</h2>
      </div>
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

<!-- Über Uns -->
<section class="fw-about">
  <div class="container">
    <div class="row align-items-center g-5">
      <div class="col-lg-6">
        <div class="fw-eyebrow">Über FraWo</div>
        <h2 class="fw-h2">Veranstaltungstechniker<br/>+ Zimmermann</h2>
        <p class="fw-lead">
          <strong>Wolfgang Prinz</strong> (Veranstaltungstechnik) und <strong>Franz Bienert</strong> (Zimmermann + Veranstaltungstechnik).
        </p>
        <p class="fw-body">
          Wir sind <strong>KEINE IT-Spezialisten</strong>.<br/>
          Wir sind <strong>KEINE eingetragenen Elektriker</strong>.<br/>
          Aber: Wir sind zuverlässige Macher mit pragmatischen Lösungen.
        </p>
        <p class="fw-body">
          Vom Bodensee. Für Events. Ehrlich. Lokal.
        </p>
        <a href="/contactus" class="fw-btn-primary btn mt-3">Kontakt aufnehmen</a>
      </div>
      <div class="col-lg-6">
        <div class="fw-img-wrapper">
          <img src="/web/image/933/team-placeholder.jpg" alt="FraWo Team" loading="lazy"/>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Radio (Gadget) -->
<section class="fw-radio-cta">
  <div class="container">
    <div class="row">
      <div class="col-lg-8 offset-lg-2 text-center">
        <div class="fw-eyebrow">FraWo Funk</div>
        <h2 class="fw-h2">Community Radio</h2>
        <p class="fw-lead">
          Radio als <strong>Gadget</strong> (nicht Kerngeschäft!). Community-Aufbau, Musikförderung.
        </p>
        <p class="fw-body">
          Du bist Musiker oder DJ? Bewirb dich gern mit deiner Musik!
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
        <h2 class="fw-h2">Bereit für dein Event?</h2>
        <p class="fw-lead">
          Lass uns über dein Projekt sprechen. Kostenlose Beratung.
        </p>
        <a href="/contactus" class="fw-btn-primary btn">Jetzt Anfrage senden</a>
      </div>
    </div>
  </div>
</section>

            </div>
        </t>
    </template>
</odoo>"""


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
