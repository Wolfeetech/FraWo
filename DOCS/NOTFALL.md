# Notfall — die drei wahrscheinlichsten Störfälle

> Für den Moment, in dem etwas nicht geht und die Zeit drängt.
> Jeder Abschnitt: **woran du es erkennst**, **was du tippst**, **woran du siehst, dass es geklappt hat**.
>
> Entstanden am 21.09.2026 nach einem Ausfall, der fünf Stunden gekostet hat, weil es
> diese Seite noch nicht gab. Aufgabe M3 aus Vorhaben „Netz professionell betreibbar machen".

## Drei Regeln, die überall gelten

1. **Ping lügt.** Windows zählt „Zielhost nicht erreichbar" als Antwort, der Rückgabewert ist
   dann trotzdem 0. Miss mit einer echten Verbindung:
   `timeout 5 bash -c "echo > /dev/tcp/1.1.1.1/443" && echo geht || echo tot`
2. **Ein gefundener Fehler ist nicht *der* Fehler.** Am 21.09. lagen drei unabhängige
   Störungen übereinander, jede mit demselben Symptom. Nach jeder Reparatur **neu messen**.
3. **Auf Windows heißt es `curl.exe`,** nicht `curl` — sonst geht die Anfrage nie raus.

---

# 1 · Kein Internet im Haus

## Die eine Frage, die alles halbiert

> **Hat `frawodirekt` auch kein Internet?**

`frawodirekt` kommt **direkt aus der EasyBox** und liegt damit *vor* dem eigenen Gateway.
Nur `central` und `iot` kommen vom UCG-Access-Point.

| frawodirekt | central / iot | Die Störung liegt |
|---|---|---|
| tot | tot | **bei EasyBox oder Vodafone** — alles Eigene ist unschuldig |
| läuft | tot | **im eigenen Netz** — weiter bei Schritt 2 |

## Schritt 1 — die Lampen an der EasyBox

Die **Telefonlampe** ist aussagekräftiger als die Internetlampe. Das Telefon meldet sich
über dieselbe Vodafone-Leitung an.

- **Telefon rot** → keine Verbindung zu Vodafone. Die Internetlampe kann trotzdem grün sein,
  die zeigt nur, dass das Kabel Signal hat. → EasyBox **zwei Minuten stromlos**.
  Hilft das nicht: bei Vodafone melden, Stichwort *„Telefon meldet sich nicht an"*.
- **Alle grün, trotzdem nichts** → weiter bei Schritt 2.

> ⚠️ Am 21.09. war die Ursache ein **umgepatchter DSL-Anschluss**. Wenn kurz vorher
> jemand an der Verkabelung war: zuerst dort nachsehen.

## Schritt 2 — was sagt das Gateway?

```bash
ssh root@10.0.0.227
curl -s -k -H 'X-API-KEY: <Schlüssel aus Vaultwarden>' \
  'https://10.1.0.1/proxy/network/api/s/default/stat/health' | python3 -m json.tool | head -40
```

Achte auf den Abschnitt `wan`:
- `wan_ip` leer → die EasyBox gibt keine Adresse heraus
- `wan_ip` da, aber `gateways` leer → Adresse ohne Weg nach draußen
- `tx_bytes-r` hoch, `rx_bytes-r` fast null → **wir senden, es kommt nichts zurück**

## Schritt 3 — wie weit kommen die Pakete?

```bash
ssh root@10.0.0.227 'traceroute -n -w 2 -q 1 -m 8 1.1.1.1'
```

- Stoppt nach **Sprung 1** (`10.0.0.1`) → hinter dem Gateway ist Schluss
- Kommt bis zur EasyBox und dann nichts → die Leitung nach draußen

## Geschafft, wenn

```bash
ssh root@10.0.0.227 '
  timeout 6 bash -c "echo > /dev/tcp/1.1.1.1/443" && echo "TCP: ok"
  getent hosts heise.de >/dev/null && echo "Namen: ok"
  curl -s -o /dev/null -m 10 -w "Web: HTTP %{http_code}\n" http://heise.de'
```

Alle drei müssen antworten. **Nur Ping reicht als Beweis nicht.**

---

# 2 · Ein Knoten kommt falsch hoch

## Woran du es erkennst

- Nach einem Neustart startet **kein einziger Gast**, obwohl Autostart an ist
- `pvecm status` sagt `Quorate: No`
- Dienste sind weg, obwohl die Rechner laufen

**Die Ursache ist fast immer dieselbe:** Der Knoten hat seine Server-Adresse verloren.
Dann findet corosync die anderen nicht, ohne Quorum wird `/etc/pve` schreibgeschützt,
und ohne Schreibrecht startet Proxmox keinen Gast.

## Prüfen

```bash
ssh root@<knoten> '
  ip -4 -br addr | grep -v "^lo"
  echo "--- corosync erwartet ---"
  grep -E "name:|ring0_addr" /etc/pve/corosync.conf
  echo "--- Konfiguration schreibbar? ---"
  touch /etc/pve/.probe 2>/dev/null && { echo JA; rm -f /etc/pve/.probe; } || echo "SCHREIBGESCHUETZT"'
```

Fehlt die Adresse, die corosync unter `ring0_addr` erwartet, ist das der Fehler.

