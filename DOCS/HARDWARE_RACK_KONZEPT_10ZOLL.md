# 10" Smart-Rack Konzept — FraWo Server & Netzwerk (OG Studio)

**Stand:** 10.09.2026 | **Status:** Freigegeben durch Wolf | **Zugeordnete Aufgabe:** Odoo Task #1175

---

## 1. Ausgangslage & Entscheidung

Ursprünglich war ein Standard 19"-Schrank im Raum gestanden. Da jedoch **kein 24-Port-Switch vorhanden** ist (und nicht benötigt wird), besteht die gesamte aktive Infrastruktur ausschließlich aus **kompakten 1-Liter Tiny PCs** und Desktop-Appliances:
- **Knoten 1 (Anker-PVE):** Lenovo ThinkCentre M720q Tiny (179 × 183 × 35 mm)
- **Knoten 2 (Ersatz / Radio / KI):** Dell OptiPlex Micro (182 × 178 × 36 mm)
- **Knoten 3 (stock-pve):** HP ProDesk 600 G4 Mini (177 × 175 × 34 mm) — Reparatur läuft
- **Gateway / Router:** Ubiquiti UniFi Cloud Gateway Ultra (UCG Ultra, 142 × 128 × 30 mm, 4× GbE LAN)
- **Speicher:** Externe USB-Musik-HDD (`/mnt/music_hdd`) + Backup-SSDs

**Entscheidung:** Einsatz eines **10-Zoll-Smart-Racks** (Breite nur ca. 31 cm, Tiefe 30 cm).
- **Vorteile:** Halb so groß wie ein 19"-Schrank, wohnzimmertauglich, flüsterleise, passgenau für 1-Liter-PCs (je 1 PC pro 10"-Fachboden), Gesamtkosten inkl. USV nur ca. 310–370 € (statt 600–850 €).

---

## 2. Höheneinheiten-Belegungsplan (12 HE Schrank)

| Ebene | Komponente | Beschreibung |
|---|---|---|
| **1 HE** | **10" Keystone Patchpanel** | 8–12 Ports für strukturierte Verkabelung aus dem Gebäude |
| **1 HE** | **10" Bürstenleiste** | Knickfreie, staubgeschützte Durchführung der Slim-Patchkabel |
| **1 HE** | **UniFi Cloud Gateway Ultra (UCG)** | Router & Firewall auf 10"-Fachboden (integrierter 4-Port Switch) |
| **1 HE** | **Zusatz-Switch (optional)** | Kleiner PoE-Switch (z. B. TP-Link 5-Port PoE) für APs / Touchboard |
| **1 HE** | **Lenovo ThinkCentre M720q (Anker)** | PVE Hypervisor (Odoo 19, PBS, HAOS, Jarvis, Paperless) |
| **1 HE** | **Dell OptiPlex Micro** | Entlastungsknoten (Radio-VM AzuraCast, Fileserver CT120) |
| **1 HE** | **HP ProDesk 600 G4 Mini** | PVE Redundanz-Knoten (sobald Ersatznetzteil verbaut) |
| **1 HE** | **Storage-Ebene** | Externe USB-Musik-HDD + 2TB Archiv-SSD |
| **1 HE** | **10" Steckdosenleiste (PDU)** | 3- oder 4-fach Schuko mit Überspannungsschutz & Schalter |
| **3 HE** | **Kabelraum / Netzteile / Reserve** | Genügend Luftraum für externe Netzteile und optimale Konvektionskühlung |

---

## 3. Notstromversorgung (USV)

Da ein 10"-Schrank bauartbedingt keine internen 19"-Batterieeinschübe aufnehmen kann, wird eine **externe lüfterlose Stand-/Wand-USV** eingesetzt:
- **Modell:** **APC Back-UPS 850 (BE850G2-GR)**
- **Leistung:** 850 VA / 520 Watt (deckt den laufenden IT-Bedarf von ca. 185–195 W für 15–20 Min. ab)
- **Ausstattung:** 8 Schuko-Dosen (6x Batteriegepuffert, 2x Überspannungsschutz), USB-Schnittstelle für automatisches Herunterfahren (NUT / Home Assistant), Wandmontage möglich.
- **Lautstärke:** Lautlos (kein Lüfter).

---

## 4. Komponenten & Beschaffungsliste

1. **Wandschrank 10" 12HE (Schwarz):** *Digitus DN-10-12U-B* (ca. 75–90 €)
   - [Galaxus Suche: Digitus 10 Zoll Wandschrank](https://www.galaxus.de/de/search?q=Digitus+10+Zoll+Wandschrank)
   - [eBay Suche: Digitus DN-10-12U](https://www.ebay.de/sch/i.html?_nkw=Digitus+DN-10-12U)
2. **Fachböden 10" 1HE (Schwarz):** *4–5x Digitus DN-10 TRAY-1-B* (je ca. 12–16 €)
   - [Galaxus Suche: DN-10 TRAY-1-B](https://www.galaxus.de/de/search?q=DN-10+TRAY-1-B)
   - [eBay Suche: Digitus DN-10 TRAY-1-B](https://www.ebay.de/sch/i.html?_nkw=Digitus+DN-10+TRAY-1-B)
3. **10" Keystone Patchpanel & Module:** *deleyCON 8/12-Port 10" Panel + Cat.6A Keystones* (ca. 35–45 €)
   - [eBay Suche: 10 Zoll Patchpanel Keystone deleyCON](https://www.ebay.de/sch/i.html?_nkw=10+Zoll+Patchpanel+Keystone+deleyCON)
4. **10" Bürstenleiste & Slim-Kabel:** *Digitus 10" 1HE Bürstenleiste + 0,25m Slim-Patchkabel* (ca. 25–30 €)
   - [eBay Suche: 10 Zoll Bürstenleiste 1HE](https://www.ebay.de/sch/i.html?_nkw=10+Zoll+B%C3%BCrstenleiste+1HE)
5. **10" Steckdosenleiste (PDU):** *10" PDU 1HE 3–4 Schuko mit Überspannungsschutz* (ca. 20–28 €)
   - [Galaxus Suche: 10 Zoll Steckdosenleiste 1HE](https://www.galaxus.de/de/search?q=10+Zoll+Steckdosenleiste+1HE)
6. **USV:** *APC Back-UPS 850 (BE850G2-GR)* (ca. 110–125 €)
   - [Galaxus Suche: APC BE850G2-GR](https://www.galaxus.de/de/search?q=BE850G2-GR)
   - [eBay Suche: APC BE850G2-GR](https://www.ebay.de/sch/i.html?_nkw=BE850G2-GR)

**Gesamtinvestition:** ca. **310 – 370 €**
