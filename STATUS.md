# Aktueller Status & Praxis-Scan (Stand: 18.05.2026)

Dieses Dokument beschreibt den **tatsächlich getesteten** Zustand des Systems. Alle anderen Pläne und Dokumente wurden ins Archiv verschoben, um Verwirrung zu vermeiden.

---

## 1. Was wirklich läuft und getestet wurde (Fakten)

### 🌍 Website & Domain
- **`https://www.frawo-tech.de/`**: **ERREICHBAR** und funktional.
  - Die Seite lädt ohne sichtbare Fehler.
  - Die neuen Bilder (Dartboard, Lautsprecher, ATEM-Switcher) sind live und an den richtigen Stellen.
- **`https://frawo-tech.de/` (ohne www)**: **ERREICHBAR**.
  - Der Browser-Scan zeigt, dass die Seite ohne www ebenfalls lädt und identischen Inhalt zeigt.

### 🖥️ Odoo Server
- **IP `10.4.0.22`**: **ERREICHBAR** (Ping erfolgreich, <1ms).
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

## 3. Nächste Schritte

1. **Stockenweiler vor Ort prüfen**: Warum ist der Server über Tailscale nicht erreichbar?
2. **Cloudflare Transform Rules**: Einrichten der Security Headers (Schritt 4).
3. **Mobile Ansicht testen**: Feedback vom echten Handy einholen.
