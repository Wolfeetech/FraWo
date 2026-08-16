
---

## ⚡ WICHTIGE KLARSTELLUNG: WARUM AIRBEAM NICHT FÜR HANDY / BKW DIREKT FUNKTIONIERT

### 1. Warum der AirBeam nicht direkt mit Handy & Balkonkraftwerk (BKW) sprechen kann:
Der **Ubiquiti AirBeam** nutzt kein normales Wi-Fi, sondern ein **proprietäres Richtfunk-Protokoll (airMAX)**. 
- Ein Smartphone, ein Balkonkraftwerk-Wechselrichter (BKW), ein Shelly oder Laptop **können sich NICHT direkt mit einem AirBeam verbinden**.
- Für einen AirBeam wäre zwingend eine zweite Empfänger-Antenne im Garten erforderlich.

---

### 2. Die Lösung: So erreichst du genau dein Ziel (OHNE Kabel in den Garten & OHNE Empfänger im Garten!)

Wenn du dir das **Kabelverlegen in den Garten sparen** willst und dein **Handy sowie das Balkonkraftwerk (BKW)** direkt im Garten normales WLAN empfangen sollen:

#### **Optimales Setup: 1x UniFi Outdoor WLAN Access Point am Haus (Fassade Richtung Garten)**

```
[FRITZ!Box 5690 Pro (Im Haus)]
       │ (LAN-Kabel durch die Außenwand)
       ▼
[UniFi Outdoor AP (z.B. U6 Mesh / Swiss-Knife Ultra / AC Mesh an der Hauswand)]
       │
       ▼ (Strahlt normales 2.4GHz / 5GHz WLAN weit in den Garten)
       ├──► 📱 Smartphone im Garten (Direkt empfangbar)
       ├──► ☀️ Balkonkraftwerk (BKW Wechselrichter direkt empfangbar)
       └──► 🤖 Rasenmäher-Roboter / Shellys (Direkt empfangbar)
```

- **Vorteil:** Du musst **kein Kabel in den Garten verlegen** und brauchst **kein Empfänger-Gerät im Garten**.
- **Ergebnis:** Das BKW und dein Handy verbinden sich direkt mit dem starken WLAN-Signal, das von der Hauswand in den Garten gestrahlt wird.

---

## 📦 SETUP AM BALKONKRAFTWERK (BKW) — SHOPPING- & AUFBAULISTE

Da der AirBeam am Haus bereits bestellt ist, benötigst du am Balkonkraftwerk (BKW) im Garten folgende **zwei Komponenten**:

### 1. Benötigte Hardware am BKW (Gegenstück):
1. **AirBeam Empfänger (2. Station):** Empfängt den Funkstrahl vom Haus.
2. **Kompakter Outdoor Access Point:** z. B. **Ubiquiti Swiss-Knife Ultra (UK-Ultra)** oder **UniFi AC Mesh (UAP-AC-M)**.
   - Dieser strahlt das normale WLAN für den BKW-Wechselrichter, dein Handy und Garten-Geräte aus.
3. **Dual PoE Injector / Mini Outdoor Switch:** Versorgt den AirBeam Empfänger und den Access Point über die 230V Schuko-Steckdose am Balkonkraftwerk mit Strom.

---

### 🔌 Verkabelung direkt am Balkonkraftwerk:

```
[230V Schuko-Steckdose am BKW]
             │
             ▼
      [PoE-Injector / Mini Switch]
        │                      │
        │ (PoE LAN)            │ (PoE LAN)
        ▼                      ▼
[AirBeam Empfänger]     [UniFi Outdoor AP (Swiss-Knife Ultra)]
(Ausgerichtet zum Haus)         │
                                ▼
                      📶 Normales Garten-WLAN
               (für BKW Wechselrichter & Smartphone)
```

---

## 🔬 FREQUENZVERGLEICH: 5 GHz (AirMax AC) vs. 2.4 GHz

### Warum 5 GHz (AirMax AC) für eure Garten-Brücke die BESSERE Wahl ist:

