# CT130 radio-node auf unprivilegiert umstellen — Umsetzungsplan

> **Für ausführende Agenten:** ERFORDERLICHE UNTER-SKILL: `superpowers:executing-plans`, Aufgabe für Aufgabe. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Ziel:** CT130 `radio-node` ist der **einzige privilegierte Container von 13**. In einem privilegierten Container ist `root` innen dasselbe `root` wie auf dem Wirt — ein Ausbruch trifft direkt den Anker. Nach dieser Umstellung ist er das nicht mehr.

**Architektur:** Proxmox kann privilegiert → unprivilegiert **nicht im laufenden Betrieb umschalten**. Der Weg ist: sichern, als **neuer Container** unprivilegiert zurückspielen, dort prüfen, und erst bei Erfolg umschwenken. Der alte Container bleibt bis zum Schluss unangetastet — er ist der Rückweg.

**Technik:** Proxmox VE auf dem Anker · CT130, 4 Kerne, 6 GB RAM, 64 GB Platte (21,3 GB belegt) · Docker mit `overlay2` auf `extfs` · Tailscale-Knoten `radio-node`

---

## Ausgangslage (02.08.2026 gemessen)

```
features: nesting=1,keyctl=1
lxc.cgroup2.devices.allow: c 10:200 rwm          ← /dev/net/tun
lxc.mount.entry: /dev/net dev/net none bind,create=dir
```

| | |
|---|---|
| Warum privilegiert | **`tailscaled` hält `/dev/net/tun`** — kein Altlast, wird aktiv gebraucht |
| Läuft darin (Docker) | `frawo-radio-backend` (9500, 9590), `frawo-radio-db` PostgreSQL (5432), `frawo-radio-redis` (6379), `uptime-kuma` (3001) |
| Docker-Speichertreiber | **`overlay2` auf `extfs`** ← der kritische Punkt |
| Belegt | 21,3 GB von 62,7 GB · davon **4,9 GB Müll** (2,38 GB Abbilder, 2,49 GB Volumes) |

## Globale Randbedingungen

- **Der alte Container wird bis zum Schluss nicht verändert.** Kein `pct set`, kein Löschen. Er ist der Rückweg.
- **Es gibt ein Ausfallfenster.** Radio-Backend und PostgreSQL sind währenddessen weg. Nicht an einem Sendetag mit Veranstaltung legen.
- **Zwei Knackpunkte entscheiden**, beide werden in Aufgabe 3 geprüft, **bevor** irgendetwas umgeschwenkt wird:
  1. Läuft Docker mit `overlay2` in einem unprivilegierten Container?
  2. Bekommt `tailscaled` dort noch `/dev/net/tun`?
- **Bei Fehlschlag an einem der beiden: abbrechen, alten Container weiterlaufen lassen, in Odoo festhalten.** Kein Herumbasteln am offenen Herzen.
- Befehle laufen als `ssh anker-pve "<BEFEHL>"`, sofern nicht anders vermerkt.

---

## Aufgabe 1: Aufräumen und Bestandsaufnahme

**Warum zuerst:** 4,9 GB Müll verkleinern die Sicherung und die Rückspielzeit spürbar. Und wer nicht weiß, wie „läuft" aussieht, kann hinterher nicht prüfen, ob es noch läuft.

- [ ] **Schritt 1: Docker-Müll wegräumen** — im Container

```sh
pct exec 130 -- docker system prune -a --volumes --filter "until=168h"
```
Das `until=168h` schützt alles, was jünger als eine Woche ist. Erwartet: ca. 4–5 GB frei.

- [ ] **Schritt 2: Ist-Zustand schriftlich festhalten**

