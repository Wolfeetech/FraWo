# Antworten auf den Realitätscheck

**Stand 09.09.2026.** Bezieht sich auf euer Übergabedokument. Ich habe alle
Zahlen und Systemangaben am laufenden Betrieb geprüft, nicht aus dem Gedächtnis
geschrieben — an zwei Stellen kam dabei etwas anderes heraus, als in meinen
Notizen stand. Das ist jeweils markiert.

---

## Vorweg: drei Dinge, die vor allen vier Fragen kommen

**1. Der Führerschein ist kein Privatthema, sondern ein Betriebsmittel.**
Ihr schreibt ihn unter „Wolfs Situation". Tatsächlich hängt daran, ob Franz
jeden Transport allein fahren muss, ob Vor-Ort-Termine bei Senioren überhaupt
möglich sind und ob Eventaufträge zu zweit angenommen werden können. **Das ist
die Investition mit dem höchsten Hebel von allem, was hier steht** — höher als
jede Maschine. Er gehört als Projekt ins System, mit Kosten, Terminen und
einem Datum.

**2. Ihr könnt eure Bücher nicht schließen, und das ist kein Odoo-Problem.**
In eure Buchhaltung wurde **noch nie eine einzige Kontobewegung importiert**.
Solange das so bleibt, ist jede EÜR Handarbeit und jede Zahl eine Schätzung —
egal wie gut Odoo eingerichtet ist. Das ist die eine Sache, die Wolf wirklich
Zeit spart, und sie ist an einem Nachmittag erledigt (Odoo-Aufgabe **#1371**).

**3. Verkauft vorerst nichts, wofür eure Anlage geradestehen muss.**
Ausführlich unter Frage 1 — aber es ist die wichtigste Aussage dieses
Dokuments, deshalb steht sie hier oben.

---

# 🎯 Frage 1: Welches regionale IT-Angebot macht wirklich Sinn?

## Die unbequeme Vorbedingung

Ihr fragt nach Diensten „mit minimalem Haftungs- und Wartungsrisiko" und nennt
in derselben Liste **Backups und Nextcloud für Handwerker und Vereine**. Das
beißt sich, und zwar hart.

Was in den letzten 72 Stunden an eurer Anlage tatsächlich passiert ist:

- Ein Knoten ist **hardwareseitig gestorben**; alles läuft jetzt auf dem einen
  verbliebenen Rechner.
- Ein Netzwerk-Skript hat wegen eines 3-Sekunden-Wacklers **12 Stunden
  Totalausfall** verursacht.
- Die Wache über die Überwachung war **zwei Tage tot**, ohne dass es jemand
  gemerkt hat.
- Die verschlüsselte Cloud-Sicherung war **systematisch einen Tag alt** und hat
  trotzdem „erfolgreich" gemeldet.
- Die Villa hat **keinen Kabelanschluss**, nur Richtfunk mit 100 Mbit.

Nichts davon ist ein Drama für einen Eigenbetrieb — genau dafür ist er da, dass
man daran lernt. Aber: **Wenn die Rechnungen eines Handwerkers auf dieser Anlage
liegen und sie ist eine Woche weg, ist das euer Problem, nicht seins.** Bei
einem Verein mit Mitgliederdaten kommt die DSGVO dazu, samt
Auftragsverarbeitungsvertrag und Meldepflicht binnen 72 Stunden.

**Empfehlung:** Fremddaten-Hosting erst verkaufen, wenn die acht Regeln aus
`DOCS/SICHERHEITSSTANDARDS.md` durchgehend grün sind. Heute sind es vier. Das
ist kein „nie", das ist ein **„noch nicht, und wir wissen genau woran es liegt"**
— was übrigens ein hervorragendes Verkaufsargument ist, wenn es soweit ist.

## Was ihr stattdessen sofort verkaufen könnt

Sortiert nach *Geld pro Stunde* im Verhältnis zu *Risiko*:

### Stufe 1 — sofort, kein Risiko, Bargeld am selben Tag

| Leistung | Realistisch | Warum es passt |
|---|---|---|
| PC/Laptop einrichten, umziehen, entrümpeln | 55–70 €/h, meist 1–2 h | keine Folgehaftung, Ergebnis sofort sichtbar |
| Drucker, WLAN, Fernseher, Handy anbinden | Pauschale 49–89 € | der häufigste Anruf überhaupt |
| Virenbefall / „da war so ein Anruf von Microsoft" | 89–149 € Pauschale | hohe Zahlungsbereitschaft, akuter Leidensdruck |
| Datenrettung von Platte/Stick (einfache Fälle) | 89–189 € | ⚠️ **nur mit schriftlichem Vorbehalt** „ohne Erfolgsgarantie" |
| Smart-Home-Einrichtung (Shelly, Kamera, Licht) | 65–85 €/h | genau das, was ihr sowieso beherrscht |

**Der entscheidende Punkt bei Stufe 1:** Ihr übergebt das Gerät und seid raus.
Keine Fernwartung, kein Abo, keine Nacht-Anrufe. Anfahrt getrennt ausweisen
(0,50–0,70 €/km oder Pauschale nach Zone).

**Preisgestaltung:** Bleibt aus dem Billigsegment raus. 35 €/h zieht genau die
Kunden an, die drei Stunden reden und dann handeln. Wer 65 € zahlt, hat ein
echtes Problem und respektiert eure Zeit.

### Stufe 2 — die einzige Wiederholung, die ich empfehle

**Eine Wartungspauschale für Privatkunden, ausdrücklich ohne kritische Daten.**

> **„Computer-Hausmeister"** — 19 €/Monat
> Einmal im Quartal Updates und Durchsicht · eine Fernhilfe im Monat inklusive
> · Vorrang bei Terminen · 10 % auf Vor-Ort-Einsätze

Warum das trägt: Bei 30 Kunden sind das **570 € im Monat wiederkehrend** — mehr
als euer bisheriger Durchschnittsumsatz. Der Aufwand ist planbar (ein
Quartalstag), und wenn ihr mal drei Tage nicht erreichbar seid, passiert
**nichts**. Das ist der Unterschied zu Server-Hosting.

30 Kunden sind im ländlichen Raum über Mundpropaganda in etwa einem Jahr
erreichbar, wenn die ersten fünf zufrieden sind.

### Stufe 3 — Radio-Streams für DJs und Vereine

Das ist eure eleganteste Idee, weil sie Infrastruktur nutzt, die ohnehin läuft.
**Aber sie hat einen rechtlichen Haken, den ihr vorher klären müsst:**

- **GEMA und GVL.** Wer Musik streamt, zahlt. Für Webradio gibt es Tarife nach
  Hörerzahl. Wenn ihr für Dritte streamt, ist zu klären, **wer Veranstalter im
  Sinne der Verwertungsgesellschaften ist** — ihr oder der DJ. Das gehört in
  den Vertrag, nicht in die Hoffnung.
- **Medienstaatsvertrag.** Rundfunkähnliche Telemedien unterhalb einer
  Nutzerschwelle sind zulassungsfrei, aber **anzeigepflichtig** bei der
  Landesmedienanstalt (für euch: BLM in Bayern bzw. LFK, je nach Sitz —
  das ist zu prüfen, nicht zu raten).

**Mein Rat:** Fangt mit **Vereinen und Veranstaltern** an, nicht mit DJs.
Ein Verein, der sein Sommerfest streamt, ist ein klarer Auftrag mit Anfang und
Ende. Ein DJ, der einen Dauerkanal will, ist ein Dauerthema mit Dauerlizenzfrage.

**Preis:** Einrichtung 150–250 € einmalig, dann 15–25 €/Monat für den Kanal.

## Wie das auf frawo.tech aussehen muss

Streicht jedes Wort, das ein Konzern auch schreiben würde. Konkret:

| statt | besser |
|---|---|
| „Ihr Partner für digitale Transformation" | „Wenn der Computer nicht mehr will." |
| „ganzheitliche IT-Lösungen" | „Wir richten ein, reparieren und erklären es so, dass Sie es verstehen." |
| „individuelle Beratung" | „Anruf, Termin, Festpreis. Sie wissen vorher, was es kostet." |

**Vier Dinge, die auf die Seite gehören, und sonst fast nichts:**

1. **Ein Gesicht und ein Vorname.** Bei Senioren entscheidet das, nicht die
   Leistungsliste. „Wolf kommt vorbei" schlägt jedes Logo.
2. **Eine Telefonnummer, groß, ganz oben.** Diese Zielgruppe schreibt keine
   Kontaktformulare.
3. **Preise.** Wer sie nicht nennt, wird nicht angerufen — die Sorge vor der
   unbekannten Rechnung ist bei älteren Kunden der stärkste Hemmschuh.
4. **Zwei, drei Sätze, was ihr *nicht* macht.** „Wir übernehmen keine
   Serverbetreuung für Firmen." Das wirkt seriöser als jede Aufzählung und
   hält euch die falschen Anfragen vom Hals.

Nachbarschaft schlägt Suchmaschine: **Aushang im Dorfladen, Zettel beim
Bäcker, Notiz im Gemeindeblatt.** Kostet fast nichts und trifft genau eure
Leute.

---

# 🛠️ Frage 2: Werkstatt-Fast-Track für Franz

## Zuerst: Die CNC-Fräse ist der falsche erste Schritt

In eurer Investitionsplanung 2027 steht eine CNC-gestützte Oberfräse mit
**3.000–8.000 €**. Das ist mehr als euer gesamter Umsatz der letzten fünf
Monate. Und für Reparatur und Einzelbau bringt sie fast nichts:

**Eine handgeführte Oberfräse mit Fräszirkel schneidet Chassisausschnitte
genauso rund wie eine CNC** — sie braucht nur zwei Minuten länger. Eine CNC
rechnet sich ab Serie, ab Wiederholteilen, ab dem Punkt, wo ihr dasselbe
Gehäuse zum zwanzigsten Mal baut. Da seid ihr nicht.

Verschiebt sie, und ihr habt die Mittel für alles Folgende **plus** Reserve.

## Die vier Anschaffungen, in dieser Reihenfolge

### 1. Absaugung — Staubklasse M · rund 350–550 €

Unromantisch und trotzdem Platz eins. Gründe:

- **MDF-Staub ist gesundheitsschädlich** (formaldehydhaltige Bindemittel,
  lungengängige Feinanteile). Bei Lautsprecherbau ist MDF das Hauptmaterial.
- **Die Werkstatt steht in der Villa** — einem Gebäude, das auch Studio und
  Geschäftsadresse ist. Ohne Absaugung staubt ihr euch die Vermietbarkeit
  desselben Hauses zu.
- Sie ist die Voraussetzung dafür, dass die anderen drei Werkzeuge **drinnen**
  benutzbar sind.

Klasse M genügt für Holz. Mit Steckdose für Elektrowerkzeug-Anlauf.

### 2. Tauchsäge mit Führungsschiene · rund 400–700 €

Das eigentliche Arbeitstier im Gehäusebau. Multiplex und MDF exakt, gerade und
wiederholbar ablängen — ohne dass ihr eine Formatkreissäge und den Platz dafür
braucht. Zwei Schienen (1,4 m + Verbinder) einplanen, damit auch
Plattenlängsschnitte gehen.

Makita oder Bosch reichen völlig. Festool ist schöner und kostet das Doppelte.

### 3. Oberfräse + Fräszirkel + Grundfrässet · rund 250–450 €

Damit macht ihr:
- **Chassisausschnitte** rund und mit Falz (versenkt eingelassene Treiber)
- **Nuten** für Verstrebungen und Rückwände
- **Bündigfräsen** von Furnier- und Deckplatten
- **Abrundungen** an den Kanten

Fräser fürs Erste: Nutfräser 8 und 12 mm, Bündigfräser mit Anlaufring,
Abrundfräser R6.

### 4. Werkbank mit richtiger Spanntechnik · rund 250–450 €

Wird immer vergessen und ist immer der Engpass. Ohne feste, ebene Fläche mit
Zwingen und Anschlag arbeitet man dreimal so lange. Eine solide
Multiplex-Platte auf Untergestell plus **sechs bis acht Schraubzwingen** ist
völlig ausreichend — das kann Franz sich am ersten Tag selbst bauen.

**Summe: rund 1.250 bis 2.150 €.** Aus laufendem Cashflow in zwei bis drei
Monaten machbar, ohne Kredit.

## Und der eine Zusatz, der euch von Bastlern unterscheidet

**Messmikrofon + Messsoftware · rund 100–150 €**

Ein kalibriertes USB-Messmikrofon (UMIK-1 o. ä.) und REW — die Software ist
kostenlos. Damit könnt ihr:

- **vorher und nachher messen** bei jeder Reparatur
- eine **Frequenzgangkurve zum Auftrag** mitliefern
- Weichenänderungen belegen statt behaupten
- Beschallungen im Raum einmessen (auch für die Events)

Das ist eure billigste Investition in Glaubwürdigkeit. Wer eine Messkurve
mitschickt, ist kein Bastler mehr — und im Verkaufsgespräch ist genau das
der Unterschied.

## Handwerkskammer — was ihr wissen müsst

⚠️ **Das ist Orientierung, keine Rechtsberatung. Holt euch das schriftlich.**

Die Lage in Kürze:

- **Anlage A der HwO** (zulassungspflichtig, Meister nötig) enthält u. a.
  **Tischler**. Wer gewerblich Möbel und Korpusse baut, fällt darunter.
- **Anlage B1/B2** (zulassungsfrei bzw. handwerksähnlich) enthält den Rest.
- Entscheidend ist **nicht das Material, sondern die Tätigkeit und wie sie
  eingeordnet wird.**

Drei Wege, die für euch realistisch sind:

**a) Der Tätigkeitszuschnitt.** Es macht einen Unterschied, ob auf der Rechnung
„Schreinerarbeiten" steht oder:
- „Instandsetzung einer Beschallungsanlage"
- „Montage und Aufbau von Veranstaltungstechnik"
- „Dekorations- und Kulissenbau"

