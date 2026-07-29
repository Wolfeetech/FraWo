# Mobile Geräte — Vorbereitung

Stand 29.07.2026. Alles, was mitgeht: Raspberry Pi im VT-Koffer, Surface Go,
Reservegeräte.

Ziel dieser Vorbereitung: **Am Einsatztag soll nichts mehr entschieden werden
müssen.** Karte flashen, Skript starten, fertig.

---

## Wofür die Geräte da sind

| Rolle | Gerät | Zweck | Odoo |
|---|---|---|---|
| `relais` | Raspberry Pi 3 | Icecast-Relais bei Veranstaltungen: holt **einen** Stream aus dem Netz und bedient davon beliebig viele Zuhörer vor Ort | #243 |
| `kiosk` | Raspberry Pi 3 oder Surface Go | Bedienterminal — Odoo Werkstatt, Anker-Tracker, Radio-Kuration | #454, #864 |
| `messplatz` | Surface Go | REW-Einmessung, Musik-Kuration | #452 |
| `reserve` | Raspberry Pi 3 | vorbereitet im Schrank, für den Fall der Fälle | — |

### Warum das Relais nicht so gebaut ist, wie in #243 beschrieben

Die alte Beschreibung sah vor, das Signal über Tailscale von CT130 zu holen.
Dagegen sprechen zwei Dinge:

1. AzuraCast läuft auf VM210 (`10.1.0.38`) und ist **gar nicht in Tailscale**.
   Der Weg über CT130 wäre ein Umweg über einen Rechner, der mit dem Sender
   nichts zu tun hat.
2. Beim Event hängt der Pi am Handy-Hotspot. Tailscale würde dann erst eine
   Verbindung nach Hause aufbauen, um Ton zu holen, den es ohnehin öffentlich
   gibt. Mehr Teile, die kaputtgehen können — bei genau der Verbindung, die
   ohnehin am wackeligsten ist.

**Stattdessen:** Der Pi holt einen Stream direkt von `funk.frawo.tech`.
Tailscale ist trotzdem drauf, aber nur für Fernwartung und Überwachung —
fällt es aus, läuft der Ton weiter.

---

## Was schon vorbereitet ist

- ✅ **Überwachung nimmt neue Geräte von selbst auf.** Ein Gerät wird durch
  Ablegen einer Datei in `/etc/prometheus/ziele/mobil/` in CT150 aufgenommen.
  Prometheus liest das Verzeichnis alle 30 Sekunden neu — kein Neustart, kein
  Eingriff in die Konfiguration. Das Bereitstellungs-Skript gibt den fertigen
  Befehl aus.
- ✅ **Eigene Alarme für mobile Geräte** (`frawo_mobil.yml`). Ein Gerät im
  Schrank löst **keinen** Alarm aus — das ist der Normalfall. Alarm gibt es,
  wenn ein Gerät **mitten im Betrieb** wegbricht, wenn die Speicherkarte
  volläuft oder wenn der Pi zu heiss wird.
- ✅ **Bereitstellungs-Skript** `raspberry/bereitstellung.sh` — macht aus einer
  frisch geflashten Karte ein fertiges Gerät. Mehrfach ausführbar.
- ✅ **Tailscale-Schlüssel** liegt auf dem ProDesk unter
  `/root/.tailscale-mobil-key` (nur root lesbar). Damit meldet sich ein Gerät
  ohne Browser-Anmeldung im Tailnet an.

## Was Wolf noch braucht

- [ ] Wie viele Pi-3-Boards gibt es, und welches soll welche Rolle bekommen?
- [ ] Speicherkarten: siehe Hinweis unten — die Kartenwahl entscheidet mehr
      über die Zuverlässigkeit als das Board.
- [ ] Netzteile prüfen (siehe unten, häufigste Fehlerquelle überhaupt)

---

## Vor dem Flashen: drei Dinge, an denen Pi-Aufbauten scheitern

**1. Das Netzteil.** Der mit Abstand häufigste Grund für einen Pi, der sich
zufällig aufhängt oder neu startet. Ein Pi 3B+ braucht **5 V / 2,5 A**. Ein
Handy-Ladegerät mit 1 A funktioniert scheinbar — bis Last dazukommt. Wenn ein
Pi sich später merkwürdig verhält, ist das die erste Verdächtige, nicht die
Software. Erkennbar an einem Blitz-Symbol auf dem Bildschirm oder per
`vcgencmd get_throttled` (alles ausser `0x0` heisst Ärger).

**2. Die Speicherkarte.** Sie stirbt an Schreibvorgängen, und billige Karten
sterben schnell. Empfehlung: Markenkarte mit **A1 oder A2**, gern
"High Endurance". Das Skript schont die Karte zusätzlich, indem es Protokolle
in den Arbeitsspeicher legt und die Auslagerungsdatei abschaltet.

**3. WLAN beim Pi 3B.** Das **3B kann nur 2,4 GHz**, erst das **3B+ kann auch
5 GHz**. Wer am Einsatzort ein reines 5-GHz-Netz aufspannt, wundert sich sonst
lange. Steht auf der Platine: `Raspberry Pi 3 Model B` gegen
`Raspberry Pi 3 Model B Plus`.

