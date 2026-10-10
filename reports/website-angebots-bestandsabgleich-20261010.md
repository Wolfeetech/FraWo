# FraWo Website – Angebots- und Bestandsabgleich

**Stand:** 10.10.2026  
**Aufgaben:** Odoo #1996 / #1644 / #1224  
**Methode:** öffentliche Website gegen aktive `product.product`-Datensätze in Odoo, read-only

## 1. Ergebnis in einem Satz

Die öffentliche Verleihseite zeigt sieben Angebote, während Odoo zusätzlich mehrere alte Paketprodukte führt. Die Website- und Odoo-Wahrheit ist deshalb noch nicht identisch; vor einem Redesign müssen die tatsächlich gewünschten Angebote festgelegt und anschließend gemeinsam bereinigt werden.

## 2. Öffentliche Website – aktuell sichtbar

Die Live-Seite `/verleih` zeigt unter anderem:

- 5m Riesen-Fußballdart – 250 €
- DJ- & Audio-Regieplatz – 50 €
- Sprachpaket JBL EON + SM58 – auf Anfrage
- Kleines Partyset · EON + 4 Moving Heads – auf Anfrage
- JBL EON 615 – 20 €
- Showtec Shark Spot – 20 €
- BeamZ Panther 35 2er-Set – 15 €

Die Seite nennt zusätzlich Bestandssprache wie „auf Anfrage“, aber die Zahl `Alle Angebote (7)` und mehrere Paketbeschreibungen sind redaktionell gesetzt und nicht automatisch aus Odoo abgeleitet.

## 3. Odoo – aktive Miet-/Event-Produkte

Read-only aus `product.product`, Kategorien Vermietung/Event:

### Mit konkretem Bestand größer 0

- 3in1 Outdoor PAR: 2 Stück
- BeamZ Panther 35: 2 Stück
- Showtec Shark: 6 Stück
- JBL EON 615: 1 Stück
- PKW-Anhänger 750 kg: 1 Stück
- Stromkabel-Set: 1 Stück

### Mit Bestand 0 oder als Service/Paket geführt

- `RENT-LIGHT-SET` Ambient & Dance Licht-Set: Bestand 0
- `RENT-PA-CLUB` Club & Open-Air Sound-System: Bestand 0
- `RENT-PA-COMPACT` Compact Party PA-Set: Bestand 0
- `RENT-AUDIO-DJ-SET` DJ & Audio-Regie-Set: Bestand 0, Serviceprodukt
- `RENT-LIGHT-01` Licht-Set Pro Show: Bestand 0
- `PAKET-S`, `PAKET-M`, `PAKET-L`: Bestand 0, Serviceprodukte
- `Fußballdart – Event-Modul`: Bestand 0, Serviceprodukt

## 4. Belastbare Abweichungen

- Odoo führt weiterhin alte große Pakete für bis zu 100, 250 und 500 Personen, obwohl die öffentliche Darstellung bereits vorsichtiger formuliert ist.
- Odoo führt mehrere Licht-/PA-Pakete mit Bestand 0; das ist kein automatischer Nachweis, dass sie öffentlich sofort angeboten werden dürfen.
- Die Website zeigt ein Partyset mit „4 Moving Heads“, während die aktuelle Odoo-Basis bei sichtbaren Einzelgeräten andere Mengen und Bestände ausweist. Das Paket braucht deshalb eine ausdrückliche Bestätigung oder muss anders beschrieben werden.
- Die Website zeigt das Sprachpaket JBL EON + SM58; der öffentliche Text ist plausibel, der konkrete Bestand des SM58 wurde in diesem Lauf noch nicht separat geprüft.
- Die Website zeigt den DJ-/Audio-Regieplatz; das Odoo-Produkt existiert, ist aber als Serviceprodukt ohne Bestandsmenge angelegt. Das ist für ein auf Anfrage vermitteltes Setup möglich, aber kein automatischer Lagerbeleg.
- Fußballdart ist preislich zwischen Website und Odoo konsistent bei 250 €, aber Odoo liefert dafür keine physische Bestandsmenge.

## 5. Vorläufige redaktionelle Konsequenz

Für die neue Website sollten zunächst drei Angebotsarten getrennt werden:

1. **Konkrete Einzelgeräte mit belegtem Bestand** – z. B. JBL EON 615, Showtec Shark, BeamZ Panther, Outdoor PAR.
2. **Zusammenstellungen auf Anfrage** – nur wenn die enthaltenen Komponenten und die Zuständigkeit dafür bestätigt sind.
3. **Betreute Veranstaltungstechnik / Crew-Leistung** – unabhängig davon, ob ein Mietartikel als Lagerprodukt geführt wird.

Die alten Pakete `PAKET-S/M/L`, `RENT-PA-CLUB`, `RENT-PA-COMPACT`, `RENT-LIGHT-SET` und `RENT-LIGHT-01` sollten nicht als fertige öffentliche Wahrheit behandelt werden, solange ihre Komponenten, Mengen und tatsächliche Lieferbarkeit nicht geprüft sind.

## 6. Nächster Schritt

Als Nächstes muss der öffentliche Bestand auf eine kleine, ehrliche Angebotsliste reduziert werden. Erst danach lohnt sich der neue Seitenentwurf. Bis dahin werden keine Angebote gelöscht und keine Odoo-Produkte geändert.