Das ist keine Wortklauberei — **Dekorationsbau und Montage sind nicht
zulassungspflichtig**, Möbelbau ist es. Schreibt auf die Rechnung, was ihr
wirklich tut.

**b) § 1 Abs. 2 HwO — der unerhebliche handwerkliche Nebenbetrieb.**
Handwerkliche Arbeiten, die als Nebenleistung zu einem nicht-handwerklichen
Hauptbetrieb erbracht werden und die in überschaubarer Zeit erlernbar sind,
fallen nicht unter die Zulassungspflicht. Bei euch ist der Hauptbetrieb
Veranstaltungstechnik — das ist eine gute Ausgangslage.

**c) § 7b HwO — die Altgesellenregelung.** Wer sechs Jahre Geselle in einem
Anlage-A-Handwerk war, davon vier in leitender Stellung, darf sich ohne
Meister eintragen lassen. **Ob das auf Franz zutrifft, weiß ich nicht** — das
wäre zu klären, denn es würde die Frage endgültig erledigen.

### Der konkrete nächste Schritt

**Ruft die zuständige Handwerkskammer an und lasst euch die Einordnung
schriftlich geben.** Die Betriebsberatung ist für Mitglieder und Gründer
kostenlos, und die Auskunft ist genau das, was ihr später vorlegen könnt, falls
jemand fragt. Beschreibt dabei ehrlich, was ihr tut: Reparatur von
Lautsprechern, Bau von Gehäusen für den eigenen Verleih, Montage bei
Veranstaltungen.

