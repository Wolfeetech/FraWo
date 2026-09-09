# FraWo GbR — Vorstellung für die CI-Findung

> Diese Datei ist dafür gemacht, **vollständig in ein KI-Werkzeug kopiert zu
> werden**. Sie beschreibt das Unternehmen so, wie es am 09.09.2026 tatsächlich
> ist — mit Stärken, Lücken und offenen Fragen. Nichts ist geschönt; eine CI, die
> auf einer geschönten Grundlage entsteht, passt später nicht.

---

## 1. Kurzprofil

| | |
|---|---|
| **Name** | FraWo GbR — aus **Fra**nz + **Wo**lf |
| **Gegründet** | 01.04.2026 (davor: Einzelunternehmen von Wolf bis 31.03.2026) |
| **Rechtsform** | Gesellschaft bürgerlichen Rechts, zwei Gesellschafter |
| **Steuerlich** | Kleinunternehmer nach § 19 UStG — **weist keine Umsatzsteuer aus** |
| **Sitz** | Rothkreuz 14, Bodenseeraum (Landkreis Lindau) — genannt „die Villa" |
| **Web** | `frawo.tech` · Radio: `funk.frawo.tech` |
| **Umsatz Apr–Aug 2026** | 4.623,25 € bei rund 3.200 € Ausgaben |
| **Größe** | zwei Gesellschafter, keine Angestellten |

**Ein Satz:** FraWo ist ein Zwei-Mann-Betrieb aus Veranstaltungstechnik und
Handwerk, der die eigene Infrastruktur so professionell aufbaut, dass sie
selbst zum Produkt wird.

---

## 2. Wer dahintersteht

**Wolf** — gelernter Veranstaltungstechniker, hauptberuflich bei einem
Kongress- und Veranstaltungshaus am Bodensee angestellt. Bringt Licht, Ton,
Bühne und die komplette IT ein: Server, Automatisierung, Radio, Smart Home.
Arbeitet sprunghaft, breit und schnell — findet Zusammenhänge, verliert
Kleinkram. (Das ist keine Nebenbemerkung, siehe Abschnitt 7.)

**Franz** — die handwerkliche Hälfte. Werkstatt, Bau, Material, Maschinen.
Treibt den Lautsprecherbau und die Werkstattausstattung voran (u. a. eine
CNC-Fräse in der Investitionsplanung 2027).

Zwei Handschriften, die sich ergänzen: **Franz baut es, Wolf steuert es.**
Der Name sagt das bereits — er ist keine Abkürzung, er ist die Partnerschaft.

---

## 3. Was FraWo heute tatsächlich tut

Elf laufende Arbeitsbereiche, geordnet nach dem, was der Kunde davon merkt:

| Bereich | Zustand |
|---|---|
| **Aufträge & Events** | läuft, trägt den Umsatz |
| **Werkstatt & Lautsprecherbau** | läuft, echte Reparaturkompetenz |
| **Studio Villa** | im Aufbau |
| **Radio „FraWo Funk"** | sendet, technisch weit, Marke offen |
| **IT & Infrastruktur** | das Rückgrat, weit entwickelt |
| **Marke & Website** | schwächster Bereich — hier setzt die CI an |
| **GrowBox** | Testmodell Indoor Gardening, kein Geschäftszweig |
| **Verleih** | vorbereitet, **noch nicht live** |

### Veranstaltungstechnik — der Umsatzträger

Eigener Bestand an Licht und Ton: sechs Moving Heads (Showtec Shark Combi
Spot), zwei Beamz Panther, Outdoor-PARs, Hazer, ein Wolfmix-W1-Hardwarepult,
DMX-Strecken. Auf der Tonseite Martin Audio CX2, Jobst-Subwoofer, KMT-Tops,
ein Omnitronic-DXO-206-Controller.

Damit werden Veranstaltungen gefahren — und, das ist der Unterschied zu
reinen Verleihern: **das Material wird selbst repariert und aufgewertet.**
Frequenzweichen werden neu bestückt, Chassis auf Beyma umgerüstet, defekte
Tops zur Manufaktur gegeben statt ersetzt.

### Lautsprecherbau & Werkstatt

Kein Nebenprodukt, sondern eine zweite Kompetenz: Bau, Restauration und
Aufwertung von Lautsprechern. Bestehende Erfahrung u. a. mit Canton-Restauration.
Für 2027 ist eine CNC-gestützte Oberfräse in Planung — der Schritt vom
Reparieren zum Fertigen.

### Radio „FraWo Funk"

Ein laufender Internet-Radiosender auf eigener Infrastruktur (AzuraCast).
Technisch weiter als die meisten Hobbyprojekte: Hörer stimmen über Kanäle ab,
die Stimmen steuern automatisch die Gewichtung der Playlisten — eine
funktionierende „Kanal-Demokratie". Dazu eine gepflegte Musikbibliothek mit
eigener Vibe-/BPM-Kuration und Anbindung an DJ-Software.

