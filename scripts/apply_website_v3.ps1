$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$WebsiteHost = "www.frawo-tech.de"
$WebsiteTitle = "FraWo"

$cssContent = @"
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');

:root {
  --fw-bg: #0a0a0a;
  --fw-surface: #141414;
  --fw-text: #f0f0ee;
  --fw-text-2: #a0a09e;
  --fw-accent: #ff6b1a;
  --fw-border: #2a2a2a;
}

body, #wrapwrap {
    background-color: var(--fw-bg) !important;
    color: var(--fw-text) !important;
    font-family: 'Inter', sans-serif !important;
}

#wrap {
    background-color: var(--fw-bg) !important;
}

header#top, footer {
    background-color: var(--fw-bg) !important;
    border-color: var(--fw-border) !important;
    color: var(--fw-text) !important;
}

.fw-section {
    padding: 100px 0;
    border-bottom: 1px solid var(--fw-border);
}
.fw-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
}
.fw-hero {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-bottom: 1px solid var(--fw-border);
    background: var(--fw-bg);
}
.fw-eyebrow {
    color: var(--fw-accent);
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    display: block;
    font-size: 0.9rem;
}
.fw-h1 {
    font-size: clamp(3.5rem, 8vw, 6rem);
    font-weight: 900;
    line-height: 1.0;
    margin-bottom: 2rem;
    letter-spacing: -0.03em;
    color: var(--fw-text);
}
.fw-h2 {
    font-size: clamp(2rem, 5vw, 4rem);
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    color: var(--fw-text);
}
.fw-h3 {
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    color: var(--fw-text);
}
.fw-lead {
    font-size: 1.25rem;
    color: var(--fw-text-2);
    line-height: 1.6;
    max-width: 800px;
    margin-bottom: 3rem;
}
.fw-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--fw-text);
    color: var(--fw-bg) !important;
    padding: 16px 32px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-decoration: none !important;
    border: 2px solid var(--fw-text);
    transition: all 0.2s ease;
}
.fw-btn:hover {
    background: var(--fw-accent);
    border-color: var(--fw-accent);
    color: var(--fw-text) !important;
}
.fw-btn-outline {
    background: transparent;
    color: var(--fw-text) !important;
    border-color: var(--fw-border);
}
.fw-btn-outline:hover {
    background: var(--fw-surface);
    border-color: var(--fw-text);
}
.fw-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 40px;
}
.fw-card {
    background: var(--fw-surface);
    border: 1px solid var(--fw-border);
    padding: 40px;
    transition: border-color 0.2s ease;
}
.fw-card:hover {
    border-color: var(--fw-accent);
}
.fw-card p {
    color: var(--fw-text-2);
    line-height: 1.6;
}
.fw-img {
    width: 100%;
    height: 400px;
    object-fit: cover;
    border: 1px solid var(--fw-border);
    filter: grayscale(20%) contrast(120%);
}

.fw-b2b-teaser {
    background: var(--fw-surface);
    border-top: 1px solid var(--fw-border);
    padding: 80px 0;
    text-align: left;
}
.fw-b2b-teaser h2 {
    color: var(--fw-text);
}

.fw-player {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 70px;
    background: var(--fw-surface);
    border-top: 1px solid var(--fw-border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    z-index: 9999;
    gap: 20px;
    font-family: 'Inter', sans-serif;
}
.fw-player-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--fw-text);
}
.fw-player-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #555;
}
.fw-player-btn {
    background: none;
    border: 1px solid var(--fw-border);
    color: var(--fw-text-2);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: not-allowed;
}
.fw-player-info {
    flex-grow: 1;
    color: var(--fw-text-2);
    font-size: 0.9rem;
}
.fw-player-controls {
    display: flex;
    gap: 15px;
    align-items: center;
}
"@

