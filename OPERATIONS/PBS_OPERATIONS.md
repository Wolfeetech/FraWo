# PBS Operations

## Zweck

`VM 240 pbs` ist der Proxmox-Backup-Server fuer den Backup- und Restore-Standard.

## Zugriff

- `192.168.2.25:8007`
- geplanter Proxmox-PBS-Target-Name nach dem guarded Rebuild: `pbs`

## Aktueller Zustand

- `VM 240` existiert, ist aber aktuell gestoppt und driftig.
- `scsi0` und `scsi1` zeigen derzeit falsch auf die deaktivierte Storage-ID `pbs-usb`.
- Der produktive PBS-Pfad ist deshalb noch nicht freigegeben.
- Der einzige erlaubte Wiederaufbaupfad ist der guarded Rebuild ueber den Geraetevertrag.

## Guarded Rebuild

1. `make pbs-device-inventory`
2. `make pbs-contract-prefill BOOT_SERIAL=... DATASTORE_SERIAL=... APPROVED_BY=...`
3. destruktive Freigaben bewusst in `manifests/pbs_rebuild/device_contract.json` setzen
4. `make pbs-rebuild-contract-check`
5. `make pbs-datastore-prepare DEV=/dev/sdX`
6. `make pbs-runner-deploy`
7. `make pbs-vm240-reconcile`
8. erst danach Installer, Datastore-Initialisierung, Proof-Backup und Restore-Drill

## Normalbetrieb Erst Nach Gruen

- PBS erreichbar
- Datastore aktiv
- letzter Backup-Lauf erfolgreich
- Restore-Proof weiterhin reproduzierbar

## Eskalation

- bei Blockern zuerst die neuesten Reports unter `artifacts/pbs_device_inventory/`, `artifacts/pbs_guarded_rebuild/` und `artifacts/pbs_vm240_reconcile/` pruefen
- keine USB-/SSD-Reformatierung ohne sichtbare Seriennummer und expliziten Geraetevertrag
