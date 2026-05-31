$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

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
}
"@

# Homepage Template with inlined CSS for guaranteed application
$homeHtml = @"
<div class="fw-homepage">
    <style>
        $cssContent
    </style>
    <section class="fw-hero oe_structure">
        <div class="fw-container">
            <span class="fw-eyebrow">FraWo Smart Media &amp; Event</span>
            <h1 class="fw-h1">Ton, Licht und<br/>gute Stimmung.</h1>
            <p class="fw-lead">Egal ob runder Geburtstag oder Gartenparty: Wir bringen die Technik, die deinen Abend unvergesslich macht. Hochzeiten auf Anfrage.</p>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
                <a href="/contactus" class="fw-btn">Projekt anfragen</a>
                <a href="/b2b" class="fw-btn fw-btn-outline">B2B Bereich</a>
            </div>
        </div>
    </section>
    
    <div id="editable_area" class="oe_structure">
        <section class="fw-section">
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
                        <h3 class="fw-h3">B2B &amp; Festivals</h3>
                        <p>FachkrÃ¤fte fÃ¼r Veranstaltungstechnik, FOH, BÃ¼hnenbau und das FuÃŸball-Dart-Rental.</p>
                    </div>
                </div>
            </div>
        </section>
    </div>
</div>
"@

$homeJson = @{ en_US = $homeHtml; de_DE = $homeHtml } | ConvertTo-Json -Compress -Depth 5

$sql = @"
set client_encoding to 'utf8';
begin;
update ir_ui_view
set arch_db = '$($homeJson.Replace("'", "''"))'::jsonb
where key = 'website.homepage';
commit;
"@

$sqlBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sql))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$sqlBase64" | base64 -d > /tmp/deploy_v3_final.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T db psql -U odoo -d FraWo_GbR < /tmp/deploy_v3_final.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Deploying v3 Design (UTF-8) with inlined CSS..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Design deployed."
