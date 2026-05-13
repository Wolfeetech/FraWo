# 🎯 Was als Nächstes? - Action Menu

**Status:** Multi-AI Setup ✅ + Odoo SSOT ✅ = READY!

---

## 🔥 SOFORT-AKTIONEN (Höchste Priorität)

### 1. **Website Legal Compliance** 🚨 DSGVO-PFLICHT!
```
Odoo Task IDs: 135, 136
Dauer: ~2 Stunden
```

**Warum jetzt?**
- www.frawo-tech.de ist LIVE ohne Impressum/Datenschutz
- DSGVO-Verstoß: Bis zu €20M Strafe möglich
- Abmahnrisiko sehr hoch

**Action:**
```bash
# Option A: Automatisch generieren
cd OneDrive/Dokumente/GitHub/FraWo
python scripts/generate_legal_pages.py  # TODO: Script erstellen

# Option B: Manuell in Odoo
# - Odoo öffnen: http://10.1.0.22:8069
# - Website Editor
# - Impressum + Datenschutz Seiten erstellen
```

---

### 2. **Stockenweiler Memory Crisis** 🚨 KRITISCH!
```
Status: Swap 99% (7.9Gi/8.0Gi)
Betroffene Services: PBS, n8n, Vaultwarden, AdGuard
Dauer: ~30 Minuten
```

**Warum jetzt?**
- System kurz vor OOM (Out of Memory)
- Services können crashen
- Backup-Server (PBS) gefährdet

**Action:**
```bash
# 1. Verbinden
ssh root@100.91.20.116

# 2. Status prüfen
free -h
htop

# 3. Services rightsizen
pct config 109  # PBS - RAM reduzieren?
pct config 110  # n8n - RAM reduzieren?
```

---

### 3. **Website SEO Basics** 🎯 Quick Wins
```
Odoo Task IDs: 132, 133, 134
Dauer: ~1 Stunde
```

**Warum jetzt?**
- Einfach zu fixen
- Große SEO-Wirkung
- Google indexiert gerade

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
# Meta Tags + OG Tags + H2 Struktur
python scripts/website_seo_boost.py
```

---

## 💡 HEUTE MÖGLICH (Mittlere Priorität)

### 4. **Radio Player Integration**
```
Odoo Task ID: 140
Dauer: ~2-3 Stunden
```

**Features:**
- Sticky Footer Player
- AzuraCast API Integration
- Now Playing Info
- Live-Stream Link

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo/apps/radio-player-frontend
# Frontend verbessern
# In Website integrieren
```

---

### 5. **Git Sync nachholen**
```
Status: 9 Commits hinter origin/main
Dauer: 5 Minuten
```

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
git pull
git log --oneline -10
```

---

### 6. **Codex Session Parser** (AI-Integration erweitern)
```
Für: Codex → Odoo Sync
Dauer: ~1 Stunde
```

**Ziel:** Codex Sessions automatisch in Odoo Tasks umwandeln

**Action:**
```python
# .ai-tools-shared/odoo_ai_sync.py erweitern
def sync_codex_activity():
    # Parse .codex/sessions/*.json
    # Extract task descriptions
    # Create Odoo tasks
```

---

## 📅 DIESE WOCHE (Geplant)

### 7. **Lane C: Security Baseline**
```
Aus MASTERPLAN Lane C
Dauer: Mehrere Tage
```

**Tasks:**
- PBS Restore-Drill
- Firewall VM 210/220 testen
- NFS/RPC Exposure begrenzen
- UniFi/Tailscale Split-DNS

---

### 8. **Lane E: Radio Migration**
```
Aus MASTERPLAN Lane E
Dauer: ~1 Tag
```

**Tasks:**
- AzuraCast Stockenweiler → Anker
- Media-Library Sync (Tailscale)
- Icecast Relay Setup
- Odoo CRM Integration

---

## 🔮 SPÄTER (Backlog)

### 9. **Bidirektionaler Odoo Sync**
```
Odoo → MASTERPLAN → Git
```

**Ziel:** Änderungen in Odoo zurück ins Git schreiben

---

### 10. **Website Performance**
```
Odoo Task IDs: 137, 138, 139
```

**Tasks:**
- JSON-LD Structured Data
- Gzip/Brotli Compression
- Bilder-Optimierung (WebP)

---

## 🎲 ODER ETWAS GANZ ANDERES?

### Optionen:
- 📊 Odoo Dashboard anschauen (Tasks durchgehen)
- 🔧 Andere Lane aus MASTERPLAN angehen
- 🐛 Bugs/Issues fixen
- 📚 Dokumentation verbessern
- 🧪 Neue Features testen
- 💬 Fragen klären

---

## 🚀 EMPFEHLUNG: TOP 3

**Meine Empfehlung für JETZT:**

1. **🔥 Website Legal Compliance** (DSGVO!)
   - KRITISCH und schnell umsetzbar
   - Impressum + Datenschutz generieren

2. **🔥 Stockenweiler Memory Fix** (System-Stabilität!)
   - Kritischer System-Status
   - PBS/n8n RAM reduzieren

3. **💡 Website SEO Quick Wins** (Traffic!)
   - Einfach + große Wirkung
   - Meta Tags + OG Tags + H2

---

**Was möchten Sie angehen? Einfach Nummer sagen (1-10) oder etwas Eigenes! 🎯**
