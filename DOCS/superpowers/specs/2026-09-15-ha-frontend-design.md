# Home Assistant Frontend — Design

**Stand:** 15.09.2026 · **Autor:** Claude · **Auftrag:** Wolf („das gesamte Frontend optimieren")
**Instanz:** `home.frawo.tech` = VM 210 `haos` auf dem Anker, `10.1.0.40`, HA Core 2026.9.2

---

## 1. Ziel

Home Assistant so ordnen, dass Wolf auf jedem seiner Bildschirme **in einem Blick sieht, ob
etwas zu tun ist**, und das Alltägliche mit dem Finger bedienen kann — ohne zwischen 1850
Entitäten zu suchen, von denen die Hälfte weder zu seinem Haus gehört noch lebt.

Nicht Ziel: neue Geräte einbinden, Automationen umbauen, Sprachsteuerung.

## 2. Ist-Zustand (am 15.09.2026 gemessen, nicht geschätzt)

| Kennzahl | Wert |
|---|---|
| Entitäten im Register | 1850 (davon 454 bereits abgeschaltet, 247 davon alte Handy-Sensoren) |
| Entitäten mit Zustand | 1409 |
| davon lebendig | 899 |
| davon `unavailable`/`unknown` | **500** |
| aus der Kopplung „Stockenweiler" (`10.1.0.248`) | **1065** — keine einzige ausgeblendet |
| Geräte / Integrationen / Bereiche | 113 / 40 / 7 |

**Steuerbar (lebendig):** 9 Lichter · 87 Schalter · 16 Thermostate · 5 Medienspieler · 1 Sauger
**Brauchbare Messwerte:** 102 Problem-Melder · 71 Energie · 62 Temperatur · 35 Leistung · 25 Batterie

**Oberflächen heute:** `Übersicht` (Standard, YAML-Modus aus `ui-lovelace.yaml`, 7 Ansichten) ·
`JARVIS Terminal` (Ablage-Modus) · `Karte` · `Kiosk` (YAML) · **eine zweite `Übersicht`** in der
Seitenleiste.

**Zwei Befunde, die den Zustand erklären:**

1. Die Anlage läuft mit `lovelace: mode: yaml`. Änderungen in `.storage/lovelace` sind damit
   **wirkungslos** — HA liest ausschließlich `ui-lovelace.yaml`. Am 15.09. ging ein kompletter
   Dashboard-Umbau deshalb ins Leere.
2. In `configuration.yaml` fehlte beim Mushroom-Eintrag der Schlüssel `type` (er war zum
   Nachbareintrag gerutscht und dort dupliziert). Dadurch lud die Kartenbibliothek nie, und
   **jede** Mushroom-Kachel zeigte „Konfigurationsfehler". Am 15.09. behoben und im Browser
   verifiziert. Ohne diese Reparatur wäre jeder Entwurf unsichtbar geblieben.

## 3. Struktur — vier Oberflächen statt fünf gewachsenen

| Oberfläche | Für | Eigenschaft |
|---|---|---|
| **Kiosk** | Surface Go (an der Wand), fester Touchscreen, Wandtablet | Fingerflächen, ohne Seitenleiste, ohne Einstellungen. Vollwertig bedienbar — es ist die meistgenutzte Oberfläche |
| **Zuhause** | Handy, StudioPC | Gleiche Gestaltung, aber mit Zugang zu Technik und Einstellungen. Passt sich der Bildschirmbreite an |
| **Stockenweiler** | alle | Nur das Wichtige aus dem anderen Haus |
| **Karte** | alle | bleibt unverändert |

**Begründung:** Feste Wandbildschirme müssen gegen Verstellen geschützt sein, Handy und
Schreibtisch brauchen das Gegenteil. Das rechtfertigt genau zwei Haupt-Oberflächen — jede
weitere wird beim nächsten Umbau vergessen (Vorfall 15.09.).

**Gestaltung ist fingerfirst**, auch auf dem Schreibtisch: große Schaltflächen, ausreichend
Abstand. Am großen Bildschirm schadet das nichts, am Surface Go entscheidet es über
Benutzbarkeit.

## 4. Inhalte

### 4.1 Startbildschirm (Kiosk und „Zuhause" identisch aufgebaut)

Reihenfolge ist Absicht: **erst die Frage „muss ich etwas tun?", dann Bedienung.**

1. **Statuszeile** — fällt nur auf, wenn etwas ist: offene Fenster/Türen, Geräte ohne Strom,
   Temperaturgrenzen, Sicherung der Nacht nicht gelaufen, Meldung aus Stockenweiler.
   Im Normalfall eine ruhige Zeile „Alles in Ordnung".
   *Quelle: ausgewählte der 102 Problem-Melder und 62 Temperaturen — **ausgewählt**, nicht alle,
   sonst entsteht wieder Rauschen.*
2. **Vier bis sechs große Schaltflächen** — das täglich Gedrückte: Alles aus · Gemütlich ·
   Sauger · Radio.
3. **Räume** — je Kachel Licht, Temperatur und was dort wirklich schaltbar ist.
   Wohnräume: Wohnzimmer, Küche, Schlafzimmer. **Growbox, Inselhalle, Anker und Cyber_Space
   gehören nicht auf den Start** — das sind Technik- bzw. Fremdbereiche und bekommen eigene
   Ansichten.
4. **Aktueller Zustand** — Radio, Sauger, Verbrauch jetzt, Solarertrag heute.

**Nicht auf dem Start:** Einzelsensoren, Batterie- und Firmwarestände, Netzwerkgeräte. Das ist
Wartung und gehört unter *Technik*.

### 4.2 Weitere Ansichten

*Räume · Klima · Energie · Technik* (nur „Zuhause") · *GrowBox* · *Mobilität* (Dobby, Lastenrad) ·
*Entertainment*. Inhalte übernehmen, was der Umbau vom 15.09. bereits angelegt hat — er war
inhaltlich brauchbar, nur unsichtbar.

### 4.3 Stockenweiler

Eigene Oberfläche mit dem, worauf Wolf reagieren müsste: Temperaturen, Wasser/Nässe, Rauch,
Stromausfall, Erreichbarkeit der Anlage. Nicht mehr.

## 5. Aufräumen

**Grundregel (aus Schaden gelernt):** Am 07.09.2026 wurden 48 Entitäten gelöscht, die zu
lebenden Geräten gehörten. Deshalb galt zunächst: „Gelöscht wird nur, was beweisbar doppelt ist."

> ### 🔴 In dieser Umsetzung wird **nichts gelöscht**.

**Warum die ursprüngliche Löschregel verworfen wurde.** Das Review (Jarvis, 15.09.) verlangte
einen Identitätsbeleg je Paar statt bloßer Namensgleichheit. Die Messung gibt ihm recht — die
Regel wäre gefährlich gewesen:

| Messung über alle `_2`-Einträge mit gleichnamigem Gegenstück | Anzahl |
|---|---|
| Paare insgesamt | 195 |
| davon **gleiches Gerät** | **1** |
| davon gleiche Integration | 6 |

Stichproben zeigen, was `_2` tatsächlich meist bedeutet:

- `light.wohnzimmer_licht_2` (`gv2mqtt-…`) vs. Original (`govee_govee_…`) — **dieselbe Lampe über
  zwei verschiedene Integrationen**, beide echt.
- `sensor.verbindungsgeschwindigkeit_2` (`…bc:24:11:3f:43:0f`) vs. Original
  (`…bc:24:11:11:89:97`) — **verschiedene Geräte**, nur ähnlich benannt.
- `device_tracker.pixel_9_pro_2` (UniFi) vs. Original (HA-App) — **zwei Quellen für dasselbe
  Handy**, beide gewollt.

`_2` ist also überwiegend Home Assistants normale Namensvergabe bei Namensgleichheit und **kein
Hinweis auf eine Dublette**. Eine Löschung nach diesem Muster hätte den Vorfall vom 07.09.
wiederholt.

**Was stattdessen passiert — ausschließlich ausblenden (`hidden_by`), vollständig umkehrbar:**

1. **Toter Rest ausblenden.** Was keinen Zustand liefert, verschwindet aus den Standard-Ansichten.
2. **Stockenweiler ausblenden, nicht abschalten.** `disabled_by` würde die Entität gar nicht erst
   anlegen; `hidden_by` erhält sie samt Zustand. **Belegt am 15.09.:**
   `switch.shellypstripg4_206ef102e44c_output_1` ist `hidden_by: integration` und liefert
   trotzdem den Zustand `on`.
   *Einschränkung aus dem Review:* „versteckt" ist eine Eigenschaft der Oberfläche und des
   Registers — es garantiert nicht, dass jeder Karteneditor die Entität ausblendet.
   **Deshalb Vorabtest mit drei Entitäten**, bevor die Masse angefasst wird: bleibt der Zustand,
   verschwindet sie aus der Standardsuche, lässt sie sich trotzdem bewusst auf dem
   Stockenweiler-Dashboard verwenden?
3. **Löschen bleibt einem späteren, eigenen Vorgang vorbehalten** — mit Identitätsbeleg je Paar
   (gleiches Gerät bzw. gleiche Herkunft der Kennung), vorgelegter Liste und Wolfs Freigabe.
4. **Doppelte „Übersicht"** in der Seitenleiste entfernen.
5. **Zeichensatz reparieren:** `lovelace.jarvis_touch` enthält doppelt kodierte Umlaute und
   Emoji (`Ã°Å¸Å½Âµ` statt 🎵). Datei mit korrekter Kodierung neu schreiben.

**Erwartetes Ergebnis:** Von 1409 Entitäten mit Zustand sind 1065 aus Stockenweiler. Nach dem
Ausblenden bleiben rund 340 eigene übrig, davon nochmals ein Teil tot — **sichtbar bleiben grob
250–350 Entitäten**. Das ist der eigentliche Hebel: Nicht die Dashboards sind zu voll, die
Auswahllisten sind es.

## 6. Betriebs- und Sicherheitsanforderungen

- **Vor jeder Änderung Sicherung** mit Datum (`*.bak-YYYYMMDD`): `configuration.yaml`,
  `ui-lovelace.yaml`, `.storage/core.entity_registry`, betroffene Dashboard-Dateien.
- 🔴 **Eine Rohkopie von `.storage` im laufenden Betrieb ist keine belastbare Sicherung**
  (Review-Auflage): Home Assistant schreibt diese Dateien verzögert, eine Kopie kann auf halbem
  Stand stehen. Maßgeblich ist eine **HA-eigene Sicherung** (`ha backups new`), die Rohkopien
  dienen nur dem schnellen Zurücklegen einzelner Dateien.
- **Wiederherstellungsweg festlegen und einmal durchspielen** — eine Sicherung gilt erst als gut,
  wenn sie zurückgelesen wurde. 🔴 **Aber kein Voll-Rückspielen auf der Produktivinstanz**
  (Review-Auflage): Der Nachweis läuft als frische Sicherung (`ha backups new`), Ablage auf einem
  externen Ziel, Entpacken des Archivs in einen getrennten Prüfpfad und Zurücklesen eines
  Dashboards daraus. Erst danach die Massenänderung.
- **Ausgangslage dazu (Stand 15.09.2026):** Es existiert genau **eine** HA-eigene Sicherung, und
  die stammt vom **03.04.2026** (13,36 MB, partiell). Vor jeder Änderung ist also ohnehin ein
  frischer Sicherungspunkt fällig — unabhängig von diesem Vorhaben.
- **Ausfall von Home Assistant selbst muss auffallen:** externe Erreichbarkeitsprüfung mit
  Alarmweg (die Blackbox-Prüfung auf CT155 deckt bisher die Eltern-Instanz ab, nicht diese).
- 🔴 **Einzige Konfigurationsquelle ist `ui-lovelace.yaml`** samt eingebundener YAML-Dateien.
  Keine parallele Pflege in `.storage` — genau daran ist der Umbau vom 15.09. gescheitert.
- **Shelly `10.4.0.11` wird nicht geschaltet** (Rote Linie). Er darf angezeigt werden, Schaltflächen
  dazu kommen nicht aufs Dashboard.
- **Keine VLAN-Verschiebung** von Geräten mit Mikrofon oder Kamera — Datenschutz vor Funktion.
- Dateien für Linux mit **LF-Zeilenenden und UTF-8** schreiben (Ursache des Zeichensatz-Fehlers).
- Änderungen an `configuration.yaml` erfordern einen Neustart von HA; `ha core check` vorher.
- **Kein Automatismus, der Datensätze vervielfältigt** (Rote Linie 6).

## 7. Grenzfälle

- **Gerät kommt zurück, dessen Entität ausgeblendet wurde:** Es liefert wieder Werte, ist nur
  nicht sichtbar — Einblenden genügt, kein Neuanlegen. Genau deshalb wird ausgeblendet statt
  gelöscht.
- **Ein `_2`-Eintrag ohne lebendes Gegenstück:** wird **nicht** gelöscht, sondern ausgeblendet.
- **Stockenweiler-Instanz ist offline:** Die Statuszeile meldet „Stockenweiler nicht erreichbar" —
  ein fehlender Wert ist selbst ein Alarm, keine stille Lücke.
- **Kiosk-Bildschirme unterschiedlicher Größe** (Surface Go 10,5", Touchscreen, Wandtablet): Das
  Layout muss bei allen dreien ohne horizontales Scrollen lesbar sein.

## 8. Abnahmekriterien

Geprüft wird **am Bildschirm**, nicht am Rückgabewert. `HTTP 200` beweist nichts — HA liefert die
Seite auch aus, wenn jede Kachel darin fehlschlägt (Vorfall 15.09.).

1. Bildschirmfoto von Kiosk und „Zuhause": **keine einzige Fehlkachel**, keine kaputten
   Sonderzeichen.
2. Im Browser geprüft: alle verwendeten Kartentypen registriert, Konsole ohne Fehler.
3. Startbildschirm zeigt bei ungestörtem Betrieb „Alles in Ordnung"; ein künstlich ausgelöstes
   Problem (Testfenster geöffnet) erscheint dort nachweislich.
4. Sichtbare Entitäten unter 400 (Ausgangswert 1409), Stockenweiler-Entitäten nicht mehr in der
   Suche — stichprobenartig mit drei Namen geprüft.
5. **Nichts gelöscht.** Register vorher und nachher gleich groß (1850 Einträge) — nur
   `hidden_by` unterscheidet sich. Soll- und Istwert dokumentiert.
6. Layout auf 10,5" ohne horizontales Scrollen.
7. Die doppelte „Übersicht" ist erst **nach** einer Browserprüfung entfernt worden — belegt,
   dass die verbliebene die richtige ist.
8. Wiederherstellung einmal durchgespielt: ein Dashboard aus der Sicherung zurückgeholt.

## 9. Testplan

0. **Vorprüfung am Ziel** (Review-Auflage): Register und Zustände frisch messen — stimmen 1850 /
   1409 / 1065 / 500 noch? Soll gegen Ist dokumentieren, bevor irgendetwas angefasst wird.
1. HA-eigene Sicherung erstellen, zusätzlich Rohkopien der betroffenen Dateien.
2. **Vorabtest mit drei Stockenweiler-Entitäten** ausblenden: Zustand bleibt? Aus der Suche
   verschwunden? Trotzdem bewusst auf einem Dashboard verwendbar? Erst wenn alle drei Fragen mit
   Ja beantwortet sind, folgt der Massenlauf.
3. Ausblenden in zwei Schritten: erst Stockenweiler, Zwischenprüfung, dann toter Rest.
4. Dashboards bauen, nach jedem Abschnitt Bildschirmfoto.
5. Testfenster öffnen → Statuszeile prüfen → wieder schließen.
6. HA neu starten → alles nochmals aufrufen (überlebt die Änderung einen Neustart?).

## 10. Nicht enthalten

- **Roborock-Raumplan zum Anklicken.** Die vier Kartenbilder existieren
  (`image.wohnzimmer_sirius_black_wohnung` u. a.) und lassen sich als Bildkachel einbinden. Ein
  anklickbarer Raumplan („hier saugen") braucht eine zusätzliche Karte aus HACS — eigener Schritt
  nach dieser Umsetzung.
- Ursachenklärung der 96 beim Start verworfenen Entitäten (doppelte Kennungen bei Shelly und
  UniFi). Betrifft die Sichtbarkeit nicht, gehört aber untersucht.
- Umbau von Automationen.