$homepageXml = @"
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
<div class="fw-homepage">
    <style>
        $cssContent
    </style>
    <section class="fw-hero">
        <div class="fw-container">
            <span class="fw-eyebrow">FraWo Smart Media &amp; Event</span>
            <h1 class="fw-h1">Ton, Licht und<br/>gute Stimmung.</h1>
            <p class="fw-lead">
                Egal ob runder Geburtstag oder Gartenparty: Wir bringen die Technik, die deinen Abend unvergesslich macht. Hochzeiten auf Anfrage. Kein Stress, einfach feiern.
            </p>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
                <a href="/contactus" class="fw-btn">Projekt anfragen</a>
                <a href="#leistungen" class="fw-btn fw-btn-outline">Was wir machen</a>
            </div>
        </div>
    </section>

    <section id="leistungen" class="fw-section">
        <div class="fw-container">
            <span class="fw-eyebrow">Unsere Leistungen</span>
            <h2 class="fw-h2">Privat feiern,<br/>professionell klingen.</h2>
            <div class="fw-grid" style="margin-top: 60px;">
                <div class="fw-card">
                    <h3 class="fw-h3">Runde Geburtstage</h3>
                    <p>Fetter Sound und das richtige Licht fÃ¼r deine Party. Wir bauen auf, stellen ein und holen alles wieder ab.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Gartenpartys</h3>
                    <p>Outdoor-taugliche Beschallung und stimmungsvolle Beleuchtung fÃ¼r die perfekte Sommernacht.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Hochzeiten</h3>
                    <p>Auf spezielle Anfrage begleiten wir auch Hochzeiten mit Technik, die nicht im Weg steht, sondern unterstÃ¼tzt.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="fw-section" style="padding-top:0; border:none;">
        <div class="fw-container">
             <img src="/web/image/858" class="fw-img" alt="FraWo Eventtechnik" />
        </div>
    </section>

    <section class="fw-b2b-teaser">
        <div class="fw-container" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:40px;">
            <div style="max-width: 600px;">
                <span class="fw-eyebrow">GeschÃ¤ftskunden &amp; Veranstalter</span>
                <h2 class="fw-h2" style="margin-bottom: 1rem;">Professionelle Eventtechnik &amp; Dienstleistung</h2>
                <p class="fw-lead" style="margin-bottom: 0;">
                    FachkrÃ¤fte fÃ¼r Veranstaltungstechnik, FOH, BÃ¼hnenbau und unser Bestseller: Das FuÃŸball-Dart-Rental.
                </p>
            </div>
            <div>
                <a href="/b2b" class="fw-btn">Zum B2B Bereich</a>
            </div>
        </div>
    </section>
</div>
        </div>
    </t>
</t>
"@

$b2bXml = @"
<t name="B2B" t-name="website.frawo_b2b">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
<div class="fw-b2b-page">
    <style>
        $cssContent
    </style>
    <section class="fw-hero" style="min-height: 60vh;">
        <div class="fw-container">
            <span class="fw-eyebrow">B2B &amp; Veranstalter</span>
            <h1 class="fw-h1">VerlÃ¤ssliche Technik.<br/>Klarer Ablauf.</h1>
            <p class="fw-lead">
                Wir unterstÃ¼tzen Festivals, Konferenzen und Open Airs mit Fachpersonal, Material und Sonderbauten. 
            </p>
            <a href="/contactus" class="fw-btn">Anfrage senden</a>
        </div>
    </section>

    <section class="fw-section">
        <div class="fw-container">
            <h2 class="fw-h2" style="margin-bottom: 60px;">Unsere B2B Leistungen</h2>
            <div class="fw-grid">
                <div class="fw-card" style="border-color: var(--fw-accent);">
                    <span class="fw-eyebrow">Bestseller</span>
                    <h3 class="fw-h3">FuÃŸball-Dart-Rental</h3>
                    <p>Der Publikumsmagnet fÃ¼r Firmenfeiern, Festivals und Fan-Zones. Komplett-Miete inklusive Aufbau und Betreuung.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">FOH &amp; Monitor</h3>
                    <p>PrÃ¤ziser Mix am Front of House und auf der BÃ¼hne. Erfahrene Techniker fÃ¼r den perfekten Sound.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Licht &amp; Medien</h3>
                    <p>Konferenz- und Eventtechnik. Vom Beamer-Setup bis zur komplexen Lichtshow fÃ¼r PrÃ¤sentationen.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Fachpersonal</h3>
                    <p>Fachkraft fÃ¼r Veranstaltungstechnik, Stage Helfer fÃ¼r Open Airs und Festivals. Wir packen an und leiten an.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Sonderbauten (Holz)</h3>
                    <p>Spezialanfertigungen fÃ¼r BÃ¼hne und Event vom Fachmann (Zimmermann). MaÃŸgeschneidert und solide.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="fw-section" style="padding-top:0;">
        <div class="fw-container">
             <img src="/web/image/859" class="fw-img" alt="FraWo B2B Eventtechnik" />
        </div>
    </section>
</div>
        </div>
    </t>
</t>
"@

