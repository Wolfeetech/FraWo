import xmlrpc.client

url = 'http://10.1.0.112:8069'
db = 'FraWo_GbR'
user = 'wolf@frawo-tech.de'
import os
pw = os.environ.get('ODOO_PASSWORD', 'INSERT_PASSWORD_HERE')

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, pw, {})
m = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def create(model, vals):
    return m.execute_kw(db, uid, pw, model, 'create', [vals])

def search_read(model, domain, fields=['id','name'], limit=10):
    return m.execute_kw(db, uid, pw, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

def write(model, ids, vals):
    return m.execute_kw(db, uid, pw, model, 'write', [ids if isinstance(ids, list) else [ids], vals])

print('=== Creating Familie Prinz as Customer ===')
existing = search_read('res.partner', [['name', 'like', 'Prinz']], ['id','name'])
if existing:
    partner_id = existing[0]['id']
    print(f'  Found existing: {existing[0]["name"]} (id={partner_id})')
else:
    partner_id = create('res.partner', {
        'name': 'Familie Prinz',
        'company_type': 'person',
        'customer_rank': 1,
        'city': 'Deutschland',
        'comment': 'Privatkunde | Barrierefreie Medizintechnik-Integration | CI + Hörgerät (bimodal)',
        'lang': 'de_DE',
    })
    print(f'  Created Familie Prinz (id={partner_id})')

print('\n=== Creating Product Category ===')
cats = search_read('product.category', [['name','like','Medizin']], ['id','name'])
if cats:
    cat_id = cats[0]['id']
    print(f'  Found: {cats[0]["name"]} (id={cat_id})')
else:
    parent_cats = search_read('product.category', [['name','=','All']], ['id'])
    parent_id = parent_cats[0]['id'] if parent_cats else False
    cat_id = create('product.category', {
        'name': 'Medizintechnik & Assistenzsysteme',
        'parent_id': parent_id,
    })
    print(f'  Created category (id={cat_id})')

print('\n=== Creating Hardware Products ===')
hardware_products = [
    {'code': 'HW-DSP-4X4', 'name': 't.racks 4x4 DSP Pro',
     'desc': '4-Kanal DSP mit Euroblock-Klemmen, parametrischer EQ + Delay + Limiter pro Kanal. Programmierung via USB.',
     'cost': 116.81, 'price': 139.00, 'note': 'Bestellt - Thomann'},
    {'code': 'HW-SPK-ERIS35', 'name': 'PreSonus Eris 3.5 (Paar)',
     'desc': 'Aktive Studio-Monitore 2-Wege, XLR/TRS-Eingang, 25W. Raumlautsprecher Mutter.',
     'cost': 83.19, 'price': 99.00, 'note': 'Bestellt - Thomann'},
    {'code': 'HW-EXT-SWIS', 'name': 'Swissonic Audio Extractor',
     'desc': 'D/A-Wandler Toslink zu Stereo-RCA. Ausgabepegel fest. PCM-Stereo kompatibel.',
     'cost': 41.18, 'price': 49.00, 'note': 'Zu bestellen - Thomann'},
    {'code': 'HW-ACC-VOL', 'name': 'Fostex PC-1e Passivregler (Schwarz)',
     'desc': 'Passiver Tisch-Lautstärkeregler. Klinke Stereo In/Out. Regler fuer Mutter (Raum).',
     'cost': 24.37, 'price': 29.00, 'note': 'Zu bestellen - Thomann'},
    {'code': 'HW-CAB-PHOEN1', 'name': 'Adapterkabel Euroblock auf XLR-Male 0,5m',
     'desc': 'Eigenbau-Adapterkabel DSP-Out zu Transmitter. Sym auf Unsym (Cold unbeschaltet). Konfektioniert.',
     'cost': 8.40, 'price': 15.00, 'note': 'Zu fertigen - Eigenbau FraWo'},
    {'code': 'HW-CAB-PHOEN2', 'name': 'Adapterkabel Euroblock auf RCA-Female 0,5m',
     'desc': 'Eigenbau-Adapterkabel DSP-Out zu PreSonus. Sym auf Unsym mit Massbruecke auf Cold.',
     'cost': 8.40, 'price': 15.00, 'note': 'Zu fertigen - Eigenbau FraWo'},
    {'code': 'HW-CAB-TOS', 'name': 'Toslink-Kabel 1,5m',
     'desc': 'Lichtwellenleiter TV Optical Out zu Swissonic Audio Extractor.',
     'cost': 0.00, 'price': 9.90, 'note': 'Aus Lager'},
    {'code': 'HW-NET-SW8', 'name': 'Managed PoE Switch 8-Port',
     'desc': 'IGMP Snooping v2/v3 und QoS aktiv. Netzwerktrennung Magenta TV Box vom WLAN-Multicast.',
     'cost': 0.00, 'price': 79.00, 'note': 'Aus Lager'},
]

for p in hardware_products:
    existing = search_read('product.template', [['default_code','=',p['code']]], ['id','name'])
    if existing:
        print(f'  Exists: {p["code"]} (id={existing[0]["id"]})')
    else:
        pid = create('product.template', {
            'name': p['name'],
            'default_code': p['code'],
            'categ_id': cat_id,
            'type': 'consu',
            'standard_price': p['cost'],
            'list_price': p['price'],
            'description_sale': p['desc'],
            'description_picking': p['note'],
            'purchase_ok': True,
            'sale_ok': True,
        })
        print(f'  Created: {p["code"]} {p["name"]} (id={pid})')

print('\n=== Creating Service Products ===')
service_products = [
    {'code': 'SRV-INSTALL', 'name': 'Systeminstallation vor Ort',
     'desc': 'Physische Montage, Kabelverlegung, Signalflusskontrolle, EMV-Schutz. Stundensatz 85 EUR/h.',
     'price': 85.00},
    {'code': 'SRV-DSP-PROG', 'name': 'DSP-Programmierung & Einmessung (bimodal)',
     'desc': 'FFT-Latenzmessung CI vs. Hörgerät (REW/Smaart), param. EQ, Delay-Kalibrierung, Limiter-Setup Gehörschutz.',
     'price': 95.00},
    {'code': 'SRV-SEN-EINW', 'name': 'Einweisung & App-Konfiguration (Senioren)',
     'desc': 'Seniorengerechte Übergabe, iPhone-App-Kopplung CI und HG, Erstellung Abnahmeprotokoll für Pflegekasse.',
     'price': 80.00},
]

for p in service_products:
    existing = search_read('product.template', [['default_code','=',p['code']]], ['id','name'])
    if existing:
        print(f'  Exists: {p["code"]} (id={existing[0]["id"]})')
    else:
        pid = create('product.template', {
            'name': p['name'],
            'default_code': p['code'],
            'categ_id': cat_id,
            'type': 'service',
            'standard_price': p['price'],
            'list_price': p['price'],
            'description_sale': p['desc'],
            'purchase_ok': False,
            'sale_ok': True,
        })
        print(f'  Created: {p["code"]} {p["name"]} (id={pid})')

print('\n=== Creating Project ===')
existing_proj = search_read('project.project', [['name','like','Prinz']], ['id','name'])
if existing_proj:
    proj_id = existing_proj[0]['id']
    print(f'  Found: {existing_proj[0]["name"]} (id={proj_id})')
else:
    proj_id = create('project.project', {
        'name': 'Barrierefreie bimodale Audiointegration – Familie Prinz',
        'partner_id': partner_id,
        'description': (
            'Projekt-ID: PRJ-2026-MED-PRINZ\n'
            'Kunde: Familie Prinz | PL: Wolf / FraWo GbR\n\n'
            'Errichtung eines barrierefreien, latenzkompensierten Audiosystems fuer bimodal versorgten Vater '
            '(Links: CI Med-El Sonnet 3 | Rechts: Phonak Hörgeraet).\n'
            'Mutter: unabhaengige Lautsstaerke-Regelung PreSonus Eris 3.5 via Fostex PC-1e.\n\n'
            'Rechtsgrundlage: SGB V § 33 (Hilfsmittel) / SGB XI § 40 (Wohnumfeldverbesserung)\n'
            'Kassen-Dokumentation fuer Erstattungsantrag.'
        ),
        'privacy_visibility': 'employees',
        'allow_timesheets': True,
    })
    print(f'  Created project (id={proj_id})')

print('\n=== Creating Task Stages ===')
stages_data = [
    ('Phase 1: AV-Infrastruktur', 10),
    ('Phase 2: Kabelkonfektion & Hardware', 20),
    ('Phase 3: Einmessung & DSP-Setup', 30),
    ('Phase 4: Abnahme & Dokumentation', 40),
]

stage_ids = {}
for sname, seq in stages_data:
    existing_stage = search_read('project.task.type', [['name','=',sname]], ['id','name'])
    if existing_stage:
        sid = existing_stage[0]['id']
        # Make sure project is linked
        m.execute_kw(db, uid, pw, 'project.task.type', 'write',
            [[sid], {'project_ids': [(4, proj_id)]}])
        print(f'  Stage linked: {sname} (id={sid})')
    else:
        sid = create('project.task.type', {
            'name': sname,
            'sequence': seq,
            'project_ids': [(4, proj_id)],
        })
        print(f'  Created stage: {sname} (id={sid})')
    stage_ids[sname] = sid

print('\n=== Creating Project Tasks ===')
tasks = [
    {'name': 'Task 1.1: Managed PoE Switch konfigurieren',
     'stage': 'Phase 1: AV-Infrastruktur', 'hours': 1.0,
     'desc': (
         'Konfiguration des Managed PoE Switches:\n'
         '- IGMP Snooping (v2/v3) aktivieren auf VLAN der Magenta TV Box\n'
         '- Multicast-Fluten im WLAN unterbinden\n'
         '- QoS-Priorisierung für Voice/Video-Traffic\n'
         '- Dokumentation der Switch-Konfiguration (Screenshot Webinterface)\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 1.2: Cat6-Kabelverlegung Magenta TV Box',
     'stage': 'Phase 1: AV-Infrastruktur', 'hours': 1.0,
     'desc': (
         'Verlegung Cat6-Kabel vom PoE-Switch zur Magenta TV Box:\n'
         '- Kabelführung über Kabelkanal oder Fußleiste\n'
         '- Funktionstest Live-TV-Stream (kein Buffering / Latenzproblem)\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 1.3: Swissonic Audio Extractor – TV Anschluss',
     'stage': 'Phase 1: AV-Infrastruktur', 'hours': 1.0,
     'desc': (
         'Montage Swissonic Audio Extractor am Samsung TV:\n'
         '- Toslink 1,5m von TV Optical Out zu Extractor\n'
         '- TV-Einstellungen: Format PCM / Stereo, Ausgabe Optisch\n'
         '- WICHTIG: Fixer TV-Ausgabepegel sicherstellen (kein automatisches Volume!)\n'
         '- Funktionstest: Stereo RCA-Signal auf Pegelmesser prüfen\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 2.1: Adapterkabel Euroblock konfektionieren',
     'stage': 'Phase 2: Kabelkonfektion & Hardware', 'hours': 2.5,
     'desc': (
         'Herstellung der Spezialverbindungskabel (Sym/Unsym-Anpassung):\n\n'
         'EINGÄNGE (Sym auf Unsym):\n'
         '- 2x RCA-Male auf Euroblock-Terminal (L+R Input)\n'
         '  -> RCA-Center auf Hot (+), Schirmung auf GND + Brücke auf Cold (-)\n\n'
         'AUSGÄNGE Out 1+2 (für PreSonus Eris):\n'
         '- 2x Euroblock auf RCA-Female\n'
         '  -> Hot (+) auf Center, GND auf Schirm, Cold (-) FREI LASSEN\n\n'
         'AUSGÄNGE Out 3+4 (für CI/HG Transmitter):\n'
         '- 2x Euroblock auf XLR-Male 3-pol oder Klinke Mono\n'
         '  -> Hot (+) auf Pin2/Spitze, GND auf Pin1/Schaft, Cold (Pin3) unbeschaltet\n\n'
         'WICHTIG: Alle Kabel beschriften, Zugentlastung, Sichtprüfung!\n\n'
         'Geschätzte Dauer: 2,5 Stunden'
     )},
    {'name': 'Task 2.2: t.racks DSP Pro montieren und verkabeln',
     'stage': 'Phase 2: Kabelkonfektion & Hardware', 'hours': 2.0,
     'desc': (
         'Montage und Inbetriebnahme t.racks 4x4 DSP Pro:\n'
         '- Aufstellung AV-Schrank / Sideboard (Belüftung beachten)\n'
         '- Anschluss 230V/50Hz Spannungsversorgung\n'
         '- IN 1: Swissonic RCA-L -> Euroblock\n'
         '- IN 2: Swissonic RCA-R -> Euroblock\n'
         '- OUT 1+2: DSP -> Fostex PC-1e -> PreSonus Eris L+R\n'
         '- OUT 3: DSP -> Med-El TV Connector (CI Transmitter, MONO)\n'
         '- OUT 4: DSP -> Phonak TV Connector (HG Transmitter, MONO)\n'
         '- USB-Verbindung mit DSP Control Software testen\n\n'
         'Geschätzte Dauer: 2 Stunden'
     )},
    {'name': 'Task 2.3: PreSonus Eris 3.5 + Fostex PC-1e installieren',
     'stage': 'Phase 2: Kabelkonfektion & Hardware', 'hours': 1.0,
     'desc': (
         'Aufstellung und Einschleifen des passiven Reglers:\n'
         '- PreSonus Eris 3.5 Paar aufstellen (Nahfeld, ca. 30° Abstrahlwinkel)\n'
         '- Fostex PC-1e einschleifen: DSP Out 1+2 -> PC-1e -> Eris L+R\n'
         '- PC-1e auf Tisch/Sideboard für Mutter positionieren\n'
         '- Eris-interne Regler auf Maximum (PC-1e = einzige Regelung für Mutter)\n'
         '- Sichtkontrolle aller Verbindungen\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 3.1: DSP Routing-Grundsetup laden und programmieren',
     'stage': 'Phase 3: Einmessung & DSP-Setup', 'hours': 1.5,
     'desc': (
         'DSP Control Software (USB) – Routing und Grundparameter:\n\n'
         'ROUTING:\n'
         '- Out 1 (L): Input 1 | Gain 0dB | HPF 60Hz Butterworth 12dB\n'
         '- Out 2 (R): Input 2 | Gain 0dB | HPF 60Hz Butterworth 12dB\n'
         '- Out 3 (CI-Mono): In 1+2 sum | Gain -3dB | HPF 150Hz Linkwitz-Riley 24dB\n'
         '- Out 4 (HG-Mono): In 1+2 sum | Gain -2dB | HPF 100Hz Butterworth 18dB\n\n'
         'EQ-VOREINSTELLUNGEN:\n'
         '- Out 1+2: PEQ1: 120Hz -3dB Q=1.5 | PEQ2: 3.2kHz +1.5dB Q=1.0\n'
         '- Out 3 (CI): PEQ1: 2.5kHz +4dB Q=2.0 | PEQ2: 6kHz -3dB Q=1.0\n'
         '- Out 4 (HG): PEQ1: 1.8kHz +3dB Q=1.5 | PEQ2: 4kHz +2dB Q=1.5\n\n'
         'LIMITER:\n'
         '- Out 3 (CI): Peak Limiter | Thresh -6dBu | Release 150ms\n'
         '- Out 4 (HG): RMS Kompressor 2.5:1 | Thresh -12dBu | Attack 20ms | Release 100ms\n\n'
         'Preset sichern! Geschätzte Dauer: 1,5 Stunden'
     )},
    {'name': 'Task 3.2: Bimodale Latenzmessung CI vs. Hörgerät (REW/Smaart)',
     'stage': 'Phase 3: Einmessung & DSP-Setup', 'hours': 2.0,
     'desc': (
         'Latenzmessung mit REW (Room EQ Wizard):\n\n'
         'VERFAHREN:\n'
         '1. Messmikrofon in Ohrposition des Vaters\n'
         '2. Impuls über DSP Out 3 (CI-Kanal) -> Latenz CI messen\n'
         '3. Impuls über DSP Out 4 (HG-Kanal) -> Latenz HG messen\n'
         '4. Delta T = T_HG - T_CI berechnen\n'
         '5. Delay auf Out 3 (CI) = Delta T programmieren\n\n'
         'ERWARTUNGSWERTE:\n'
         '- Phonak AirStream (HG): ~15-20ms Funklatenz\n'
         '- Med-El Transmitter (CI): herstellerspezifisch, i.d.R. kuerzer\n\n'
         'DOKUMENTATION:\n'
         '- Messprotokoll Screenshots sichern (Kassen-Nachweis!)\n'
         '- Delay-Wert in Preset eintragen\n\n'
         'Geschätzte Dauer: 2 Stunden'
     )},
    {'name': 'Task 3.3: Brickwall-Limiter kalibrieren – Gehörschutz',
     'stage': 'Phase 3: Einmessung & DSP-Setup', 'hours': 1.0,
     'desc': (
         'Gehörschutz-Kalibrierung nach EU-RL 2003/10/EG:\n'
         '- Rosa Rauschen mit kalibriertem Pegel einspeisen\n'
         '- Max. Ausgangspegel Out 3 (CI) und Out 4 (HG) auf <= 85 dBA am Ohrhörer\n'
         '- Impulstest: Film-Explosionen, Starthilfepistole (simuliert)\n'
         '- Sicherstellen: Kein Clipping, keine Verzerrung bei Impulsspitzen\n'
         '- Limiter-Preset passwortgeschützt abspeichern\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 4.1: Funktionstest Mutter – Lautstärkeregelung Raum',
     'stage': 'Phase 4: Abnahme & Dokumentation', 'hours': 0.5,
     'desc': (
         'Abnahmetest mit der Mutter:\n'
         '- Stufenloser Test Fostex PC-1e (Vollbereich 0–max)\n'
         '- Sicherstellen: Raum-Lautstaerke beeinflusst CI/HG-Signal NICHT\n'
         '- Hörtest TV-Normalprogramm und Nachrichten\n'
         '- Bedienungseinweisung: Einschalten, Lautstaerke, Stummschalten\n'
         '- Mutter unterschreibt Abnahmeprotokoll Teil A\n\n'
         'Geschätzte Dauer: 30 Minuten'
     )},
    {'name': 'Task 4.2: Funktionstest Vater – CI + Hörgerät bimodal',
     'stage': 'Phase 4: Abnahme & Dokumentation', 'hours': 1.0,
     'desc': (
         'Abnahmetest mit dem Vater (bimodale Hörerperspektive):\n'
         '- TV-Ton über CI (Out 3) und HG (Out 4) synchron testen\n'
         '- Vater berichtet: Echo? Phasendifferenz? Verstaendlichkeit?\n'
         '- Feinjustage Delay und EQ nach Hörurteil\n'
         '- Test: Nachrichten, Film, Musik\n'
         '- Unabhaengige Lautstaerke via CI/HG und iPhone-App testen\n'
         '- Vater unterschreibt Abnahmeprotokoll Teil B\n\n'
         'Geschätzte Dauer: 1 Stunde'
     )},
    {'name': 'Task 4.3: Abnahmeprotokoll & Kassen-Dokumentation erstellen',
     'stage': 'Phase 4: Abnahme & Dokumentation', 'hours': 0.5,
     'desc': (
         'Vollständige Kassendokumentation erstellen:\n\n'
         'ABNAHMEPROTOKOLL:\n'
         '- Systembeschreibung und Signalflussplan\n'
         '- Gemessene Latenzwerte (CI, HG, Delta T, Delay-Korrektur)\n'
         '- Pegel-Kalibrierungsprotokoll (max. Ausgangspegel dBu/dBA)\n'
         '- Unterschriften: Vater, Mutter, FraWo GbR\n\n'
         'KASSENANTRAG:\n'
         '- Formloser Antrag SGB XI §40 oder SGB V §33\n'
         '- Qualifikationsnachweis: Berufsabschluss Fachkraft Veranstaltungstechnik\n'
         '- Kostenvoranschlag aus Odoo (PDF)\n'
         '- Fotos der Installation (Vorher/Nachher)\n'
         '- Alle Dokumente als Anhang in Odoo hinterlegen\n\n'
         'Geschätzte Dauer: 30 Minuten'
     )},
]

task_ids = []
for t in tasks:
    stage_id = stage_ids.get(t['stage'])
    existing = search_read('project.task',
        [['name','=',t['name']], ['project_id','=',proj_id]], ['id','name'])
    if existing:
        print(f'  Exists: {t["name"][:55]}')
        task_ids.append(existing[0]['id'])
    else:
        tid = create('project.task', {
            'name': t['name'],
            'project_id': proj_id,
            'stage_id': stage_id,
            'description': t['desc'],
            'planned_hours': t['hours'],
        })
        task_ids.append(tid)
        print(f'  Created: {t["name"][:55]} (id={tid})')

print(f'\n=== SUMMARY ===')
print(f'Customer: Familie Prinz (id={partner_id})')
print(f'Project:  PRJ-2026-MED-PRINZ (id={proj_id})')
print(f'Tasks:    {len(task_ids)} tasks in 4 phases')
print(f'Products: {len(hardware_products)} hardware + {len(service_products)} service items')
print(f'Odoo URL: http://10.1.0.112:8069/odoo/project')