```sh
pct exec 130 -- docker ps --format '{{.Names}} {{.Status}} {{.Ports}}' > /root/ct130-vorher.txt
pct exec 130 -- tailscale status --self --peers=false >> /root/ct130-vorher.txt
cat /root/ct130-vorher.txt
```
Erwartet: 4 Container (nach dem Abschalten von uptime-kuma laut #888 nur noch 3), Tailscale-Knoten `radio-node` verbunden.

- [ ] **Schritt 3: Datenbank-Sicherung, unabhängig vom Container**

Der Container-Abzug allein reicht nicht — eine laufende PostgreSQL wird nicht sauber eingefroren.
```sh
pct exec 130 -- docker exec frawo-radio-db pg_dumpall -U postgres > /root/ct130-db-20260802.sql
ls -lh /root/ct130-db-20260802.sql
```
Erwartet: Datei **deutlich über 1 MB**. Bei 0 Bytes abbrechen — genau dieser blinde Fleck hat den wochenlangen Sicherungsausfall verursacht.

---

## Aufgabe 2: Sicherung ziehen

- [ ] **Schritt 1: Dienste geordnet anhalten**

```sh
pct exec 130 -- docker stop frawo-radio-backend frawo-radio-db frawo-radio-redis
```
Erst Backend, dann Datenbank — nicht umgekehrt, sonst schreibt das Backend ins Leere.

- [ ] **Schritt 2: Vollsicherung im Stopp-Modus**

```sh
vzdump 130 --mode stop --compress zstd --storage local
```
Erwartet: `INFO: Finished Backup of VM 130`. Pfad merken (`/var/lib/vz/dump/vzdump-lxc-130-*.tar.zst`).

- [ ] **Schritt 3: Sicherung auf Brauchbarkeit prüfen — nicht nur auf Existenz**

```sh
ls -lh /var/lib/vz/dump/vzdump-lxc-130-*.tar.zst
zstd -t /var/lib/vz/dump/vzdump-lxc-130-*.tar.zst && echo "Archiv lesbar"
```
Erwartet: Größe im Bereich mehrerer GB **und** „Archiv lesbar". Ohne beides nicht weitermachen.

- [ ] **Schritt 4: Alten Container wieder starten**

```sh
pct start 130
```
Ab hier läuft der Betrieb normal weiter, während der Testklon gebaut wird.

---

## Aufgabe 3: Testklon bauen und die zwei Knackpunkte prüfen

**Das ist die Weiche des ganzen Plans.** Hier zeigt sich, ob die Umstellung überhaupt tragfähig ist — ohne dass der Betrieb daran hängt.

- [ ] **Schritt 1: Als CT131 unprivilegiert zurückspielen**

```sh
pct restore 131 /var/lib/vz/dump/vzdump-lxc-130-*.tar.zst --unprivileged 1 --hostname radio-node-test --storage local-lvm
```
Der Rückspielvorgang verschiebt die Dateibesitzer automatisch (0 → 100000). Erwartet: fehlerfrei.

- [ ] **Schritt 2: Netzwerk entkoppeln, damit sich nichts in die Quere kommt**

```sh
pct set 131 --net0 name=eth0,bridge=vmbr0,ip=dhcp,type=veth
pct set 131 --onboot 0
```
Neue MAC → neue IP. **Kein Portkonflikt mit dem laufenden CT130.**

- [ ] **Schritt 3: Gerätedurchreichung übernehmen**

```sh
pct set 131 --features nesting=1,keyctl=1
grep -qE 'lxc.cgroup2.devices.allow: c 10:200' /etc/pve/lxc/131.conf || cat >> /etc/pve/lxc/131.conf <<'EOF'
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net dev/net none bind,create=dir
EOF
cat /etc/pve/lxc/131.conf
```

- [ ] **Schritt 4: Starten**

```sh
pct start 131 && sleep 20 && pct status 131
```
Erwartet: `status: running`. Startet er nicht, in `/var/log/pve/tasks/` nachsehen.

- [ ] **Schritt 5: 🔑 KNACKPUNKT 1 — läuft Docker mit overlay2?**

```sh
pct exec 131 -- docker info 2>&1 | grep -iE "Storage Driver|ERROR|Cannot connect"
pct exec 131 -- docker run --rm hello-world
```
Erwartet: `Storage Driver: overlay2` **und** „Hello from Docker!".

**Scheitert das:** `overlay2` funktioniert im unprivilegierten Container nicht. Ausweg wäre `fuse-overlayfs`. Das ist ein eigener Vorgang — **hier abbrechen, in Odoo festhalten, CT130 bleibt wie er ist.**

- [ ] **Schritt 6: 🔑 KNACKPUNKT 2 — bekommt Tailscale sein TUN-Gerät?**

```sh
pct exec 131 -- ls -l /dev/net/tun
pct exec 131 -- systemctl status tailscaled --no-pager 2>&1 | head -5
pct exec 131 -- ip -o link show tailscale0 2>&1
```
Erwartet: Gerät vorhanden, Dienst `active`, Schnittstelle `tailscale0` da.

**Scheitert das:** Rückfallweg wäre Tailscale im Benutzerraum (`--tun=userspace-networking`) — dann kann der Knoten aber nicht mehr routen. **Erst entscheiden lassen, nicht selbst umstellen.**

- [ ] **Schritt 7: Fachliche Prüfung**

```sh
pct exec 131 -- docker start frawo-radio-db && sleep 15
pct exec 131 -- docker exec frawo-radio-db psql -U postgres -c "\l"
```
Erwartet: Datenbankliste — nicht nur „Container läuft", sondern **die Daten sind lesbar**.

---

## Aufgabe 4: Umschwenken

**Erst ausführen, wenn Aufgabe 3 in allen Punkten grün war.** Ab hier gibt es ein Ausfallfenster.

- [ ] **Schritt 1: Fenster ankündigen und alten Container anhalten**

```sh
pct exec 130 -- docker stop frawo-radio-backend frawo-radio-db frawo-radio-redis
pct stop 130
```

- [ ] **Schritt 2: Testklon auf die richtige Adresse setzen**

```sh
pct set 131 --hostname radio-node --onboot 1
pct set 131 --net0 name=eth0,bridge=vmbr0,hwaddr=BC:24:11:54:AC:31,ip=dhcp,type=veth
```
Dieselbe MAC wie vorher → dieselbe DHCP-Adresse **10.1.0.200**. Nur so stimmen alle Verweise weiter.

- [ ] **Schritt 3: Starten und die vier Dienste prüfen**

```sh
pct start 131 && sleep 30
pct exec 131 -- docker ps --format '{{.Names}} {{.Status}}'
pct exec 131 -- ip -4 addr show eth0 | grep inet
```
Erwartet: Adresse **10.1.0.200**, Radio-Backend, Datenbank und Redis laufen.

- [ ] **Schritt 4: Von aussen prüfen, nicht von innen**

```sh
curl -sS -o /dev/null -w '%{http_code}\n' http://10.1.0.200:9500
tailscale status | grep radio-node
```
Und in der Überwachung nachsehen: **Grafana `frawo-ueberblick` muss weiterhin 0/grün zeigen**, Prometheus alle Ziele grün.

- [ ] **Schritt 5: Unprivilegiert bestätigen — der eigentliche Zweck**

```sh
grep unprivileged /etc/pve/lxc/131.conf
```
Erwartet: `unprivileged: 1`. **Ohne diese Zeile war die ganze Übung umsonst.**

---

## Aufgabe 5: Aufräumen — frühestens nach einer Woche

- [ ] **Schritt 1: Eine Woche Ruhe abwarten.** Der alte CT130 bleibt gestoppt liegen. Er kostet nur Plattenplatz und ist der schnellste Rückweg.

- [ ] **Schritt 2: Danach umbenennen, damit CT130 wieder frei wird**

Erst wenn eine Woche störungsfreier Betrieb belegt ist:
```sh
pct destroy 130
```
**Verschieben statt löschen gilt auch hier:** Die vzdump-Sicherung aus Aufgabe 2 bleibt liegen, bis der nächste PBS-Lauf den neuen Container erfasst hat.

- [ ] **Schritt 3: Unterlagen nachziehen**

`NOW.md`: In der Anker-Zeile steht „CT130 `radio-node` — **einziger privilegierter Container von 13**". Nach erfolgreicher Umstellung ersetzen durch: „CT131 `radio-node` (`10.1.0.200`) — unprivilegiert seit 08/2026. **Alle 13 Container unprivilegiert.**" Odoo #887 schliessen.

---

## Rückweg

Zu jedem Zeitpunkt vor Aufgabe 5:
```sh
pct stop 131
pct start 130
```
CT130 ist unverändert. Der Rückweg dauert unter einer Minute.

Geht auch das schief, liegt die Vollsicherung unter `/var/lib/vz/dump/` und der Datenbankabzug unter `/root/ct130-db-20260802.sql`.
