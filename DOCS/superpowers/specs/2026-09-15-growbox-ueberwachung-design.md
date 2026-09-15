# GrowBox — Überwachung und Steuerung, Design

**Stand:** 15.09.2026 · **Autor:** Claude · **Auftrag:** Wolf („auf Profi-Developer-Level bauen")
**Anlage:** GrowBox 120×60, Shelly PowerStrip Gen4 `10.4.0.13`, Tapo-Kamera `10.4.0.35`

---

## 1. Ziel

Die GrowBox soll **selbst dann sicher laufen, wenn Home Assistant aus ist**, und gleichzeitig
sichtbar machen, was drin passiert. Kein Blindflug, keine Automatik, die lautlos überstimmt wird.

Nicht Ziel: Düngung, Bewässerung, Ertragsprognose.

## 2. Ist-Zustand (15.09.2026 gemessen, nicht angenommen)

| Bereich | Befund |
|---|---|
| Schalten | 4 Ausgänge am Shelly PowerStrip, funktionieren |
| **Messen** | 🔴 **nichts** — kein Temperatur-, kein Feuchtewert |
| **Kamera** | vorhanden (`10.4.0.35`), aber **nicht eingebunden** |
| Dashboard | 4 Schalter, sonst leer |

### 2.1 🔴 Befund 1: Die Steuerung liegt im Gerät, nicht in Home Assistant

`Schedule.List` auf `10.4.0.13` (rev 12):

| Zeitpunkt | Aktion |
|---|---|
| `@sunrise-1h` | Ausgang 3 ein |
| `@sunrise-30min` | Ausgang 1 **und** 0 ein |
| `@sunset` | Ausgang 1 aus |
| `@sunset+1h` | Ausgang 3 aus |

Dazu `Switch.GetConfig` je Ausgang:

| Ausgang | Selbsttätiger Timer | Bedeutung |
|---|---|---|
| 0 | — | wird nur eingeschaltet, nie abgeschaltet |
| 1 | `auto_off` nach **18 h** | Sicherheitsabschaltung (Licht) |
| 2 | 🔴 `auto_on` nach **5 min** | **schaltet sich selbst wieder ein** |
| 3 | — | |

**Konsequenz:** Eine Home-Assistant-Automatik, die Ausgang 2 abschaltet, wird fünf Minuten
später vom Gerät überstimmt — ohne Fehlermeldung, ohne Spur im Protokoll. Das ist der
dokumentierte Stolperstein vom 06.09.2026 und der Grund, warum „smarte Steuerung" bisher
nicht funktionieren *konnte*.

### 2.2 🔴 Befund 2: Der Klimasensor existiert nicht mehr

`sensor.wolf_temp_sensor_*` (Temperatur, Luftfeuchte, Batterie) stehen auf `unavailable` —
**alle vier, auch die Batterie**. Ursache: Die Entitäten stammen nicht von dieser Anlage,
sondern kamen über `remote_homeassistant` aus der **Stockenweiler-Instanz**. Dort existieren
sie inzwischen **gar nicht mehr** (`10.1.0.248` direkt abgefragt: kein Treffer). Übrig sind
tote Spiegelbilder.

Die Überwachung der Box hing damit an: fremder Instanz → VPN-Tunnel → Kopplung → Batteriegerät.
Vier Glieder, von denen jedes einzeln reißen kann — und als es riss, fiel es niemandem auf.

## 3. Entwurfsentscheidungen

### 3.1 Wer steuert? Gerät für den Grundrhythmus, HA für die Ausnahme

**Entscheidung: Der Lichtzyklus bleibt im Shelly.** Pflanzen verzeihen keinen ausgefallenen
Server. Der Grundrhythmus muss laufen, wenn HA, Netz oder Anker ausfallen.

**Home Assistant bekommt die Ausnahmen:** Not-Lüftung bei Hitze, Alarm bei Grenzwerten,
Aufzeichnung, Bild. HA schaltet nur Ausgänge, die **keinen** selbsttätigen Timer tragen.

**Daraus folgt verbindlich:**
- Ausgang 2 (`auto_on 300 s`) ist für HA **tabu**, solange der Timer besteht. Entweder HA
  bekommt ihn ganz (Timer entfernen) oder das Gerät behält ihn — **nicht beides**.
- Jede Automatik dokumentiert im Kopf, welcher Ausgang wem gehört.
- Vor jeder Änderung an einer Automatik: `Schedule.List` und `Switch.GetConfig` lesen.

### 3.2 Messen: eigener Sensor auf dieser Anlage

**Entscheidung: Der neue Sensor wird lokal eingebunden**, nicht über eine zweite Instanz
gespiegelt. Ein Messwert, von dem eine Automatik abhängt, darf nicht über drei fremde
Glieder laufen.

Anforderungen an die Hardware: Temperatur **und** Luftfeuchte, netzbetrieben oder mit
Batteriestandsmeldung, lokal auslesbar ohne Cloud-Zwang. Ein Shelly H&T Gen3 erfüllt das und
passt zur vorhandenen Landschaft (Aufgabe #1177 liegt dafür bereits vor).

**Abgeleiteter Wert: VPD** (Dampfdruckdefizit) aus Temperatur und Luftfeuchte — die Kennzahl,
nach der man eine Box tatsächlich fährt, statt nach zwei Einzelwerten.

### 3.3 🔴 Der Wächter über den Wächter

**Eine fehlende Messung ist selbst ein Alarm.** Genau daran ist der jetzige Zustand
unbemerkt geblieben.

- Regel „Messwert älter als 30 Minuten" → Meldung. Nicht „Wert zu hoch" allein, denn die
  schweigt, wenn der Wert ganz wegfällt.
- Batteriestand unter 20 % → rechtzeitige Meldung, bevor die Messung ausfällt.
- Beide Regeln in die bestehende Kette: `critical` → Telegram an Wolf, `warning` → Agenten.
  Keine neuen Alarmwege (Rote Linie).

### 3.4 Kamera

Tapo an `10.4.0.35`, aus Home Assistant erreichbar (Ports 554/443/2020 geprüft).
**Bleibt im IoT-Netz** — keine Netzverschiebung, Datenschutz vor Bequemlichkeit.

- Einbindung über die bereits installierte Integration *Tapo: Cameras Control* mit einem
  **lokalen Kamerakonto** (Tapo-App → Erweitert → Kamerakonto), nicht über die Cloud.
- Zugangsdaten trägt **Wolf** ein. Agenten fassen keine Passwörter an.
- Auf dem Dashboard: Live-Bild plus ein tägliches Standbild zur festen Uhrzeit (Wachstums-
  vergleich). Zeitraffer ist Kür, nicht Teil dieser Stufe.

## 4. Aufbau

**Ansicht „GrowBox"** — Reihenfolge nach der Frage „stimmt etwas nicht?":

1. **Zustandszeile** — grün, solange Messwert frisch, Temperatur und VPD im Rahmen,
   Lichtzyklus plausibel. Sonst benennt sie das Problem.
2. **Kamerabild**
3. **Klima** — Temperatur, Luftfeuchte, VPD, dazu 24-h-Verlauf
4. **Ausgänge** — vier Schalter, jeder beschriftet mit seiner Funktion **und** dem Hinweis,
   ob er einem Gerätetimer unterliegt
5. **Strom** — Verbrauch je Ausgang, Tagesenergie

## 5. Grenzfälle

- **Sensor fällt aus:** Not-Lüftung geht in einen definierten sicheren Zustand (Abluft an),
  Zustandszeile wird rot, Meldung raus. **Keine Automatik rät weiter** auf Basis alter Werte.
- **HA fällt aus:** Gerätezeitpläne laufen weiter, Licht bleibt korrekt. Erwartetes Verhalten,
  kein Fehler.
- **Kamera nicht erreichbar:** Kachel zeigt letzten Stand mit Zeitstempel, keine Fehlermeldung
  über das ganze Dashboard.
- **Gerätetimer wird verändert:** Prüfung vergleicht `Schedule.List` gegen einen hinterlegten
  Sollstand und meldet Abweichungen — sonst fällt eine stille Änderung wieder erst nach
  Wochen auf (Lehre aus dem Shelly-Vorfall vom 14.09.).

## 6. Abnahmekriterien

Gemessen am Ergebnis, nicht am Rückgabewert.

1. Temperatur und Luftfeuchte liefern Werte; VPD wird berechnet und angezeigt.
2. **Sensor testweise stromlos/außer Reichweite** → innerhalb 30 min kommt eine Meldung an.
   *Eine Prüfung, die nicht scheitern kann, zählt nicht.*
3. Not-Lüftung schaltet bei künstlich ausgelöstem Grenzwert nachweislich — und wird
   **nicht** binnen fünf Minuten vom Gerätetimer überstimmt (Beleg: Schaltzähler).
4. Live-Bild der Kamera auf der Ansicht sichtbar, Bildschirmfoto als Beleg.
5. Dokumentiert: welcher Ausgang wem gehört (Gerät oder HA), im Dashboard und in `NOW.md`.
6. Ein Neustart von Home Assistant ändert am Lichtzyklus nichts.

## 7. Reihenfolge

1. Sensor beschaffen und **lokal** einbinden (#1177) — ohne Messwert ist alles andere Zierde
2. Tote Spiegel-Entitäten `wolf_temp_sensor_*` ausblenden
3. Kamera einbinden (#1472, Zugangsdaten Wolf)
4. Zustandszeile und Wächter-Regeln
5. Not-Lüftung — erst nachdem die Eigentumsfrage bei Ausgang 2 entschieden ist
6. Dashboard-Ansicht neu aufbauen

## 8. Offene Entscheidung für Wolf

**Ausgang 2 (Abluft):** Der Gerätetimer `auto_on 300 s` und eine HA-Automatik schließen
einander aus. Entweder der Timer bleibt (dann regelt allein das Gerät und HA schaut nur zu),
oder er wird entfernt (dann regelt HA, und bei HA-Ausfall lüftet nichts mehr).
**Ohne diese Entscheidung wird keine Lüftungsautomatik gebaut.**
