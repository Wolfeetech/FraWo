# frawo.tech — Domain Migration Plan

**Status:** In Planung | **Erstellt:** 2026-06-02 | **Priorität:** HOCH

## Domains-Übersicht

| Domain | Status | Rolle |
|--------|--------|-------|
| `yourparty.tech` | ⚠️ Auslaufmodell | Kein aktiver Betrieb mehr |
| `frawo-tech.de` | ✅ Aktiv/Prod | Aktuelle Produktions-Domain (Generalprobe) |
| `frawo.tech` | 🆕 **GESICHERT!** | **FINALE Domain — Migrations-Ziel** |

## Zielarchitektur frawo.tech

| Subdomain | Dienst | Backend |
|-----------|--------|---------|
| `frawo.tech` | Hauptwebsite + Odoo Portal | VM220 10.4.0.22:8069 |
| `cloud.frawo.tech` | Nextcloud | VM300 10.4.0.21 |
| `funk.frawo.tech` | FraWo Funk Radio | CT130 10.4.0.28 |
| `navidrome.frawo.tech` | Musik-Player | CT130 navidrome |
| `vault.frawo.tech` | Vaultwarden (optional) | CT120 10.4.0.26 |
| `status.frawo.tech` | Uptime Kuma | CT100 toolbox |

## Email-Adressen (neu @frawo.tech)

- `wolf@frawo.tech` → Weiterleitung → w.prinz1101@gmail.com
- `franz@frawo.tech` → Franz Bienert
- `agent@frawo.tech` → Odoo Catchall
- `info@frawo.tech` → Allgemein / Impressum

---

## Migrations-Phasen

### Phase 1 — DNS + Cloudflare (Wolf manuell)
**Voraussetzung für alles andere!**

1. **Registrar:** Nameserver auf Cloudflare umstellen
   ```
   aria.ns.cloudflare.com
   bolt.ns.cloudflare.com
   ```
2. **Cloudflare:** dash.cloudflare.com → "Add a Site" → `frawo.tech`
3. SSL/TLS Mode: **Full (strict)**
4. Warten auf Propagation (meist <1h)

**Prüfen:** `dig NS frawo.tech` → Cloudflare NS

---

### Phase 2 — Cloudflare Tunnel + Subdomains (Agent)
**Voraussetzung: Phase 1 done**

```bash
# Tunnel-ID ermitteln
pct exec 100 -- cloudflared tunnel list

# Routes anlegen
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> frawo.tech
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> cloud.frawo.tech
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> funk.frawo.tech
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> navidrome.frawo.tech
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> status.frawo.tech
pct exec 100 -- cloudflared tunnel route dns <TUNNEL-ID> vault.frawo.tech
```

**Caddy-Config in CT100 erweitern:**
Neue VHosts für alle frawo.tech Subdomains anlegen (analog frawo-tech.de)

---

### Phase 3 — Services umkonfigurieren (Agent)
**Voraussetzung: Phase 2 done**

**Odoo:**
```
# /etc/odoo/odoo.conf
proxy_mode = True
# In Odoo Einstellungen → Website-Domain: https://frawo.tech
# Technisch → E-Mail-Alias-Domain: frawo.tech
```

**Nextcloud:**
```php
// /var/www/html/config/config.php
'trusted_domains' => ['cloud.frawo.tech', 'cloud.frawo-tech.de'],
'overwrite.cli.url' => 'https://cloud.frawo.tech',
```

**AzuraCast:**
```
Station-URL → https://funk.frawo.tech
Icecast hostname → frawo.tech
```

**n8n Workflows:** Alle URLs auf frawo.tech updaten

**OpenClaw SOUL.md:** frawo.tech als primary eintragen

---

### Phase 4 — Email-Setup (Wolf + Agent)
**Cloudflare Email Routing:**

1. Cloudflare → frawo.tech → Email → Email Routing aktivieren
2. Weiterleitungen konfigurieren:
   - `wolf@frawo.tech` → w.prinz1101@gmail.com
   - `*@frawo.tech` → Catch-all (info@frawo.tech)

**DNS Records (automatisch von Cloudflare):**
```
MX  route1.mx.cloudflare.net  10
MX  route2.mx.cloudflare.net  50
TXT v=spf1 include:_spf.mx.cloudflare.net ~all
TXT _dmarc: v=DMARC1; p=quarantine; rua=mailto:wolf@frawo.tech
```

---

### Phase 5 — Parallelbetrieb testen (Agent)

**Test-Checklist:**
- [ ] https://frawo.tech → Odoo lädt
- [ ] https://cloud.frawo.tech → Nextcloud Login
- [ ] https://funk.frawo.tech → Radio Stream läuft
- [ ] https://navidrome.frawo.tech → Musik-Player
- [ ] wolf@frawo.tech → Email-Empfang
- [ ] SSL A+ auf ssllabs.com/ssltest/
- [ ] Mobile: alle URLs
- [ ] Odoo Login + Portal
- [ ] Nextcloud Mobile App
- [ ] AzuraCast Streamer BUTT-Config

---

### Phase 6 — Cutover / Go-Live (Agent + Wolf)
**Voraussetzung: Phase 5 alle Tests grün**

**Reihenfolge:**
1. Odoo: Website-Domain → frawo.tech (primär)
2. Caddy: frawo-tech.de → 301 Redirect auf frawo.tech
3. DJ-Accounts: neue Stream-URLs per Telegram kommunizieren
4. SOUL.md + n8n final updaten
5. Telegram Bot-Beschreibung aktualisieren

**Caddy Redirect-Config:**
```caddy
frawo-tech.de {
    redir https://frawo.tech{uri} permanent
}
cloud.frawo-tech.de {
    redir https://cloud.frawo.tech{uri} permanent  
}
funk.frawo-tech.de {
    redir https://funk.frawo.tech{uri} permanent
}
```

**Nach Cutover:**
- frawo-tech.de: 12 Monate Redirect, dann kündigen
- yourparty.tech: nach Cutover sofort kündigen

---

## Warum frawo.tech besser ist

| Aspekt | frawo-tech.de | frawo.tech |
|--------|---------------|------------|
| Merkbarkeit | OK | **Besser** (kürzer) |
| TLD | .de (regional) | **.tech** (passend zum Profil) |
| Email | @frawo-tech.de | **@frawo.tech** |
| Branding | Bindestrich | **Sauber** |
| GbR-Außenwirkung | OK | **Professioneller** |
| Kosten | ~10€/Jahr | ~15-20€/Jahr |

---

## Wann starten?

**Sofort (Wolf-Aktion):** Phase 1 DNS/Cloudflare  
**Dann Agent:** Phasen 2-6 autonom sobald CF Zone aktiv

**Geschätzte Gesamtdauer:** 1-2 Tage nach Phase 1
