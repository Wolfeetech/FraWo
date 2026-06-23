# Franz iPhone Onboarding Guide - Homeserver 2027

Dieses Dokument ist die Schritt-fuer-Schritt-Anleitung fuer Franz, um sein iPhone mit dem Homeserver zu verbinden.

## 1. Voraussetzungen

- [ ] iPhone im WLAN oder LTE
- [ ] Zugang zum Apple App Store
- [ ] Zugang zu `Tailscale`
- [ ] Franz-Passwort fuer `Vaultwarden` falls beim ersten Login benoetigt

## 2. Tailscale einrichten (Mobil-Netzwerk)

Tailscale ist unser privates Tunnel-Netzwerk. Es macht den Homeserver von ueberall sicher erreichbar.

1. [ ] Installiere die **Tailscale** App aus dem App Store.
2. [ ] Klicke auf `Log In` und logge dich mit deinem `FraWo` Account ein (falls bereits angelegt) oder verwende den bereitgestellten Zugang (Wolf fragen).
3. [ ] Bestaetige die VPN-Konfiguration auf dem iPhone.
4. [ ] Achte darauf, dass der Schalter oben links auf `Connected` steht.

Hinweis:

- Der aktuelle MVP-Mobilpfad fuer `Franz` nutzt den direkten Start unter `http://100.91.20.116/franz/` (oder lokal im WLAN `http://10.1.0.149/franz/`).
- Fuer diesen aktuellen MVP-Pfad ist kein zusaetzlicher Zertifikatsschritt noetig.

## 3. Das Franz-Portal aufrufen

Unser zentraler Einstiegspunkt ist das Portal.

1. [ ] Oeffne **Safari** auf dem iPhone.
2. [ ] Gib die Adresse: `http://10.1.0.149/franz/` (im lokalen WLAN) oder `http://100.91.20.116/franz/` (via Tailscale) ein.
3. [ ] Klicke in Safari auf das **Teilen-Icon** (das Quadrat mit dem Pfeil nach oben).
4. [ ] Waehle **"Zum Home-Bildschirm"**.
5. [ ] Gib als Name **"Franz Mobil Start"** ein und klicke auf `Hinzufuegen`.

## 4. Apps nutzen

Du hast nun ein Icon auf deinem iPhone-Startbildschirm. Wenn du darauf klickst, hast du direkten Zugriff auf:

- **Nextcloud:** (Archiviert / Offline)
- **Paperless:** (Archiviert / Offline)
- **Odoo:** (Rechnungen und ERP) -> Odoo-Login unter `/web/login`.
- **Vaultwarden:** (Passwort-Tresor)

## 5. Sichtbare Abnahme fuer den MVP

- [ ] `Franz Mobil Start` laedt sichtbar auf dem iPhone
- [ ] `Odoo` ist vom mobilen Startpfad sichtbar erreichbar
- [ ] `Vaultwarden` ist vom mobilen Startpfad sichtbar erreichbar

## 6. Wenn es nicht klappt

1. [ ] Pruefe, ob die Tailscale App gruen (`Connected`) leuchtet (falls du nicht im lokalen WLAN bist).
2. [ ] Pruefe, ob du WLAN oder eine gute LTE-Verbindung hast.
3. [ ] Falls die Seite nicht laedt, frage den Operator (Wolf).
