# FraWo Workspace Setup - Zentrale Konfiguration
**Datum**: 2026-04-30
**Status**: ✅ Production Ready

---

## 🎯 **PROBLEM GELÖST**

**Vorher**: Jeder PC hatte eigene VS Code Settings, Extensions, Workspace-Konfiguration
**Nachher**: **EINE zentrale Konfiguration** im Git-Repo, die für ALLE gilt

---

## 📁 **NEUE ZENTRALE STRUKTUR**

```
FraWo/
├── .vscode/
│   ├── settings.json         # ✅ Zentrale Editor-Settings
│   ├── extensions.json       # ✅ Empfohlene Extensions
│   └── cspell.json          # ✅ Rechtschreibprüfung
├── .editorconfig            # ✅ Editor-agnostische Config
├── FraWo.code-workspace     # ✅ Multi-Folder Workspace
└── manifests/workspaces/
    └── canonical_workspace.json  # Pfad-Definitionen
```

---

## 🚀 **SETUP AUF JEDEM RECHNER**

### 1. Repo klonen (falls noch nicht vorhanden)
```powershell
cd C:\WORKSPACE
git clone https://github.com/Wolfeetech/FraWo.git
cd FraWo
```

### 2. Workspace-Pfade unified (nur Windows)
```powershell
# Führt Junctions zu C:\WORKSPACE\FraWo aus
powershell -ExecutionPolicy Bypass -File scripts\workspace\force_unify_workspaces.ps1
```

**Resultat:**
- `C:\WORKSPACE\FraWo` → Canonical Path
- `C:\Users\Admin\Workspace\FraWo` → Junction zu Canonical
- `C:\Users\Admin\Workspace\Repos\FraWo` → Junction zu Canonical

### 3. VS Code Workspace öffnen
```powershell
code FraWo.code-workspace
```

**ODER** einfach:
```powershell
code .
```

### 4. Empfohlene Extensions installieren
VS Code zeigt automatisch eine Notification:
- **"Do you want to install the recommended extensions?"**
- → Klicke **"Install All"**

---

## ✅ **WAS IST JETZT ZENTRAL?**

### 1. **Editor Settings** (.vscode/settings.json)
- Font: Cascadia Code / Fira Code
- Tab Size: 4 (Python), 2 (YAML/JSON/HTML)
- Encoding: UTF-8
- Line Endings: LF
- Auto-Save: Nach 2 Sekunden
- Format on Save: **AUS** (manuell formatieren!)

### 2. **Extensions** (.vscode/extensions.json)
**Empfohlen** (automatisch vorgeschlagen):
- ✅ Python + Pylance
- ✅ PowerShell
- ✅ GitLens + Git Graph
- ✅ Remote SSH
- ✅ Ansible
- ✅ YAML
- ✅ Markdown
- ✅ Spell Checker (EN+DE)
- ✅ Odoo Snippets

**Nicht erwünscht**:
- ❌ C++ Tools
- ❌ C# Tools

### 3. **Code-Workspace** (FraWo.code-workspace)
**Multi-Folder Struktur**:
- 🏠 FraWo (Root)
- 📜 Scripts
- 📚 DOCS
- 🌐 Website (Codex)
- 🤖 Ansible
- 📦 Manifests

**Vorteile**:
- Schneller Wechsel zwischen Ordnern
- Dedizierte Search-Scopes
- Terminal startet immer im Root
- Launch-Configs für Python/PowerShell

### 4. **EditorConfig** (.editorconfig)
Funktioniert auch mit **Vim, Sublime, IntelliJ, etc.**!
- Encoding: UTF-8
- Line Endings: LF
- Indentation: Spaces (außer Makefiles)
- Trailing Whitespace: Entfernt

---

## 🔄 **SYNC-WORKFLOW**

### Vor dem Arbeiten (IMMER!)
```bash
git pull
```

### Nach dem Arbeiten
```bash
git add .
git commit -m "Deine Änderungen"
git push
```

### Settings geändert?
Wenn du `.vscode/settings.json` oder `extensions.json` änderst:
```bash
git add .vscode/
git commit -m "Update workspace settings"
git push
```

**WICHTIG**: Alle anderen Rechner machen dann `git pull` und haben die neuen Settings!

---

## 📋 **CHECKLISTE: NEUER PC**

- [ ] Git installiert
- [ ] VS Code installiert
- [ ] Repo geklont nach `C:\WORKSPACE\FraWo`
- [ ] `force_unify_workspaces.ps1` ausgeführt
- [ ] `code FraWo.code-workspace` geöffnet
- [ ] Empfohlene Extensions installiert
- [ ] Git konfiguriert (name, email)
- [ ] SSH-Key für GitHub hinterlegt

---

## 🛠️ **TROUBLESHOOTING**

### Problem: "Extensions nicht synchronisiert"
**Lösung**:
```powershell
# In VS Code Command Palette (Ctrl+Shift+P):
> Extensions: Show Recommended Extensions
> Install All
```

### Problem: "Settings werden nicht übernommen"
**Lösung**:
1. Prüfe ob `.vscode/settings.json` existiert
2. Reload VS Code Window (Ctrl+Shift+P → "Reload Window")
3. Prüfe ob Workspace geöffnet ist (nicht nur Folder!)

### Problem: "Line Endings falsch (CRLF statt LF)"
**Lösung**:
```bash
git config --global core.autocrlf input
```

---

## 🎓 **BEST PRACTICES**

### 1. **IMMER Workspace öffnen** (nicht nur Folder)
```powershell
# ✅ Richtig
code FraWo.code-workspace

# ❌ Falsch
code .
```

### 2. **Nie lokale Settings überschreiben**
- User Settings (Global) → Für persönliche Präferenzen (Theme, Font-Size)
- Workspace Settings → Im Repo, für alle gleich

### 3. **Extensions installieren wie empfohlen**
- Installiere NUR die empfohlenen Extensions
- Keine Random-Extensions ohne Grund

### 4. **Git-Workflow einhalten**
- Pull before work
- Commit after work
- Push completed work

---

## 📊 **VORHER/NACHHER**

| Aspekt | Vorher | Nachher |
|--------|--------|---------|
| **Settings** | Jeder PC anders | ✅ Zentral im Git |
| **Extensions** | Chaos | ✅ Empfohlene Liste |
| **Workspace** | Verschiedene Pfade | ✅ Unified Junctions |
| **Line Endings** | CRLF/LF Mix | ✅ Immer LF |
| **Encoding** | Mix | ✅ Immer UTF-8 |
| **Tabs/Spaces** | Chaos | ✅ Definiert pro Language |

---

## 🔗 **RELEVANTE FILES**

- [.vscode/settings.json](../.vscode/settings.json) - Editor Settings
- [.vscode/extensions.json](../.vscode/extensions.json) - Extension Liste
- [FraWo.code-workspace](../FraWo.code-workspace) - Workspace Definition
- [.editorconfig](../.editorconfig) - Editor-agnostisch
- [manifests/workspaces/canonical_workspace.json](../manifests/workspaces/canonical_workspace.json) - Pfad-Manifest

---

## ✅ **FERTIG!**

Ab jetzt hat **jeder PC die gleichen Settings**, sobald er das Repo pullt!

**Keine Verwirrung mehr!** 🎉
