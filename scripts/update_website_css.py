#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update FraWo Website CSS - Add Service Card Styles
==================================================
Adds missing CSS for service cards, referenzen, about sections
"""

import os
import sys
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')


# Additional CSS for Service Cards + Sections
ADDITIONAL_CSS = """
/* ===== SERVICE CARDS (kabaus-inspired) ===== */
.fw-services {
  padding: 80px 0;
  background: var(--fw-bg);
  border-top: 1px solid var(--fw-border);
}

.fw-h2 {
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--fw-text);
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

.fw-h3 {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--fw-text);
  margin-bottom: 1rem;
}

.fw-service-card {
  background: var(--fw-bg);
  border: 1px solid var(--fw-border);
  padding: 2.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s ease;
}

.fw-service-card:hover {
  border-color: var(--fw-text-dimmer);
}

.fw-service-icon {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.fw-service-desc {
  color: var(--fw-text-dim);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.fw-service-list {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
  flex-grow: 1;
}

.fw-service-list li {
  color: var(--fw-text-dim);
  font-size: 0.9rem;
  line-height: 1.7;
  padding: 0.35rem 0;
  padding-left: 1rem;
  position: relative;
}

.fw-service-list li:before {
  content: "—";
  position: absolute;
  left: 0;
  color: var(--fw-text-dimmer);
}

.fw-service-link {
  color: var(--fw-text-dim);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: color 0.2s ease;
  margin-top: auto;
}

.fw-service-link:hover {
  color: var(--fw-text);
}

/* ===== REFERENZEN ===== */
.fw-referenzen {
  padding: 80px 0;
  background: var(--fw-bg);
  border-top: 1px solid var(--fw-border);
}

.fw-ref-item {
  text-align: center;
  padding: 2rem 1rem;
}

.fw-ref-item strong {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--fw-text);
  display: block;
  margin-bottom: 0.5rem;
}

.fw-ref-item p {
  font-size: 0.8rem;
  color: var(--fw-text-dimmer);
  margin: 0;
}

/* ===== ABOUT SECTION ===== */
.fw-about {
  padding: 80px 0;
  background: var(--fw-bg);
  border-top: 1px solid var(--fw-border);
}

.fw-body {
  color: var(--fw-text-dim);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

/* ===== RADIO CTA ===== */
.fw-radio-cta {
  padding: 80px 0;
  background: var(--fw-bg);
  border-top: 1px solid var(--fw-border);
}

/* ===== CTA SECTION ===== */
.fw-cta {
  padding: 80px 0;
  background: var(--fw-bg);
  border-top: 1px solid var(--fw-border);
  border-bottom: 1px solid var(--fw-border);
}

/* ===== TRUST LINE ===== */
.fw-trust-line {
  font-size: 0.8rem;
  color: var(--fw-text-dimmer);
  margin-top: 2rem;
  line-height: 1.8;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .fw-services, .fw-referenzen, .fw-about, .fw-radio-cta, .fw-cta {
    padding: 50px 0;
  }

  .fw-service-card {
    padding: 2rem;
  }

  .fw-ref-item {
    padding: 1.5rem 1rem;
  }
}
"""


def update_css():
    """Add service card CSS to Odoo website"""
    print("[*] Connecting to Odoo...")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        return 1

    print(f"[OK] Auth OK (UID:{uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Find custom CSS asset
    assets = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.asset', 'search_read',
        [[['path', 'ilike', 'frawo']]],
        {'fields': ['id', 'name', 'path', 'directive']}
    )

    print(f"[*] Found {len(assets)} FraWo assets")

    # Read current CSS file
    css_path = Path(__file__).parent.parent / 'Codex' / 'website' / 'frawo_custom_css.css'

    if not css_path.exists():
        print(f"[FAIL] CSS file not found: {css_path}")
        return 1

    with open(css_path, 'r', encoding='utf-8') as f:
        current_css = f.read()

    # Check if service card CSS already exists
    if '.fw-service-card' in current_css:
        print("[INFO] Service card CSS already exists, skipping...")
        return 0

    # Append new CSS
    updated_css = current_css + "\n" + ADDITIONAL_CSS

    # Write back to file
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(updated_css)

    print(f"[OK] CSS updated: {css_path}")
    print("[INFO] You need to upload this CSS to Odoo manually or via asset manager")

    return 0


if __name__ == "__main__":
    sys.exit(update_css())
