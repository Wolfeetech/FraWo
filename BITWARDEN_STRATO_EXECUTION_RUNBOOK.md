# Vaultwarden And STRATO Execution Runbook

## Status

Dieses Dokument ist jetzt ein Uebergangs- und Referenzdokument.

Der kanonische Betriebsstand liegt jetzt in:

- `OPERATIONS/BITWARDEN_OPERATIONS.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `VAULTWARDEN_SELFHOST_START.md`

Stand: `2026-03-27`

## Restnutzen

- CSV-Import nur noch lokal ausserhalb des Repos
- Sichtpruefung des importierten Bestands
- kontrollierter Wechsel auf `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`

## Noch Relevante Kommandos

- `python scripts/export_access_register_to_vaultwarden_csv.py --dry-run`
- `python scripts/export_access_register_to_vaultwarden_csv.py --split-by-collection`
- `python scripts/build_vaultwarden_reference_register.py`

## Heute Wirklich Offen

1. `FraWo` sichtbar pruefen
2. Mail- und Domain-Eintraege in Vaultwarden pruefen
3. `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` als Arbeitsreferenz bestaetigen
4. Desktop-Archiv von `ACCESS_REGISTER.md` nur noch ausserhalb des Repos als Altquelle behalten
