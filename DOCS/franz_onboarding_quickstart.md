# Quick-Start Handout für Franz Bienert - FraWo System

Herzlich willkommen im FraWo-System! Dieses Handout bietet dir eine kompakte Übersicht aller Zugänge, Anleitungen für mobile Tools und die Erfassung von Arbeitszeiten.

---

## 1. Login-Daten Übersicht

| Dienst | URL / Zugangsart | Benutzername / Kennung | Anmerkung / Status |
| :--- | :--- | :--- | :--- |
| **Odoo (ERP & Zeiterfassung)** | `http://10.1.0.149:8069` (lokal) / Tailscale | `franz` / `franz.bienert@frawo.tech` | Hauptsystem für Stundenzettel, Aufgaben & Projekte |
| **Tailscale (VPN)** | App / SSO (`w.prinz1101@...` / FraWo) | `franz-iphone15` / `franz` | Sichere Verbindung von unterwegs |
| **Telegram Bot** | `@ServAssi_bot` | Telegram User | Assistenz & Benachrichtigungen |
| **Nextcloud (Dateispeicher)** | `http://cloud.hs27.internal` / `10.4.0.21` | `franz` / `franz.bienert` | Werkstatt-Ordner & FraWo-Shares *(Archiviert / read-only Status)* |

---

## 2. Anleitung: Tailscale Mobile einrichten (Schritt-für-Schritt)

Tailscale ermöglicht dir den sicheren Zugriff auf alle FraWo-Systeme (Odoo, Dokumente, Werkstatt-Tools) von unterwegs.

1. **App herunterladen**:
   - Öffne den **App Store** auf deinem iPhone.
   - Suche nach **Tailscale** und installiere die App.
2. **Anmelden**:
   - Starte die Tailscale App und wähle **Log In**.
   - Melde dich mit deinem bereitgestellten FraWo-Konto / Einladungslink an.
3. **VPN-Profil erlauben**:
   - Das iPhone fordert dich auf, eine VPN-Konfiguration hinzuzufügen. Bestätige dies mit deinem iPhone-Entsperrcode.
4. **Verbindung aktivieren**:
   - Schalte den Hauptschalter in der App oben links auf **Connected** (Symbol leuchtet grün).
5. **Erfolgsprüfung**:
   - Wenn Tailscale aktiv ist, kannst du `http://10.1.0.149:8069` im Safari-Browser aufrufen, auch wenn du nicht im Werkstatt-WLAN bist.

---

## 3. Anleitung: Telegram @ServAssi_bot nutzen

Der **@ServAssi_bot** unterstützt dich bei täglichen Aufgaben und Benachrichtigungen.

1. **Bot suchen & starten**:
   - Öffne **Telegram** auf deinem Smartphone.
   - Suche nach `@ServAssi_bot`.
   - Klicke unten auf **Start** (oder tippe `/start`).
2. **Konto verknüpfen**:
   - Sende deinen Namen oder die vom Operator bereitgestellte PIN an den Bot, um dein Odoo-Benutzerkonto zu verknüpfen.
3. **Wichtige Befehle & Funktionen**:
   - `/status` – Aktueller System status und Aufgaben-Übersicht.
   - `/tasks` – Liste deiner aktuell zugewiesenen Aufgaben aus Odoo.
   - **Sprachnachrichten / Texte**: Du kannst dem Bot Aufgaben, Notizen oder Rückfragen direkt per Sprache/Text senden – er verarbeitet diese automatisch im FraWo-System.

---

## 4. Anleitung: Stundenzettel in Odoo erfassen

Die Arbeitszeiterfassung erfolgt direkt in Odoo (Modul Zeiterfassung / Timesheets).

### Variante A: Zeiterfassung per Web/Browser (PC oder iPhone)
1. **In Odoo einloggen**:
   - Öffne `http://10.1.0.149:8069` (im WLAN oder per Tailscale) und melde dich an.
2. **Modul öffnen**:
   - Navigiere im Hauptmenü zum Modul **Zeiterfassung** (Timesheets).
3. **Eintrag erstellen**:
   - Klicke auf **Neu** (oder `+`).
   - **Datum**: Tag der Arbeitsleistung auswählen.
   - **Projekt / Aufgabe**: Wähle das entsprechende Projekt (z.B. `Werkstatt`, `WP Stockenweiler 3`, `Wartung`) und die konkrete Aufgabe aus.
   - **Dauer**: Gib die gearbeiteten Stunden an (z.B. `4.5` für 4 Std. 30 Min.).
   - **Beschreibung**: Kurze Info zur ausgeführten Tätigkeit (z.B. *Holzarbeiten Werkstatt, Säge gewartet*).
4. **Speichern**:
   - Der Eintrag wird automatisch gespeichert und deinem Stundenzettel hinzugefügt.

### Variante B: Timer-Funktion nutzen
1. Öffne die zugewiesene Aufgabe im Modul **Projekte**.
2. Klicke auf **Starten**, um den Timer während der Arbeit laufen zu lassen.
3. Nach Abschluss auf **Stoppen** klicken – die Zeit wird automatisch eingetragen.

---

## 5. Ansprechpartner & Support

Bei Fragen oder Problemen erreichst du den System-Admin (Wolf) direkt per Telegram oder Odoo Chatter.