---

## Karte flashen — die Einstellungen im Raspberry Pi Imager

Diese Einstellungen ersparen später das Anschliessen von Bildschirm und
Tastatur. Im Imager auf das Zahnrad klicken:

| Feld | Wert |
|---|---|
| Betriebssystem | **Raspberry Pi OS Lite (64-bit)** — kein Desktop nötig |
| Hostname | der geplante Name, z.B. `funk-relais-1` |
| Benutzer | `frawo` + ein Passwort (kommt später nach Vaultwarden) |
| SSH aktivieren | **ja**, und dort den öffentlichen Schlüssel des StudioPC einfügen |
| WLAN | Netz und Passwort des Anker-WLAN, Land: **DE** |
| Zeitzone | Europe/Berlin, Tastatur `de` |

> ⚠️ **Wichtig:** Der alte Trick, eine Datei `wpa_supplicant.conf` auf die
> Karte zu legen, **funktioniert seit Raspberry Pi OS „Bookworm" nicht mehr** —
> das WLAN wird jetzt vom NetworkManager verwaltet. Wer danach googelt,
> findet massenhaft veraltete Anleitungen. Die Einstellungen im Imager sind
> der richtige Weg.

> 💡 Zur Wahl 64-bit gegen 32-bit: Beide Pi-3-Modelle können 64-bit. Bei nur
> 1 GB Arbeitsspeicher braucht 64-bit etwas mehr davon. Für ein Relais, das im
> Wesentlichen Daten weiterreicht, spielt das keine Rolle — und 64-bit ist das,
> was langfristig gepflegt wird.

---

## Am Einsatztag: die Schritte

```bash
# 1. Anmelden (Name aus dem Imager, Schlüssel liegt schon drauf)
ssh frawo@funk-relais-1.local

# 2. Skript holen und starten
curl -fsSLO https://raw.githubusercontent.com/Wolfeetech/FraWo/main/deployments/mobil/raspberry/bereitstellung.sh
chmod +x bereitstellung.sh
sudo ./bereitstellung.sh relais funk-relais-1

# 3. Tailscale anmelden — den Schlüssel vorher vom ProDesk holen:
#    ssh stock-pve "cat /root/.tailscale-mobil-key"
sudo tailscale up --authkey=<SCHLUESSEL> --hostname=funk-relais-1

# 4. Skript nochmal starten. Es kennt jetzt die Tailscale-Adresse und
#    gibt den fertigen Befehl für die Überwachung aus.
sudo ./bereitstellung.sh relais funk-relais-1
```

Danach den ausgegebenen `pct push`-Befehl **auf dem ProDesk** ausführen —
fertig, das Gerät ist in Grafana sichtbar.

### Prüfen, ob das Relais wirklich Ton liefert

Nicht darauf verlassen, dass der Dienst läuft — das sagt nichts über den Ton
aus. Das ist dieselbe Lehre wie beim Sender selbst:

```bash
curl -r 0-100000 -o /dev/null -w '%{http_code} %{size_download} %{content_type}\n' \
     http://funk-relais-1.local:8000/frawo.mp3
```

Erwartet: `200` oder `206`, rund 100000 Bytes, und `audio/mpeg`.
Kommt `text/html` zurück, läuft zwar Icecast, aber es kommt kein Ton an.

---

## Surface Go

Das Surface Go ist bereits als Kiosk-Terminal eingerichtet gewesen
(Odoo #826, #452 — beide erledigt), war aber zuletzt **26 Tage offline**
(Tailscale-Name `surface-go-frontend`).

Vor dem nächsten Einsatz:

- [ ] Einschalten, Windows-Updates durchlaufen lassen (nach so langer Pause
      dauert das eine Weile — nicht am Einsatztag machen)
- [ ] Tailscale-Anmeldung prüfen: Das Gerät war so lange weg, dass der
      Schlüssel abgelaufen sein kann
- [ ] Verknüpfungen aus `deployments/franz_surface/Surface Shortcuts/`
      gegenprüfen — sie zeigen teils auf Adressen aus der Zeit vor der
      Netz-Umnummerierung
- [ ] In die Überwachung aufnehmen (dieselbe Datei-Ablage wie beim Pi,
      Windows braucht dafür den `windows_exporter` wie auf dem StudioPC)

---

## Namen und Adressen

Feste Adressen werden **nicht** vergeben. Mobile Geräte hängen mal am
Anker-WLAN, mal am Handy-Hotspot — eine feste LAN-Adresse wäre am Einsatzort
wertlos. Stattdessen gilt überall die **Tailscale-Adresse**; die bleibt gleich,
egal wo das Gerät steht.

| Name | Rolle | Tailscale | Status |
|---|---|---|---|
| `funk-relais-1` | relais | wird bei Anmeldung vergeben | geplant |
| `surface-go-frontend` | messplatz / kiosk | `100.106.67.127` | vorhanden, seit 26 Tagen offline |

Weitere Boards hier eintragen, sobald die Rollen feststehen.
