# Verschlüsselung der Cloud-Sicherungen

**Eingerichtet am 28.07.2026.** Diese Seite ist die einzige Stelle, an der
erklärt wird, wie man im Ernstfall an die verschlüsselten Sicherungen kommt.

---

## Der Grundgedanke in einem Satz

**Lokal unverschlüsselt, Cloud verschlüsselt.**

| Wo | Zustand | Warum |
|----|---------|-------|
| ProDesk `/mnt/data_family/…` | unverschlüsselt | steht im Haus, physisch geschützt — Wiederherstellung **ohne jeden Schlüssel** möglich |
| Anker `/var/backups/…` | unverschlüsselt | zweite Maschine, ebenfalls im Haus |
| Google Drive | **verschlüsselt** | dort liegen die Daten bei einem Fremdanbieter |

Das ist bewusst so gewählt. **Wären alle Kopien verschlüsselt und der Schlüssel
ginge verloren, wäre alles weg.** So bleibt der lokale Weg immer offen — der
Schlüssel wird nur gebraucht, wenn beide Maschinen im Haus zerstört sind.

---

## Wo der Schlüssel liegt

Es sind zwei Dateien, Passwort und Salt. Beide werden gebraucht.

| Ort | Pfad |
|-----|------|
| ProDesk (10.1.0.128) | `/root/.frawo-crypt-pw` und `/root/.frawo-crypt-salt` |
| Anker (10.1.0.92) | dieselben Pfade |

Beide Dateien haben Rechte `600` — nur root kann sie lesen.

### ⚠️ Was noch fehlt

Der Schlüssel liegt bisher **nur auf den beiden Servern**. Brennt das Haus,
sind Sicherung und Schlüssel gleichzeitig weg — dann nützt auch die
Cloud-Kopie nichts.

**Wolf sollte den Schlüssel zusätzlich ablegen:**

1. In **Vaultwarden** als sicherer Eintrag „Cloud-Verschlüsselung Sicherungen"
2. **Auf Papier**, an einem Ort ausserhalb des Hauses

Auslesen lässt er sich mit:

```
ssh root@10.1.0.128 "cat /root/.frawo-crypt-pw; echo '---'; cat /root/.frawo-crypt-salt"
```

---

## Wie man im Ernstfall herankommt

Auf einer Maschine mit rclone und den beiden Schlüsseldateien:

```bash
# Was liegt in der Cloud?
rclone lsl gcrypt:Odoo

# Sicherung herunterladen und entschlüsseln (passiert automatisch)
rclone copy gcrypt:Odoo/FraWo_GbR-JJJJMMTT-HHMM.dump /ziel/
```

Ohne die Schlüsseldateien sieht man bei Google nur unlesbare Namen wie
`j5eo1op2ur3kegb2529dmlmbmg/1igsv68mtioihv24eq3q4kbq…` — und daraus lässt
sich nichts gewinnen.

### Auf einer neuen Maschine

```bash
# rclone-Konfiguration um das verschlüsselte Ziel ergänzen
rclone config create gcrypt crypt \
  remote gdrive:FraWo-Verschluesselt \
  filename_encryption standard \
  directory_name_encryption true \
  password "$(rclone obscure "$(cat /root/.frawo-crypt-pw)")" \
  password2 "$(rclone obscure "$(cat /root/.frawo-crypt-salt)")"
```

Voraussetzung ist ein funktionierender `gdrive`-Zugang.

---

## Was verschlüsselt in der Cloud liegt

| Ordner | Inhalt |
|--------|--------|
| `gcrypt:Odoo` | tägliche Odoo-Sicherung (Datenbank + Filestore) |
| `gcrypt:Alt-Sicherungen-2026-06` | ältere Sicherungen vom 18.06.2026, nachträglich verschlüsselt |

**Noch nicht verschlüsselt:** die VM-Abbilder (`gdrive:FraWo-ProDesk-VMs`) und
die Musik (`gdrive:FraWo_Musik`). Beide sind weniger heikel als die
Geschäftsdaten — die Musik ist ohnehin kein Geheimnis, und die VM-Abbilder
sind sehr gross. Kann später nachgezogen werden.

---

## Nachweis, dass es funktioniert

Am 28.07.2026 vollständig durchgetestet:

1. Datei verschlüsselt hochgeladen
2. Rohansicht bei Google zeigt nur unlesbare Datei- und Ordnernamen
3. Datei zurückgeholt und entschlüsselt
4. **MD5-Prüfsumme identisch mit dem Original**, Archiv öffnet sich

Der Backup-TÜV greift täglich über `gcrypt:` zu. Damit prüft er nebenbei
mit, dass die Entschlüsselung noch funktioniert: Wäre der Schlüssel kaputt,
käme keine Dateiliste zurück und die Prüfung fiele durch.
