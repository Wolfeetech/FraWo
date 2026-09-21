# Adressplan Rothkreuz — die verbindliche Quelle

> **Diese Datei gilt.** Widerspricht ihr ein anderes Dokument, hat dieses hier recht.
> Wer eine Adresse ändert, ändert sie **zuerst hier** und arbeitet dann die Spalte
> „Wer verlässt sich darauf" ab.
>
> Stand 21.09.2026 · Grundlage: Messung am Gateway, an allen drei Knoten und von außen.
> Aufgabe M1 aus Vorhaben „Netz professionell betreibbar machen".

## Warum es diese Datei gibt

Am 21.09.2026 hat **ein einziger unbemerkter Netzwechsel vier Systeme gleichzeitig
stillgelegt**: die WireGuard-Regeln nach Stockenweiler, die Odoo- und Home-Assistant-
Anbindungen, sechs öffentliche Web-Adressen und die Firewall-Trennung zwischen IoT
und den Servern.

Keines dieser Systeme hat sich beschwert. Sie zeigten einfach weiter auf Adressen,
die es nicht mehr gab. **Es gab keine Liste, wer sich worauf verlässt.** Das ist diese Liste.

---

## Die Bereichsregel

Innerhalb jedes Netzes gilt dieselbe Aufteilung. Wolfs Vorgabe: **Basis 1–10 für die
Infrastruktur.**

| Bereich | Zweck |
|---|---|
| `.1 – .10` | Netzinfrastruktur: Gateway, Switches, Access Points |
| `.11 – .49` | Physische Rechner: die drei Proxmox-Knoten, StudioPC |
| `.50 – .99` | Kerndienste, fest vergeben |
| `.100 – .199` | Weitere Gäste, fest vergeben |
| `.200 – .254` | Adressvergabe für Geräte, die kommen und gehen |

**Harte Regel: Der DHCP-Bereich und feste Vergaben überschneiden sich nie.**
Heute tun sie das — der Bereich läuft von `.10` bis `.254` und deckt damit alles ab.
Das gehört auf `.200 – .254` eingekürzt.

---

## Die Netze

| VLAN | Netz | Zweck | Zustand |
|---|---|---|---|
| — (ungetaggt) | `192.168.1.0/24` | Werksnetz „Default" | ungenutzt, **darf nichts tragen** |
| **100** | `10.0.0.0/24` | Anker-LAN — Arbeitsplätze | in Betrieb |
| **101** | `10.1.0.0/24` | Anker-Server — **Zielnetz aller Dienste** | derzeit fast leer |
| 102 | `10.2.0.0/24` | DMZ | leer |
| 103 | `10.3.0.0/24` | DMZ Radio | leer |
| **104** | `10.4.0.0/24` | IoT | 14 Geräte, in Betrieb |
| 105 | `10.5.0.0/24` | Gäste | leer |
| 110 / 111 | `10.10./10.11.0.0/24` | Stockenweiler | leer |

> ⚠️ **`Anker-Lan` ist VLAN 100 und damit getaggt.** Ungetaggt läuft am Gateway das
> Werksnetz. Damit die Geräte ihr Netz ungetaggt bekommen, muss an **jedem** LAN-Port
> eine Sonderregel stehen (`native_networkconf_id` = Anker-Lan, `forward` = `all`).
> Fällt sie weg, ist das ganze Haus tot, während jeder Server weiterläuft.

---

## Anschlussbelegung am Gateway

| Port | Was hängt dran | Geschwindigkeit |
|---|---|---|
| 1 | StudioPC | 100 Mbit — gedrosselt |
| 2 | ProDesk 600 G3 + dessen Gäste | 1000 |
| 3 | OptiPlex 7050 | 1000 |
| 4 | Anker (ThinkCentre M720q) + dessen Gäste | 1000 |
| 5 | **WAN** — EasyBox | 1000 |

---

## Die Geräte

**Soll** ist der Zielzustand nach M1. **Ist** ist der Stand vom 21.09.2026 abends.

### Infrastruktur · `.1 – .10`

| Gerät | Soll | Ist | Hardware-Adresse |
|---|---|---|---|
| UCG Gateway (VLAN 100) | `10.0.0.1` | `10.0.0.1` | `1e:6a:1b:38:af:00` |
| UCG Gateway (VLAN 101) | `10.1.0.1` | `10.1.0.1` | dieselbe |
| Access Point „AC Mesh" | `10.1.0.143` | `10.1.0.143` | `74:ac:b9:6c:79:5a` |

> 🔴 **Die Gateway-Adresse `10.0.0.1` darf niemals von einem Gast getragen werden.**
> Am 21.09. hatte der WireGuard-Tunnel `wg0` sie fest eingetragen und dem Gateway
> weggenommen — das ganze Haus war tot. `wg0` ist seitdem abgeschaltet
> (`/etc/wireguard/wg0.conf.aus`) und **bleibt es**.

### Physische Rechner · `.11 – .49`

| Gerät | Soll (VLAN 101) | Arbeitsplatz-Netz | Ist | Hardware-Adresse |
|---|---|---|---|---|
| Anker `proxmox-anker` | `10.1.0.92` | `10.0.0.99` | beide | `f8:75:a4:06:40:8a` |
| ProDesk `pve` | `10.1.0.128` | `10.0.0.191` | beide | `10:62:e5:14:97:ed` |
| OptiPlex `Optiplex` | `10.1.0.227` | `10.0.0.227` | beide | `14:b3:1f:2c:1c:2c` |
| StudioPC | — | `10.0.0.156` | ja | `34:5a:60:44:22:f4` |

