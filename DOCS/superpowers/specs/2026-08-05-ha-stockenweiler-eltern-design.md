# Home Assistant Stockenweiler (Eltern) — Geräte-Einbindung, Gruppierung & Verbrauchs-Fundament

**Datum:** 2026-08-05
**Status:** Design freigegeben (Wolf), bereit für Umsetzungsplan
**Odoo-Bezug:** #885 (EGS-Nachverhandlung / Wärmepumpe 13–14 kW vs. 12 kW genehmigt), #692 (Lotti VLAN-Isolation, gleiche Schutzlogik hier auf Geräte-Ebene angewendet)

> **Sicherheitshinweis:** Dieses Repo ist öffentlich. KEINE Zugangsdaten (API-Keys, Passwörter, HA-Tokens) in dieses Dokument oder Code committen.

## 1. Ziel

Die Home-Assistant-Instanz der Eltern (`homeassistant_stocki`, VM360, `10.1.0.248:8123`, Stockenweiler) bekommt die im Alopri-Netz gefundenen, noch nicht eingebundenen Geräte (15 Shelly-Schalter + 3 Cast-Geräte) sauber integriert, benannt und nach Hausbereich gruppiert. Darauf aufbauend entsteht das Fundament für Verbrauchs-Sichtbarkeit pro Bereich — als Vorbereitung auf die geplante Wärmepumpe (Odoo #885) und ein späteres Kiosk-Dashboard, ohne diese beiden schon heute zu bauen.

## 2. Ist-Zustand (verifiziert 2026-08-05)

- **Zwei getrennte HA-Instanzen** existieren, nicht verwechseln: `homeassistant_stocki` (VM360, 10.1.0.248, Eltern/Stockenweiler) und eine zweite, unbenannte Instanz (VM210, 10.1.0.40, proxmox-anker) für GrowBox/Studio/Container-Automatisierung (dokumentiert in `DOCS/HOME_ASSISTANT_PRODUCTION_RUNBOOK.md`). Diese Spec betrifft **ausschließlich** die Eltern-Instanz.
- `homeassistant_stocki` hat bereits Bereiche für die Eltern (`Büro_Eltern`, `Wohnküche_Eltern`, `Buero_Controlroom_Eltern`) mit Klimasensoren, Schaltern, Medienplayern.
- Laut `NOW.md` (Alopri-Anbindung, 04.08.2026) wurde ein WireGuard-Site-to-Site-Tunnel (CT106, `wg1`) zum Elternnetz (Fritzbox, `192.168.178.0/24`, WLAN „alopriwlan") gebaut. Ein Netzwerk-Scan fand dort 15 Shelly-Geräte, 3 Cast-fähige Geräte, 1 Drucker, 1 HPE-Switch/AP und 7 unklassifizierte Geräte — **keines davon ist bisher in HA eingebunden**.
- Firewall-Regel auf CT106 erlaubt **nur** `10.1.0.248` (die Eltern-HA-Instanz) vollen Zugriff auf `192.168.178.0/24`. Kein anderes FraWo-Gerät (auch nicht StudioPC) kommt direkt an die Alopri-Geräte heran — Integration muss über HA selbst laufen.
- **Historischer Kontext:** Ein älterer, archivierter Plan (`DOCS/Task_Archive/STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`, Stand März/April 2026) führte die Eltern als externen Test-Kunden für ein vorsichtiges Managed-Support-Produkt („Rentner OS") mit expliziter Regel „kein volles Smart Home, keine Standort-VPN in V1". Diese Zurückhaltung wurde durch die seither gewachsene Praxis (Alopri-Tunnel, bestehende Eltern-Bereiche in HA) überholt — hier dokumentiert als Kontext, nicht als Blocker.

## 3. Abgrenzung (hart, sicherheitsrelevant)

Das Haus in Stockenweiler hat **3 Parteien**:

| Partei | Rolle | In dieser Spec? |
|---|---|---|
| Eltern (Rentner) | Zielgruppe dieser Arbeit | ✅ Ja |
| Lotti (Einliegerwohnung, Mieterin) | separate Partei, eigenes Netz-Isolationsprotokoll (Odoo #692) | ❌ Nein — bleibt komplett draußen aus HA |
| Container-Bereich | eigenes Thema, eigener Stromzähler | ❌ Nein — separates Vorhaben |

Von den 18 im Alopri-Netz gefundenen Geräten kommt **nur** hinein, was Wolf explizit als „gehört den Eltern" bestätigt (Abgleich über die Shelly-Cloud-App, siehe Ablauf unten). Alles andere wird ignoriert, nicht recherchiert, nicht anfasst.

## 4. Architektur-Ansatz

**Gewählt:** Bestehende Instanz `homeassistant_stocki` weiterverwenden, neue Geräte nur in vorhandene/neue Eltern-Bereiche einhängen, zusätzlich Label `Eltern` vergeben.

**Verworfen — zweite, isolierte HA-Instanz nur für die Eltern:** Würde Isolation technisch garantieren, aber doppelten Pflegeaufwand (Updates, Backups, Härtung zweimal) für einen Nutzen erzeugen, den die bestehende Areas/Labels-Konvention bereits abdeckt. Nicht verhältnismäßig (YAGNI).

## 5. Phase 1 (heute): Geräte identifizieren, einbinden, gruppieren

1. Ich rufe pro Gerät (die 18 IPs aus `NOW.md`, Abschnitt Alopri-Anbindung) in Wolfs Chrome-Browser (per Bildschirmsteuerung) `Einstellungen → Geräte & Dienste → Integration hinzufügen` in `homeassistant_stocki` auf. Jedes Gerät liefert dabei seine Geräte-ID/MAC/Modell.
2. Ich übergebe Wolf diese Rohliste (IP + ID + Modell).
3. Wolf gleicht über die Shelly-Cloud-App ab, welches physische Gerät/Zimmer das ist und ob es den Eltern gehört.
4. Für alle als „Eltern" bestätigten Geräte: sinnvollen Namen + passenden Bereich in HA setzen. Rest bleibt unintegriert.
5. **Schutzregel analog `HOME_ASSISTANT_PRODUCTION_RUNBOOK.md`:** Sobald erkennbar ist, dass ein Gerät sicherheits-/gesundheitsrelevant ist (z. B. Kühlschrank, Notruf-nahe Geräte), wird es hier als „nie automatisiert schalten" markiert, bevor irgendeine Automation entsteht.

## 6. Phase 2 (Fundament heute mitdenken, Feinausbau später): Verbrauch

- Nicht jeder Shelly misst Strom (nur PM-Modelle). Wo doch: HA-Energie-Dashboard pro Bereich nutzen.
- Bestehende Zähler decken die Eltern nicht vollständig ab (ELW-Zähler „Lotti" hat z. B. keine Küche drauf; Container hat eigenen Zähler, separates Thema). Lücke wird vorerst **manuell** geschlossen: ein `input_number`-Helfer für periodisch von Wolf eingetragene Zählerstände, gegengerechnet mit der Summe der Shelly-PM-Werte im selben Zeitraum.
- **Offene Anschaffungsentscheidung (nicht Teil von Phase 1):** Ein dedizierter Gesamtzähler (z. B. Shelly Pro 3EM am Sicherungskasten der Eltern) würde Phase 2 sauber lösen und wäre auch für Phase 3 (Lastmanagement) direkt nützlich. Elektriker + Budget nötig — Wolf entscheidet, wann.

## 7. Ausblick, nicht Teil der heutigen Umsetzung

- **Phase 3 — WP-Lastmanagement (Odoo #885):** Genehmigt sind 12 kW, die geplante Wärmepumpe braucht 13–14 kW. Sobald der Einbau feststeht, braucht es eine Automation, die bei hoher WP-Last andere große Verbraucher kurz abschaltet. Die heutige Bereichs-/Label-Struktur und das Energie-Fundament aus Phase 2 werden so gebaut, dass diese Automation später draufgesetzt werden kann, ohne Umbau.
- **Phase 4 — Kiosk-Board:** Eine feste, bewusst einfache (Wolf: „weniger Spielereien") Anzeige-/Bedienoberfläche für die Eltern, die Verbrauch und Steuerung zeigt. Hardware, Standort und genaue Funktionen sind noch offen — eigene Detailrunde, sobald Phase 1–2 stehen.

## 8. Risiken & Guardrails

- **Party-Grenze verletzen:** Größtes Risiko dieser Arbeit. Gegenmaßnahme: nur Geräte einbinden, die Wolf nach Shelly-Cloud-Abgleich explizit als „Eltern" bestätigt (Abschnitt 3+5).
- **Automatisch etwas abschalten, das nicht abgeschaltet werden darf:** Keine Automationen in Phase 1 — nur Einbindung/Benennung/Gruppierung. Automationen erst nach expliziter Schutzliste (Abschnitt 5).
- **Browser-Automatisierung bricht andere offene Tabs/Sessions:** Nur in einem neuen Tab arbeiten, bestehende Wolf-Sessions nicht schließen.

## 9. Definition of Done (Phase 1)

- Alle von Wolf als „Eltern" bestätigten Geräte sind in `homeassistant_stocki` sichtbar, sinnvoll benannt, richtigem Bereich zugeordnet, Label `Eltern` gesetzt.
- Keine Lotti-/ELW- oder Container-Geräte wurden angefasst oder recherchiert.
- Rohliste (IP/ID/Modell → Zuordnung Eltern ja/nein) ist dokumentiert (Odoo-Aufgabe oder Anhang zu dieser Spec).
