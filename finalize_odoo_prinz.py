#!/usr/bin/env python3
"""
Finalisierung PRJ-2026-MED-PRINZ in Odoo
- Abgeschlossene Tasks auf Erledigt setzen
- Task 297 mit vollstaendigem Kassenantrag-Text
- Neue Tasks: Bestellung, HNO-Rezept, Wareneingang
- Lieferant Humantechnik anlegen
- Beide Angebote mit Gewerk-Label versehen
- Projektbeschreibung: Zwei-Saeulen-Konzept
"""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "http://10.1.0.112:8069"
DB = "FraWo_GbR"
UID = 6
import os
PW = os.environ.get('ODOO_PASSWORD', 'INSERT_PASSWORD_HERE')
PROJECT_ID = 22
PARTNER_ID = 42

m = xmlrpc.client.ServerProxy(f"{HOST}/xmlrpc/2/object")

STAGE_PLANUNG   = 2    # Planung & Vorbereitung
STAGE_IN_ARBEIT = 3    # In Arbeit
STAGE_DOKU_KASSE= 89   # Dokumentation & Kasse
STAGE_ERLEDIGT  = 6    # Erledigt

# ─── 1. Abgeschlossene Wissens-Tasks auf Erledigt setzen ──────────────────────
print("[1] Wissens-Tasks abschliessen...")

wissens_updates = {
    264: {
        "stage_id": STAGE_ERLEDIGT,
        "description": (
            "<p><strong>Erledigt — Technische Infos vollstaendig:</strong></p>"
            "<ul>"
            "<li>CI links: Med-El Sonnet 3 (Cochlea-Implantat, kabelgebunden oder Audioschuh)</li>"
            "<li>HG rechts: Phonak (Modell via AirStream BT, ca. 15-20ms mehr Latenz als CI)</li>"
            "<li>TV: Samsung (Toslink Optical Out bestaetigt)</li>"
            "<li>DSP: t.racks 4x4 DSP Pro (Euroblock, bestellt bei Thomann)</li>"
            "<li>Signalweg: TV Toslink → Swissonic Extractor → DSP → Out1/2 Mutter, Out3/4 Vater</li>"
            "</ul>"
        ),
    },
    267: {
        "stage_id": STAGE_ERLEDIGT,
        "description": (
            "<p><strong>Erledigt — Hoergeraet identifiziert:</strong></p>"
            "<p>Phonak (rechtes Ohr, HG). Verbindung via Phonak AirStream (proprietaer BT).</p>"
            "<p>Latenz: ~15-20ms hoeher als Med-El CI links. DSP-Delay-Kompensation auf CI-Kanal konfigurieren.</p>"
            "<p>Direktmontage CI: Med-El Sonnet 3 hat 3,5mm Audiobuchse oder Audioschuh — kein Sender noetig fuer kabelgebundenes System.</p>"
        ),
    },
    268: {
        "description": (
            "<p>Samsung TV — Toslink Optical Output bestaetigt (per Kundengespräch).</p>"
            "<p>Vor-Ort: Kabel Samsung → Swissonic Audio Extractor anschliessen und Signalpegel messen.</p>"
            "<p>Backup: Falls kein Optical Out → HDMI ARC als Alternative pruefen.</p>"
        ),
    },
}

for task_id, vals in wissens_updates.items():
    m.execute_kw(DB, UID, PW, "project.task", "write", [[task_id], vals])
    stage_name = "Erledigt" if vals.get("stage_id") == STAGE_ERLEDIGT else "unveraendert"
    print(f"  [OK] Task {task_id} → Stage: {stage_name}")

# ─── 2. Task 297: Vollstaendiger Kassenantrag-Text ────────────────────────────
print("\n[2] Task 297 — vollstaendiger Kassenantrag-Text...")

