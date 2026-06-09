#!/usr/bin/env python3
"""Lege frawo.tech Migration Tasks in Odoo an — ausführen wenn Odoo wieder oben."""
import xmlrpc.client, sys
sys.stdout.reconfigure(encoding='utf-8')
url='https://frawo-tech.de'; db='FraWo_GbR'
uid=6; pw='FrawoWolf2026!'
m = xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')

tasks = [
    {
        'name': '[EPIC] frawo.tech — Finale Domain Migration',
        'priority': '1',
        'description': '<h2>frawo.tech — Finale Domain</h2><p>Siehe /tmp/FraWo/SSOT/FRAWO_TECH_MIGRATION.md für vollständigen Plan.</p><p>Subdomains: frawo.tech, cloud.frawo.tech, funk.frawo.tech, navidrome.frawo.tech, status.frawo.tech, vault.frawo.tech</p><p>Email: wolf@frawo.tech, agent@frawo.tech, info@frawo.tech</p>'
    },
    {
        'name': '[M1 🐺] frawo.tech: Nameserver auf Cloudflare + Zone anlegen',
        'stage': 'planning',
        'description': '<h3>Wolf manuell</h3><ol><li>Registrar: NS auf aria.ns.cloudflare.com + bolt.ns.cloudflare.com setzen</li><li>Cloudflare: dash.cloudflare.com → Add Site → frawo.tech</li><li>SSL: Full (strict)</li></ol><p><b>Blockiert alle weiteren Phasen!</b></p>'
    },
    {
        'name': '[M2 🤖] frawo.tech: Cloudflare Tunnel Routes + Caddy VHosts',
        'stage': 'brainstorm',
        'description': '<h3>Agent-Task (nach M1)</h3><p>pct exec 100 -- cloudflared tunnel route dns TUNNEL-ID frawo.tech (+ alle Subdomains)</p><p>Caddy neue VHosts für frawo.tech anlegen</p>'
    },
    {
        'name': '[M3 🤖] frawo.tech: Odoo + Nextcloud + AzuraCast umkonfigurieren',
        'stage': 'brainstorm',
        'description': '<h3>Agent-Task (nach M2)</h3><p>Odoo: proxy_mode, Website-Domain, Email-Alias-Domain</p><p>Nextcloud: trusted_domains, overwrite.cli.url</p><p>AzuraCast: Station-URL, Icecast hostname</p><p>n8n: alle Workflow-URLs updaten</p>'
    },
    {
        'name': '[M4 🤖+🐺] frawo.tech: Email SPF/DKIM/DMARC + Cloudflare Email Routing',
        'stage': 'brainstorm',
        'description': '<h3>Wolf: Cloudflare Email Routing aktivieren</h3><p>wolf@frawo.tech → w.prinz1101@gmail.com, *@frawo.tech catch-all</p><h3>Agent: DNS Records prüfen, Odoo SMTP updaten</h3>'
    },
    {
        'name': '[M5 🤖] frawo.tech: Parallelbetrieb + vollständige Test-Checklist',
        'stage': 'brainstorm',
        'description': '<h3>Agent-Task (nach M3+M4)</h3><p>Alle Dienste auf frawo.tech testen: Odoo, Nextcloud, Radio, Email, SSL A+, Mobile, AzuraCast Streams</p>'
    },
    {
        'name': '[M6 🤖+🐺] frawo.tech: Go-Live Cutover + frawo-tech.de → Redirect',
        'stage': 'brainstorm',
        'description': '<h3>Letzter Schritt</h3><p>Odoo primär auf frawo.tech, Caddy 301 Redirects für frawo-tech.de, DJ-Accounts informieren, yourparty.tech kündigen</p>'
    },
]

stage_map = {'planning': 2, 'brainstorm': 86, 'in_progress': 3}

for i, t in enumerate(tasks):
    stage = stage_map.get(t.get('stage', 'brainstorm'), 86)
    tid = m.execute_kw(db,uid,pw,'project.task','create',[{
        'name': t['name'],
        'project_id': 1,
        'stage_id': stage,
        'priority': t.get('priority', '0'),
        'description': t['description'],
        'tag_ids': [(4, 5)]
    }])
    print(f'T{tid}: {t["name"][:60]}')

print('Alle Tasks angelegt!')