Das Radio ist zugleich **Marke und Werkzeug**: Es soll als eigenständige Marke
stehen und den DJs ein Programmier-Werkzeug an die Hand geben.

### IT & Infrastruktur — das Rückgrat

Eine vollständige, selbst betriebene Anlage: Virtualisierung (Proxmox),
Warenwirtschaft und Aufgabensteuerung (Odoo 19), Dokumentenarchiv mit
Texterkennung (Paperless), Passwortsafe, Home Assistant, Überwachung mit
Prometheus/Grafana, VPN, verschlüsselte Cloud-Sicherungen, Zugriff von außen
über Cloudflare-Tunnel.

Betrieben wird das an drei Standorten, verbunden über VPN und Richtfunk.
Es gibt Nachtsicherungen, Wiederherstellungstests, Alarme aufs Handy und ein
schriftliches Regelwerk für den Betrieb.

**Das ist der eigentliche Kern des Unternehmens** — siehe nächster Abschnitt.

### Smart Home & Energie

Verbrauchsmessung mit Shelly-Geräten bis auf Stromkreis-Ebene, ein
Balkonkraftwerk, eine Wärmepumpen-Umrüstung im Elternhaus. Die Eltern sind
dabei ausdrücklich der **erste Testkunde** — an ihrer Anlage wird erprobt,
was später verkauft wird.

---

## 4. Der Kern: das Geschäftsmodell hinter dem Geschäftsmodell

Das Wichtigste an FraWo ist nicht, was heute Umsatz macht, sondern die
Klammer darüber:

> **Alles, was für uns selbst gebaut wird, ist der Prototyp für ein
> Kundenangebot.**

Der Maßstab bei jeder Aufgabe lautet deshalb: **reproduzierbar? dokumentiert?
von jemand anderem betreubar?** Wenn eine Lösung diese drei Fragen besteht, ist
sie verkaufbar. Wenn nicht, ist sie Bastelei.

Vier Vorhaben tragen das:

1. **Radio** — als Marke und als Werkzeug für DJs
2. **Odoo als „Jarvis"** — Auftrag, Angebot, Lager, Buchhaltung, Aufgaben in
   einem System, mit Automatisierung darauf
3. **Server-Garten** — die selbst betriebene Anlage als Dienstleistung:
   kleine Betriebe bekommen eine eigene Infrastruktur statt Mietsoftware
4. **Smart Home** — Energiemessung und Steuerung, erprobt am Elternhaus

Der rote Faden: **Digitale Selbstständigkeit für kleine Betriebe.** Keine
Abo-Falle, keine Cloud eines Konzerns — eigene Hardware, eigene Daten,
betreut von jemandem, den man anrufen kann.

---

## 5. Wo es hingehen soll

**Kurzfristig (2026):**
- Verleih endlich live bekommen — Material, Preise und Abwicklung stehen,
  der Vertriebsweg fehlt
- Studio in der Villa fertigstellen: Doppelnutzung als **Vermietungsobjekt**
  und als **eigenes Produktionsstudio** fürs Radio
- Website und Außenauftritt auf ein Niveau bringen, das zur Substanz passt

**Mittelfristig (2027):**
- Das Infrastruktur-Angebot als bezahlte Dienstleistung an erste Kunden
- Fertigung statt nur Reparatur (CNC)
- Radio als tragende Marke, nicht als Nebenprojekt

**Was dafür gebraucht wird — und was die CI leisten muss:** Bisher kommt
Umsatz fast ausschließlich über persönliche Kontakte. Für alles oben Genannte
braucht es einen Auftritt, der **Vertrauen erzeugt, bevor jemand anruft.**

---

## 6. Die Zahlen, ehrlich

- Umsatz April bis August 2026: **4.623,25 €**
- Ausgaben im selben Zeitraum: rund **3.200 €**
- Überschuss: rund **1.400 €** — verteilt auf fünf Monate und **zwei**
  Gesellschafter
- **88 % des Umsatzes stammen von einem einzigen Auftraggeber.** Das ist das
  größte wirtschaftliche Risiko und zugleich das stärkste Argument für einen
  eigenständigen Außenauftritt.
- Beide Gesellschafter arbeiten daneben; FraWo trägt sich noch nicht selbst.

Das ist kein Start-up mit Kapital. Es ist ein Betrieb, der aus vorhandenem
Können und vorhandener Technik wächst — langsam, aus eigener Kraft.

---

## 7. Was die Marke tragen muss — die Spannungen

Diese Punkte sind für eine CI wichtiger als jede Leistungsliste, weil eine
gute Marke aus echten Spannungen entsteht, nicht aus Adjektiven.

**Substanz ohne Auftritt.** Technisch und handwerklich ist FraWo weiter als
der Auftritt vermuten lässt. Die Anlage im Hintergrund würde manchem
IT-Dienstleister gut anstehen — nach außen sieht man davon nichts. **Die CI
muss Substanz sichtbar machen, nicht Substanz behaupten.**

