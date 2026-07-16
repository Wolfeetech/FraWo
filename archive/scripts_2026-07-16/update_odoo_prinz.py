import xmlrpc.client

url = 'http://10.1.0.112:8069'
db = 'FraWo_GbR'
import os
pw = os.environ.get('ODOO_PASSWORD', 'INSERT_PASSWORD_HERE')
uid = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common').authenticate(db, 'wolf@frawo-tech.de', pw, {})
m = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
proj_id = 22

def create(model, vals):
    return m.execute_kw(db, uid, pw, model, 'create', [vals])

def write(model, ids, vals):
    return m.execute_kw(db, uid, pw, model, 'write', [[ids] if isinstance(ids, int) else ids, vals])

def search_read(model, domain, fields=['id','name'], limit=10):
    return m.execute_kw(db, uid, pw, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

print('1. Updating project with customer and description...')
write('project.project', proj_id, {
    'partner_id': 42,
    'description': (
        'Projekt-ID: PRJ-2026-MED-PRINZ\n'
        'Auftraggeber: Familie Prinz | PL: Wolf / FraWo GbR\n\n'
        'ZIELSYSTEM:\n'
        '- Links: CI Med-El Sonnet 3 (Out 3 Mono)\n'
        '- Rechts: Phonak Hoergeraet (Out 4 Mono)\n'
        '- Mutter: PreSonus Eris 3.5 via Fostex PC-1e (Out 1+2 unabhaengig)\n'
        '- Signalquelle: Samsung TV -> Toslink -> Swissonic -> t.racks 4x4 DSP Pro\n\n'
        'RECHTSGRUNDLAGE: SGB V §33 / SGB XI §40\n'
        'Kassenantrag mit Abnahmeprotokoll (FraWo als Elektrofachkraft VDE).\n\n'
        'HARDWARE:\n'
        '- Bestellt: t.racks 4x4 DSP Pro, PreSonus Eris 3.5 (Thomann)\n'
        '- Zu bestellen: Swissonic Audio Extractor, Fostex PC-1e\n'
        '- Zu fertigen: Euroblock-Adapterkabel (4 Stueck)'
    ),
})
print('   OK')

print('\n2. Adding stage: Dokumentation & Kasse...')
existing_stage = search_read('project.task.type', [['name', 'like', 'Kasse']], ['id'])
if existing_stage:
    kasse_stage_id = existing_stage[0]['id']
    write('project.task.type', kasse_stage_id, {'project_ids': [(4, proj_id)]})
    print(f'   Linked existing (id={kasse_stage_id})')
else:
    kasse_stage_id = create('project.task.type', {
        'name': 'Dokumentation & Kasse',
        'sequence': 50,
        'project_ids': [(4, proj_id)],
    })
    print(f'   Created (id={kasse_stage_id})')

stage_arbeit = 3
stage_planung = 2

print('\n3. Creating subtasks...')
subtasks = [
    {'parent': 270, 'name': 'TV Audio-Ausgang: Swissonic Extractor anschliessen',
     'stage': stage_planung, 'hours': 1.0,
     'desc': (
         'Toslink 1,5m von TV Optical Out zu Swissonic Audio Extractor\n'
         'TV-Einstellungen: Format PCM Stereo, Ausgabe Optisch, FIXER Pegel!\n'
         'Stereo RCA Output auf Pegelmesser pruefen\n'
         'Kein automatisches Volume-Management des TV!'
     )},
    {'parent': 270, 'name': 'Euroblock-Adapterkabel konfektionieren (Sym/Unsym)',
     'stage': stage_planung, 'hours': 2.5,
     'desc': (
         'EINGANG (Sym auf Unsym, 2x RCA-Male -> Euroblock):\n'
         '  Hot = RCA-Center, GND = Schirmung, Cold = GND-Bruecke\n\n'
         'AUSGANG Out1+2 (2x Euroblock -> RCA-Female fuer PreSonus):\n'
         '  Hot -> Center, GND -> Schirm, Cold FREI LASSEN\n\n'
         'AUSGANG Out3+4 (2x Euroblock -> XLR-Male/Klinke fuer Transmitter):\n'
         '  Hot -> Pin2/Spitze, GND -> Pin1/Schaft, Cold unbeschaltet\n\n'
         'Alle Kabel beschriften! Zugentlastung!'
     )},
    {'parent': 270, 'name': 't.racks DSP Pro montieren und vollstaendig verkabeln',
     'stage': stage_planung, 'hours': 2.0,
     'desc': (
         'Aufstellung (Belueftung!)\n'
         'IN1: Swissonic RCA-L via Euroblock-Kabel\n'
         'IN2: Swissonic RCA-R via Euroblock-Kabel\n'
         'OUT1+2: Fostex PC-1e -> PreSonus Eris L+R (Mutter)\n'
         'OUT3: Med-El TV Connector (CI, Mono)\n'
         'OUT4: Phonak TV Connector (HG, Mono)\n'
         'USB-Verbindung DSP Control Software testen'
     )},
    {'parent': 270, 'name': 'Fostex PC-1e Tischregler fuer Mutter einschleifen',
     'stage': stage_planung, 'hours': 0.5,
     'desc': (
         'PC-1e einschleifen: DSP Out1+2 -> PC-1e -> PreSonus Eris\n'
         'PreSonus-interne Regler auf Maximum setzen\n'
         'PC-1e auf Tisch/Sideboard platzieren (gut erreichbar fuer Mutter)'
     )},
    {'parent': 269, 'name': 'DSP Routing-Grundsetup programmieren (4 Kanaele)',
     'stage': stage_planung, 'hours': 1.5,
     'desc': (
         'ROUTING:\n'
         '  Out1 L:  In1 | 0dB | HPF 60Hz Butterworth 12dB\n'
         '  Out2 R:  In2 | 0dB | HPF 60Hz Butterworth 12dB\n'
         '  Out3 CI: In1+2 sum | -3dB | HPF 150Hz Linkwitz-Riley 24dB\n'
         '  Out4 HG: In1+2 sum | -2dB | HPF 100Hz Butterworth 18dB\n\n'
         'EQ Out1+2: PEQ1 120Hz -3dB Q=1.5 | PEQ2 3.2kHz +1.5dB Q=1.0\n'
         'EQ Out3 CI: PEQ1 2.5kHz +4dB Q=2.0 | PEQ2 6kHz -3dB Q=1.0\n'
         'EQ Out4 HG: PEQ1 1.8kHz +3dB Q=1.5 | PEQ2 4kHz +2dB Q=1.5\n\n'
         'LIMITER Out3 CI: Peak | Thresh -6dBu | Release 150ms\n'
         'LIMITER Out4 HG: RMS 2.5:1 | Thresh -12dBu | Att 20ms | Rel 100ms\n\n'
         'Preset sichern!'
     )},
    {'parent': 269, 'name': 'Bimodale Latenzmessung CI vs. HG (REW/Smaart)',
     'stage': stage_planung, 'hours': 2.0,
     'desc': (
         '1. Messmikrofon in Ohrposition Vater\n'
         '2. Impuls via Out3 -> CI-Latenz messen\n'
         '3. Impuls via Out4 -> HG-Latenz messen\n'
         '4. Delta T = T_HG - T_CI berechnen\n'
         '5. Delay auf Out3 = Delta T programmieren -> synchrone Wahrnehmung\n\n'
         'Phonak AirStream: ca. 15-20ms Latenz (Referenz)\n'
         'Med-El Transmitter: kuerzer, herstellerspezifisch\n\n'
         'WICHTIG: Messprotokoll-Screenshots fuer Kassendokumentation!'
     )},
    {'parent': 269, 'name': 'Limiter kalibrieren - Gehoerschutz 85dBA max.',
     'stage': stage_planung, 'hours': 1.0,
     'desc': (
         'Rosa Rauschen einspeisen\n'
         'Max. Ausgangspegel Out3+4 auf <= 85dBA am Ohrhoerer kalibrieren\n'
         'Impulstest: Film-Explosionen, ploetzliche Lautstaerkespitzen\n'
         'Preset passwortgeschuetzt abspeichern\n'
         'Rechtsgrundlage: EU-RL 2003/10/EG, Laermschutz 85dBA TWA'
     )},
    {'parent': 271, 'name': 'Abnahmetest mit Mutter - Raumlautsprecher',
     'stage': stage_planung, 'hours': 0.5,
     'desc': (
         'Stufenlos Fostex PC-1e testen (Vollbereich)\n'
         'Sicher: Mutter-Regelung beeinflusst CI/HG NICHT\n'
         'Bedienungseinweisung fuer Mutter\n'
         'Unterschrift Abnahmeprotokoll Teil A'
     )},
    {'parent': 271, 'name': 'Abnahmetest mit Vater - CI und HG synchron (bimodal)',
     'stage': stage_planung, 'hours': 1.0,
     'desc': (
         'TV-Ton ueber CI und HG gleichzeitig testen\n'
         'Alois: Echo? Phasenfehler? Verstaendlichkeit?\n'
         'Feinjustage Delay + EQ nach subjektivem Hoerurteil\n'
         'Test: Nachrichten, Film, Musik\n'
         'iPhone-App Lautstaerkeregelung CI/HG testen\n'
         'Unterschrift Abnahmeprotokoll Teil B'
     )},
    {'parent': None, 'name': 'Kassenantrag erstellen (SGB XI §40 / SGB V §33)',
     'stage': kasse_stage_id, 'hours': 1.0,
     'desc': (
         'Abnahmeprotokoll:\n'
         '- Systembeschreibung + Signalflussplan (DSP-Routing)\n'
         '- Gemessene Latenzwerte + Delay-Korrektur\n'
         '- Pegel-Kalibrierungsprotokoll (max. Ausgangspegel)\n'
         '- Unterschriften: Alois Prinz, Mutter, FraWo GbR\n\n'
         'Kassenantrag:\n'
         '- Qualifikationsnachweis FraWo (Fachkraft Veranstaltungstechnik)\n'
         '- Kostenvoranschlag aus Odoo als PDF\n'
         '- Fotos der Installation\n'
         '- In Odoo als Anhang hinterlegen'
     )},
    {'parent': None, 'name': 'Kostenvoranschlag / Angebot in Odoo erstellen',
     'stage': kasse_stage_id, 'hours': 0.5,
     'desc': (
         'Odoo Verkauf -> Angebot erstellen:\n'
         'Hardware: HW-DSP-4X4, HW-SPK-ERIS35, HW-EXT-SWIS, HW-ACC-VOL\n'
         'Kabel: HW-CAB-PHOEN1 (2x), HW-CAB-PHOEN2 (2x), HW-CAB-TOS, HW-NET-SW8\n'
         'Services: SRV-INSTALL (3h), SRV-DSP-PROG (Festpreis), SRV-SEN-EINW\n'
         'Als PDF exportieren fuer Kasseneinreichung'
     )},
]

for t in subtasks:
    existing = search_read('project.task',
        [['name', '=', t['name']], ['project_id', '=', proj_id]], ['id'])
    if existing:
        print(f'  Exists: {t["name"][:55]}')
        continue
    vals = {
        'name': t['name'],
        'project_id': proj_id,
        'stage_id': t['stage'],
        'description': t['desc'],
        'allocated_hours': t['hours'],
    }
    if t['parent']:
        vals['parent_id'] = t['parent']
    tid = create('project.task', vals)
    print(f'  Created: {t["name"][:55]} (id={tid})')

print('\n4. Creating product catalog (Medizintechnik)...')
cats = search_read('product.category', [['name', 'like', 'Medizin']], ['id'])
if cats:
    cat_id = cats[0]['id']
else:
    parent = search_read('product.category', [['name', '=', 'All']], ['id'])
    cat_id = create('product.category', {
        'name': 'Medizintechnik & Assistenzsysteme',
        'parent_id': parent[0]['id'] if parent else False,
    })

all_products = [
    {'code': 'HW-DSP-4X4', 'name': 't.racks 4x4 DSP Pro', 'type': 'consu',
     'cost': 116.81, 'price': 139.00, 'buy': True,
     'desc': '4-Kanal DSP, Euroblock-Klemmen, param. EQ + Delay + Limiter pro Kanal, USB-Programmierung.'},
    {'code': 'HW-SPK-ERIS35', 'name': 'PreSonus Eris 3.5 Paar', 'type': 'consu',
     'cost': 83.19, 'price': 99.00, 'buy': True,
     'desc': 'Aktive Studio-Monitore 2-Wege 25W. XLR/TRS Input. Raumlautsprecher Mutter.'},
    {'code': 'HW-EXT-SWIS', 'name': 'Swissonic Audio Extractor', 'type': 'consu',
     'cost': 41.18, 'price': 49.00, 'buy': True,
     'desc': 'D/A-Wandler Toslink zu Stereo-RCA. Ausgabepegel fest. PCM-Stereo.'},
    {'code': 'HW-ACC-VOL', 'name': 'Fostex PC-1e Passivregler schwarz', 'type': 'consu',
     'cost': 24.37, 'price': 29.00, 'buy': True,
     'desc': 'Passiver Tisch-Lautstaerkeregler Klinke Stereo In/Out. Bedienregler Mutter.'},
    {'code': 'HW-CAB-PHOEN1', 'name': 'Kabel Euroblock auf XLR-Male 0,5m', 'type': 'consu',
     'cost': 8.40, 'price': 15.00, 'buy': False,
     'desc': 'Eigenbau FraWo. DSP Out zu Transmitter. Sym auf Unsym (Cold frei).'},
    {'code': 'HW-CAB-PHOEN2', 'name': 'Kabel Euroblock auf RCA-Female 0,5m', 'type': 'consu',
     'cost': 8.40, 'price': 15.00, 'buy': False,
     'desc': 'Eigenbau FraWo. DSP Out zu PreSonus. Sym auf Unsym mit Massbruecke.'},
    {'code': 'HW-CAB-TOS', 'name': 'Toslink-Kabel 1,5m', 'type': 'consu',
     'cost': 0.00, 'price': 9.90, 'buy': True,
     'desc': 'Lichtwellenleiter. TV Optical Out zu Swissonic Extractor.'},
    {'code': 'HW-NET-SW8', 'name': 'Managed PoE Switch 8-Port', 'type': 'consu',
     'cost': 0.00, 'price': 79.00, 'buy': True,
     'desc': 'IGMP Snooping v2/v3, QoS. Netzwerktrennung Magenta TV Box.'},
    {'code': 'SRV-INSTALL', 'name': 'Systeminstallation vor Ort', 'type': 'service',
     'cost': 85.00, 'price': 85.00, 'buy': False,
     'desc': 'Physische Montage, Kabelverlegung, Signalfluss. Stundensatz 85 EUR netto.'},
    {'code': 'SRV-DSP-PROG', 'name': 'DSP-Programmierung & bimodale Einmessung', 'type': 'service',
     'cost': 95.00, 'price': 95.00, 'buy': False,
     'desc': 'FFT-Latenzmessung CI/HG (REW/Smaart), EQ, Delay-Kalibrierung, Limiter (Gehoerschutz).'},
    {'code': 'SRV-SEN-EINW', 'name': 'Einweisung & App-Konfiguration Senior', 'type': 'service',
     'cost': 80.00, 'price': 80.00, 'buy': False,
     'desc': 'Seniorengerechte Uebergabe, iPhone-App CI/HG, Abnahmeprotokoll Pflegekasse.'},
]

for p in all_products:
    existing = search_read('product.template', [['default_code', '=', p['code']]], ['id'])
    if existing:
        print(f'  Exists: {p["code"]}')
        continue
    pid = create('product.template', {
        'name': p['name'],
        'default_code': p['code'],
        'categ_id': cat_id,
        'type': p['type'],
        'standard_price': p['cost'],
        'list_price': p['price'],
        'description_sale': p['desc'],
        'purchase_ok': p['buy'],
        'sale_ok': True,
    })
    print(f'  Created: {p["code"]} {p["name"]} (id={pid})')

print('\nFERTIG!')
print('Projekt: http://10.1.0.112:8069/odoo/project')
print('Produkte: http://10.1.0.112:8069/odoo/inventory/products')
