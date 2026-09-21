# Geplant: Netzwerk neu ordnen — Adressen, Bereiche, VLANs

> **Status:** Noch nicht in Odoo angelegt — das Netz war beim Erfassen ausgefallen.
> Beim nächsten Zugriff als Vorhaben in Projekt 105 eintragen.
> Aufgenommen am 21.09.2026 auf Wolfs Anweisung.

## Warum das jetzt ansteht

Am 20./21.09.2026 hat **ein einziger IP-Konflikt das gesamte Netz lahmgelegt**: Der
WireGuard-Container (CT106, `10.1.0.239`) hatte sich zusätzlich die Gateway-Adresse
`10.0.0.1` genommen. Nachweis aus der Adresstabelle:

```
10.0.0.1     ->  bc:24:11:ef:ff:1a
10.1.0.239   ->  bc:24:11:ef:ff:1a    dieselbe Hardware-Adresse
```

Folgen: kein Internet im ganzen Haus, alle Server unerreichbar, Cloudflare meldete
530, sämtliche Tailscale-Knoten offline. Die Server liefen die ganze Zeit weiter —
niemand kam nur noch an sie heran.

**Das war kein Zufall, sondern eine Frage der Zeit.** Die Adressvergabe ist
historisch gewachsen: feste Adressen quer über den ganzen Bereich verstreut,
DHCP-Bereiche, die sich mit fest vergebenen Adressen überlappen, keine Regel,
welcher Bereich wofür gedacht ist.

## Was erreicht werden soll

Eine Infrastruktur, die professionellem Standard entspricht — mit einer
nachvollziehbaren Ordnung statt gewachsenem Bestand.

### 1. Adressbereiche nach Zweck aufteilen

Wolfs Vorgabe: **Basis 1–10 für die Infrastruktur.** Vorschlag zur Abstimmung:

| Bereich | Zweck | Beispiel |
|---|---|---|
| `.1 – .10` | Netzinfrastruktur | Gateway, Switches, Zugangspunkte |
| `.11 – .49` | Physische Server | die drei Proxmox-Knoten, StudioPC |
| `.50 – .99` | Kerndienste, fest vergeben | Odoo, Vaultwarden, Monitoring, DNS |
| `.100 – .199` | Weitere Gäste, fest vergeben | Radio, n8n, Nextcloud, Paperless |
| `.200 – .254` | DHCP für Geräte, die kommen und gehen | Notebooks, Handys, Gäste |

Entscheidend ist nicht die genaue Grenze, sondern: **Jede Adresse hat einen
erkennbaren Platz, und DHCP-Bereich und feste Vergabe überschneiden sich nie.**

### 2. VLANs sauber zuordnen und markieren

Die VLAN-Struktur existiert bereits und ist gut gedacht:

| VLAN | Netz | Zweck |
|---|---|---|
| 100 | `10.0.0.0/24` | Anker-LAN (Arbeitsplätze) |
| 101 | `10.1.0.0/24` | Anker-Server |
| 102 | `10.2.0.0/24` | DMZ |
| 103 | `10.3.0.0/24` | DMZ Radio |
| 104 | `10.4.0.0/24` | IoT |
| 105 | `10.5.0.0/24` | Gäste |
| 110 / 111 | `10.10/10.11.0.0/24` | Stockenweiler |

**Was fehlt, ist die Umsetzung auf der Port-Ebene:** Welcher Anschluss führt welches
Netz, wo ist markiert und wo nicht. Heute hat sich gezeigt, dass ein Gerät beim
Umstecken von einem Anschluss auf den anderen sein Netz wechselt, ohne dass das
irgendwo ersichtlich wäre.

### 3. Doppelvergaben unmöglich machen

- Feste Zuteilungen am Gateway statt fest im Gerät konfigurierter Adressen, wo
  immer möglich — dann weiß das Gateway von jeder Adresse
- Überwachung, die eine doppelt vergebene Adresse **meldet, bevor** sie Schaden
  anrichtet (genau das fehlte heute)
- Die Gateway-Adresse jedes Netzes gegen Übernahme schützen

### 4. Eine belastbare Übersicht am Ende

Eine gepflegte Liste aller vergebenen Adressen mit Zweck, Gerät, VLAN und
Anschluss — im Repo versioniert, nicht in jemandes Kopf. Dazu eine Zeichnung,
die zeigt, was wo hängt.

## Fertig, wenn

- Jede vergebene Adresse liegt in ihrem vorgesehenen Bereich
- Kein DHCP-Bereich überschneidet sich mit fest vergebenen Adressen
- Jeder Anschluss am Gateway ist beschriftet und seinem Netz zugeordnet
- Eine doppelte Adressvergabe löst einen Alarm aus
- Die Übersicht liegt im Repo und stimmt mit der Wirklichkeit überein

## Wichtig bei der Umsetzung

**Das ist ein Umbau am offenen Herzen.** Eine falsch gesetzte Adresse trennt den
Zugang zum betroffenen Gerät — heute mehrfach erlebt. Deshalb:

- Schrittweise, ein Netz nach dem anderen
- Vor jeder Änderung den Rückweg klären: Wie komme ich an das Gerät, wenn die
  Änderung es aussperrt?
- Nie am Gateway und an einem Gerät gleichzeitig arbeiten
- Wartungsfenster für alles, was Kerndienste betrifft

## Vorarbeit, die schon vorliegt

- Vollständiges Geräteinventar: `DOCS/baseline/ist-zustand-2026-09-20.txt`
- Netzwerk- und VLAN-Struktur: Memory `reference_frawo_network_vlan`
- Rack-Planung mit Anschlussbelegung: Artefakt „Rothkreuz Rack-Aufriss"
