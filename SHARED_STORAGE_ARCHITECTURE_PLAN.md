# Zentrales Storage-Architektur Konzept (Single Source of Truth)

## Zielsetzung
Abschaffung von doppelter Datenhaltung. Die Homeserver 2027 Infrastruktur benötigt eine vernetzte "Single Source of Truth" (SST) für Dokumente und Medien, bei der eine einzige Datei auf dem Datenträger liegt und von allen berechtigten Systemen konsumiert wird.

## Das Problem der Isolation
Aktuell leben die Dienste in ihren eigenen VMs/LXCs:
- **Nextcloud (VM 200)** hat sein eigenes Root-Filesystem.
- **Paperless (VM 230)** hat sein eigenes PDF-Archiv verschlossen.
- **Jellyfin (CT 100)** und **AzuraCast (Radio Pi)** kopieren Medien über `rsync` hin und her.

## Best Practice Lösung: Der "Data Node" (LXC 110)
Anstatt NFS/Samba unsauber direkt auf dem Proxmox-Hypervisor zu installieren, kapseln wir unseren zentralen Datenpool in einem minimalistischen Container (File-Server).

- **ID**: `CT 110 data-node`
- **OS**: Debian 12 (bookworm)
- **Storage**: Eine große virtuelle Disk (z. B. auf `local-lvm`), die später einfach auf SSDs oder ein ZFS-Mirror migriert werden kann.
- **Protokoll**:
  - `NFSv4` (extrem schnell, nativ für Linux, ideal für VMs)
  - `Samba / SMB` (optional, falls ein direkter Windows-Mount im LAN gewünscht ist)

---

## Umsetzung: Dokumenten-Verschmelzung

**Ziel:** Paperless-Archiv = Nextcloud-Ordner

1. Auf `CT 110` wird eine NFS-Freigabe `/mnt/data/documents` erstellt.
2. **Paperless (VM 230)** bindet dies per `/etc/fstab` (NFS) als sein `media/archive` Verzeichnis ein. Jedes OCR-verarbeitete PDF landet sofort auf dem NFS.
3. **Nextcloud (VM 200)** bindet **exakt diesen** NFS-Ordner ebenfalls schreibgeschützt (oder als Admin mit vollen Rechten) als "Externen Speicher" (Typ: Lokal gemounteter NFS) unter `/Freigaben/Paperless-Archiv` ein.
4. **Odoo (VM 220)** kann optional Dokumente über das Nextcloud-WebDAV reingeben oder selbst lesend auf das NFS zugreifen.

**Vorteile:** Nextcloud-User müssen nicht in Paperless springen, um alte PDFs durchzusuchen. Alles ist native im Dateimanager.

---

## Umsetzung: Medien-Verschmelzung

**Ziel:** Raspberry Pi Radio = Jellyfin Bibliothek = 1 zentraler Ort

1. Auf `CT 110` wird eine NFS-Freigabe `/mnt/data/media` erstellt.
2. Das Master-Verzeichnis (`/music`, `/shows`, `/movies`) liegt zentral hier.
3. **Jellyfin (CT 100)** bindet `/mnt/data/media/music` über einen Proxmox Bind-Mount (bei LXC zu LXC) oder über NFS ins eigene `/srv/media-library/music` ein.
4. **AzuraCast Pi (via Tailscale)** bindet sich per Tailnet-IP `100.x.x.x` das NFS-Laufwerk als `/var/azuracast/stations/frawo_funk/media/network` ein.
5. Die teure "Rsync-Kopie" entfällt. Wenn ein neues Lied hochgeladen wird, haben BEIDE Seiten es in derselben Sekunde abspielbereit im Index.

---

## Checkliste für Codex (Abendschicht)

Codex sollte heute Abend folgende Schritte nahtlos abarbeiten:

- [ ] **1. Data Node Provisionierung:**
  Erstellen eines neuen Ansible-Playbooks (`deploy_data_node.yml`), welches einen neuen Debian LXC Container `CT 110` (Name: `storage`) hochzieht.
- [ ] **2. NFS-Server Konfiguration:**
  Den LXC als NFSv4 Server einrichten (`apt install nfs-kernel-server`) und `/etc/exports` definieren (Absicherung via IP-Subnet `192.168.2.0/24` und Tailscale-Subnet).
- [ ] **3. Paperless Migration:**
  Das aktuelle Archiv temporär sichern, `/media/archive` auf den NFS-Mount umbiegen und Dateien rüberschieben.
- [ ] **4. Nextcloud `fstab`:**
  Das NFS-Share in der Nextcloud-VM mounten und den External Storage in der Nextcloud config via OCC-Command registrieren.
- [ ] **5. Any-Sync Node (Anytype):**
  Zusätzlich das Anytype Backbone als Docker Container (any-sync) in `CT 100 toolbox` oder `VM 200` vorbereiten, um P2P Offline-Sync zu garantieren.

---
*Dieser Blueprint orientiert sich strikt an Proxmox Separation of Concerns (SoC) und vermeidet Host-OS Pollution.*