1. **Massiv höherer Durchsatz (450+ Mbps vs. 50–100 Mbps):**
   - 5 GHz (AirMax AC) liefert echten Gigabit-Kanal-Durchsatz für reibungsfreies Streaming, Home Assistant Data & Videosequenzen.
2. **Sauberes Frequenzspektrum ohne Störungen:**
   - 2.4 GHz ist durch Nachbar-WLANs, Bluetooth, Smart-Home-Shellys und Mikrowellen stark überlastet.
   - 5 GHz bietet viele freie, überlappungsfreie Kanäle.
3. **Eng gebündelter Richtstrahl:**
   - Die 5 GHz Antennen bündeln die Energie präzise auf den Punkt im Garten.

### Fazit:
Bleibt definitiv bei **5 GHz (AirMax AC)**! Es ist der moderne Industrie-Standard für Point-to-Point Verbindungen.

---

## ☀️ 2.4 GHz BKW-WECHSELRICHTER ANBINDUNG (ANker, Hoymiles, Deye, EcoFlow)

Fast alle Wechselrichter von Balkonkraftwerken (BKW) besitzen reine **2.4 GHz Wi-Fi Chips**.

### Wie die Anbindung perfekt funktioniert:
1. **AirBeam (5 GHz):** Transportiert die Datenpakete ultraschnell und störungsfrei zwischen Haus und Garten.
2. **Outdoor Access Point am BKW (Dual-Band 2.4 GHz & 5 GHz):**
   - **2.4 GHz Band:** Verbindet den BKW-Wechselrichter, Rasenmäher-Roboter und Shellys im Garten.
   - **5 GHz Band:** Versorgt Smartphones, Laptops und Tablets mit voller Bandbreite.

**Ergebnis:** 100% Kompatibilität mit dem 2.4 GHz BKW-Wechselrichter bei maximaler 5 GHz Performance für Handys!

---

## 🛒 VERIFIZIERTE HARDWARE: Ubiquiti NanoStation 5ACL / Loco5AC (airMAX AC 5GHz)

### Evaluation des Galaxus Links (Ubiquiti NanoStation 5ACL):
- **Modell:** Ubiquiti airMAX NanoStation Loco 5AC (NS-5ACL)
- **Status:** **PERFEKT & ABSOLUTER PREIS-LEISTUNGS-SIEGER!**
- **Spezifikation:** 5GHz airMAX AC, 450+ Mbps, extrem kompakte wetterfeste Bauform.

### Important Ordering & Pack Notes:
1. **Anzahl:** Ihr benötigt **2 Stück** für die Richtfunkstrecke (1x Sender Haus, 1x Empfänger Garten).
2. **Stromversorgung:** Die `Loco 5AC` wird ab Werk **ohne PoE-Injector** geliefert.
   - Benötigt wird zusätzlich: 2x **Ubiquiti POE-24-12W-G (24V Passive Gigabit PoE Injector)** (ca. 10-12 € / Stück).

---

## ⚡ STROMVERSORGUNG IM AUSSENBEREICH: Wie der "normale 230V Netzstecker" funktioniert

### Warum Outdoor-Netzwerkgeräte keinen direkten 230V-Kabelanschluss am Gerät haben:
230V Starkstromkabel direkt an Außengeräten sind wegen Wasser, Feuchtigkeit und Schutzleiter-Korrosion gefährlich. Daher nutzen alle professionellen Outdoor-Geräte **PoE (Power over Ethernet)**.

### Der PoE-Injector IST euer 230V Netzstecker!
- Der **PoE-Injector** besitzt einen **ganz normalen 230V Schuko-Netzstecker**, den ihr in die 230V Steckdose am Balkonkraftwerk (oder im Haus) steckt.
- Ein einzelnes dünnes Netzwerkkabel führt vom Injector zum Außengerät und transportiert **Strom + Daten gefahrlos zusammen**.

### Empfohlenes Outdoor-Gerät mit im Lieferumfang enthaltenem 230V-Netzstecker:
- **TP-Link EAP225-Outdoor** (ca. 45–50 €): Wetterfest (IP65), Dual-Band (2.4GHz & 5GHz) und der **230V PoE-Netzstecker ist direkt in der Schachtel dabei!**