| Knoten | Erwartete Server-Adresse | Zugang über Tailscale |
|---|---|---|
| Anker (`proxmox-anker`) | `10.1.0.92` | `100.69.179.87` |
| ProDesk (`pve`) | `10.1.0.128` | `100.91.20.116` |
| OptiPlex (`Optiplex`) | `10.1.0.227` | — |

> Der Tailscale-Name **`stockenweiler-pve` ist der ProDesk** und steht in Rothkreuz.
> Ein alter Name, der nichts über den Standort sagt.

## Reparieren — erst laufend, nicht fest

So bleibt ein Neustart als Rückweg:

```bash
ssh root@<knoten> '
  modprobe 8021q
  ip link show vmbr0.101 >/dev/null 2>&1 || ip link add link vmbr0 name vmbr0.101 type vlan id 101
  ip addr add <ADRESSE>/24 dev vmbr0.101
  ip link set vmbr0.101 up'
```

**Wichtig beim ProDesk:** Dessen Brücke filtert VLANs (`bridge-vlan-aware yes`).
Dort muss VLAN 101 zusätzlich freigegeben werden, sonst kommen die Pakete zwar an der
Netzwerkkarte an, aber nie bei der Schnittstelle:

```bash
bridge vlan add vid 101 dev eno1
bridge vlan add vid 101 dev vmbr0 self
```

Danach:

```bash
systemctl restart corosync
sleep 14
pvecm status | grep -E "Nodes:|Quorate"
```

## Geschafft, wenn

`Quorate: Yes` und die Knotenzahl stimmt. Dann starten die Gäste wieder — notfalls
von Hand mit `pct start <id>` bzw. `qm start <id>`.

## Damit es nicht wiederkommt

Die Adresse gehört **fest** in `/etc/network/interfaces` (Sicherung vorher anlegen!).
Beide Knoten haben diesen Eintrag seit 21.09.2026 — wenn er fehlt, wurde die Datei ersetzt.

---

# 3 · Sicherung ausgefallen

> Der gefährlichste Fall, weil er **nicht weh tut**, bis man die Sicherung braucht.

## Schritt 1 — lebt der Datenträger?

```bash
ssh root@100.69.179.87 'zpool status anker-backup'
```

- `state: ONLINE` → gut
- `state: DEGRADED` → **eine Platte fehlt oder macht Fehler.** Häufigste Ursache:
  Die USB-Platten fallen ohne aktiven Hub nach einigen Stunden ab.
- Spalte `CKSUM` über 0 → die Platte macht bereits Lesefehler

## Schritt 2 — liegt wirklich etwas da?

**Nicht dem Aufgabenprotokoll glauben — am Ziel nachsehen.** Bei dieser Anlage haben
Sicherungen mehrfach „OK" gemeldet und nichts geschrieben.

```bash
ssh root@100.69.179.87 '
for id in 101 106 108 110 130 140 150 155 210 300; do
  f=$(ls -1t /mnt/google-drive/dump/vzdump-*-${id}-*.zst 2>/dev/null | head -1)
  if [ -n "$f" ]; then
    printf "%-5s %6s MB  %s\n" "$id" "$(( $(stat -c %s "$f") / 1048576 ))" "$(basename "$f" | cut -c1-44)"
  else
    printf "%-5s  KEINE SICHERUNG\n" "$id"
  fi
done'
```

Jeder der zehn Gäste muss eine Datei haben, und das Datum darin muss frisch sein.

## Schritt 3 — von Hand nachholen

Geht der Weg in die Cloud wieder, erst die Schreibprobe:

```bash
ssh root@100.69.179.87 '
  mkdir -p /mnt/google-drive/dump && \
  echo test > /mnt/google-drive/dump/.probe && \
  cat /mnt/google-drive/dump/.probe && rm -f /mnt/google-drive/dump/.probe'
```

Klappt das, die Sicherung anstoßen — **erst das Geschäftskritische**:

```bash
ssh root@100.69.179.87 '
  vzdump 140 108 110 155 --storage google-drive --mode snapshot \
    --compress zstd --prune-backups keep-last=3'
```

`140` = Odoo + Website · `108` = Vaultwarden · `110` = n8n + Paperless · `155` = Monitoring

Danach der Rest: `vzdump 101 106 130 150 210 300 <gleiche Optionen>`

Das fertige Skript dafür liegt auf dem Anker unter
`/usr/local/bin/frawo-notsicherung.sh`.

## Geschafft, wenn

Schritt 2 für alle zehn Gäste eine frische Datei zeigt — **nicht**, wenn der Befehl
ohne Fehler durchgelaufen ist.

---

## Wenn gar nichts mehr geht

Der Weg hinein, der am 21.09. als einziger gehalten hat, war **Tailscale**. Er läuft
unabhängig vom Hausnetz, solange die Rechner Strom und irgendeine Internetverbindung haben:

```bash
ssh root@100.69.179.87    # Anker
ssh root@100.91.20.116    # ProDesk
tailscale status          # zeigt, wer noch lebt
```

Ist auch das tot, hilft nur der Weg vor Ort. Dann in dieser Reihenfolge:
**EasyBox → Gateway → Knoten.** Immer von außen nach innen.
