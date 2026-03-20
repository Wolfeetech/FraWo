# HAOS VM 210 Setup Plan

## Zielbild

`VM 210` wird als dedizierte Home Assistant OS VM auf Proxmox betrieben. Sie ist die stabile Smart-Home-Zentrale fuer Supervisor, Add-ons sowie USB-Passthrough von Zigbee- und Bluetooth-Adaptern.

## Defaults

- VM-ID: `210`
- Name: `haos`
- Ziel-IP: `192.168.2.24`
- CPU: `2 vCPU`
- RAM: `4096 MB`
- Disk: `32-64 GB` auf NVMe-Storage
- Machine Type: `q35`
- BIOS: `OVMF (UEFI)`
- SCSI Controller: `virtio-scsi-single`
- Netzwerk: `virtio` an `vmbr0`
- Bootdisk: `scsi0`
- Konsolenmodus: `serial0` als Recovery-Hilfe
- QGA-Kanal: aktiviert, aber nicht als harte Betriebsabhaengigkeit behandelt

## Quellenstand

Der Plan ist auf aktuelle offizielle Quellen vom 2026-03-17 abgestimmt:

- Home Assistant empfiehlt fuer neue Installationen Home Assistant OS auf 64-Bit-Systemen.
- Home Assistant OS fuer virtuelle Umgebungen wird als `haos_ova-<version>.qcow2.xz` aus dem offiziellen Release-Kanal bezogen.
- Proxmox empfiehlt fuer moderne Geraete-/Firmware-Pfade `q35` und `OVMF`.
- Proxmox USB-Passthrough unterstuetzt sowohl Vendor/Product-ID als auch Resource-Mapping fuer feste Portzuordnung.

## Audit Snapshot - 2026-03-18

Auf dem echten Proxmox-Host ist der aktuelle Live-Stand fuer `VM 210` wie folgt verifiziert:

- `VM 210` existiert jetzt und laeuft.
- Basiskonfiguration:
  - `q35`
  - `OVMF`
  - `2 vCPU`
  - `4096 MB` RAM
  - `32 GB` Disk auf `local-lvm`
  - MAC `BC:24:11:D5:BA:30`
- Aktueller Netzwerkstand:
  - hostname `homeassistant.local`
  - stabile In-Guest-Adresse `192.168.2.24`
  - Home Assistant antwortet dort mit `HTTP 200` auf Port `8123`
  - `ha.hs27.internal` liefert intern ueber Caddy ebenfalls `HTTP 200`
- Der Host zeigt bei `lsusb` derzeit nur die Linux-Root-Hubs.
- `/dev/serial/by-id` und `/dev/serial/by-path` sind leer.
- Das bedeutet:
  - aktuell ist noch kein Zigbee-, SkyConnect- oder USB-Bluetooth-Adapter am Host sichtbar
  - USB-Passthrough ist deshalb noch nicht praktisch konfigurierbar
  - der HAOS-Basisaufbau ist bereits erfolgreich ohne Dongles erfolgt
- Ressourcenstand am Host zum Auditzeitpunkt:
  - Host-RAM gesamt: etwa `15 GiB`
  - `MemAvailable`: etwa `8.4-8.5 GiB`
  - `local-lvm` frei: deutlich ueber `130 GiB`
- Betriebsfolgerung:
  - eine HAOS-VM mit `4096 MB` und `32 GB` Disk ist technisch tragfaehig
  - der Basisschritt Adressstabilisierung ist abgeschlossen; naechster Fokus ist Backup-Standard plus spaeter USB
  - lokale KI-Workloads wie `Ollama` bleiben deshalb weiterhin ausserhalb des aktiven Plans
  - fuer USB-Themen muss erst echte Hardware am Host sichtbar sein

## Phase 0 - Vorbedingungen

Vor der Provisionierung muessen folgende Punkte erfuellt sein:

1. Snapshot-Regel aktiv:
   - Vor aendernden Arbeiten Snapshot von `CT 100` oder betroffenen VMs ziehen, falls bestehende Infrastruktur beruehrt wird.
2. Ziel-Storage festgelegt:
   - Beispiel: `local-lvm`
3. Netzwerkpfad festgelegt:
   - `vmbr0`
   - DHCP-Reservation oder statische Adressplanung fuer `192.168.2.24`
4. Download-Pfad auf dem Proxmox-Host verfuegbar:
   - Beispiel: `/var/lib/vz/template/qcow2`

## Workspace-Automation

Der manuelle CLI-Pfad bleibt gueltig, aber im Workspace ist jetzt auch der kontrollierte Betriebsweg vorbereitet:

- Host-Variablen:
  - `ansible/inventory/host_vars/proxmox.yml`
- Runner-Deployment:
  - `ansible/playbooks/deploy_haos_vm_runner.yml`
- Runner auf Proxmox:
  - `/usr/local/sbin/homeserver2027-deploy-haos-vm.sh`
- Operative Checks:
  - `make haos-preflight`
  - `make haos-stage-gate`
  - `make haos-vm-check`

