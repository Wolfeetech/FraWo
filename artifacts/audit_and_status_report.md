# Vollständiger Praxis-Scan & Audit-Bericht

**Datum/Uhrzeit:** 2026-05-18 09:40
**Geprüft durch:** Antigravity (AI Agent)

---

## 1. Was wirklich läuft und getestet wurde (Fakten)

### 🌍 Website & Domain
- **`https://www.frawo-tech.de/`**: **ERREICHBAR** und funktional.
  - Die Seite lädt ohne sichtbare Fehler.
  - Die neuen Bilder (Dartboard, Lautsprecher, ATEM-Switcher) sind live und an den richtigen Stellen.
- **`https://frawo-tech.de/` (ohne www)**: **ERREICHBAR**.
  - Der Browser-Scan zeigt, dass die Seite ohne www ebenfalls lädt und identischen Inhalt zeigt. (Kein 404-Fehler im Test!).

### 🖥️ Odoo Server
- **IP `10.1.0.112`**: **ERREICHBAR** (Ping erfolgreich, <1ms).
- **Homepage-Deployment**: **FUNKTIONAL**. Die Skripte können die Homepage erfolgreich in Odoo aktualisieren.

---

## 2. Was unvollständig oder fehlerhaft ist

### 🔴 Stockenweiler Server
- **SSH `stock-pve` (100.91.20.116)**: **NICHT ERREICHBAR**.
  - Der SSH-Versuch lief in einen Timeout.
  - Der Tailscale-Bridge-Check meldet den Status `pending` (Wartend).
  - Die Route `192.168.178.0/24` ist lokal zwar sichtbar, aber der Server antwortet nicht auf Anfragen.
  - **Fazit:** Stockenweiler ist aktuell von außen/über Tailscale nicht erreichbar.

### ⚠️ Cloudflare Security Headers
- Die "Transform Rules" (Schritt 4 der Anleitung) für die Sicherheits-Header sind noch nicht eingerichtet.

### 📱 Mobile Responsiveness
- Ich habe CSS-Regeln hinzugefügt, um den Header auf Handys zu verkleinern.
- **Status:** Unbestätigt. Wir haben keinen echten Handy-Testbericht, sondern nur die Bestätigung, dass die Seite generell lädt.

---

## 3. Wo wir stehen (Überblick)

- **Wer bin ich?** Ich bin **Antigravity**, dein aktueller AI-Partner. Ich arbeite direkt auf den Dateien in deinem Workspace.
- **Dateien-Chaos:** Auf dem StudioPC (im GitHub-Ordner) liegen aktuell **49 Dateien im Root-Verzeichnis**, davon sehr viele `.md` Dokumente (Zustände, Pläne, Anleitungen). Viele davon sind veraltet oder beschreiben Soll-Zustände, die nicht der Realität entsprechen.

---

## 4. Handlungsempfehlung (Wie machen wir weiter?)

1. **Aufräumen auf dem StudioPC:**
   - Wir sollten alle alten `.md` Dateien im Root-Verzeichnis, die du nicht mehr brauchst (z.B. alte Pläne von 2024/2025), in einen Ordner `archive` verschieben, um den Überblick zurückzugewinnen.
2. **Stockenweiler prüfen:**
   - Da der Server nicht antwortet, müsstest du prüfen, ob er vor Ort läuft und ob Tailscale dort aktiv ist.
3. **Cloudflare abschließen:**
   - Wenn du den Kopf dafür frei hast, machen wir die Transform Rules in Cloudflare fertig.

Möchtest du, dass ich direkt anfange, die alten Dateien auf dem StudioPC in einen Archiv-Ordner zu verschieben?