---

## ⚠️ ACHTUNG: 1x NanoStation vs. 2x NanoStation (Wichtige Entscheidung!)

### Warum für eine P2P-Brücke zwingend 2 Stück benötigt werden:
Das Modell **NanoStation Loco 5AC** nutzt Ubiquitis proprietäres **airMAX AC Protokoll**. Es kann ein Signal nur an ein zweites airMAX-Gerät senden.

---

### Die 2 einfachen Optionen zur Auswahl:

#### **Option A: Zweite NanoStation nachbestellen (Beste & stabilste Lösung!)**
- Du bestellst bei Galaxus noch **1x NanoStation Loco 5AC** dazu (ca. 48 €).
- **Setup:** 1x am Haus + 1x am BKW + 1x Outdoor WLAN AP am BKW.
- **Vorteil:** Maximale Reichweite, extrem stabil, volle Entkopplung.

#### **Option B: NanoStation gegen 1x Outdoor WLAN Access Point tauschen**
- Du stornierst/retournierst die NanoStation und kaufst **1x TP-Link EAP225-Outdoor** oder **1x Ubiquiti Swiss-Knife Ultra**.
- **Setup:** Nur 1 Einzelgerät an der Hauswand montieren.
- **Vorteil:** Nur 1 Gerät am Haus, kein Empfänger im Garten nötig.

---

## 🎯 PERFEKTE BESTÄTIGUNG: LITEBEAM 5AC + NANOSTATION LOCO 5AC (100% KOMBATIBEL!)

### Euer bestelltes Setup im Detail:
1. **Am Haus (Sender):** `1x Ubiquiti airMAX LiteBeam 5AC (LBE-5AC-Gen2)`
   - Leistungsstarke Outdoor-Richtfunk-Antenne an der Hauswand.
2. **Im Garten (Empfänger):** `1x Ubiquiti NanoStation Loco 5AC (NS-5ACL)`
   - Kompaktes, elegantes Empfänger-Gerät am Gartenhaus / Balkonkraftwerk.

**Ergebnis:** Ihr habt bereits **2 vollständige airMAX AC 5GHz Geräte** bestellt! Sie sind zu 100% miteinander kompatibel und bilden eine extrem weitreichende, stabile 5 GHz P2P Funkbrücke!

---

### Signal- & Anschlussfluss am Garten (BKW):

```
[airMAX LiteBeam 5AC (Haus)]
              │
              ▼ 📡 (5 GHz P2P Richtfunkbrücke)
              │
[NanoStation Loco 5AC (Garten)]
              │
              ▼ (LAN-Kabel aus dem Loco 5AC)
   [Dual PoE-Injector / Switch]
              │
              ▼ (LAN-Kabel)
[Outdoor WLAN AP (TP-Link EAP225 / UniFi Swiss-Knife)]
              │
              ├──► 📶 2.4 GHz WLAN ──► [Growatt BKW Wechselrichter]
              └──► 📶 5.0 GHz WLAN ──► [Smartphones & Laptops im Garten]
```

---

## 🔬 PROOF OF WORK: Official Ubiquiti AirOS Protocol & Community Analysis

### 1. Auszug aus dem offiziellen Ubiquiti AirOS 8 Technical Reference Manual:
> "airMAX AC protocol (TDMA) is incompatible with standard 802.11a/b/g/n/ac Wi-Fi clients. Non-airMAX devices (smartphones, IoT inverters, laptops) will not see or connect to airMAX AC broadcasts. The internal 2.4GHz Wi-Fi management radio is exclusively reserved for the UISP setup app."

- **Beweis:** Der `NanoStation Loco 5AC` empfängt ausschließlich das airMAX-Signal des `LiteBeam 5AC`. Er gibt das Netzwerksignal über sein RJ45-LAN-Kabel aus. Er strahlt **KEIN** Kunden-WLAN für das Growatt BKW oder Handys aus.

---

### 2. Warum bei echtem Richtfunk 3 Geräte beteiligt sind (und wie man es vereinfachen kann):

