# Verleih-Seite umbauen (Wolf 05.10.2026: „Ja, alles umsetzen“). Arbeitet auf der Live-Fassung.
import re, sys
src = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n')
s = src
def ersetze(alt, neu, anzahl=1):
    global s
    n = s.count(alt)
    if n != anzahl:
        sys.exit(f'ABBRUCH: "{alt[:60]}" kommt {n}x vor, erwartet {anzahl}')
    s = s.replace(alt, neu)

# 1) Buchungsknoepfe auf die richtigen Odoo-Artikel
ersetze("openRentalModal('FW-027', '5m Riesen-Fußballdart Event-Modul')", "openRentalModal('VER-005', '5m Riesen-Fußballdart Event-Modul')")
ersetze("openRentalModal('RENT-LIGHT-SET', 'Licht-Set »Pro Show«')", "openRentalModal('RENT-LIGHT-01', 'Licht-Set »Pro Show«')")
ersetze("openRentalModal('RENT-LIGHT-SET', 'Showtec Shark Spot Moving Head')", "openRentalModal('VT-LIC-02', 'Showtec Shark Spot Moving Head')")
ersetze("openRentalModal('RENT-PA-COMPACT', 'JBL EON 615 Aktivbox')", "openRentalModal('VT-TON-01', 'JBL EON 615 Aktivbox')")
ersetze("openRentalModal('SRV-ANFAHRT', 'PKW-Anhänger 750kg Transport')", "openRentalModal('VT-TRP-01', 'PKW-Anhänger 750kg Transport')")

# 2) Fussballdart 250 EUR (Wolf: bleibt 250), Wochenende wie ueberall 1,5-fach
ersetze('<div class="fw-price-large">180 € <span', '<div class="fw-price-large">250 € <span')
ersetze('TAGESSATZ (24H): 180 € · GANZES WOCHENENDE (FR–MO): 270 €', 'TAGESSATZ (24H): 250 € · GANZES WOCHENENDE (FR–MO): 375 €')

# 3) Club & Open-Air: auf Anfrage statt sofort verfuegbar (Status-Tag direkt nach dem Bild dieser Karte)
m = re.search(r'(<!-- Item 02: Sound-System »Club & Open-Air« -->.*?)<div class="fw-card-status-tag"><span style="font-size: 8px;">●</span> SOFORT VERFÜGBAR</div>', s, re.S)
if not m: sys.exit('ABBRUCH: Club-Statusfeld nicht gefunden')
s = s[:m.end(1)] + '<div class="fw-card-status-tag" style="color:#f59e0b;"><span style="font-size: 8px;">●</span> AUF ANFRAGE</div>' + s[m.end():]

# 4) Techniker-Option: kein 110-EUR-Lockpreis mehr, Verweis auf Pakete mit Betreuung
ersetze('<span>Aufbau &amp; Soundcheck durch FraWo-Techniker <strong>(+110 €)</strong></span>',
        '<span>Techniker vor Ort gewünscht – Aufbau, Betreuung, Abbau <strong>(Preis nach Aufwand, siehe Pakete S/M/L)</strong></span>')

# 5) Hero-Text + neuer Bereich „Technik mit Betreuung“ vor der Filterleiste
ersetze('Vorkonfektionierte Ton-, Licht- und Event-Sets für Konzerte, Clubs, Hochzeiten und Vereinsfeste. Geprüfte Markenhardware, DSP-Limiter und 24h-Bereitstellung ab Lager Weißensberg.',
        'Technik mit Betreuung – wir bringen, bauen auf, betreuen und bauen ab. Oder zum Selbstabholen: geprüfte Ton-, Licht- und Event-Sets ab Lager Weißensberg.')