**Ein Anruf, kostenlos, erledigt eine Frage, die euch sonst monatelang im
Hinterkopf sitzt.** Das ist ein besseres Geschäft als jedes Werkzeug.

---

# 🔄 Frage 3: Odoo 19 und Paperless als schlankes Büro

## Korrektur vorweg

In meinen Notizen stand, euer Odoo sei so abgespeckt, dass Angebote gar nicht
gehen. **Das stimmt nicht.** Nachgesehen am 09.09.2026 — installiert und
nutzbar sind:

| Modul | Bedeutung für euch |
|---|---|
| `sale_management` | **Angebote und Aufträge — funktioniert** |
| `account` | Rechnungen, § 19 UStG |
| `stock` + `sale_stock` | Lagerbestand, Lieferung |
| `hr_timesheet` | **Zeiterfassung auf Aufgaben — vorhanden** |
| `purchase` | Lieferantenrechnungen |
| `project`, `crm`, `maintenance`, `mrp` | Aufgaben, Kontakte, Wartung, Fertigung |

Nicht verfügbar (Enterprise): Helpdesk, Planning, Sign, **Rental**. Für den
Verleih gibt es also kein fertiges Modul — dazu unten.

## Der Wochenablauf, der in 60 Minuten passt

Nicht mehr Werkzeuge, sondern **ein fester Termin**. Vorschlag: Freitag, eine
Stunde, immer gleich:

| Minuten | Was |
|---|---|
| 0–15 | **Belege**: alles der Woche in Paperless werfen, Vorschläge bestätigen |
| 15–30 | **Rechnungen**: erledigte Aufträge abrechnen, offene anmahnen |
| 30–45 | **Angebote**: Anfragen der Woche beantworten |
| 45–60 | **Aufräumen**: Tagesbericht-Rückstände, „🙋 braucht Wolf" leeren |

Das ist die ganze Verwaltung. Alles darüber hinaus ist Ausbau, nicht Betrieb.

## Was Wolf konkret vor dem Chaos bewahrt

Das meiste davon läuft seit heute:

**Der Tagesbericht.** Kommt täglich per Mail und beantwortet fünf Fragen:
Sicherung gelaufen? Fristen überfällig? Was liegt seit 14 Tagen unbewegt? Welche
Rechnungen sind noch Entwurf? Was wartet auf eine Entscheidung? Und seit heute
zusätzlich: **was steht wo an** (@rk22, @villa, @stockenweiler …).

**17 gespeicherte Ansichten** in Odoo unter *Favoriten* — u. a. „Überfällig",
„Braucht eine Entscheidung von Wolf", „Läuft gerade", „Liegengeblieben",
„Ohne Beschreibung".

**Zeiterfassung: `hr_timesheet` ist da.** Aber ein Rat: **Fangt nicht an, alles
zu stempeln.** Bei zwei Leuten ohne Stundenabrechnung bringt lückenlose
Zeiterfassung nichts als Frust. Erfasst Zeit **nur auf Kundenaufträgen** — dann
wisst ihr am Jahresende, was ein L.H.-Job wirklich kostet und ob der Verleih
sich lohnt. Genau das ist die Zahl, die euch heute fehlt.

