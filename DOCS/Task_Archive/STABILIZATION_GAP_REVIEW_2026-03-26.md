# Stabilization Gap Review 2026-03-26

## Ziel

Diese Notiz trennt zwischen:

- akutem Live-Betrieb
- unprofessionellen Zwischenloesungen
- den naechsten technischen Bereinigungen

## Harte Blocker

### 1. Backup ist aktuell nicht produktionsreif

- Das USB-/PBS-Ziel ist technisch ausgefallen.
- Live-Stand:
  - `pbs-usb` deaktiviert
  - `pbs-interim` deaktiviert
  - `sdb1` zeigte echte `I/O error`-Meldungen
- Der aktuelle Backup-Pfad ist damit **nicht belastbar**.

Beleg:

- `ansible/inventory/host_vars/pbs.yml:8`
- `MASTERPLAN.md:147`
- `PLATFORM_STATUS.md:73`

### 2. Secrets liegen an zu vielen falschen Orten

- Zugangsdaten stehen noch im Klartext in Markdown.
- Einzelne Hilfsskripte enthalten noch `sshpass` plus Host-Root-Zugriff.
- Das ist nicht nur unschoen, sondern blockiert jede saubere Handover-/Recovery-Strategie.

Beleg:

- `ACCESS_REGISTER.md:36`
- `CHECKLIST_NEXT_STEPS_WOLF_FRANZ.md:74`
- `ct100_delete_bootstrap.sh:2`
- `probe_jf_schema.sh:2`
- `probe_jf_tables.sh:2`
- `probe_jf_db.py.sh:2`
- `probe_paperless_users.sh:2`
- `probe_jf_users.sh:2`

### 3. Proxmox-Admin-Modell ist noch Break-Glass statt Standard

- Wir arbeiten aktuell ueber `root` auf dem PVE-Host.
- Das war fuer Recovery vertretbar.
- Es ist **nicht** der richtige Dauerstandard.

Beleg:

- Live-Zugriff zuletzt ueber `root@192.168.2.10`
- `ansible.cfg:3` ist zudem workstation-spezifisch

### 4. Storage-Policy ist noch inkonsistent

- `CT100 toolbox` liegt mit einem grossen `raw`-Rootfs auf `local`.
- `VM200 nextcloud` liegt noch auf `local`.
- Andere VMs liegen bereits auf `local-lvm`.
- Das ist kein akuter Totalschaden mehr, aber eine klare Quelle fuer kuenftigen Root-Druck.

Live-Beleg:

- `pct config 100` -> `rootfs: local:100/vm-100-disk-0.raw,size=96G`
- `qm config 200` -> `scsi0: local:200/vm-200-disk-0.qcow2,size=32G`

### 5. Repo und Live-System waren nicht mehr deckungsgleich

- `vault.hs27.internal` war im Repo vorbereitet, aber live unvollstaendig.
- `AdGuard`-Rewrite und `Caddy`-/TLS-Verhalten mussten live nachgezogen werden.
- Damit ist Ansible aktuell **nicht voll die Source of Truth**.

Beleg:

- `ansible/inventory/host_vars/toolbox.yml:33`
- `ansible/templates/stacks/toolbox-network/Caddyfile.j2:2`
- `ansible/templates/stacks/toolbox-network/docker-compose.yml.j2:8`

## Mittlere Probleme

### 6. Dokumentationsdrift

- Mehrere Dateien behaupten noch, `pbs-interim` sei aktiv.
- Das ist live falsch und fuehrt bei der naechsten Session direkt in Fehlentscheidungen.

Beleg:

- `MASTERPLAN.md:147`
- `MASTERPLAN.md:155`
- `PLATFORM_STATUS.md:65`
- `PLATFORM_STATUS.md:73`
- `BACKUP_RESTORE_PROOF.md:8`

### 7. DNS-/Interner-Namenspfad ist nicht sauber genug dokumentiert

- Clients nutzen nicht zwingend direkt `192.168.2.20` als DNS.
- Solange das nicht bewusst standardisiert ist, bleiben interne Hostnamen stoeranfaellig.

### 8. Mail ist funktional, aber noch kein sauberer Endzustand

- `webmaster` als technisches Basis-Postfach ist als Uebergang okay.
- `wolf`, `info`, `noreply` sind derzeit Alias-Loesungen.
- `franz@frawo-tech.de` ist noch nicht als sauberer eigener Produktivpfad abgeschlossen.

Beleg:

- `MAIL_SYSTEM_ROLLOUT.md:27`
- `STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md:79`

## Was wir selbst unprofessionell gemacht haben

1. Storage kurzfristig mit Ad-hoc-Massnahmen statt klarer Policy entlastet.
2. Auf dem PVE-Host zu lange ohne sauberen Nicht-Root-Adminpfad gearbeitet.
3. Plaintext-Secrets in Uebergangsdateien zu lange stehen gelassen.
4. Hilfsskripte mit `sshpass` und hart codierten Zugaengen nicht rechtzeitig aus dem Betrieb genommen.
5. Statusdokumente nach den Live-Reparaturen nicht sofort konsistent nachgezogen.
6. USB-/PBS-v1 zu frueh wie ein belastbarer Backup-Standard behandelt.

## Richtiger Zielstandard

### Admin

- Proxmox Host:
  - `root` nur fuer Break-Glass und Konsole
  - sonst `ops`-Benutzer + API-Token
- Gaeste:
  - benannter Admin-User + SSH-Key
  - kein `sshpass`

### Storage

- `local` auf dem Host nur fuer das, was dort bewusst liegen soll
- produktive VM-/CT-Disks mit klarer Policy
- keine spontanen Symlink-/Auslagerungs-Hacks in Proxmox-Storage-Pfaden

### Backup

- PBS erst wieder als produktiv markieren, wenn:
  - neues gesundes Zielmedium steht
  - Backup gruen laeuft
  - Restore erneut bewiesen ist

### Secrets

- `Vaultwarden` ist der Zielort
- Markdown nur noch als Referenz, nicht als Klartext-Quelle
- Hilfsskripte ohne feste Passwoerter

## Naechste Bereinigung in richtiger Reihenfolge

1. Backup- und PBS-Stand im Workspace auf den echten Ist-Zustand korrigieren.
2. `sshpass`-/Hartpasswort-Skripte entfernen oder neutralisieren.
3. Proxmox-Adminstandard aufsetzen:
   - Nicht-Root-Admin
   - API-Token
   - Root nur noch Break-Glass
4. Storage-Policy sauber festziehen:
   - `VM200` von `local` weg
   - `CT100` spaeter gezielt neu bewerten
5. `Vaultwarden` jetzt produktiv befuellen.
6. Danach Markdown-Zugangsdaten zurueckbauen.

## Aktuelle Entscheidung

Der groesste verbliebene Fachblocker ist **nicht** mehr `Vaultwarden`.

Der groesste Blocker ist jetzt:

- fehlender belastbarer Backup-Standard
- plus die noch unaufgeraeumte Admin-/Secret-/Dokudrift