def karte(code, titel, gaeste, preis, punkte):
    li = ''.join(f'<li>{p}</li>' for p in punkte)
    return f'''        <div class="fw-svc-card">
          <div class="fw-svc-tag">{gaeste}</div>
          <h3 class="fw-svc-title">{titel}</h3>
          <ul class="fw-svc-list">{li}</ul>
          <div class="fw-svc-price">ab {preis} €</div>
          <button type="button" class="fw-btn-book" style="cursor:pointer; width:100%;" onclick="openRentalModal('{code}', '{titel}')">⚡ Paket anfragen →</button>
        </div>
'''
bereich = '''    <!-- Technik mit Betreuung: Pakete S/M/L (Wolf 05.10.2026) -->
    <style>
      .fw-svc { padding: 50px 20px 30px; border-bottom: 1px solid var(--fw-border); }
      .fw-svc-head { text-align:center; margin-bottom: 28px; }
      .fw-svc-head h2 { font-size: clamp(1.5rem, 3vw, 2.2rem); font-weight: 800; text-transform: uppercase; color: var(--fw-text-bright); margin-bottom: 8px; }
      .fw-svc-head p { color: var(--fw-text-mid); max-width: 720px; margin: 0 auto; }
      .fw-svc-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; max-width: 1100px; margin: 0 auto; }
      .fw-svc-card { background: var(--fw-card); border: 1px solid var(--fw-card-border); padding: 22px; display:flex; flex-direction:column; }
      .fw-svc-tag { display:inline-block; align-self:flex-start; background: var(--fw-primary); color:#fff; font-size: 0.72rem; font-weight:700; letter-spacing: 0.1em; text-transform: uppercase; padding: 4px 10px; margin-bottom: 12px; }
      .fw-svc-title { font-size: 1.15rem; font-weight: 800; color: var(--fw-text-bright); margin-bottom: 10px; }
      .fw-svc-list { color: var(--fw-text-mid); font-size: 0.9rem; padding-left: 18px; margin-bottom: 16px; flex:1; }
      .fw-svc-list li { margin-bottom: 4px; }
      .fw-svc-price { font-size: 1.6rem; font-weight: 800; color: var(--fw-text-bright); margin-bottom: 12px; }
      .fw-svc-note { text-align:center; color: var(--fw-text-muted); font-size: 0.8rem; margin-top: 18px; }
    </style>
    <section class="fw-svc">
      <div class="fw-svc-head">
        <h2>Technik mit Betreuung</h2>
        <p>Ihr feiert, wir kümmern uns: Anlieferung, Aufbau, Betreuung während der Veranstaltung und Abbau durch unsere Fachkraft für Veranstaltungstechnik. Anfahrt bis 30 km inklusive.</p>
      </div>
      <div class="fw-svc-grid">
''' + karte('PAKET-S', 'Paket S · Hoffest &amp; Vereinsabend', 'bis 100 Personen', 449,
            ['2 aktive Lautsprecher, Mischpult, Funkmikrofon', '4 LED-Scheinwerfer', 'Techniker: Aufbau, bis 6 h Betreuung, Abbau']) \
    + karte('PAKET-M', 'Paket M · Fest &amp; Feier', 'bis 250 Personen', 890,
            ['PA mit Tops und Doppel-12″-Bass, Mischpult, 2 Funkmikrofone', 'Licht: 4 LED-Scheinwerfer, 2 Moving Heads, Lichtsteuerung', 'Fachkraft: Aufbau, bis 10 h Betreuung, Abbau']) \
    + karte('PAKET-L', 'Paket L · Open Air &amp; Event', 'bis 500 Personen', 1490,
            ['wie Paket M, mit zusätzlichem Bass und erweitertem Licht', 'Fachkraft plus Helfer', 'genaue Zusammenstellung nach Absprache']) + '''      </div>
      <p class="fw-svc-note">Endpreise – gemäß §19 UStG wird keine Umsatzsteuer berechnet. Darunter: Equipment zum Selbstabholen.</p>
    </section>

'''
ersetze('    <!-- Sticky Filter Controls -->', bereich + '    <!-- Sticky Filter Controls -->')
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(s)
print('ok', len(src), '->', len(s))
