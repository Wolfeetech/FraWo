# Home-Assistant-Audit — homeassistant_stocki (home.prinz-stockenweiler.de)

**Datum:** 2026-08-06
**Quelle:** vollständiger Registry-Dump per WebSocket-API (Agent-Nutzer, Long-Lived Token), read-only, nichts verändert.
**Zahlen:** 10 Bereiche (3 Etagen-Gruppen: Eltern, Einliegerwohnung, Outdoor + 2 nicht-Eltern-Gruppen: Dachgeschoss, Container), 178 Geräte, 1497 Entitäten (915 aktive States), 65 Integrationen.

> Ziel laut Wolf: Diese Instanz soll **nur noch für Eltern (Alois & Heide) und aktuelle Bewohner** (Lotti) sein. Alles was Admin/Wolfs eigener Rothkreuz-Betrieb ist, gehört zu `home.frawo.tech`.

---

## 1. Haushalts-/Parteien-Modell (Stand nach Wolfs Erklärung)

| Partei | Wer | Bereiche | Stromzähler |
|---|---|---|---|
| **Familie Prinz (Eltern)** | Alois & Heide, gelegentlich Hund Dobby zu Besuch | Büro_Eltern, Buero_Controlroom_Eltern, Wohnküche_Eltern, **Garten** (Heidis Kräutergarten + Growatt-Balkonkraftwerk) | eigener Zähler (nicht auf dem geteilten) |
| **Lotti** | Bewohnerin Einliegerwohnung | ELW_Bad, ELW_Wohnen — eigener Shelly 4PM (Küche, Bad etc.) | **teilt sich Gesamtzähler mit Container** |
| **Container** (Techniklager/Serverraum) | Wolf/FraWo-Technik, eigenes Thema | Server, Studio — eigener Shelly 4PM (Server, Licht, Allgemein) | **teilt sich Gesamtzähler mit Lotti** |

🔴 **Wichtig:** Lottis 4PM und der Container-4PM hängen am selben Gesamtzähler → der im Container getrackte Verbrauch ist nicht rein, sondern vermischt mit Lottis Anteil. Für saubere Abrechnung braucht es **3 getrennte Energie-Auswertungen** (Familie Prinz / Lotti / Container), nicht nur eine Summe.

---

## 2. Kaputte Integrationen (7 gefunden, alle live bestätigt)

| Integration | Fehler | Vermutliche Ursache |
|---|---|---|
| Growatt Server "BKW Stockenweiler" | `setup_error: communication_error` | Cloud-Verbindung zum Growatt-Portal gestört (Login/API) |
| Google Home | `not_loaded` | unklar, noch nicht untersucht |
| Brother MFC-J5730DW (IPP, "@ MacBook Pro von Alois") | `setup_retry`, IPP-Kommunikationsfehler | Drucker/Netzwerk nicht erreichbar über diesen Pfad |
| fritzbox (Smart-Home-Thermostate/Steckdosen) | `setup_error` | kein Grund angegeben, näher prüfen |
| FRITZ!Repeater 3000 | `setup_retry`, Host `192.168.178.187` nicht erreichbar | Repeater offline oder IP hat sich geändert |
| UPnP FRITZ!Box-Erkennung (2 Einträge, IGDv1+v2) | `setup_retry`, Gerät nicht gefunden | vermutlich UPnP am Router aus oder redundant zu fritzbox/fritz-Integration |
| FRITZ!Repeater 600 | `setup_error`, **401 Unauthorized** | gespeichertes Passwort stimmt nicht mehr — **braucht dich**, ich darf das nicht selbst eintragen |

Zusätzlich unter "Entdeckt" (noch nie eingerichtet): ein zweiter, neuer FRITZ!Repeater 600 und ein Tuya-Konto (`wwolfitec@gmail.com`) verlangen "Neu konfigurieren".

**271 von 915 Entitäten (30%) stehen aktuell auf "nicht verfügbar/unbekannt"** — davon ist ein Großteil normal (52 Geräte-Tracker = Handys/Laptops, die gerade nicht im WLAN sind), aber **102 Sensoren + 52 Schalter unverfügbar** ist viel und hängt vermutlich direkt mit den obigen kaputten Integrationen zusammen (ein kaputter Repeater reißt alle seine Sensoren mit).

