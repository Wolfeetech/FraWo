# Radio Bridge — Fernbedienung fürs Radio-Programm

Bisher **komplett undokumentiert** live auf dem ProDesk gelaufen — beim
Infrastruktur-Audit am 19.08.2026 gefunden (unerklärter offener Port 8888)
und nachträglich ins Repo aufgenommen.

## Wozu

Wolf will von unterwegs (z. B. vom Handy, als DJ auf Tour) neue Titel in
die Radio-Bibliothek hochladen können, ohne selbst am Server zu sitzen.

`frawo_radio_daemon.py` läuft als eigener kleiner Webdienst auf dem
ProDesk (`0.0.0.0:8888`, per `Authorization: Bearer <FRAWO_BRIDGE_TOKEN>`
geschützt) und bietet:

| Endpunkt | Zweck |
|---|---|
| `GET /status` | Zeigt laufende Kuration, Dateien im Eingangsordner, Protokoll |
| `POST /upload` | Datei(en) in den Eingangsordner hochladen |
| `POST /delete` | Datei aus dem Eingangsordner löschen |
| `POST /curate` | Löst `curate_radio.py` im Hintergrund aus |

## Was `curate_radio.py` tut

1. Importiert alles im Eingangsordner (`/mnt/music_hdd/Inbox/Radio`) per
   `beet import` in CT120 (Fileserver) — erst mit automatischer
   Erkennung, dann als Rückfallebene ohne.
2. Stößt danach `azuracast:media:reprocess` in der Radio-VM (210) an,
   damit AzuraCast die neuen Titel bemerkt.

**Kein Kopierschritt mehr nötig** — AzuraCast liest seine Musik direkt
aus `//10.1.0.94/music`, derselben Freigabe, die beets über
`/mnt/music_hdd` verwaltet. Import und Radio-Bibliothek sind dieselbe
Ablage.

## Was am 19.08.2026 repariert wurde

**Fehlerbild:** Wolf berichtete, die Funktion sei gewollt, funktioniere
aber nicht wie erwartet.

**Root Cause:** `curate_radio.py` hatte ursprünglich einen zweiten
Schritt, der importierte Titel zusätzlich nach
`/mnt/musicstick/yourparty.radio/<Genre>/` kopierte. Das war ein
Überbleibsel des alten Raspberry-Pi-Radioaufbaus (siehe
`README_FRAWO_LIBRARY_ROLE.txt` auf dem alten USB-Stick, gefunden beim
selben Audit) — vor der heutigen, gemeinsamen beets-Bibliothek musste
man Titel manuell auf einen Stick kopieren, den ein Pi separat las.

Dieser Zielordner (`/mnt/musicstick`) ist außerdem derselbe
**gefälschte USB-Stick** (meldet 982 GB, real ~60 GB — siehe Erinnerung
`project_frawo_2026-08-17_serverumzug.md`), dessen automatisches
Einhängen zudem deaktiviert war. Der Kopierschritt landete also nie am
richtigen Ort — nicht nur kaputt, sondern seit der Umstellung auf die
gemeinsame Bibliothek auch komplett unnötig.

**Fix:** Kopierschritt entfernt. Pipeline jetzt: Import → AzuraCast
neu scannen lassen, fertig. Alte Fassung liegt auf dem ProDesk unter
`/root/curate_radio.py.backup-20260819`.

⚠️ **Noch nicht mit einer echten Datei über die API end-zu-Ende
getestet** (nur der Leer-Fall — "Eingangsordner leer" — geprüft). Beim
nächsten echten Upload prüfen, ob der Titel danach wirklich im Radio
auftaucht.

## Deployment (ProDesk, `stock-pve`)

```sh
scp frawo_radio_daemon.py curate_radio.py stock-pve:/usr/local/bin/
ssh stock-pve "chmod +x /usr/local/bin/frawo_radio_daemon.py /usr/local/bin/curate_radio.py"
```

`FRAWO_BRIDGE_TOKEN` (Zugangs-Token) liegt nur in der Server-Umgebung,
nicht im Repo.
