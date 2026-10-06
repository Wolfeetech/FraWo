# QLC+-Fixtures für Lukis Licht (Halloween 31.10.2026, Odoo #1906)

Licht-Backup: Laptop mit QLC+ und USB-DMX-Dongle (#1451).

| Lampe | Anzahl | Datei | Quelle |
|---|---|---|---|
| Eurolite LED IP PIX Strobe MK2 | 12 | `Eurolite-LED-IP-PIX-Strobe-MK2.qxf` | QLC+-Bibliothek (ist in QLC+ schon enthalten) |
| Showtec Phantom 65 | 2 | `Showtec-Phantom-65.qxf` | QLC+-Bibliothek (ist in QLC+ schon enthalten) |
| Showtec Spectral M800 Q4 IP65 | 4 | `Showtec-Spectral-M800-Q4-IP65.qxf` | **selbst erstellt** nach Herstellerhandbuch 43571 V2, S. 36–39 (fehlt in QLC+ und Open Fixture Library) |

## Einbinden

Eigene Datei nach `%USERPROFILE%\QLC+\Fixtures\` (Windows) bzw. `~/.qlcplus/fixtures/` (Linux) kopieren, dann QLC+ neu starten. Danach erscheint sie unter Showtec. Neu erzeugen: `python _erzeuge_m800_q4_ip65.py`.

## Vorher bei Luki prüfen

- **Strobe:** MK2 oder Vorgänger? Für den Vorgänger gibt es in QLC+ „LED IP PIX Strobe RGB-CW-WW“ bzw. „Frost“.
- **M800:** eingestellter DMX-Modus (Menü „dMX → PErS“). Die Datei kennt alle 9 Modi: AR1.D, TOUR, TR16, ARC.2, AR2.D, AR2.S, SSP, 8BIT, 16BI. Außerdem „Classic“ oder „Special Strobe“ (Menü), wirkt sich auf Kanal Strobe aus.
- **Phantom 65:** Typenschild (laut Wolf „glaub ich“) und Modus Basic (8) oder Advanced (13).

## Vorschlag Adressplan (1 Universum, 186 von 512 Kanälen)

Vorausgesetzt, Luki stellt diese Modi ein. Sonst Plan an die tatsächlichen Modi anpassen.

| Lampe | Modus | Kanäle | Startadressen |
|---|---|---|---|
| PIX Strobe 1–12 | 10 Channel | 10 | 1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111 |
| Spectral M800 1–4 | 8BIT (RGBW) | 10 | 121, 131, 141, 151 |
| Phantom 65 1–2 | Advanced | 13 | 161, 174 |

## Strom (Höchstwerte laut Datenblatt)

12 × 180 W + 4 × 65 W + 2 × 125 W ≈ **2,7 kW**, also mindestens zwei getrennt abgesicherte 16-A-Stromkreise. Die Strobes allein (2,2 kW) nicht an einen Kreis mit Ton hängen.
