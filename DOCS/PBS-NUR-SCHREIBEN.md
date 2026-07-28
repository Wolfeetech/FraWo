# Backup-Server: Nur-Schreiben-Zugang (Schutz gegen Verschlüsselungstrojaner)

**Eingerichtet am 28.07.2026.** Letzter offener Punkt aus dem Sicherungs-Audit.

---

## Das Problem

Der ProDesk meldete sich beim Backup-Server als `root@pam` an — mit vollen
Rechten, also auch zum Löschen. **Wer den ProDesk übernimmt, konnte alle
Sicherungen darauf mitlöschen.** Genau so arbeiten moderne
Verschlüsselungstrojaner: erst die Sicherungen vernichten, dann die Daten.

## Die Lösung

Ein eigener Zugang, der schreiben aber nicht löschen darf.

| Was | Wert |
|-----|------|
| Benutzer | `prodesk@pbs` |
| Token | `prodesk@pbs!backup` |
| Rechte | `DatastoreAudit` auf `/datastore/local-backups`<br>`DatastoreBackup` auf `/datastore/local-backups/prodesk` |

Das Aufräumen alter Stände übernimmt jetzt der Backup-Server selbst
(Prune-Auftrag `prodesk-prune`), nicht mehr der ProDesk. Der PVE-Auftrag steht
deshalb auf `prune-backups keep-all=1`.

---

## Zwei Fallen, über die ich gestolpert bin

**1. Ein Token kann nie mehr dürfen als sein Benutzer.**
Die Rechte müssen dem *Benutzer* **und** dem *Token* gegeben werden. Stehen
sie nur am Token, ist die Schnittmenge leer und der Zugang sieht nichts —
ohne dass eine sprechende Fehlermeldung käme.

**2. `DatastoreBackup` erlaubt nur Zugriff auf EIGENE Sicherungen.**
Die bestehenden Gruppen gehörten `root@pam`, der neue Zugang sah deshalb eine
leere Liste. Der Besitz musste umgeschrieben werden:

```bash
proxmox-backup-client change-owner "ct/<id>" 'prodesk@pbs!backup' \
  --repository 'root@pam@10.1.0.7:local-backups' --ns prodesk
```

Umkehrbar mit demselben Befehl und `root@pam` als neuem Besitzer.

---

## Nachweis, dass es wirkt

Am 28.07.2026 durchgetestet:

| Test | Ergebnis |
|------|----------|
| Lesen | ✅ 25 Sicherungen sichtbar |
| Schreiben | ✅ Sicherung erstellt, Auftrag ohne Fehler beendet |
| **Löschen** | ✅ **verweigert** — `permission check failed - missing Datastore.Modify\|Datastore.Prune` |
| Sicherung danach | ✅ unversehrt vorhanden |

---

## Nebenbefund: die Aufbewahrung war viel kürzer als gedacht

Beim Einrichten fiel ein Prune-Auftrag `daily-prune` auf, der **täglich über
den gesamten Datastore** lief — mit `keep-last 2`. Er hat die im PVE-Auftrag
eingestellten sieben Stände jede Nacht wieder auf zwei zusammengestrichen.

**Die tatsächliche Aufbewahrung waren 2 bis 3 Tage, nicht 7.** Gemessen: genau
drei Snapshots je Container, bei einer Vorgabe von sieben.

Der Auftrag deckte nichts anderes ab — der Namespace `anker` ist leer, dessen
Gäste sichern in die Cloud. Er wurde entfernt und durch `prodesk-prune`
ersetzt (7 täglich, 4 wöchentlich, 2 monatlich, nur Namespace `prodesk`).

---

## Rückweg, falls etwas klemmt

```bash
# Auf dem ProDesk: zurück auf den alten Zugang
pvesm set pbs-frawo --username 'root@pam' \
  --password "$(cat /root/pbs-frawo.pw.sicherung-20260728)"

# Aufräumen wieder durch PVE erledigen lassen
pvesh set /cluster/backup/28c8fb76-91c9-4a4e-bd81-5596167a2122 \
  --prune-backups 'keep-last=7,keep-weekly=4,keep-monthly=2'
```

Gesicherte Konfigurationen auf dem ProDesk unter `/root/`:
`storage.cfg.sicherung-20260728`, `jobs.cfg.sicherung-20260728`,
`pbs-frawo.pw.sicherung-20260728`.
