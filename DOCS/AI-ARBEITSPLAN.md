# FraWo KI-Arbeitsplan

Stand: 08.10.2026

## Ziel

KI soll im Alltag nicht nur Antworten formulieren, sondern Wolfs und Hermes' Arbeit
messbar beschleunigen: Vorgänge lesen, Informationen ordnen, Entwürfe liefern,
Risiken markieren und sichere nächste Schritte vorbereiten. Produktive Änderungen,
Freigaben, Geld, externe Nachrichten und Abschlüsse bleiben ausdrücklich geschützt.

## Rechenrouting

1. **Normaler Odoo-Auftrag mit `@Ollama`**
   - zuerst StudioPC-GPU: `frawo-mitarbeiter:latest`
   - nur bei Nichterreichbarkeit: OptiPlex-CPU `frawo-mitarbeiter-fast:latest`
   - der verwendete Knoten wird in der internen Antwort genannt
2. **`🤖 Ollama Power`**
   - ausschließlich StudioPC-GPU
   - kein stiller CPU-Ersatz; bei Ausfall bleibt die Frage offen
3. **Alarme und Kurztexte**
   - StudioPC zuerst
   - OptiPlex als Formulierungs-Fallback
   - bei beiden Ausfällen deterministische Rohmeldung

## Modellrollen

- **`frawo-mitarbeiter:latest` auf dem StudioPC**: Standard für Odoo-Aufgaben,
  Recherche, Zusammenfassungen, Entscheidungsgrundlagen und strukturierte Berichte.
- **`qwen2.5-coder:7b` auf dem StudioPC**: Code, Bash, Python, Tests und
  technische Fehlersuche. Änderungen werden trotzdem vom Hermes-Prozess geprüft.
- **`deepseek-r1:8b` auf dem StudioPC**: längere Abwägungen, Ursachenanalyse und
  Alternativen. Nicht für schnelle Alarmtexte.
- **`frawo-mitarbeiter-fast:latest` auf dem OptiPlex**: kurze Routineantworten,
  falls der StudioPC ausgeschaltet oder nicht erreichbar ist.
- **`nomic-embed-text:latest`**: lokale Suche/RAG, nicht als Antwortmodell.

## Praktischer Arbeitsablauf

### 1. Odoo als Eingang

Wolf erwähnt `@Ollama` direkt an der Aufgabe und formuliert eine konkrete Frage,
z. B.:

- „Lies den Vorgang und gib mir die drei wichtigsten offenen Entscheidungen.“
- „Prüfe die Angaben gegen die vorhandenen Unterlagen und markiere Unsicherheiten.“
- „Erstelle einen kurzen Arbeitsplan, noch nichts live ändern.“
- „Vergleiche die zwei Varianten und empfehle eine.“

Die Antwort landet als interne Notiz am selben Vorgang. Sie ist Zuarbeit, keine
Freigabe und kein automatischer Abschluss.

### 2. Hermes führt sichere Arbeit aus

Wenn eine Umsetzung gewünscht ist, übernimmt Hermes den vollständigen Ablauf:
Ist-Stand lesen, Backup, kleine Änderung, echte Prüfung, Chatter-Nachweis,
Commit/Push und nur dann Abschlussentscheidung.

### 3. Wolf entscheidet nur an den roten Linien

Wolf muss nur gefragt werden, wenn eine Entscheidung wirklich erforderlich ist:
Kauf/Geld, Löschen, Neustart kritischer Systeme, Netzwerk-/Firewalländerung,
externe Nachricht oder eine unklare fachliche Entscheidung.

## Was das konkret bringt

- **Schneller Überblick:** lange Aufgaben und Chatter-Verläufe werden auf offene
  Punkte, Fristen und Abhängigkeiten reduziert.
- **Bessere Vorbereitung:** Angebote, Technikpakete, Radio-Kuration und Website-
  Änderungen starten mit einer geordneten Faktenbasis statt mit Vermutungen.
- **Weniger Fehlstarts:** Unsichere Bilder, unklare Bestände, falsche Playlist-
  Zuordnungen und fehlende Nachweise werden vor einer Änderung markiert.
- **GPU-Nutzung im Normalfall:** normale Odoo-Zuarbeit läuft schnell auf dem
  StudioPC; der OptiPlex bleibt die belastbare Rückfallebene.
- **Kein stiller Qualitätsverlust:** fällt die GPU aus, ist der Fallback sichtbar;
  Power-Aufträge werden nicht heimlich auf das schwächere Modell verschoben.

## Abnahme des Routings

Das Routing gilt als funktionsfähig, wenn:

- StudioPC erreichbar → normale Odoo-Anfrage nutzt `frawo-mitarbeiter:latest` auf
  `10.0.0.156`;
- StudioPC nicht erreichbar → dieselbe Anfrage nutzt den OptiPlex-Fallback;
- `Ollama Power` bei StudioPC-Ausfall offen scheitert und keinen stillen Ersatz nutzt;
- Antwort im selben Odoo-Chatter landet;
- keine Aufgabe automatisch abgeschlossen oder eine externe Nachricht gesendet wird.