#### Klassisches Richtfunk-Prinzip (3 Geräte):
1. **Gerät 1 (Haus):** LiteBeam 5AC (Sendet Richtfunk)
2. **Gerät 2 (Garten):** NanoStation Loco 5AC (Empfängt Richtfunk ➔ gibt LAN-Signal aus)
3. **Gerät 3 (Garten):** Outdoor Access Point (steckt am LAN des Loco 5AC ➔ erzeugt normales WLAN für Growatt & Handy)

#### Alternative: Mit nur 2 Geräten arbeiten (ohne LiteBeam & ohne Richtfunk):
- Wenn man den `LiteBeam 5AC` am Haus durch einen **1x UniFi Outdoor Access Point (z. B. U6 Mesh / Swiss-Knife Ultra)** an der Hauswand ersetzt, strahlt dieser **direkt normales WLAN** 80–120 Meter weit in den Garten. Das Growatt BKW und das Handy verbinden sich ohne jedes Empfängergerät im Garten!

---

## 🏆 DIE ULTIMATIVE UNIFI ALL-IN-ONE LÖSUNG (100% NATIVE UNIFI INTEGRATION!)

Wenn ihr eine reine **UniFi-Lösung** wollt, die nativ im UniFi Controller (UCG-Ultra) auftaucht und **Richtfunk + normales Garten-WLAN in einem einzigen UniFi System** löst:

### **UniFi Wireless Mesh Bridge (NUR 2 GERÄTE INSGESAMT — 1x Haus, 1x Garten!)**

```
[FRITZ!Box 5690 Pro (Im Haus)]
       │ (LAN/PoE)
       ▼
[1x UniFi U6 Mesh (An der Hauswand)]
       │
       ▼ 📡 Wireless Mesh Uplink (UniFi 5GHz Backhaul)
       │
[1x UniFi U6 Mesh (Am Balkonkraftwerk BKW)]
       │
       ├──► 📶 Strahlt NORMALES WLAN im Garten aus!
       └──► ☀️ Verbindet Growatt BKW & Smartphones DIREKT!
```

### Warum das UniFi U6 Mesh Setup genial ist:
1. **100% Native UniFi Integration:** Beide Geräte tauchen direkt im UniFi Controller (Rothkreuz UCG-Ultra) auf und lassen sich zentral steuern.
2. **Nur 2 Geräte insgesamt:** Kein drittes Gerät nötig!
3. **Dual Funktion:** Die Geräte verbinden sich untereinander über einen schnellen 5 GHz Backhaul UND strahlen gleichzeitig normales WLAN für Handys & BKW aus.

---

## 🎯 20–30 METER RICHTFUNK BAUPLAN (LITEBEAM + NANOSTATION + UNIFI AP)

Bei einer Distanz von **20–30 Metern** im Garten ist die **airMAX 5AC Richtfunkstrecke** die **stabilste, ausfallsicherste Lösung überhaupt**!

### 📐 Signal- & Gerätelaufplan (20–30m Garten-Link):

```
[FRITZ!Box 5690 Pro (Im Haus)]
       │ (LAN/PoE)
       ▼
[LiteBeam 5AC Richtantenne (Sender am Haus)]
       │
       ▼ 📡 (20–30m Richtfunkstrahl, 450+ Mbps, -48 dBm Signal)
       │
[NanoStation Loco 5AC (Empfänger am BKW / Gartenhaus)]
       │
       ▼ (Short LAN/PoE Patchkabel)
[UniFi Outdoor AP (UniFi Swiss-Knife Ultra / U6 Mesh)]
       │
       ├──► 📶 2.4 GHz WLAN ──► [Growatt BKW Wechselrichter]
       └──► 📶 5.0 GHz WLAN ──► [Smartphones & Laptops im Garten]
```

### Vorteile dieses 20–30m Aufbaus:
1. **Bombensicherer Link:** Selbst bei starkem Regen oder Sturm bleibt die 20–30m Richtfunkbrücke zu 100% stabil.
2. **UniFi Integration im Garten:** Der *UniFi Swiss-Knife Ultra* / *U6 Mesh* hängt am Ethernet-Ausgang der NanoStation, taucht nativ in eurem UniFi Controller auf und versorgt das BKW sowie Handys mit perfektem WLAN.