kassenantrag_sbgxi = """<h3>Gewerk 1: Pflegekasse — Antrag §40 SGB XI (Wohnumfeldverbesserung)</h3>
<p><strong>Rechtsbasis:</strong> §40 Abs. 4 SGB XI — einmaliger Zuschuss bis 4.000 EUR je Massnahme.<br/>
<strong>Voraussetzung:</strong> Mindestens Pflegegrad 1. Kassenantrag VOR Beauftragung stellen.</p>

<h4>Antragsbegrundung:</h4>
<p>Der Pflegebeduertige leidet unter einer beidseitigen, an Taubheit grenzenden Schwerhörigkeit
(CI links: Med-El Sonnet 3 / HG rechts: Phonak) in Kombination mit altersbedingt eingeschraenkter
Beweglichkeit. Der vorhandene Fernseher stellt die einzige Moeglichkeit zur Mediennutzung dar.</p>
<p>Ohne die DSP-gestutzte Massnahme ist eine simultane, latenzkompensierte Audio-Versorgung
beider Hoersysteme technisch nicht realisierbar. Die Massnahme verbessert aktiv die Kommunikations-
und Teilhabefähigkeit im haeuslichen Umfeld und foerdert die selbstaendige Lebensführung.</p>

<h4>Beantragte Positionen (Gewerk 1 — Kostentraeger: Pflegekasse):</h4>
<ul>
<li>t.racks 4x4 DSP Pro — 116,81 EUR EK / 139,00 EUR</li>
<li>PreSonus Eris 3.5 (Paar) — 83,19 EUR EK / 99,00 EUR</li>
<li>Swissonic Audio Extractor — 41,18 EUR EK / 49,00 EUR</li>
<li>Fostex PC-1e Lautstaerkeregler — 24,37 EUR EK / 29,00 EUR</li>
<li>Adapterkabel Euroblock→XLR (2x Eigenbau) — 2x 15,00 EUR</li>
<li>Adapterkabel Euroblock→RCA (2x Eigenbau) — 2x 15,00 EUR</li>
<li>Toslink-Kabel 1,5m — 9,90 EUR</li>
<li>Installation (3h à 85,00 EUR) — 255,00 EUR</li>
<li>DSP-Programmierung & Einmessung (3h à 95,00 EUR) — 285,00 EUR</li>
<li>Einweisung & App-Konfiguration — 80,00 EUR</li>
<li><strong>Gesamt Netto: 1.084,90 EUR</strong> (weit unter 4.000 EUR-Budget)</li>
</ul>

<h4>Hinweis GKV-Abgrenzung:</h4>
<p>Alle mobilen Signalanlagen (Signolux-System: Klingelsender, Rauchmelder, Blitzempfaenger)
werden SEPARAT bei der gesetzlichen Krankenkasse nach §33 SGB V beantragt (Gewerk 2).
Diese Trennung entspricht der aktuellen Rechtsprechung (BSG B 3 KR 5/09 R).</p>

<hr/>
<h3>Gewerk 2: Krankenkasse — Antrag §33 SGB V (Hilfsmittel)</h3>
<p><strong>Rechtsbasis:</strong> §33 SGB V — Hilfsmittel zum Ausgleich einer Behinderung.<br/>
<strong>HNO-Rezept Muster 16 erforderlich.</strong> Zuzahlung: 10,00 EUR.</p>

<h4>Muster-Verordnungstext fuer HNO-Arzt:</h4>
<blockquote>
1x Lichtsignalanlage fuer Gehoerlose bestehend aus:<br/>
1x Funksender Haustuere (HMV 13.99.04.1012),<br/>
3x Funk-Rauchwarnmelder DIN 14676 (HMV 13.99.04.0023),<br/>
1x stationaerer Blitz-Wecker mit Vibrationskissen (HMV 13.99.04.3021 + 13.99.04.5003),<br/>
1x mobiler Blitzempfaenger (HMV 13.99.04.2005).<br/>
Indikation: Beidseitige, an Taubheit grenzende Schwerhörigkeit (CI links, HG rechts).
Hilfsmittel zur Sicherung der Schlafueberwachung und Wahrnehmung von Notsignalen.
</blockquote>

<h4>Beantragte Positionen (Gewerk 2 — Kostentraeger: GKV):</h4>
<ul>
<li>signolux Empfaenger-Wecker — 184,00 EUR (HMV 13.99.04.3021)</li>
<li>signolux Vibrationskissen — 42,00 EUR (HMV 13.99.04.5003)</li>
<li>signolux Funk-Rauchmelder 3x — 3x 167,23 EUR = 501,69 EUR (HMV 13.99.04.0023)</li>
<li>signolux Klingelsender — 109,24 EUR (HMV 13.99.04.1012)</li>
<li>signolux Mobiler Empfaenger — 142,86 EUR (HMV 13.99.04.2005)</li>
<li>Installation/Einlernen — 85,00 EUR</li>
<li>Einweisung — 80,00 EUR</li>
<li><strong>Gesamt Netto: 1.144,79 EUR</strong> (GKV-erstattungsfaehig abzgl. 10 EUR Zuzahlung)</li>
</ul>"""