> Die `10.1.0.x`-Adressen der Knoten sind **Pflicht**: corosync sucht sie dort.
> Fehlen sie, findet der Verbund sich nicht, `/etc/pve` wird schreibgeschützt und
> **kein Gast startet mehr**. Seit 21.09. fest in `/etc/network/interfaces` eingetragen.
> Beim ProDesk zusätzlich nötig, weil dessen Brücke VLAN-filternd ist:
> `bridge vlan add vid 101 dev eno1` und `… dev vmbr0 self`.

### Kerndienste · `.50 – .99`

| Gast | Dienst | Soll (VLAN 101) | Ist (VLAN 100) | Wirt |
|---|---|---|---|---|
| CT140 | Odoo + Website + Cloudflare-Tunnel | `10.1.0.112` | `10.0.0.55` | Anker |
| CT108 | Vaultwarden | `10.1.0.95` | `10.0.0.64` | Anker |
| CT155 | Monitoring (Prometheus, Grafana) | `10.1.0.35` | `10.0.0.100` | Anker |
| CT101 | AdGuard (Replica) | `10.1.0.27` | `10.0.0.97` | Anker |
| CT103 | AdGuard (Master) | `10.1.0.52` | `10.0.0.10` | ProDesk |
| CT120 | Fileserver + beets | `10.1.0.94` | `10.0.0.157` | ProDesk |

### Weitere Gäste · `.100 – .199`

| Gast | Dienst | Soll (VLAN 101) | Ist (VLAN 100) | Wirt |
|---|---|---|---|---|
| CT110 | n8n + Paperless | `10.1.0.100` | `10.0.0.106` | Anker |
| CT130 | Radio-Backend | `10.1.0.200` | `10.0.0.233` | Anker |
| CT150 | OpenClaw (Jarvis) | `10.1.0.31` | `10.0.0.31` | Anker |
| CT106 | WireGuard nach Stockenweiler | `10.1.0.239` | `10.0.0.152` | Anker |
| VM210 | Home Assistant Rothkreuz | `10.1.0.40` | `10.0.0.183` | Anker |
| VM300 | Nextcloud | `10.1.0.21` | `10.0.0.204` | Anker |
| VM220 | AzuraCast (Radio) | `10.1.0.38` | `10.0.0.186` | ProDesk |
| VM360 | Home Assistant Eltern | `10.1.0.248` | `10.0.0.215` | ProDesk |
| VM240 | PBS (Sicherungsserver) | `10.1.0.7` | — | Anker, **defekt** |
| VM102 | AdGuard OptiPlex | — | läuft | OptiPlex |

### IoT · VLAN 104, `10.4.0.x`

14 Geräte, Adressen stabil, **nicht betroffen**. Enthält unter anderem:

| Gerät | Adresse | Anmerkung |
|---|---|---|
| Surface-Touchboard | `10.4.0.38` | 🔴 braucht Odoo — hat eine eigene Firewall-Ausnahme |
| Shelly Outdoor Plug S Gen3 | `10.4.0.11` | 🔴 **IT-Strom — niemals aus der Ferne schalten** |
| Shelly BLU Gateway G3 | `10.4.0.12` | |
| Shelly 4-fach (GrowBox) | `10.4.0.13` | |

---

## Wer verlässt sich auf welche Adresse

**Die wichtigste Tabelle dieses Dokuments.** Wer eine Adresse ändert, arbeitet diese
Liste ab — sonst passiert wieder, was am 21.09. passiert ist.

| Abnehmer | Wo | Verweist auf |
|---|---|---|
| **Cloudflare-Tunnel** | Zero-Trust-Weboberfläche (nicht im Repo!) | `home.` `vault.` `cloud.` `paperless.` `funk.frawo.tech` |
| **WireGuard Stockenweiler** | `/etc/wireguard/wg1.conf` in CT106 | Ziel-Adressen in den `PostUp`-Regeln |
| **Gegenstelle Stockenweiler** | FritzBox der Eltern, nicht von hier änderbar | akzeptiert **nur Absender aus `10.1.0.0/24`** |
| **corosync** | `/etc/pve/corosync.conf` | `ring0_addr` der drei Knoten |
| **Claude-Anbindungen** | `~/.claude.json` auf dem StudioPC | Odoo, beide Home Assistant |
| **Prometheus** | `/etc/prometheus/prometheus.yml` in CT155 | alle Messziele |
| **Firewall am Gateway** | UCG, `rest/firewallrule` | Trennung IoT ↔ Server |
| **Feste Zuteilungen** | UCG, `rest/user` | jede Adresse, plus `network_id` |
| **Namensauflösung** | `/etc/resolv.conf` der Knoten | Gateway-Adresse |

> ⚠️ **Der Cloudflare-Tunnel ist der gefährlichste Abnehmer**, weil seine Konfiguration
> **nicht im Repo liegt**, sondern nur in der Cloudflare-Weboberfläche. Eine
> Adressänderung dort zu vergessen fällt erst auf, wenn ein Kunde anruft.

---

## Fertig, wenn

- [ ] Jede Adresse liegt im vorgesehenen Bereich
- [ ] Der DHCP-Bereich ist auf `.200 – .254` eingekürzt und überschneidet sich mit keiner festen Vergabe
- [ ] Alle Dienste sind wieder in VLAN 101 und unter ihrer Soll-Adresse erreichbar
- [ ] Die festen Zuteilungen am Gateway nennen Adresse **und** das richtige Netz
- [ ] `funk.` `vault.` `cloud.` `paperless.` `home.frawo.tech` antworten wieder
- [ ] Der Tunnel nach Stockenweiler trägt echten Verkehr, nicht nur Handschläge
- [ ] Ein Neustart aller drei Knoten ändert nichts an dieser Tabelle