**Zwei Handschriften.** Handwerk und Software, Sägespäne und Serverschrank.
Das ist kein Widerspruch, den man glätten sollte — es ist das
Unterscheidungsmerkmal. Wer beides kann, baut die Box *und* die Steuerung.

**Ordnung aus Unordnung.** Wolf arbeitet chaotisch. Statt das zu bekämpfen,
wurde ein System gebaut, das Chaos aushält: Regeln, die dafür sorgen, dass
nichts still verlorengeht. Der Leitsatz dieses Systems lautet
**„Chaos ist erlaubt. Stille ist es nicht."** Daraus lässt sich ein
Markenversprechen ableiten, das ehrlicher ist als jedes Qualitätssiegel:
*Verlässlichkeit für Leute, die selbst nicht ordentlich sind.*

**Klein, aber nicht billig.** Kleinunternehmerstatus, keine Umsatzsteuer,
knappe Mittel — aber die Arbeit ist gründlich. Die Marke darf nicht nach
Discount aussehen und nicht nach Konzern.

**Nähe.** Alles spielt in einem überschaubaren Umkreis am Bodensee, teils auf
dem Grundstück der eigenen Eltern. Regionalität ist hier keine Behauptung,
sondern der Betriebszustand.

---

## 8. Was schon existiert (und was davon bleiben soll)

| | Stand |
|---|---|
| **Name FraWo** | gesetzt, aus den Vornamen — bleibt |
| **frawo.tech** | aktive Domain, Website vorhanden, inhaltlich dünn |
| **„FraWo Funk"** | Name des Radios, etabliert im eigenen Umfeld |
| **Standortname** | 🔴 **offen** — „Villa Bienert" ist der alte Name des Gebäudes, ein neuer wird gesucht |
| **Logo / Farbwelt / Typografie** | 🔴 **nicht vorhanden** oder nicht konsistent |
| **Bildsprache** | 🔴 nicht definiert |

Es gibt bereits ein internes Gestaltungsdokument („CI v3.0") für Rechnungen
und Angebote. Das ist ein Anfang, aber kein Markenauftritt.

---

## 9. Der Auftrag an die CI

Gesucht wird ein Auftritt, der:

1. **die Doppelbegabung sichtbar macht** — Handwerk *und* Technik, nicht
   entweder–oder
2. **Vertrauen vor dem ersten Gespräch erzeugt**, weil der Umsatz heute
   fast nur über persönliche Kontakte kommt
3. **über drei sehr verschiedene Felder trägt**: Veranstaltungstechnik,
   Radio, IT-Dienstleistung — ohne beliebig zu werden
4. **von zwei Leuten ohne Marketingbudget gepflegt werden kann.** Was nicht
   in fünf Minuten anwendbar ist, wird nicht angewendet.
5. **klein und trotzdem ernsthaft wirkt.** Nicht Konzern, nicht Bastelkeller.

Konkret gebraucht: Wortmarke und Bildmarke, Farbwelt, Typografie,
Bildsprache, Tonalität — und die Frage, ob **„FraWo Funk"** eine
eigenständige Marke wird oder eine Untermarke bleibt.

---

## 10. Abgrenzung — was FraWo nicht ist

- **Kein reiner Verleiher.** Das Material wird gefahren, repariert und
  aufgewertet, nicht nur herausgegeben.
- **Kein Systemhaus.** Es gibt keine Zertifikate und keine Hotline, sondern
  zwei Leute, die ihre eigene Anlage betreiben und wissen, warum sie was tun.
- **Kein Start-up.** Kein Kapital, kein Wachstumsversprechen. Ein Betrieb,
  der aus eigener Kraft wächst.
- **Keine Agentur.** Das Radio ist eigenes Programm, kein Kundenauftrag.

---

## 11. Offene Fragen, die die CI mitentscheiden sollte

1. **Steht „FraWo" für beide Felder oder braucht die IT-Dienstleistung einen
   eigenen Namen?** Ein Veranstaltungskunde und ein Handwerksbetrieb, der
   seinen Server sucht, haben wenig gemeinsam.
2. **Wie heißt der Standort?** Der Gebäudename wird gesucht — er kann Teil
   der Marke werden (Studio, Adresse, Aufnahmeort fürs Radio).
3. **Wie viel Bodensee?** Regionalität ist echt vorhanden. Als Markenkern
   nutzen oder bewusst zurückhalten, um überregional anschlussfähig zu bleiben?
4. **Ist das Radio Marke oder Kanal?** Es könnte das sichtbarste
   Aushängeschild werden — oder ein Nebenschauplatz, der Kraft kostet.

---

*Stand 09.09.2026. Zusammengestellt aus dem laufenden Betrieb: Odoo-Projekten,
Buchhaltung, Anlagendokumentation und Standortnotizen. Die Zahlen sind
Ist-Zahlen, keine Planung.*
