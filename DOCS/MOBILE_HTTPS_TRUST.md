# Mobile HTTPS Vertrauen & Zertifikats-Setup (Business MVP)

Dieses Dokument beschreibt, wie mobile Endgeraete (Android & iOS) die interne HTTPS-Infrastruktur des Homeservers 2027 validieren. Dies ist Voraussetzung fuer die Nutzung der Bitwarden-App, Nextcloud und Odoo ueber sichere Verbindungen.

## 1. Warum ist das noetig?

Unser Homeserver nutzt eine eigene Zertifizierungsstelle (CA) fuer `*.hs27.internal`. Da globale Browser diese private CA nicht standardmaessig kennen, muss das Stamm-Zertifikat einmalig manuell installiert werden.

## 2. Stamm-Zertifikat herunterladen

Stelle sicher, dass du mit **Tailscale** verbunden bist oder dich im **Heim-WLAN** befindest.

- **URL:** `http://100.99.206.128:8447/frawo-ca.crt`
- **Alternativ:** `http://portal.hs27.internal/frawo-ca.crt`

## 3. Installation auf Android (z.B. Pixel 8)

1. Lade die Datei `frawo-ca.crt` herunter.
2. Oeffne die **Einstellungen**.
3. Gehe zu **Sicherheit & Datenschutz** ➜ **Weitere Sicherheitseinstellungen**.
4. Waehle **Verschluesselung und Anmeldedaten**.
5. Waehle **Zertifikat installieren** ➜ **CA-Zertifikat**.
6. Bestaetige die Sicherheitswarnung mit "Trotzdem installieren".
7. Waehle die heruntergeladene Datei `frawo-ca.crt` aus.
8. Android bestaetigt: "CA-Zertifikat installiert".

## 4. Installation auf iOS (iPhone / iPad)

1. Oeffne den Link in **Safari** und lade das Profil/Zertifikat herunter.
2. Oeffne die **Einstellungen** ➜ **Profil geladen** (ganz oben).
3. Klicke auf **Installieren** und gib deinen Passcode ein.
4. **WICHTIG (Zusaetzlicher Schritt):**
   - Gehe zu **Einstellungen** ➜ **Allgemein** ➜ **Info**.
   - Scrolle ganz nach unten zu **Zertifikatsvertrauenseinstellungen**.
   - Aktiviere den Schalter fuer **"Caddy Local Authority - 2026..."** unter "Vollen Vertrauensschutz fuer Stammzertifikate aktivieren".

## 5. Verifikation

Oeffne `https://vault.hs27.internal` im mobilen Browser. Das Schloss-Symbol sollte nun ohne Warnung erscheinen.

---
*Ansprechpartner bei Problemen: Wolf (Operator)*
