# Kritische Review – FraWo-Funk-Vollprogramm-Pilot

Stand: 2026-10-10, nach Schedule-Korrektur, Cache-Bereinigung und erneutem Live-Readback.

## Freigabestatus

**Der datierte Pilot 12.–18. Oktober 2026 und der Fallback ab 19. Oktober sind technisch konfliktfrei.**

Die redaktionelle Dauerfreigabe bleibt für die noch offenen BPM-/Energie-/Übergangs- und Wiederholungsabstände ein eigener nächster Prüfschritt. Der technische Scheduler-Blocker ist behoben.

## Was bestanden ist

- Pilot-Schedule 12.–18.10.2026: 55 Einträge.
- 168 Stunden Abdeckung.
- Keine Lücke und keine Überschneidung in der 30-Minuten-Prüfung.
- Die neuen Queues wurden am echten AzuraCast-Ziel rückgelesen.
- Now-Playing HTTP 200.
- Öffentlicher Player HTTP 200.
- Stream HTTP 206, `audio/mpeg`.
- Restart der Radiostation nach der Schedule-Änderung erfolgreich; Live-Ausspielung kam sauber zurück.

## Kritische Befunde und Korrektur

### 1. Scheduler-Cache und datierte Fallback-Einträge

Die erste Prüfung zeigte eine Abweichung zwischen Playlistdefinition und ausgelieferter Schedule-Ansicht. Ursache war eine Kombination aus alten generierten Schedule-Vorkommen und nicht geleertem AzuraCast-Scheduler-Cache.

Korrigiert wurden die datierten Sonntagseinträge für:

- `FraWo Selects` (ID 901)
- `Sunday Soul` (ID 898)
- `Sunday Sunset` (ID 899)
- `⭐ Best of the Week` (ID 869)

Die ersten regulären Fallback-Vorkommen sind jetzt ab Dienstag, 20.10.2026, datiert; dadurch entsteht kein rückwirkendes Vorkommen mehr im Pilotfenster. Danach wurde der AzuraCast-Cache über den Admin-Endpunkt geleert.

### 2. Finaler Schedule-Readback

Nach der Korrektur und Cache-Bereinigung wurde die öffentliche Schedule-API erneut geprüft:

- Pilot 12.–18.10.2026: 54 relevante Einträge, 168 Stunden Abdeckung, 0 Lücken, 0 Überschneidungen.
- Fallback 19.–25.10.2026: 32 relevante Einträge, 168 Stunden Abdeckung, 0 Lücken, 0 Überschneidungen.
- Nachtübergang auf Montag, 26.10.2026: `Night Drive` 00:00–06:00, danach `Morning Flow` und `Afro-Noon` ohne Lücke.

Die zuvor gefundenen Fälle `Night Drive`/`Night Drive`, `FraWo Selects`/`Sunday Soul` und `⭐ Best of the Week`/`Sunday Sunset` sind im finalen Readback nicht mehr vorhanden.

### 3. Pool-Kuration ist noch regelbasiert, nicht vollständig musikalisch geprüft

Die neuen Pools wurden aus belegten Genregruppen und tatsächlichen Quellplaylists gebaut. Das ist sicherer als Dateinamenraten, ersetzt aber noch nicht die vollständige Prüfung von:

- BPM und Energieverlauf
- Übergangstauglichkeit
- Mix-/Versionstyp
- Lautheits-/Qualitätsunterschieden
- tatsächlicher Hörwirkung

Vor einer endgültigen redaktionellen Dauerrotation müssen diese Punkte pro Mood-Familie nachgeprüft werden.

### 4. Cross-Pool-Dubletten sind bewusst vorhanden, aber noch nicht global gesteuert

Die 18 neuen Pools teilen sich insgesamt 93 Titelüberschneidungen über 19 Pool-Paare. Das ist musikalisch teilweise sinnvoll, aber ohne globale Titel- und Künstler-Sperrzeiten kann ein Titel bei dicht aufeinanderfolgenden Pools zu früh wieder auftauchen.

### 5. Manche Pools haben wiederholte Künstler

Beispiele aus den geprüften Pools:

- Friday Disco Drive: bis zu drei Titel desselben Künstlers.
- Deep Night — Hypnotic Drift: bis zu drei Titel eines Künstlers.
- einige Morgen-, Sunset- und Global-Pools enthalten ebenfalls Künstlerwiederholungen.

Shuffle allein löst dieses Problem nicht zuverlässig.

## Verbleibende redaktionelle Aufgaben

1. Pro Mood-Familie BPM, Energie und Übergänge auditieren.
2. Globale Titel-/Künstler-Sperrzeiten festlegen und mit einem mehrtägigen Queue-Test prüfen.
3. Danach den technisch konfliktfreien Plan als redaktionellen Dauerbetrieb freigeben.

Der technische Scheduler-Blocker ist erledigt; die verbleibenden Punkte sind keine Schedule-Lücken oder Überschneidungen, sondern Qualitäts- und Rotationsprüfung.