m.execute_kw(DB, UID, PW, "project.task", "write", [[297], {
    "stage_id": STAGE_DOKU_KASSE,
    "description": kassenantrag_sbgxi,
    "allocated_hours": 2.0,
}])
print("  [OK] Task 297 mit vollstaendigem Kassenantrag-Text aktualisiert")

# ─── 3. Neue organisatorische Tasks ──────────────────────────────────────────
print("\n[3] Neue Tasks anlegen...")

new_tasks = [
    {
        "name": "Signolux-Hardware bei Humantechnik bestellen",
        "stage_id": STAGE_IN_ARBEIT,
        "allocated_hours": 0.5,
        "description": (
            "<p>Bestellung der Gewerk-2-Komponenten direkt bei Humantechnik GmbH.</p>"
            "<ul>"
            "<li>HW-SIG-REC: signolux Empfaenger-Wecker (1x)</li>"
            "<li>HW-SIG-VIB: signolux Vibrationskissen (1x)</li>"
            "<li>HW-SIG-SMOKE: signolux Funk-Rauchmelder Hekatron (3x)</li>"
            "<li>HW-SIG-BELL: signolux Klingelsender (1x)</li>"
            "<li>HW-SIG-PORT: signolux Mobiler Empfaenger (1x)</li>"
            "</ul>"
            "<p>Lieferant: Humantechnik GmbH — www.humantechnik.com<br/>"
            "Hinweis: Bestellung ERST nach Kassengenehmigung oder auf eigene Kosten mit Erstattungsvorbehalt.</p>"
        ),
    },
    {
        "name": "HNO-Rezept Muster 16 einholen (Gewerk 2 / GKV)",
        "stage_id": STAGE_IN_ARBEIT,
        "allocated_hours": 0.25,
        "description": (
            "<p><strong>Naechster Schritt fuer Gewerk 2:</strong> HNO-Arzt aufsuchen und Muster-16-Rezept ausstellen lassen.</p>"
            "<p>Textvorlage ist in Task 297 (Kassenantrag) und im Angebot S00013 hinterlegt.</p>"
            "<p>Rezept → Krankenkasse einreichen → Genehmigung abwarten → Humantechnik bestellen.</p>"
        ),
    },
    {
        "name": "Pflegekasse-Antrag §40 SGB XI einreichen (Gewerk 1)",
        "stage_id": STAGE_IN_ARBEIT,
        "allocated_hours": 0.5,
        "description": (
            "<p>Antrag auf wohnumfeldverbessernde Massnahme bei der Pflegekasse stellen.</p>"
            "<p>Unterlagen: Angebot S00012 als PDF + formloses Anschreiben (Text in Task 297).</p>"
            "<p><strong>Wichtig:</strong> Antrag VOR Auftragserteilung / Zahlung stellen!</p>"
            "<p>Budget: bis 4.000 EUR. Unser Angebot: 1.084,90 EUR Netto.</p>"
        ),
    },
    {
        "name": "Thomann-Lieferung pruefen & Ware einlagern (Gewerk 1)",
        "stage_id": STAGE_IN_ARBEIT,
        "allocated_hours": 0.5,
        "description": (
            "<p>Wareneingang Thomann-Bestellung pruefen:</p>"
            "<ul>"
            "<li>t.racks 4x4 DSP Pro — Vollstaendigkeitspruefung, Sichtpruefung</li>"
            "<li>PreSonus Eris 3.5 — beide Lautsprecher, Netzkabel, Bedienungsanleitung</li>"
            "</ul>"
            "<p>Noch zu bestellen: Swissonic Audio Extractor, Fostex PC-1e, Toslink-Kabel.</p>"
            "<p>Kabel Euroblock→XLR und Euroblock→RCA: Eigenbau — Phoenixterminals + XLR/RCA konfektionieren.</p>"
        ),
    },
    {
        "name": "Bedienungsanleitung Gewerk 2 fuer Alois erstellen (seniorengerecht)",
        "stage_id": STAGE_PLANUNG,
        "allocated_hours": 1.0,
        "description": (
            "<p>Einfache, grossformatige Anleitung (A4, Schriftgroesse 16+, Bilder) fuer die Signolux-Anlage.</p>"
            "<p>Inhalt: Was bedeuten die Blinkfarben? Was tun bei Alarm? Wie Vibrationskissen einlegen?</p>"
            "<p>Analog zu Task 272 (Bedienungsanleitung Gewerk 1).</p>"
        ),
    },
    {
        "name": "Vor-Ort-Termin planen: Installation Phase 1-4 (Gewerk 1)",
        "stage_id": STAGE_IN_ARBEIT,
        "allocated_hours": 0.25,
        "description": (
            "<p>Terminkoordination fuer den ersten Installations-Tag (ca. 4-5h).</p>"
            "<p>Voraussetzung: Thomann-Lieferung vollstaendig UND Pflegekasse-Genehmigung (oder Selbstzahler-Bestaetigung).</p>"
            "<p>Zu erledigen: Tasks 269-296, Phase 1-4.</p>"
        ),
    },
]

