# Router Lease Reconciliation Runbook

## Ziel

Dieses Runbook beschreibt den sauberen manuellen Abgleich zwischen der Easy-Box-Lease-Ansicht und dem kanonischen Inventar.

Es ist bewusst auf den aktuellen Zustand zugeschnitten:

- EasyBox-Login ist manuell moeglich
- ein authentifizierter Browser-Kontext kann inzwischen `overview.json` reproduzierbar abrufen
- die volle Lease-/DHCP-Navigation bleibt dennoch browser-first, solange nicht jede Unterseite headless belegt ist

## Readiness

Vor dem eigentlichen Lease-Abgleich:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make easybox-browser-probe
make easybox-authenticated-overview
make inventory-resolution-check
```

Erwartung:

- `browser_probe_ready=yes`
- `authenticated_overview_ready=yes`
- `inventory_unknown_review_count` zeigt den noch offenen Rest sauber

## Aktuell offene Punkte

### Bereits headless aufgeloeste Router-Labels

- `fireTV` -> `192.168.2.100`
- `Franz_iphone` -> `192.168.2.122`
- `udhcpc1.21.1` -> `192.168.2.101`
- `udhcp 1.24.1` -> `192.168.2.134`
- `Shelly_plug_repeater` -> `192.168.2.114`
- `shellyplugsg3-8cbfea968024` -> `192.168.2.107`

### Unknown-Review Hosts

- `192.168.2.141`
- `192.168.2.142`
- `192.168.2.143`
- `192.168.2.144`

## Was die EasyBox hier wahrscheinlich tut

Der aktuelle Forschungsstand ist jetzt zweigeteilt:

- offiziell dokumentiert ist das normale DHCP-/Reservierungsverhalten der EasyBox
- die konkrete `overview.json`-Struktur ist nicht als API dokumentiert und wurde lokal browser-seitig nachvollzogen

Saubere Arbeitsannahmen:

1. Die EasyBox fuehrt eine Liste "bereits bekannter Geraete".
   - Das Handbuch erwaehnt bei MAC-Filter und Band-Steering jeweils die Auswahl "bereits bekannter Geraete".
   - Praktisch bedeutet das: Router-Namen koennen aus einer internen Geraeteliste stammen und muessen nicht 1:1 der gerade per DNS sichtbare Hostname sein.
2. DHCP und statische Zuordnung laufen normal MAC-basiert.
   - Das Handbuch beschreibt den DHCP-Pool und statisches DHCP pro MAC-Adresse.
   - Fuer Reservierungen ist deshalb die MAC-Adresse wichtiger als ein schoener Router-Name.
3. `overview.json` ist ein UI-Backend fuer die Uebersichtsseite.
   - Lokal reproduziert: nach Login liefert `overview.json` die Felder `wifi_user` und `ethernet`.
   - Diese enthalten pipe-separierte Client-Datensaetze mit Name, MAC, IP, PHY/Band und Linkrate.
4. Router-Namen sind nicht immer "Geraetemodell".
   - `RE355` ist sehr wahrscheinlich der TP-Link-Repeater selbst.
   - `udhcpc1.21.1` und `udhcp 1.24.1` sehen nach DHCP-Client-Bezeichnern aus BusyBox/Embedded-Linux aus, nicht nach benutzerfreundlichen Hostnamen.
   - Apple-Geraete koennen wegen "Private Wi-Fi Address" mit privaten, netzbezogenen WLAN-MACs auftauchen.
5. Repeater-/Mesh-Naehe kann Mehrdeutigkeiten erzeugen.
   - In unseren lokalen Dumps tauchen bei einzelnen Clients sowohl Endgeraete-MACs als auch repeaternahe Darstellungen auf.
   - Fuer Reservierungen und finale Inventar-Eintraege ist deshalb immer die aktuelle Kombination aus `Name + MAC + IP` aus dem authentifizierten Overview-Dump massgeblich.

## Arbeitsreihenfolge

### 1. Router oeffnen

1. Auf dem ZenBook im Browser `https://192.168.2.1` oeffnen
2. Mit dem bekannten Easy-Box-Zugang einloggen
3. DHCP-/Geräte-/Lease-Liste oeffnen

### 2. Authentifizierten Router-Ueberblick zuerst sichern

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make easybox-authenticated-overview
```

Ziel:

- aktuelle Router-Namen, MACs und IPs als Read-only-Dump sichern
- danach nur noch die wirklich offenen Owner-Zuordnungen manuell schliessen

### 3. Unknown-Review danach schliessen

Prioritaet:

1. `.141-.144`
2. `Surface_Laptop` bzw. weitere neu sichtbare Router-Namen nur dann uebernehmen, wenn sie fachlich bestaetigt sind

Regel:

- nur bestaetigte Zuordnungen uebernehmen
- nichts raten
- wenn unklar, im Inventar explizit offen lassen

### 4. Shelly-Disambiguierung danach

Ziel:

- `.107`
- `.114`
- `Shelly_plug_repeater`
- `shellyplugsg3-8cbfea968024`

Sauberer Abschluss:

- jede Shelly-Bezeichnung genau einem Inventarobjekt zuordnen
- Growbox-Zuordnung beibehalten

### 5. Medien-/Haushaltslabels zuletzt

- `Surface_Laptop`
- doppelte oder alte Consumer-Labels wie `SonRoku` nur mit Zusatzbestaetigung anfassen

## Update-Regeln fuer das Inventar

Wenn ein Geraet sauber identifiziert ist, in [NETWORK_INVENTORY.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/NETWORK_INVENTORY.md) aktualisieren:

- `Owner`
- `Zone`
- `Device Class`
- `Mgmt`
- `Status`
- `Next Action`

Wenn ein Geraet nach dem Router-Abgleich weiter unklar ist:

- `unknown-review` beibehalten
- im `Next Action` notieren, was noch fehlt

## Definition of Done

Minimal fertig:

- `.141-.144` sind entweder identifiziert oder bewusst weiter offen mit klarer Notiz
- `Franz_iphone` ist entweder gemappt oder bewusst weiter offen

Fertig fuer Gateway-Cutover:

- `unknown-review` leer
- offene Router-only Labels geschlossen
- DHCP-Reservierungsplan dokumentiert
