# DJ-Stick automatische Sicherung

Wolf nimmt als DJ mehrere USB-Sticks mit auf Tour. Statt eines Zeittakts
("alle 5 Minuten nachsehen"), sichert der ProDesk automatisch, sobald ein
Stick tatsächlich angesteckt wird.

## Wie es funktioniert

1. `99-dj-stick.rules` (udev) löst bei jedem neu angesteckten USB-Datenträger
   `dj-stick-sync@<Gerätename>.service` aus (z. B. `dj-stick-sync@sdb1.service`).
2. `dj-stick-sync.sh` hängt den Datenträger kurz ein und prüft auf die
   unsichtbare Markierungsdatei `.frawo-dj-stick`. Fehlt sie, wird nichts
   getan (z. B. bei fremden USB-Geräten oder dem gefälschten Stick).
3. Ist die Markierung da, wird der Inhalt nach
   `gdrive:Stockenweiler/dj_sticks/<Datenträgername>` gesichert — der Name
   ist frei wählbar (Show, Datum, Sender, egal was Wolf möchte).

**Erkennung und Benennung sind bewusst getrennt:** die Markierungsdatei
entscheidet "ist das einer von unseren Sticks", der sichtbare Name
entscheidet nur, wie der Sicherungsordner heißt.

## Neuen Stick vorbereiten

```sh
# Stick vorher formatieren + Namen vergeben (z.B. unter Windows), dann
# einhängen und:
dj-stick-vorbereiten.sh /media/wolf/MEIN-STICK-NAME
```

## Deployment (ProDesk, `stock-pve`)

```sh
scp dj-stick-sync.sh dj-stick-vorbereiten.sh stock-pve:/usr/local/bin/
scp "dj-stick-sync@.service" stock-pve:/etc/systemd/system/
scp 99-dj-stick.rules stock-pve:/etc/udev/rules.d/
ssh stock-pve "chmod +x /usr/local/bin/dj-stick-sync.sh /usr/local/bin/dj-stick-vorbereiten.sh && udevadm control --reload-rules && systemctl daemon-reload"
```

## Ersetzt

Die alte `musicstick-sync.timer`-Lösung (alle 5 Minuten, feste Geräte-Zuordnung
über `/dev/sda1`, keine Trennung Erkennung/Name). Lief seit 23.07.2026 ins
Leere, weil das Auto-Einhängen zwischenzeitlich deaktiviert wurde, ohne dass
es auffiel. Alte Dateien liegen auf dem ProDesk unter
`/root/systemd-leichen-backup-20260819/`.

⚠️ **Stand 19.08.2026: noch nicht mit einem echten Stick End-zu-Ende getestet.**