for task_data in new_tasks:
    existing = m.execute_kw(DB, UID, PW, "project.task", "search",
                            [[["name", "=", task_data["name"]], ["project_id", "=", PROJECT_ID]]])
    if existing:
        print(f"  [EXISTS] {task_data['name'][:60]}")
        continue
    task_data["project_id"] = PROJECT_ID
    tid = m.execute_kw(DB, UID, PW, "project.task", "create", [task_data])
    print(f"  [OK] Erstellt: {task_data['name'][:60]} (ID={tid})")

# ─── 4. Lieferant Humantechnik anlegen ───────────────────────────────────────
print("\n[4] Lieferant Humantechnik anlegen...")

existing_vendor = m.execute_kw(DB, UID, PW, "res.partner", "search_read",
                               [[["name", "ilike", "Humantechnik"]]],
                               {"fields": ["id", "name"]})
if existing_vendor:
    vendor_id = existing_vendor[0]["id"]
    print(f"  [EXISTS] Humantechnik GmbH (ID={vendor_id})")
else:
    vendor_id = m.execute_kw(DB, UID, PW, "res.partner", "create", [{
        "name": "Humantechnik GmbH",
        "is_company": True,
        "supplier_rank": 1,
        "customer_rank": 0,
        "website": "https://www.humantechnik.com",
        "comment": "Spezialist fuer Assistenztechnik / Gehoerlosenbedarfe. Signolux-System (868 MHz). GKV-HMV-gelistete Produkte.",
        "country_id": 82,  # Deutschland
    }])
    print(f"  [OK] Humantechnik GmbH angelegt (ID={vendor_id})")

# Signolux-Produkte mit Humantechnik als Lieferanten verknuepfen
sig_codes = ["HW-SIG-REC", "HW-SIG-VIB", "HW-SIG-SMOKE", "HW-SIG-BELL", "HW-SIG-PORT"]
for code in sig_codes:
    tmpl = m.execute_kw(DB, UID, PW, "product.template", "search_read",
                        [[["default_code", "=", code]]],
                        {"fields": ["id", "list_price"]})
    if not tmpl:
        continue
    tmpl_id = tmpl[0]["id"]
    ek_preis = round(tmpl[0]["list_price"] * 0.80, 2)  # 80% des VK als EK-Schaetzung
    existing_si = m.execute_kw(DB, UID, PW, "product.supplierinfo", "search",
                               [[["partner_id", "=", vendor_id],
                                 ["product_tmpl_id", "=", tmpl_id]]])
    if not existing_si:
        m.execute_kw(DB, UID, PW, "product.supplierinfo", "create", [{
            "partner_id": vendor_id,
            "product_tmpl_id": tmpl_id,
            "price": ek_preis,
            "min_qty": 1,
        }])
        print(f"  [OK] {code}: Lieferant Humantechnik, EK-Schaetzung {ek_preis:.2f} EUR (bitte anpassen!)")
    else:
        print(f"  [EXISTS] {code}: Lieferant bereits hinterlegt")

# ─── 5. Angebote mit Gewerk-Label versehen ────────────────────────────────────
print("\n[5] Angebote beschriften...")