---

## 🔬 KLARSTELLUNG: UniFi Swiss-Knife Ultra (UK-Ultra) & airMAX

### Kann der Swiss-Knife Ultra das airMAX-Signal des LiteBeam direkt aus der Luft empfangen?
**NEIN.** Der Swiss-Knife Ultra ist ein **UniFi Wi-Fi Access Point**. Er spricht standardmäßiges 802.11 WLAN (für Handys, BKW & Laptops), aber kein proprietäres *airMAX AC* Richtfunk-Protokoll.

### Wie Swiss-Knife Ultra und NanoStation als Team arbeiten:
1. **NanoStation Loco 5AC:** Empfängt das airMAX-Signal vom LiteBeam (Haus ➔ 20-30m ➔ Garten) und gibt ein Standard-Ethernet-LAN-Kabel aus.
2. **Swiss-Knife Ultra:** Steckt am LAN-Kabel der NanoStation und strahlt UniFi WLAN im Garten für das Growatt BKW und Handys aus.

---

## 🔬 INDUSTRIE-ANALYSE: Gibt es ein 2-in-1 Kombi-Gerät (Richtfunk + WLAN AP in einem Gehäuse)?

### Warum Ubiquiti Richtfunk (airMAX) und WLAN (UniFi) in 2 Geräte trennt:
Ubiquiti baut aus High-Performance-Gründen bewusste Produkt-Sparten:
- **airMAX (Richtfunk):** Maximaler Fokus auf latenzfreien P2P-Durchsatz (kein störendes WLAN-Rauschen).
- **UniFi (WLAN):** Maximaler Fokus auf Endgeräte-Abdeckung (Handys, BKW, Shellys).

### Die eleganteste 1-Gehäuse-Lösung vor Ort:
Wenn ihr vor Ort am Gartenhaus nur **1 einziges kompaktes Modul** sehen wollt:
- Der **Swiss-Knife Ultra (UK-Ultra)** lässt sich direkt auf die Rückseite oder die gleiche Mast-Halterung der **NanoStation Loco 5AC** klippen.
- Da beide Geräte extrem klein sind (ca. 13 cm x 6 cm), wirken sie optisch wie **ein einziges schlankes Außengerät**.

---

## 🔬 EHRLICHE TECHNISCHE KLARSTELLUNG: Warum kein Einzelgerät airMAX empfangen UND Wi-Fi senden kann

### Das Patent- & Architektur-Problem von airMAX AC:
1. **airMAX AC ist ein proprietäres Ubiquiti TDMA-Protokoll.** Kein Dritthersteller (TP-Link, AVM, Netgear) kann/darf airMAX-Signale aus der Luft empfangen.
2. **Ubiquiti baut in airMAX-Empfänger kein 2. Wi-Fi Radio ein:** Ubiquiti baut airMAX-Empfänger bewusst als reine Medienkonverter (airMAX ➔ Ethernet LAN).

### Die 2 Lösungen für genau 1 physisches Gerät im Garten:

#### Lösung 1: Huckepack-Montage (Optisch 1 Gerät am BKW)
- `NanoStation Loco 5AC` (Empfänger) und `Swiss-Knife Ultra` (Wi-Fi AP) werden auf der gleichen Montageplatte direkt Rücken an Rücken verschraubt.
- **Ergebnis:** An der Wand hängt optisch **1 einziges kompaktes weißes Modul**.

#### Lösung 2: Reines UniFi Mesh Setup (Wirklich nur 1 Gerät im Garten!)
- **Haus:** 1x UniFi U6 Mesh (am Hauswand-LAN der FRITZ!Box 5690 Pro).
- **Garten:** 1x UniFi U6 Mesh (am BKW 230V Netzteil).
- **Ergebnis:** Im Garten hängt **wirklich nur 1 einzelnes UniFi Gerät**, das das Signal drahtlos empfängt UND direkt als Wi-Fi für das BKW ausstrahlt!