## Verleih ohne Rental-Modul

Es gibt drei Wege. Meine Empfehlung ist der erste:

**a) Angebot + Lager, Zeitraum im Text.** Verleihartikel sind Produkte mit
Tagespreis. Ein Verleihvorgang ist ein Auftrag mit Von-Bis im Kommentar,
Lieferschein raus, Rücknahme rein. **Kein Zusatzmodul, funktioniert heute.**
Für euer Volumen völlig ausreichend.

**b) Ein freies Rental-Modul aus dem OCA-Katalog.** Kostenlos, aber Wartung
bei jedem Odoo-Update. Lohnt ab etwa 20 Vorgängen im Monat.

**c) Selbst bauen.** Nicht empfohlen — ihr habt genug Baustellen.

⚠️ **Wichtiger als das Werkzeug ist die Kaution und der Zustand bei Rückgabe.**
Beides gehört in eure Verleihbedingungen, nicht in ein Odoo-Feld.

## Paperless → Odoo

Die Strecke ist zurzeit **unterbrochen** (Odoo-Aufgabe #1363). Solange sie
steht, tippt ihr jeden Beleg zweimal. Das ist die zweitwichtigste
Zeitersparnis nach dem Bankimport — und beides sind Dinge, die ich für euch
erledigen kann.

---

# 🛑 Frage 4: Die Stop-Doing-Liste

Ihr habt **elf aktive Projekte mit zusammen über 900 Aufgaben**. Bei
realistisch 10 Feierabendstunden pro Woche zu zweit ist das mehrere Jahre
Arbeit. Nicht priorisieren heißt hier: alles gleichzeitig ein bisschen, nichts
fertig.

## Die fünf, die eingefroren gehören

### 1. 🪴 GrowBox — komplett einfrieren
Wolfs eigene Einordnung: „kein Geschäftszweig". Damit ist die Entscheidung
eigentlich schon gefallen — sie war nur nie ausgesprochen. **Projekt
archivieren**, die 8 Aufgaben bleiben lesbar erhalten.

### 2. 🚐 Ducato-Ausbau — komplett einfrieren
Wolfs Worte: „reines Luxusprojekt". Das Fahrzeug war gratis, es steht, es
kostet nichts. **Bis es fahrbereit beschriftet werden soll, gibt es nichts zu
tun.** Wieder aufnehmen, wenn ein Auftrag Transport braucht.

### 3. 📻 Radio — Sender läuft weiter, Entwicklung stoppt
Das ist die schmerzhafteste, deshalb die Begründung ausführlich: Der Sender
läuft, die Kanal-Demokratie funktioniert, die Bibliothek ist kuratiert. **Es
ist fertig genug.** Jede weitere Ausbaustufe kostet Wochen und bringt keinen
Euro. Als Aushängeschild wirkt es genau so, wie es ist.

*Ausnahme:* Der Umzug der Radio-VM auf den OptiPlex, sobald das Netzteil da
ist — das ist Wiederherstellung, kein Ausbau.

### 4. 🛠️ IT-Infrastruktur — nur noch das Fangnetz
**610 Aufgaben.** Das ist Wolfs Kaninchenbau, und er ist gefährlich, weil sich
die Arbeit gut anfühlt und nach Fortschritt aussieht.

**Neue Regel: In diesem Projekt wird nur noch bearbeitet, was auf der
Umsetzungsliste der Sicherheitsstandards steht.** Aktuell sind das vier Punkte
(Backup-TÜV, Cloudflare-Benachrichtigung, Paperless→Odoo, Bankimport). Alles
andere bleibt liegen, bis diese vier grün sind.

### 5. 🏡 Stockenweiler — nur noch echte Verpflichtungen
55 Aufgaben, überwiegend Familienarbeit ohne Umsatz. **Weiterlaufen darf, was
Termine oder Geld hat** (Wärmepumpe, EGS-Zählersetzen, Förderfristen). Der
Rest — Smart-Home-Ausbau, Optimierungen, Bastelthemen — wird eingefroren.

Das ist kein Liebesentzug. Es ist die Feststellung, dass das Elternhaus euer
**Testkunde** ist und nicht euer Arbeitgeber.

## Was bleibt

| Projekt | warum es bleibt |
|---|---|
| 💼 **Aufträge & Events** | trägt 88 % vom Umsatz |
| 🔧 **Werkstatt & Lautsprecherbau** | Franz' Fast-Track, nächster Umsatzträger |
| 💶 **Business, Recht & Finanzen** | Fristen mit Folgen |
| 🎨 **Marke & Website** | die CI-Findung läuft gerade |
| 🎬 **Studio Villa — aber nur die Werkstatt** | siehe unten |

**Zum Studio:** Nur der Teil „Werkstatt nutzbar machen" bleibt. Der Ausbau zum
vermietbaren Produktionsstudio wird mit eingefroren — er ist teuer, weit weg
und blockiert nichts, wenn er wartet. Die Werkstatt dagegen bringt Franz sofort
ins Verdienen.

## Und drei Dinge, die neu aufs Blatt gehören

1. **Führerschein** — mit Kosten, Terminen und Zieldatum
2. **Bankimport in Odoo** — ein Nachmittag, danach stimmen die Zahlen
3. **Die ersten fünf IT-Kunden** — nicht als Idee, sondern als Aufgabe mit
   Namen: wen fragt ihr zuerst?

---

## Was ich davon selbst übernehmen kann

Ohne dass ihr etwas tun müsst außer freigeben:

- Die fünf Projekte einfrieren und die Aufgaben sauber archivieren
- Bankimport einrichten (Odoo #1371)
- Paperless → Odoo reparieren (Odoo #1363)
- Führerschein, Werkstatt-Beschaffung und Kundenakquise als Projekte anlegen —
  mit Fristen, damit sie im Tagesbericht auftauchen
- Die Werkzeugliste als Einkaufsliste mit Preisrahmen in Odoo

Was **ihr** tun müsst, weil es niemand sonst kann:

- Der Anruf bei der Handwerkskammer
- Die Entscheidung, welche fünf Leute ihr als erste IT-Kunden fragt
- Der Führerschein

---

*Alle Systemangaben am 09.09.2026 am laufenden Betrieb geprüft. Preisangaben
sind Orientierungswerte für die Region, keine Angebote. Rechtliche Hinweise
sind Orientierung und ersetzen keine Beratung durch Kammer, Steuerberater
oder Anwalt.*
