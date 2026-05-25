import re

file_path = "C:\\Users\\StudioPC\\.gemini\\antigravity\\brain\\3e87f07a-f13e-4c85-baf6-2bde80e7f0fa\\FRWO_ROADMAP_2026.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_section = """
## 📻 Phase 5: Radio Ecosystem (AzuraCast & Odoo)

**Odoo Projekt:** `Radio Ecosystem`  
**Status:** 🟡 Konzept / Planung (Basics First)  
**Verantwortlich:** Agent (Integration) / Wolf (Playlists)  

Aufbau eines professionellen, zentral steuerbaren 24/7 Webradios. Odoo dient als "Master of Data" (Benutzerverwaltung, Feedback-Auswertung), während AzuraCast als hochstabile Sende-Engine für den Stream sorgt.

**Die nächsten Schritte (Basics First!):**
1. **Epic 1: Basic Integration & AutoDJ**
   - Ordnerstruktur in AzuraCast für Genre-Sortierung anlegen.
   - 3 Basis-Playlists konfigurieren (Standard Rotation, Nightshift, Primetime).
   - Ziel: Stabiler 24/7 Stream ohne manuelle Eingriffe.
2. **Epic 2: Odoo User Sync (Die Brücke)**
   - API-Keys in AzuraCast generieren und als Secret in Odoo hinterlegen.
   - Automatisierung: Odoo DJ-Benutzer -> AzuraCast Streamer-Account synchronisieren.
3. **Epic 3: Interactive Frontend (Herz/Scheiße)**
   - Hörer-Feedback-Buttons im FraWo Funk Player integrieren.
   - Feedback-Speicherung im Backend (Odoo) zur Optimierung der Playlists.

---
"""

# Insert before Phase 4 if it exists, or just append before Anker Lounge
if "## 🛋️ Nebenprojekt: \"Anker Lounge\"" in content:
    content = content.replace("## 🛋️ Nebenprojekt: \"Anker Lounge\"", new_section + "## 🛋️ Nebenprojekt: \"Anker Lounge\"")
else:
    content += "\n" + new_section

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Roadmap successfully.")