---

## 3. Geräte ohne Bereich (sollten aber einem zugeordnet sein)

| Gerät | Modell | Vermutlich gehört zu |
|---|---|---|
| **Rentnerbüro** | Shelly Plug S Gen3 | Büro_Eltern oder Buero_Controlroom_Eltern (Name sagt es eigentlich schon) |
| **ELW - BAD 301 #17** | FRITZ!Smart Thermo 301 | ELW_Bad |
| **ELW - WohKü - 301 #18** | FRITZ!Smart Thermo 301 | ELW_Wohnen |
| BZP2N6L0KY (Growatt) | — | vermutlich Garten (Schwestergerät von "BKW Stockenweiler", das schon korrekt in Garten liegt) |
| [TV]wolf tv | Samsung UE48H6200 | 🟡 nach Wolfs eigenem Namen — Kandidat für Migration nach home.frawo.tech statt Bereichszuordnung hier |
| Home mini / Wohnzimmer / Badezimmer / WohnzimmerTV (Google/Chromecast/Blaupunkt) | diverse | unklar wessen — bitte klären (Eltern, Lotti oder Wolf-Rest?) |
| FRITZ!Repeater 600 / FRITZ!WLAN Repeater 1750E | — | Netzwerk-Infrastruktur, Bereich optional |

## 4. Geräte ohne eigenen Namen (zeigen nur die rohe Geräte-ID)

| Rohname | Modell | Bereich |
|---|---|---|
| shellyblugwg3-34cdb07897c8 | Shelly BLU Gateway Gen3 | ELW_Wohnen |
| shellyrgbw2-D88F55 | Shelly RGBW2 (Lichtsteuerung) | keiner |
| shellyplugsg3-e4b063e5ec38 | Shelly Plug S Gen3 | Büro_Eltern |

*(zwei weitere "shelly...*"-Rohnamen sind nur Netzwerk-Tracking-Duplikate der FRITZ!Box, keine echten separaten Geräte — kein Handlungsbedarf)*

## 5. Mögliche Fehlzuordnung zur Klärung mit Wolf

- **"Balkonkraftwerk"** (Shelly Pro 4PM, Kanal im Container-4PM) liegt im Bereich **Studio** — das ist vermutlich technisch korrekt (misst den Container-seitigen Anschluss des Balkonkraftwerks), aber optisch verwirrend neben "BKW Stockenweiler" in Garten. Klären: zwei verschiedene Messpunkte am selben Kraftwerk, oder Dopplung?
- **Container/Studio/Server-Bereiche insgesamt** (13 Geräte: Balkonkraftwerk, Container/Allgemein, Container/Licht, Pro4PM-container, Server, Shelly Licht Container, Growatt Noah2000, Keller Pumpe Shelly) — nach Wolfs neuer Ansage gehört das administrativ zu Rothkreuz/`home.frawo.tech`, nicht zu dieser Eltern-Instanz. **Migrations-Kandidat**, nicht nur Umbenennung.
- **"Wolf ELW Kühlschrank"** (ELW_Wohnen) — nach Wolf ist die ELW eigentlich Lottis Wohnung. Gehört der Kühlschrank wirklich Wolf (dann eigener Fall), oder ist der Name nur ein Überbleibsel?

## 6. Neue Nutzer/Zugänge (heute erledigt)

- HA-Nutzer **"Agent"** (Benutzername `agent`) angelegt, Administrator, Passwort von Wolf selbst gesetzt.
- Eigenes Long-Lived-Token für den Agent-Nutzer erstellt und für diese Prüfung verwendet (liegt nur lokal im Scratchpad, nicht im Repo).
- 🔴 Offen: Wolf wollte `FrawoAgent2026!` in Vaultwarden sichern — das muss er **selbst** eintragen, das darf ich nicht für ihn tun.

---

## Nächster Schritt

Wolf geht das mit Claude "Schritt für Schritt" durch — Reihenfolge noch offen, Vorschlag: (1) Bereichs-Zuordnung + Umbenennung der oben gelisteten Lücken, (2) Container/Studio/Server-Migrationsentscheidung, (3) kaputte Integrationen einzeln (teils braucht es Wolfs Passwort-Eingabe).
