# Standorte in Home Assistant: Orte, Personen, neue Geräte

> Odoo #1483 · Stand 05.10.2026 · Gilt für **beide** Instanzen: Rothkreuz (`10.1.0.40`) und Eltern (`10.1.0.248`).
> Ziel: Jede Person zeigt einen **Ortsnamen** (Rothkreuz / Stockenweiler / Lindau Insel / unterwegs)
> und keine Koordinaten. Eine Karte ist dafür nicht nötig.

## 1. Orte (Zonen), auf beiden Instanzen gleich

| Zone | Breite | Länge | Radius | Anmerkung |
|---|---|---|---|---|
| **Rothkreuz** | 47.586522 | 9.726519 | 300 m | RK22 und RK14 (Villa/Studio) als **ein** Ort; auf der Rothkreuz-Instanz ist das die Heimatzone (Ort-Name „Home“ → „Rothkreuz“) |
| **Stockenweiler** | 47.620160 | 9.790173 | 200 m | Elternhaus; auf der Eltern-Instanz ist das die Heimatzone (heißt dort schon so) |
| **Lindau Insel** | 47.546200 | 9.684500 | 650 m | ganze Insel inkl. **Inselhalle** (47.5480 / 9.6854, ca. 200 m vom Mittelpunkt) |

- Die Koordinaten von Rothkreuz und Stockenweiler stammen aus der Heimatzone der jeweiligen Instanz (gemessen 05.10.).
  Inselhalle: Zwanzigerstraße 10, öffentliche Ortsangabe.
- Abstände: Rothkreuz ↔ Lindau Insel ≈ 5 km, Rothkreuz ↔ Stockenweiler ≈ 6 km. Die Zonen **überlappen nicht**.
- Außerhalb aller Zonen zeigt HA `not_home`. Auf den Dashboards heißt das **„unterwegs“**.

## 2. Personen und ihre Geräte (Soll)

| Person | Rothkreuz-Instanz | Eltern-Instanz | Stand 05.10. |
|---|---|---|---|
| Wolf | `pixel_9_pro_3` (gespiegelt aus Eltern-HA per `remote_homeassistant`) | `pixel_9_pro_3` | GPS kommt nur auf der Eltern-Instanz an; `pixel`, `pixel_8a_2` sind tot → von der Person lösen |
| Luis | gespiegelt | `luis_iphone_15`, `luis_ipad_10` | GPS ✅ |
| Lotti | gespiegelt | `lotti_handy` | meldet nichts → in der Companion-App Standort freigeben (vor Ort) |
| Heidi | – | – | kein Gerät |
| Dobby | `tracker_ujyejxlh` (Tractive) | gespiegelt | GPS ✅ |
| Lastenrad (R&M Cargo Line) | – | – | **liefert keine Position** (Bosch eBike: nur Akku/Strecke). Nur mit eigenem GPS-Tracker möglich |

**Sichtbarkeit (Wolf, 05.10.):** Die Standorte von Luis und Lotti dürfen auf **allen** Dashboards erscheinen.

Eine Person bündelt mehrere Geräte. HA nimmt das Gerät mit der frischesten GPS-Meldung,
also ist ein Mensch mit Handy und Tablet an **einem** Ort.

## 3. Neues Gerät hinzufügen (Vorlage)

1. Companion-App installieren und bei der Instanz anmelden, auf der die Person „zu Hause“ ist
   (Familie Stockenweiler → Eltern-HA, FraWo/Rothkreuz → Rothkreuz-HA).
2. In der App: **Standort „Immer erlauben“** und Hintergrund-Standort an. Sonst meldet das Gerät nur WLAN
   (`source_type: router`) und keinen Ort. Das war der Fehler bei `pixel_9_pro` in Rothkreuz.
3. HA → Einstellungen → Personen → Person öffnen → unter „Geräte verfolgen“ das neue `device_tracker.*` hinzufügen.
4. Fertig. Zonen und Ortsnamen gelten automatisch. Auf der anderen Instanz erscheint die Person über die Spiegelung.

**Prüfen:** Unter Entwicklerwerkzeuge → Zustände bei `device_tracker.<gerät>` müssen `latitude`/`longitude` stehen
und `source_type: gps`.

## 4. Was bewusst nicht dazugehört

- 3D-Modelle der Räume → eigene Aufgabe.
- Die eingebaute Kartenansicht rendert unter HA 2026.9 weiß (#1473). Die Textauskunft funktioniert ohne Karte.