Empfohlene Reihenfolge:

1. `make haos-preflight`
2. `make haos-stage-gate`
3. `make haos-runner-deploy`
4. Erst nach gruener Stage-Gate-Pruefung den eigentlichen Build ausfuehren

Wichtiger Guardrail:

- Das reine Runner-Deployment ist unkritisch.
- Die echte Erstellung von `VM 210` ist nach sauberem Tailscale-Join auf `CT 100` jetzt erfolgt.

## Phase 1 - HAOS-Image beziehen

Empfohlener Pfad: immer das aktuelle stabile Release aus dem offiziellen GitHub-Release-Feed verwenden und keine fest eingebrannte Versionsnummer in Skripte schreiben.

### Variablen

```bash
VMID=210
VM_NAME=haos
VM_STORAGE=local-lvm
IMG_DIR=/var/lib/vz/template/qcow2
```

### Release-Tag bestimmen

Manuell:

- https://github.com/home-assistant/operating-system/releases

Automatisiert:

```bash
HAOS_TAG="$(curl -fsSL https://api.github.com/repos/home-assistant/operating-system/releases/latest | grep -m1 '"tag_name"' | cut -d '\"' -f4)"
HAOS_FILE="haos_ova-${HAOS_TAG}.qcow2.xz"
HAOS_URL="https://github.com/home-assistant/operating-system/releases/download/${HAOS_TAG}/${HAOS_FILE}"
```

### Image herunterladen und entpacken

```bash
mkdir -p "${IMG_DIR}"
curl -fL "${HAOS_URL}" -o "${IMG_DIR}/${HAOS_FILE}"
unxz -f "${IMG_DIR}/${HAOS_FILE}"
HAOS_IMAGE="${IMG_DIR}/haos_ova-${HAOS_TAG}.qcow2"
```

## Phase 2 - VM 210 auf Proxmox anlegen

### VM erzeugen

```bash
qm create "${VMID}" \
  --name "${VM_NAME}" \
  --ostype l26 \
  --machine q35 \
  --bios ovmf \
  --cpu host \
  --cores 2 \
  --memory 4096 \
  --scsihw virtio-scsi-single \
  --net0 virtio,bridge=vmbr0,firewall=1 \
  --serial0 socket \
  --vga serial0 \
  --agent enabled=1 \
  --onboot 1 \
  --protection 1
```

### HAOS-Disk importieren und anbinden

```bash
qm importdisk "${VMID}" "${HAOS_IMAGE}" "${VM_STORAGE}"
IMPORTED_DISK="$(qm config "${VMID}" | awk -F': ' '/^unused[0-9]+:/ {print $2; exit}')"
qm set "${VMID}" --scsi0 "${IMPORTED_DISK},discard=on,ssd=1,iothread=1"
qm set "${VMID}" --boot order=scsi0
qm set "${VMID}" --efidisk0 "${VM_STORAGE}:0,efitype=4m,pre-enrolled-keys=0"
```

### Optional sinnvolle Defaults

```bash
qm set "${VMID}" --rng0 source=/dev/urandom
```

### Disk auf Zielgroesse bringen

```bash
qm resize "${VMID}" scsi0 32G
```

## Phase 3 - Erststart und Basisverifikation

### Erststart

```bash
qm start "${VMID}"
qm status "${VMID}"
```

### Erwartetes Verhalten

- Die VM bootet per UEFI.
- Home Assistant wird beim ersten Start zusaetzliche Komponenten aus dem Internet nachladen.
- Die Erstinitialisierung kann mehrere Minuten dauern.

### Erstpruefung

1. Proxmox-Konsole oeffnen und Bootpfad auf Fehler pruefen.
2. IP-Adresse ueber DHCP-Lease oder Netzwerk-Inventory ermitteln.
3. Home Assistant im LAN oeffnen:
   - aktuell `http://192.168.2.24:8123`
   - intern auch ueber `http://ha.hs27.internal`
4. Erfolgsmerkmale:
   - Onboarding-Seite erscheint
   - Supervisor ist vorhanden
   - Add-on-Store ist vorhanden

### Baseline-Snapshot

Direkt nach erfolgreichem Erstboot und vor weiterer Konfiguration:

- Snapshot `vm-210-baseline-clean-install`

## Phase 4 - Adressierung stabilisieren

### Ziel

Der erfolgreiche First-Boot-Zustand wurde in die geplante stabile Zieladresse `192.168.2.24` ueberfuehrt.

### Operative Konsequenz

- `ha network update enp6s18` wurde im Gast genutzt, um `192.168.2.24/24` mit Gateway `192.168.2.1` zu setzen
- Home Assistant vertraut jetzt dem internen Reverse Proxy von `CT 100` (`192.168.2.20`)
- `ha.hs27.internal` ist bereits auf `192.168.2.24:8123` umgestellt

## Phase 5 - USB-Passthrough fuer Zigbee und Bluetooth

### Ziel

USB-Geraete sollen nach Host- und VM-Reboots stabil wieder in `VM 210` landen.

### Audit vor dem Durchgriff

