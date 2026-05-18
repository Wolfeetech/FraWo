# FraWo Repository Cleanup Plan
**Datum**: 2026-04-30
**Ziel**: Chaos beseitigen, Struktur schaffen, nur Relevantes behalten

---

## 📊 AKTUELLE SITUATION

### Ordner-Statistik
| Folder | Files | Size (MB) | Subdirs | Status |
|--------|-------|-----------|---------|--------|
| apps | 579 | 23.24 | 85 | 🔴 GROSS - Review needed |
| artifacts | 441 | 2.11 | 184 | 🔴 VIELE Subdirs - Konsolidieren |
| scripts | 394 | 1.18 | 11 | 🔴 254 Files im Root! |
| lifeboat | 7 | 1.44 | 1 | ⚠️ Was ist das? |
| DOCS | 118 | 0.58 | 6 | ⚠️ Review needed |
| Codex | 36 | 0.50 | 2 | ✅ OK, aber prüfen |
| ansible | 91 | 0.21 | 24 | ⚠️ Review needed |
| assets | 13 | 0.68 | 3 | ✅ Scheint OK |
| brand_assets | 6 | 0.22 | 0 | ✅ OK |
| manifests | 23 | 0.11 | 14 | ⚠️ Review needed |
| scratch | 9 | 0.19 | 0 | 🔴 LÖSCHEN? |
| OPERATIONS | 21 | 0.10 | 0 | ⚠️ Review needed |
| deployment | 13 | 0.01 | 6 | ⚠️ vs deployments? |
| deployments | 7 | 0.00 | 2 | ⚠️ Doppelt? |
| infrastructure | 4 | 0.05 | 0 | ⚠️ Review needed |
| operator_snapshots | 3 | 0.11 | 1 | 🔴 Archivieren? |
| COMMUNICATION | 1 | 0.00 | 0 | ⚠️ Fast leer |
| SSOT | 2 | 0.00 | 1 | ⚠️ Fast leer |

**TOTAL**: 1768 Files, 30.76 MB, 340 Subdirs

---

## 🎯 CLEANUP-STRATEGIE

### Phase 1: `/scripts` Aufräumen (PRIORITÄT 1)
**Problem**: 254 Files im Root-Verzeichnis - völliges Chaos!

#### Kategorien identifiziert:
1. **Odoo/Business** (deploy_odoo_*, fix_odoo_*, sync_*_to_odoo.py)
2. **PBS/Proxmox** (pbs_*, proxmox_*)
3. **Stockenweiler** (stockenweiler_*)
4. **Toolbox/Media** (toolbox_*)
5. **Radio/Azuracast** (rpi_*, radio_*)
6. **Security/Access** (security_*, vaultwarden_*)
7. **Infrastructure** (haos_*, tailscale_*, networking_*)
8. **Audits/Gates** (*_audit.py, *_gate.py, *_check.*)
9. **Bootstrap/Setup** (bootstrap_*, install_*, prepare_*)
10. **Windows-specific** (*.ps1, *.cmd, *.bat)

#### Vorschlag: Verschieben nach `/scripts/<kategorie>/`
- `/scripts/business/` ✅ EXISTS
- `/scripts/remediations/` ✅ EXISTS
- `/scripts/archive/` ✅ EXISTS
- **NEU**: `/scripts/infrastructure/`
- **NEU**: `/scripts/media/`
- **NEU**: `/scripts/security/`
- **NEU**: `/scripts/audits/`
- **NEU**: `/scripts/bootstrap/`
- **NEU**: `/scripts/stockenweiler/`

#### Definitiv LÖSCHEN:
- `fix_db.sh` - generisch, veraltet
- `fix_nc.sh` - zu unspezifisch
- `pwd_reset.sql` - sicherheitsrelevant, nicht im Repo
- `fix_odoo_final.sql` - SQL direkt im Repo ist schlecht
- `210.fw`, `220.fw` - was ist das?
- `deploy_v3_5_final.ps1` - veraltet, neue Version deployed
- `deploy_fix_final.py` - veraltet
- `deploy_odoo_standalone.py` - veraltet
- Alle `*_final.sh` - "final" gibt's nicht in Software

---

### Phase 2: `/artifacts` Konsolidieren
**Problem**: 184 Subdirs, 441 Files - zu granular!

#### Vorschlag: Zusammenführen
Viele Ordner sind einzelne Audit-Reports. Diese sollten in:
- `/DOCS/audits/YYYY-MM/` verschoben werden
- Nur aktive Artefakte in `/artifacts/active/`
- Historische in `/artifacts/archive/YYYY/`

#### Kandidaten für Archivierung:
- `pbs_vm240_reconcile` - spezifische VM, vermutlich erledigt
- `public_edge_preview` - Preview, nicht Production
- `release_mvp_audit` - historisch
- `stress_tests` - in `/tests/` verschieben
- `temp` - 🔴 LÖSCHEN

---

### Phase 3: `/apps` Review
**Problem**: 579 Files, 23 MB - größter Ordner!

#### Analyse notwendig:
- `fayanet` - was ist das?
- `radio-player-frontend` - aktiv?
- `yourparty` - aktiv?

