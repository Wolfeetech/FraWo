# Kritische Review – FraWo-Funk-Vollprogramm-Pilot

Stand: 2026-10-09, nach Schedule- und Live-Readback.

## Freigabestatus

**Der datierte Pilot 12.–18. Oktober 2026 ist technisch sauber. Der Fallback ab 19. Oktober ist noch nicht freigabefertig.**

## Was bestanden ist

- Pilot-Schedule 12.–18.10.2026: 55 Einträge.
- 168 Stunden Abdeckung.
- Keine Lücke und keine Überschneidung in der 30-Minuten-Prüfung.
- Die neuen Queues wurden am echten AzuraCast-Ziel rückgelesen.
- Now-Playing HTTP 200.
- Öffentlicher Player HTTP 200.
- Stream HTTP 206, `audio/mpeg`.
- Restart der Radiostation nach der Schedule-Änderung erfolgreich; Live-Ausspielung kam sauber zurück.

## Kritische Befunde

### 1. Fallback-Schedule stimmt noch nicht mit Playlist-Definitionen überein

Die Playlist-API zeigt für mehrere Einträge bereits die korrigierten Zeitblöcke. Die öffentliche und interne Schedule-Ansicht liefert jedoch weiterhin alte, bereits ersetzte Vorkommen:

- `Night Drive — Midnight Motion` erscheint am 19.10. noch 00:00–02:00 zusätzlich zu `Night Drive`.
- `FraWo Selects` überschneidet sich am 25.10. noch mit `Sunday Soul`.
- `⭐ Best of the Week` überschneidet sich am 25.10. noch mit `Sunday Sunset`.

Das ist kein redaktionelles Detail, sondern eine Abweichung zwischen gespeicherter Playlistdefinition und tatsächlich ausgelieferter Schedule-Ansicht. Der Fallback darf deshalb noch nicht als sauber abgenommen gelten. Vermutete Ursache: alte generierte Schedule-Vorkommen bzw. Scheduler-Cache werden durch die Playlist-Updates nicht vollständig entfernt.

### 2. Pool-Kuration ist noch regelbasiert, nicht vollständig musikalisch geprüft

Die neuen Pools wurden aus belegten Genregruppen und tatsächlichen Quellplaylists gebaut. Das ist sicherer als Dateinamenraten, ersetzt aber noch nicht die vollständige Prüfung von:

- BPM und Energieverlauf
- Übergangstauglichkeit
- Mix-/Versionstyp
- Lautheits-/Qualitätsunterschieden
- tatsächlicher Hörwirkung

Vor einer endgültigen Dauerrotation müssen diese Punkte pro Mood-Familie nachgeprüft werden.

### 3. Cross-Pool-Dubletten sind bewusst vorhanden, aber noch nicht global gesteuert

Die 18 neuen Pools teilen sich insgesamt 93 Titelüberschneidungen über 19 Pool-Paare. Das ist musikalisch teilweise sinnvoll, aber ohne globale Titel- und Künstler-Sperrzeiten kann ein Titel bei dicht aufeinanderfolgenden Pools zu früh wieder auftauchen.

### 4. Manche Pools haben wiederholte Künstler

Beispiele aus den geprüften Pools:

- Friday Disco Drive: bis zu drei Titel desselben Künstlers.
- Deep Night — Hypnotic Drift: bis zu drei Titel eines Künstlers.
- einige Morgen-, Sunset- und Global-Pools enthalten ebenfalls Künstlerwiederholungen.

Shuffle allein löst dieses Problem nicht zuverlässig.

## Korrektur vor endgültiger Freigabe

1. Die generierten alten Schedule-Vorkommen am echten AzuraCast-Scheduler entfernen oder sauber neu aufbauen.
2. Den Fallback erneut über die öffentliche Schedule-API prüfen.
3. Globale Titel-/Künstler-Sperrzeiten festlegen.
4. Pro Mood-Familie BPM, Energie und Übergänge auditieren.
5. Erst dann den Wochenplan als dauerhaften Regelbetrieb statt als datierten Pilot verwenden.
