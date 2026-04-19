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

- Der aktuelle MVP-Mobilpfad fuer `Franz` nutzt den direkten Tailscale-Start unter `http://100.82.26.53:8447/franz/`.
- Fuer diesen aktuellen MVP-Pfad ist kein zusaetzlicher Zertifikatsschritt noetig.

## 3. Das Franz-Portal aufrufen

Unser zentraler Einstiegspunkt ist das Portal.

1. [ ] Oeffne **Safari** auf dem iPhone.
2. [ ] Gib die Adresse: `http://100.82.26.53:8447/franz/` ein.
   - *Hinweis:* Dies ist der aktuelle mobile MVP-Pfad ueber das Tailnet.
3. [ ] Klicke in Safari auf das **Teilen-Icon** (das Quadrat mit dem Pfeil nach oben).
4. [ ] Waehle **"Zum Home-Bildschirm"**.
5. [ ] Gib als Name **"Franz Mobil Start"** ein und klicke auf `Hinzufuegen`.

## 4. Apps nutzen

Du hast nun ein Icon auf deinem iPhone-Startbildschirm. Wenn du darauf klickst, hast du direkten Zugriff auf:

- **Nextcloud:** (Dokumente und Fotos) -> Logge dich mit deinem Franz-Login ein.
- **Paperless:** (GbR Beleg-Archiv) -> Logge dich ein, um Belege zu suchen.
- **Odoo:** (Rechnungen und ERP) -> Odoo-Login unter `/web/login`.

## 5. Sichtbare Abnahme fuer den MVP

- [ ] `Franz Mobil Start` laedt sichtbar auf dem iPhone
- [ ] `Nextcloud` ist vom mobilen Startpfad sichtbar erreichbar
- [ ] `Paperless` ist vom mobilen Startpfad sichtbar erreichbar
- [ ] `Odoo` ist vom mobilen Startpfad sichtbar erreichbar
- [ ] `Vaultwarden` ist vom mobilen Startpfad sichtbar erreichbar

## 6. Wenn es nicht klappt

1. [ ] Pruefe, ob die Tailscale App gruen (`Connected`) leuchtet.
2. [ ] Pruefe, ob du WLAN oder eine gute LTE-Verbindung hast.
3. [ ] Falls die Seite `http://100.82.26.53:8447/franz/` nicht laedt, frage den Operator (Wolf).