**Frage**: Gehören Apps ins Hauptrepo oder eigene Repos?

---

### Phase 4: Doppelte Ordner Mergen
**Problem**: `deployment` vs `deployments`

#### Vorschlag:
- Inhalt vergleichen
- In einen Ordner zusammenführen (vermutlich `deployment`)
- Anderen löschen

---

### Phase 5: Fast-leere Ordner
**Aktion**:
- `COMMUNICATION` (1 File) - Inhalt nach `/DOCS/` verschieben
- `SSOT` (2 Files) - Prüfen ob relevant, sonst nach `/DOCS/`
- `scratch` (9 Files) - 🔴 KOMPLETT LÖSCHEN (temp files)

---

### Phase 6: `/DOCS` Strukturieren
**Aktuell**: 118 Files, 6 Subdirs

#### Vorschlag:
- `/DOCS/audits/` - alle Audit-Reports
- `/DOCS/plans/` ✅ EXISTS
- `/DOCS/reports/` - alle Reports
- `/DOCS/archive/` ✅ EXISTS
- `/DOCS/handover/` - Handover-Dokumente
- `/DOCS/consolidation/` - Konsolidierung-Docs

---

## 📋 CLEANUP-AKTIONEN (REIHENFOLGE)

### Schritt 1: Backup erstellen
```bash
git commit -am "Pre-cleanup snapshot"
git tag cleanup-2026-04-30-before
```

### Schritt 2: Offensichtlich Löschen
- `/scratch/` - komplett
- `/artifacts/temp/` - komplett
- SQL-Files aus `/scripts/` root
- `*.fw` Files
- Alle `*_final.*` Scripts

### Schritt 3: Scripts strukturieren
- Kategorien anlegen
- Files verschieben (git mv)
- README.md in jeder Kategorie

### Schritt 4: Artifacts konsolidieren
- Archive-Struktur anlegen
- Alte Audits verschieben
- Nur aktive behalten

### Schritt 5: Duplikate mergen
- deployment + deployments
- Andere Duplikate identifizieren

### Schritt 6: Docs aufräumen
- Kategorien anlegen
- Files sortieren
- Index erstellen

---

## 🎯 ZIEL-STRUKTUR

```
FraWo/
├── .github/           # CI/CD Workflows
├── .vscode/           # Editor Config
├── ansible/           # Ansible Playbooks & Inventory
├── apps/              # Eigenständige Applikationen
│   ├── radio-player/  # (wenn aktiv)
│   └── README.md
├── assets/            # Medien-Assets (Bilder, Logos)
├── Codex/             # Website-Code
│   └── website/
├── DOCS/              # Alle Dokumentation
│   ├── audits/        # Audit-Reports
│   ├── plans/         # Planungsdokumente
│   ├── reports/       # Status-Reports
│   ├── handover/      # Übergabe-Docs
│   └── archive/       # Historisch
├── infrastructure/    # Infrastructure as Code
├── manifests/         # Config-Manifeste
├── scripts/           # Alle Scripts (sauber kategorisiert)
│   ├── business/      # Odoo, Business-Logik
│   ├── infrastructure/# PBS, Proxmox, Networking
│   ├── media/         # Radio, Toolbox, Jellyfin
│   ├── security/      # Vaultwarden, SSH, Tailscale
│   ├── audits/        # Audit & Gate Scripts
│   ├── bootstrap/     # Setup & Installation
│   ├── stockenweiler/ # Remote-Site spezifisch
│   ├── tools/         # Helper-Tools
│   └── archive/       # Alte/deprecated Scripts
└── SSOT/              # Single Source of Truth
    └── README.md

GELÖSCHT:
- scratch/
- deployment/ (merged in scripts/)
- deployments/ (merged in scripts/)
- lifeboat/ (evaluieren)
- operator_snapshots/ (archivieren)
- COMMUNICATION/ (merged in DOCS/)
- artifacts/temp/
```

---

## 📊 ERWARTETE REDUKTION

| Metrik | Vorher | Nachher | Reduktion |
|--------|--------|---------|-----------|
| Root-Level Folders | 21 | ~12 | -43% |
| Files in /scripts root | 254 | 0 | -100% |
| Subdirs in /artifacts | 184 | ~10 | -95% |
| Temp/Scratch Files | ~20 | 0 | -100% |

**Geschätzte Gesamtreduktion**: ~30% weniger Files, 60% bessere Struktur

---

## ⚠️ RISIKEN

1. **Scripts könnten sich gegenseitig referenzieren**
   - Lösung: Grep nach Pfaden, relative Imports prüfen

2. **CI/CD könnte auf Pfade zeigen**
   - Lösung: `.github/workflows` prüfen

3. **Ansible könnte Scripts einbinden**
   - Lösung: `ansible/` nach script-Pfaden durchsuchen

---

## ✅ NÄCHSTE SCHRITTE

1. User-Freigabe für Cleanup-Plan
2. Backup-Commit erstellen
3. Schritt für Schritt durchgehen
4. Nach jedem Schritt testen
5. Finale Commit-Message