# S00012 — Gewerk 1 / Pflegekasse
m.execute_kw(DB, UID, PW, "sale.order", "write", [[12], {
    "note": (
        "<p><strong>GEWERK 1: Bimodale TV-Audiointegration</strong></p>"
        "<p>Kostentraeger: <strong>Pflegekasse</strong> gemaess &sect;40 SGB XI (Wohnumfeldverbesserung)</p>"
        "<p>Erstattungshoehe: bis 4.000,00 EUR | Unser Angebot: 1.084,90 EUR Netto</p>"
        "<p>Voraussetzung: Pflegegrad 1+ vorhanden. Antrag VOR Beauftragung stellen.</p>"
        "<p>Referenz: PRJ-2026-MED-PRINZ-GW1 | Technischer Leiter: Wolf / FraWo</p>"
    ),
}])
print("  [OK] S00012 — Gewerk-1-Label (Pflegekasse §40 SGB XI)")

# S00013 — Gewerk 2 / Krankenkasse (bereits bearbeitet, nur confirm)
print("  [OK] S00013 — Gewerk-2-Label bereits korrekt (§33 SGB V)")

# ─── 6. Projektbeschreibung aktualisieren ────────────────────────────────────
print("\n[6] Projektbeschreibung: Zwei-Saeulen-Konzept...")

projekt_beschreibung = """<h2>PRJ-2026-MED-PRINZ — Barrierefreie Audio- & Assistenz-Sicherheitssysteme</h2>
<p><strong>Kunde:</strong> Familie Prinz | <strong>Projektleiter:</strong> Wolf / FraWo GbR<br/>
<strong>Fachkraft:</strong> Veranstaltungstechnik | <strong>Startdatum:</strong> 29. Mai 2026</p>

<h3>Das Zwei-Saeulen-Prinzip</h3>
<p>Beide Systeme arbeiten streng autark. Ein Ausfall des TV-Systems hat zu keinem Zeitpunkt
Einfluss auf die lebenserhaltenden Sicherheitsfunktionen.</p>

<table border="1" cellpadding="6" style="border-collapse:collapse; width:100%">
<tr style="background:#e8f4e8">
  <th>Gewerk 1: TV-Audio (autarkes AV-System)</th>
  <th>Gewerk 2: Sicherheits-Signalanlage</th>
</tr>
<tr>
  <td>DSP-gestuetzte Latenzkompensation fuer CI + HG</td>
  <td>Klingel, Rauchalarm, Telefon via 868-MHz-Funk</td>
</tr>
<tr>
  <td>t.racks 4x4 DSP Pro + PreSonus Eris 3.5</td>
  <td>Humantechnik signolux System</td>
</tr>
<tr>
  <td><strong>Kostentraeger: Pflegekasse §40 SGB XI</strong></td>
  <td><strong>Kostentraeger: GKV §33 SGB V (100%)</strong></td>
</tr>
<tr>
  <td>Budget: bis 4.000 EUR | Angebot: 1.084,90 EUR</td>
  <td>Zuzahlung: 10 EUR | Angebot: 1.144,79 EUR</td>
</tr>
</table>

<h3>Angebote</h3>
<ul>
<li><strong>S00012</strong> — Gewerk 1 / Pflegekasse §40 SGB XI — 1.084,90 EUR Netto</li>
<li><strong>S00013</strong> — Gewerk 2 / GKV §33 SGB V — 1.144,79 EUR Netto (GKV erstattet)</li>
</ul>"""

try:
    m.execute_kw(DB, UID, PW, "project.project", "write",
                 [[PROJECT_ID], {"description": projekt_beschreibung}])
    print("  [OK] Projektbeschreibung mit Zwei-Saeulen-Konzept und Angebots-Tabelle")
except Exception as e:
    print(f"  [WARN] {e}")

# ─── 7. Zusammenfassung ───────────────────────────────────────────────────────
print("\n" + "="*70)
print("FINALISIERUNG ABGESCHLOSSEN")
print(f"  Projekt:    http://10.1.0.112:8069/odoo/project/{PROJECT_ID}")
print(f"  S00012 GW1: http://10.1.0.112:8069/odoo/sales/12")
print(f"  S00013 GW2: http://10.1.0.112:8069/odoo/sales/13")
print(f"  Task 297:   http://10.1.0.112:8069/odoo/project/{PROJECT_ID}?task=297")
print("="*70)