$contactXml = @"
<t name="Contact us" t-name="website.contactus">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
<div class="fw-contact-page">
    <style>
        $cssContent
    </style>
    <section class="fw-hero" style="min-height: 70vh;">
        <div class="fw-container">
            <span class="fw-eyebrow">Kontakt</span>
            <h1 class="fw-h1">Lass uns reden.</h1>
            <p class="fw-lead">
                Egal ob privates Fest oder groÃŸes Festival: Ruf uns an oder schreib eine Mail. Wir kÃ¼mmern uns.
            </p>
            <div class="fw-grid" style="margin-top: 60px;">
                <div class="fw-card">
                    <span class="fw-eyebrow">E-Mail</span>
                    <a href="mailto:info@frawo-tech.de" class="fw-h3" style="text-decoration:none; display:block; margin-bottom:10px;">info@frawo-tech.de</a>
                    <p>FÃ¼r Anfragen, Details und Planung.</p>
                </div>
                <div class="fw-card">
                    <span class="fw-eyebrow">Telefon</span>
                    <a href="tel:+4915155243164" class="fw-h3" style="text-decoration:none; display:block; margin-bottom:10px;">+49 151 55243164</a>
                    <p>FÃ¼r direkte Fragen und schnelle Abstimmung.</p>
                </div>
                <div class="fw-card">
                    <span class="fw-eyebrow">Standort</span>
                    <h3 class="fw-h3" style="margin-bottom:10px;">FraWo GbR</h3>
                    <p>Rothkreuz 14<br/>88138 WeiÃŸensberg</p>
                </div>
            </div>
        </div>
    </section>
</div>
        </div>
    </t>
</t>
"@

$playerXml = @"
<data inherit_id="website.layout" name="FraWo Player Overlay" active="True">
    <xpath expr="//div[@id='wrapwrap']" position="inside">
<div class="fw-player">
  <style>
      $cssContent
  </style>
  <div class="fw-player-brand">
    <span class="fw-player-dot"></span>
    FraWo Funk
  </div>
  <button class="fw-player-btn">â–¶</button>
  <div class="fw-player-info">
    Stream offline â€” Coming soon
  </div>
  <div class="fw-player-controls">
    <span style="color:var(--fw-text-2);">ðŸ”ˆ</span>
    <input type="range" min="0" max="100" value="50" disabled="disabled" style="width: 80px; opacity: 0.5;"/>
    <button class="fw-player-btn" style="width:30px; height:30px; font-size:12px;">ðŸ‘</button>
    <button class="fw-player-btn" style="width:30px; height:30px; font-size:12px;">ðŸ‘Ž</button>
  </div>
</div>
    </xpath>
</data>
"@


$homeJson = @{ en_US = $homepageXml; de_DE = $homepageXml } | ConvertTo-Json -Compress -Depth 5
$b2bJson = @{ en_US = $b2bXml; de_DE = $b2bXml } | ConvertTo-Json -Compress -Depth 5
$contactJson = @{ en_US = $contactXml; de_DE = $contactXml } | ConvertTo-Json -Compress -Depth 5

$sql = @"
begin;

-- Update Homepage view
update ir_ui_view
set arch_db = `$JSON`$$homeJson`$JSON`$::jsonb
where key = 'website.homepage';

-- Update Contact view
update ir_ui_view
set arch_db = `$JSON`$$contactJson`$JSON`$::jsonb
where key = 'website.contactus';

-- B2B Page
-- Upsert the B2B view
DO `$$
DECLARE
    v_id integer;
BEGIN
    SELECT id INTO v_id FROM ir_ui_view WHERE key = 'website.frawo_b2b';
    IF v_id IS NULL THEN
        INSERT INTO ir_ui_view (name, type, key, mode, arch_db)
        VALUES ('B2B', 'qweb', 'website.frawo_b2b', 'primary', `$JSON`$$b2bJson`$JSON`$::jsonb)
        RETURNING id INTO v_id;
        
        INSERT INTO website_page (url, view_id, is_published, website_indexed)
        VALUES ('/b2b', v_id, true, true);
    ELSE
        UPDATE ir_ui_view SET arch_db = `$JSON`$$b2bJson`$JSON`$::jsonb WHERE id = v_id;
    END IF;
END;
`$$;

-- Player Skeleton
DO `$$
DECLARE
    v_id integer;
    layout_id integer;
BEGIN
    SELECT id INTO layout_id FROM ir_ui_view WHERE key = 'website.layout' LIMIT 1;
    SELECT id INTO v_id FROM ir_ui_view WHERE key = 'website.frawo_player_override';
    IF v_id IS NULL THEN
        INSERT INTO ir_ui_view (name, type, key, mode, inherit_id, arch_db, active)
        VALUES ('FraWo Player Overlay', 'qweb', 'website.frawo_player_override', 'extension', layout_id, '$($playerXml.Replace("'", "''"))', true);
    ELSE
        UPDATE ir_ui_view SET arch_db = '$($playerXml.Replace("'", "''"))' WHERE id = v_id;
    END IF;
END;
`$$;

commit;
"@

$sqlBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($sql))

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/frawo_site_v3.sql").write_bytes(base64.b64decode("$sqlBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T db psql -U odoo -d FraWo_GbR < /tmp/frawo_site_v3.sql
docker-compose restart web'
"@

Write-Host "Deploying v3 Website via SQL..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Deployment complete."