Auf dem Proxmox-Host erfassen:

```bash
lsusb
ls -l /dev/serial/by-id
```

Dokumentieren:

- Hersteller
- Geraetetyp
- Vendor-ID
- Product-ID
- ob mehrere identische Geraete vorhanden sind
- welcher Adapter in HAOS fuer Zigbee bzw. Bluetooth vorgesehen ist

### Standardpfad: Vendor/Product-ID

Wenn der Adapter eindeutig ist:

```bash
qm set 210 --usb0 host=<vendor_id>:<product_id>,usb3=1
```

Beispiel:

```bash
qm set 210 --usb0 host=10c4:ea60,usb3=1
```

### Fallback: Resource Mapping / Portbindung

Wenn mehrere identische Dongles vorhanden sind oder ein Adapter nach Reboots auf einen anderen Port wandert:

1. Proxmox USB Resource Mapping fuer den physischen Port anlegen.
2. Mapping statt nackter Vendor/Product-ID an die VM binden.
3. Testen:
   - Host reboot
   - VM reboot
   - erneute Geraeteerkennung in Home Assistant

### Verifikation in HAOS

- Zigbee- oder Bluetooth-Integration sieht den Zieladapter.
- Nach VM-Neustart bleibt der Adapter sichtbar.
- Nach Host-Neustart bleibt der Adapter sichtbar.

## Phase 5 - Netzwerk- und Betriebsintegration

### Adressierung

- Bevorzugt DHCP-Reservation fuer `192.168.2.24`
- Optional spaeter interne DNS-Aufloesung:
  - `ha.hs27.internal -> 192.168.2.24`

### Caddy / Tailscale

- Caddy in `CT 100` routet intern zu `http://192.168.2.24:8123`
- Kein oeffentliches Publishing
- Remote-Zugriff nur ueber Tailscale-Tailnet

### QEMU Guest Agent

- Der QGA-Kanal ist auf Proxmox-Seite aktiviert.
- Backup-Konsistenz darf in Phase 1 nicht davon abhaengen, dass HAOS sofort auf `qm agent` antwortet.
- Nach Erstinbetriebnahme pruefen:

```bash
qm agent 210 ping
```

Wenn der Ping funktioniert:

- QGA kann fuer saubere Shutdowns und moegliche Freeze/Thaw-Nutzung mitverwendet werden.

Wenn der Ping nicht funktioniert:

- Betrieb trotzdem fortsetzen
- Snapshot-Backups weiter nutzen
- im Backup-Runbook dokumentieren, dass QGA-Freeze fuer `VM 210` derzeit nicht erzwungen wird

## Phase 6 - Update- und Snapshot-Workflow

Vor jedem Home-Assistant- oder HAOS-Update:

1. Snapshot ziehen:
   - `vm-210-pre-update-<datum>`
2. Update durchfuehren
3. Neu booten und Grundfunktionen pruefen:
   - UI erreichbar
   - Supervisor gesund
   - Zigbee/Bluetooth-Adapter vorhanden
4. Snapshot entweder:
   - bei Fehlern fuer Rollback verwenden
   - oder nach Validierung loeschen bzw. in den regulaeren PBS-Zyklus uebergehen lassen

## Phase 7 - Backup-Integration in PBS

### Ziel

`VM 210` wird als normale QEMU-VM taeglich in PBS gesichert.

### Standard

- Backup-Modus: Snapshot
- Ziel: dedizierte PBS-Instanz oder PBS-VM
- Frequenz: taeglich
- Retention-Beispiel:
  - `keep-last 7`
  - `keep-weekly 4`
  - `keep-monthly 3`

### Restore-Test

Mindestens monatlich:

1. Restore auf freie Test-ID, zum Beispiel `910`
2. Test-VM booten
3. Home Assistant Login pruefen
4. Ergebnis dokumentieren

## Abnahmekriterien

Die Implementierung gilt als erfolgreich, wenn alle folgenden Punkte erfuellt sind:

- `VM 210` bootet stabil mit `q35` und `OVMF`
- Home Assistant ist unter `http://192.168.2.24:8123` erreichbar
- Supervisor und Add-on-Store sind vorhanden
- mindestens ein USB-Adapter ist stabil in HAOS sichtbar
- Snapshot vor Update und Rollback-Pfad sind dokumentiert
- `VM 210` ist in den taeglichen PBS-Backupumfang aufgenommen

## Referenzen

- Home Assistant Generic x86-64 Install:
  - https://www.home-assistant.io/installation/generic-x86-64/
- Home Assistant OS Releases:
  - https://github.com/home-assistant/operating-system/releases
- Home Assistant Hinweis zur Installationsstrategie:
  - https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/
- Proxmox `qm` Manual:
  - https://pve.proxmox.com/pve-docs/qm.1.html
- Proxmox QEMU Guest Agent:
  - https://pve.proxmox.com/wiki/Qemu-guest-agent
- Proxmox USB Physical Port Mapping:
  - https://pve.proxmox.com/wiki/USB_Physical_Port_Mapping
