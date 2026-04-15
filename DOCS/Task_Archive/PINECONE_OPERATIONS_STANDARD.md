# Pinecone Operations Standard

Stand: `2026-04-09`

## Zweck

Dieses Dokument definiert den verbindlichen Standard fuer die Nutzung des Pinecone Vektor-Datenbank-Service innerhalb des Homeserver 2027 Ecosystems.

## Infrastruktur

- **Provider**: Pinecone Cloud (Serverless)
- **Region**: `us-east-1` (AWS)
- **Index-Name**: `homelab`
- **Dimension**: `1024`
- **Metrik**: `cosine`
- **Modell**: `llama-text-embed-v2`

## Sicherheits-Richtlinien

1. **API-Keys**: 
   - Niemals im Repo einchecken.
   - Ablage ausschliesslich in Vaultwarden (Organisation: `FraWo`).
   - Laufzeit-Zugriff via Environment-Variable `PINECONE_API_KEY`.
2. **Namensraeume (Namespaces)**:
   - `knowledge-base`: Fuer Repo-Dokumentation und AI-Handoffs.
   - `radio-metadata`: Fuer semantische Musik-Suche (Lyrics, Stimmung, Genre-Beziehungen).
   - `odoo-sync`: Fuer Aufgaben-Matching und ERP-Kontext.

## Betriebliche Nutzung

### AI Knowledge Base
Der Index dient als "Long-Term Memory" fuer die KI-Agenten. Handoffs und Masterplane werden hier vektorisiert, um agentenuebergreifende Konsistenz zu garantieren.

### Radio Operations
Durch Einbettung von Song-Metadaten lassen sich komplexe Abfragen wie "Finde Songs, die klingen wie [Track X] fuer eine Abend-Playlist" realisieren.

## Wartung & Monitoring

Check der Index-Erreichbarkeit:
```bash
python scripts/pinecone_ping.py
```

## Naechste Schritte
1. Synchronisation der aktuellen Repodaten in den `knowledge-base` Namespace.
2. Integration der AzuraCast 'Now Playing' Historie in `radio-metadata`.
