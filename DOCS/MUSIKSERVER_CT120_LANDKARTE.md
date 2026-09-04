# Musikserver CT120 — Landkarte

**Stand 04.09.2026.** Reine Bestandsaufnahme, alles nur gelesen — **nichts
verschoben, umbenannt oder gelöscht.** Wolf wollte zuerst den Überblick,
Entscheidungen später. Aufräumen ist bewusst **nicht** Teil dieses Dokuments.

Gehört zu Odoo-Aufgabe **#1263** („[EPIC] Musikserver (CT120) aufräumen").
Zahlen stammen aus `pct exec 120` direkt auf dem Container, nicht aus der
Windows-Freigabe.

---

## 🚨 Zuerst: die drei Funde, die wehtun

| Fund | Was tatsächlich gemessen wurde |
|---|---|
| **`R:` liegt auf der Proxmox-Systemplatte** | `/mnt/musicstick` auf `stock-pve` ist **kein Mountpoint** — die `fstab`-Zeile ist **auskommentiert** (`# /dev/sda1 /mnt/musicstick exfat …`). Der Ordner liegt damit auf `pve-root` (68 GB, 44 % voll, 37 GB frei). Jeder Upload über `R:` frisst die **Systemplatte des Wirts**. Aktuell 6,9 GB. Läuft sie voll, steht der ganze Knoten. |
| **`Quarantine` ist wieder da — 439 GB** | Am 19.08.2026 wurden `Duplicates` (1,1 TB) und `Corrupt` (34 GB) gelöscht (siehe `NOW.md`). Heute: `Duplicates` **433 GB / 13.725 Dateien**, `Corrupt` 77 MB / 4.552. **5.079 Dateien sind neuer als 01.09.2026**, Ordner-Zeitstempel 04.09. 12:34 — es wird **gerade wieder** hineingeschrieben. `Quarantine` ist mit 439 GB der **grösste Posten der Platte**, grösser als die Hauptbibliothek. |
| **27 GB private Fotos und Handyvideos in der Musikbibliothek** | `_STAGING_RAW/yourparty_Libary/UNSORTED` — 8.648 Einträge, u. a. `20230708_214529000_iOS.mp4` (117 MB), `CHANNEL (Smartphone-Video).mp4` (210 MB), `Worship_2024…mp4`, `IMG_20190616_153637.jpg` (81 MB). **Keine Musik.** Der ganze Zweig `_STAGING_RAW/yourparty_Libary` ist 33 GB gross und enthält nur **38 Audiodateien** — der Rest sind 11.963 JPG, 1.862 NFO, 258 PNG, 143 MP4. |

---

## Warum `M:` und `R:` so verschieden aussehen

Keine `veto files`, keine `hide files` — in `/etc/samba/smb.conf` (CT120)
steht **kein einziges** solches Schlüsselwort. Die Erklärung ist banal:

| Freigabe | `path =` | Physisch |
|---|---|---|
| `M:` `[music]` | `/mnt/music` | Wirt `/mnt/music_hdd` → `sdb2`, **NTFS**, 1,8 TB (912 GB belegt), WDC WD20SDRW-34VUUS0 |
| `R:` `[radio]` | `/mnt/stick/yourparty.radio` | Wirt `/mnt/musicstick` → **nicht gemountet**, liegt auf `pve-root` |

**`M:` zeigt `/mnt/music` vollständig und ungefiltert.** Die Windows-Ansicht
ist korrekt und komplett — es fehlt nichts.

**`R:` ist keine Teilmenge von `M:`, sondern eine andere Platte.** Deshalb
taucht dort ein `yourparty_Libary` auf, das es unter `M:` nicht gibt.

### Wo `Ranger_07.26`, `radio_library`, `Library`, `yourparty_Libary` geblieben sind

Sie liegen **nicht** gelöscht, sondern **eine Ebene tiefer**:

```
/mnt/music/_STAGING_RAW/Ranger_07.26      (früher /mnt/music/Ranger_07.26)
/mnt/music/_STAGING_RAW/radio_library
/mnt/music/_STAGING_RAW/Library
/mnt/music/_STAGING_RAW/yourparty_Libary
```

`_STAGING_RAW` ist der **alte Wurzelinhalt der NTFS-Platte**. Beweis: dort
liegt `System Volume Information` — den Ordner legt nur Windows im
**Laufwerkswurzelverzeichnis** an. Ausserdem drei tote Symlinks nach
`/mnt/music_hdd/radio_library/…` (der alte Mountpfad, innerhalb des
Containers nicht auflösbar).

➡️ **Das erklärt die toten beets-Pfade** (`/mnt/music/Ranger_07.26/…`): Sie
waren korrekt, bis alles nach `_STAGING_RAW` einsortiert wurde. Nicht die
Dateien sind weg, der **Präfix** hat sich geändert.

### Nebenbefund: kaputte Freigabe

`[documents]` zeigt auf `/mnt/music/Dokumente` — **den Ordner gibt es nicht.**
Es existiert nur `Dokumente_Inbox`. Die Freigabe läuft ins Leere.

---

## Die Platte in Zahlen (`/mnt/music`, 912 GB belegt)

| Ordner | Grösse | Dateien | davon Audio | Einordnung |
|---|---|---|---|---|
| `Quarantine` | **439 G** | 28.100 | — | 🔴 grösster Posten, wächst wieder |
| `Master_Library` | **375 G** | 19.451 | **9.768** | ✅ **die echte Bibliothek** |
| `Inbox` | 17 G | ~700 | 682 | ⚠️ gemischt, teils live genutzt |
| `_STAGING_RAW` | ~42 G + | ~17.000 | ~2.200 | ⚠️ Altbestand, aber nicht nur |
| `.albumart` | 2,5 G | — | — | beets-Bildzwischenspeicher |
| `MusicBrainz_Input` | 1,8 G | 118 | 118 | |
| `_BACKUPS_ODOO` | 1,7 G | — | — | gehört hier eigentlich nicht hin |
| `_GERETTET_aus_Quarantaene` | 1,4 G | 53 | 53 | |
| `Curated_Playlists` | 31 M | — | — | ✅ nur Symlinks, keine Kopien |
| `.covers` | 30 M | — | — | |
| `Dokumente_Inbox` · `Scans` | je 64 K | — | — | praktisch leer |
| `_playlisten` | 0 | 0 | — | leer (aber als Freigabe eingebunden) |

### `Quarantine` aufgeschlüsselt

| | Grösse | Dateien |
|---|---|---|
| `Duplicates` | **433 G** | 13.725 |
| `Unidentified_Research` | 6,2 G | 123 |
| `Corrupt` | 77 M | 4.552 |
| `Non_Music` | 3,8 M | 9.700 |

---

## ✅ `Master_Library` ist bestätigt die richtige Struktur

Nicht angenommen, sondern nachgemessen:

- **Alle** Symlinks der vier laufenden Radiokanäle zeigen dorthin:
  `Ch1` 1.502, `Ch2` 3.963, `Ch3` 2.072, `Ch4` 1.823 — **9.360 von 9.360 nach
  `Master_Library`**, kein einziger woandershin.
- 9.768 Audiodateien — deckt sich mit den „9.264 erfasst" aus `NOW.md`
  (Stand 29.07., seither kam Import dazu).
- Nur Audio: 5.281 FLAC, 4.224 MP3, 167 WAV, 96 M4A, 1 OGG. Keine Bilder,
  keine Videos, keine Fremddateien.

**Zwei Einschränkungen, ehrlich gesagt:**

1. **Die Ordnernamen sind nicht aufgeräumt.** `Master_Library` hat **426**
   Genre-Ordner der ersten Ebene, nicht 16. Darunter Namen wie
   `Ambient;Deep House;Downtempo;Electronic;Trip Hop`, `Ambient  Electro`
   (doppeltes Leerzeichen), `Bpitch Control` (ein **Label**, kein Genre),
   `Belgium`, `Brazil` (Länder). Die „16 kanonischen Genres" aus `NOW.md`
   beziehen sich auf die **beets-Tags in den Dateien**, nicht auf die
   Ordnerstruktur. Die Ordner haben die alte Unordnung geerbt.
2. **93 Interpretenordner heissen rein numerisch** (`01`, `02`, …) — dort ist
   die Tracknummer als Interpret gelandet. ⚠️ Nicht überbewerten: von den
   7.149 Interpretenordnern sehen 26 nach Tracknummer aus, davon sind die
   meisten **echte Bandnamen** (`2 Unlimited`, `187 Lockdown`, `1000 Ohm`,
   `16 Channels`). Nur die 93 rein numerischen sind wirklich kaputt.
3. **18 Audiodateien sind 0 Byte** (u. a. das komplette Album
   `House;Electronic/Marlon Hoffstadt/Planet Love`).

### Die 9.682 „Geisterdateien" — Entwarnung

`Master_Library` meldet 19.451 Dateien, aber nur 9.768 sind Audio. Der Rest
sind **9.682 Dateien der Form `<name>.flac.ntfs-3g-0000001641`** — Reste, die
`ntfs-3g` bei abgebrochenen Schreibvorgängen hinterlässt.

**Sie kosten keinen Speicherplatz:** alle sind **0 Byte**, und sie sind
untereinander hart verlinkt (Linkzähler 686 auf einem einzigen Inode).
Tree-weit 19.364 Stück — 9.682 in `Master_Library`, dieselben 9.682 in
`Quarantine/Non_Music`. Alle vom **03.08.2026 11:30**, seit 01.09. kam
**keine** dazu. Es ist ein einmaliger Unfall, kein laufendes Problem — aber
er verfälscht jede Dateizählung um Faktor 2.

---

## Die vier `yourparty_Libary` — vier verschiedene Dinge

| Ort | Grösse | Dateien | Genre-Ordner | Was es ist |
|---|---|---|---|---|
| `_STAGING_RAW/yourparty_Libary` | **33 G** | 14.289 | 5 | 🔴 **keine Musik** — 38 Audio. Foto-/Video-/NFO-Halde |
| `Inbox/yourparty_Libary` | 9,3 G | 277 | 135 | ⚠️ **wird gerade benutzt** (siehe unten) |
| `Inbox/yourparty_Libary_R` | 6,9 G | 422 | 5 | 🔁 **1:1-Kopie von `R:`** |
| `R:` `…/yourparty.radio/yourparty_Libary` | 6,6 G | 404 | 80 | eigener Bestand auf der Systemplatte |

**Es sind physisch getrennte Kopien, kein Bind-Mount, kein Hardlink** —
`/mnt/music` liegt auf `sdb2`, `/mnt/stick` auf `pve-root`. Zwei
Dateisysteme, gemeinsame Inodes ausgeschlossen.

**`Inbox/yourparty_Libary_R` ist nachweislich eine vollständige Kopie der
Radio-Freigabe:** 80 von 80 Ordnernamen identisch, 0 Abweichungen, beide
6,9 GB. Stichprobe mit `md5sum` über drei Dateien — **alle drei
bitgleich**. Also 6,9 GB doppelt.

**`Inbox/yourparty_Libary` und der `R:`-Bestand sind dagegen verschieden:**
nur **10** von 135 bzw. 80 Ordnernamen kommen in beiden vor.

⚠️ **Wichtig: `Inbox/yourparty_Libary` ist kein toter Altbestand.** Die neue
Show-Playlist `Curated_Playlists/Sunrise` (angelegt 04.09.2026) verlinkt
19 Titel nach `Master_Library` und **2 dorthin**. Wer diesen Ordner anfasst,
zerschiesst laufende Kuratierungsarbeit.

### Sind die Kopien redundant?

Nach Dateinamen verglichen: **0 Überschneidung** — weder `R:` (299
eindeutige Namen) noch `Inbox/yourparty_Libary` (276) haben auch nur einen
Namen mit `Master_Library` (8.569) gemeinsam.

🔴 **Das ist aber KEIN Beweis, dass die Musik verschieden ist.** Die
Namensschemata unterscheiden sich schlicht:

```
R:              01 - Adam Pits - Real Taste of Gravity.flac
Master_Library  $uicideboy$ - Big Shot Cream Soda.flac
```

Ob derselbe Song doppelt liegt, lässt sich **nur über Tags oder
Audio-Fingerabdruck** klären, nicht über Dateinamen. Offen.

---

## `01_WARMUP` … `06_REKORDBOX_EXPORT` — abgebrochenes Gerüst, **älter** als der 8-Fenster-Sendeplan

| Ordner | Dateien | Grösse |
|---|---|---|
| `01_WARMUP` | 1 | 25 M |
| `02_PEAKTIME` | 3 | 88 M |
| `03_CLASSICS` | 3 | 144 M |
| `04_AFTERHOUR` | 2 | 84 M |
| `05_JINGLES_VOICEOVERS` | **0** | leer |
| `06_REKORDBOX_EXPORT` | **0** | leer |

**Alle 9 Dateien tragen denselben Zeitstempel: 24.07.2026, 13:54–14:04.** In
elf Minuten angelegt und **seither nie wieder angefasst**.

➡️ **Kein Überbleibsel des 8-Fenster-Sendeplans.** Der Umbau, der diesen
Plan überschrieb, datiert auf den **29.07.2026** (dokumentiert in Commit
`2838cf4`, „Sendeplan-Umbau entdeckt"). Das Gerüst hier ist **fünf Tage
älter** und damit ein **eigener, früherer Versuch** — vermutlich aus der
DJ-/Rekordbox-Ecke (`06_REKORDBOX_EXPORT` deutet darauf), nicht aus der
Radio-Sendeplanung.

Die einzige Datei in `01_WARMUP` ist `02 - Way Out (2).flac` (Ellen Allien &
Apparat, 25 MB). Das `(2)` im Namen verrät die Herkunft: händisch aus einem
entdoppelten Bestand herauskopiert — dieselbe Handschrift wie bei allen
anderen acht Dateien (`(1)`, `(2)`, `(3)`).

**Einordnung:** verlassenes Gerüst. Vier Ordner mit zusammen 9 Titeln, zwei
leer. Inhaltlich ist nichts drin, was verloren gehen könnte. Der *Gedanke*
(Warmup → Peaktime → Classics → Afterhour) ist brauchbar und deckt sich mit
dem, was die aktuelle Show-Kuratierung ohnehin gerade neu aufbaut — aber die
**Ordner** selbst tragen dazu nichts bei.

---

## `_STAGING_RAW` aufgeschlüsselt

| Ordner | Grösse | Anmerkung |
|---|---|---|
| `yourparty_Libary` | **33 G** | davon `UNSORTED` 27 G (private Fotos/Videos), `radio_nas` 6,0 G |
| `Library` | 2,0 G | 61 Audiodateien |
| `Ranger_07.26` | 1,8 G | 45 Dateien, 31 Audio |
| `_QUARANTAENE_Duplicates_20260729` | 1,6 G | |
| `radio_library` | ⚠️ nicht messbar | siehe unten — 4 Unterordner, ~2.136 Dateien |
| `Pixel` | 568 M | |
| `_RETTUNG_yourparty_radio_20260727` | 525 M | |
| `SUNDAY MORNING` | 228 M | |
| `Unbenannt-1-001` | 172 M | |
| `Traxx Images` | 77 M | |
| Rest (`VT`, `Sammlung`, `_archive`, `_nach_Genre`, `_nach_Label`, …) | < 10 M | teils **völlig leer** |

`radio_library` enthält `DJ-SETS` (1 Datei), `Music` (2.032, darunter das
Zwischenlager `Music/_input` mit 49 Einträgen), `Playlist import` (66),
`Wolfradio2025` (37).

---

## ⚠️ Dateisystem-Schaden in `radio_library/.albumart`

`du` **stürzt dort reproduzierbar ab** (`Aborted`, Rückgabewert 134). Ursache:

```
du: cannot access '…/radio_library/.albumart/950d25f5903e4adc680a9320.jpg':
    Input/output error
```

Gezählt: von **2.469** Dateien in dem Ordner sind **26 unlesbar**.

**Die Platte selbst ist in Ordnung** — nachgeprüft, nicht vermutet:
`smartctl -H /dev/sdb` meldet **PASSED**, und `dmesg` zeigt **keine** I/O-,
ATA- oder NTFS-Fehler. Es ist also **lokaler NTFS-Metadatenschaden**, kein
sterbendes Laufwerk. Sauber reparieren kann das nur ein `chkdsk` unter
Windows — die Platte ist NTFS und hängt per `ntfs-3g` im Linux-Container.

Betroffen sind ausschliesslich Bildvorschauen, **keine Musik**.

---

## Zusammenfassende Bewertung

| Ordner | Urteil |
|---|---|
| `Master_Library` | ✅ **Die echte Bibliothek.** Belegt durch 9.360 von 9.360 Playlist-Symlinks. Ordnernamen unsauber, Inhalt gut. |
| `Curated_Playlists` | ✅ Sauber. Nur Verweise, 31 MB, keine Dateidopplung. |
| `Inbox/yourparty_Libary` | ⚠️ **Nicht anfassen.** Wird von der laufenden Show-Kuratierung benutzt. |
| `Inbox/yourparty_Libary_R` | 🔁 Nachweisbare Volldopplung von `R:` (6,9 GB, md5-bestätigt). |
| `Inbox` (Rest) | ⚠️ Sammelsurium: HEIC-Fotos, Lexware-Export, `.lnk`, `paperless_sync.py`. Nichts davon gehört in eine Musikbibliothek. |
| `Quarantine` | 🔴 439 GB, wächst wieder, wird gerade beschrieben. Grösster Hebel — **und die grösste offene Frage.** |
| `_STAGING_RAW/yourparty_Libary/UNSORTED` | 🔴 27 GB **private Fotos/Videos**. Kein Musikproblem, aber ein Datenproblem. |
| `_STAGING_RAW` (Rest) | ⚠️ Alter Plattenwurzelinhalt. Etliche Ordner leer, drei Symlinks tot. |
| `radio_library` | ⚠️ Echter Inhalt (~2.100 Dateien) **plus** 26 defekte Bilddateien. |
| `Ranger_07.26`, `Library` | ⚠️ Klein (1,8 G / 2,0 G), Zweck unklar — braucht Wolfs Blick. |
| `R:` `yourparty.radio` | 🔴 Liegt auf der **Systemplatte des Wirts**. Inhalt egal, Ort falsch. |
| `01_WARMUP`…`06_…` | 🗑️ Verlassenes Gerüst vom 24.07.2026, 9 Dateien, zwei Ordner leer. |
| `_BACKUPS_ODOO` | ⚠️ 1,7 GB Odoo-Sicherungen auf der Musikplatte. Falscher Ort. |
| `[documents]`-Freigabe | 🔴 Zeigt auf `/mnt/music/Dokumente` — existiert nicht. |

---

## Offene Fragen — nur Wolf kann sie beantworten

1. **`Quarantine/Duplicates` (433 GB):** Am 19.08. schon einmal geleert, jetzt
   wieder da und wächst. **Was schreibt da hinein?** Solange das ungeklärt
   ist, bringt erneutes Löschen nichts — es kommt wieder.
2. **`Unidentified_Research` (6,2 GB, 123 Dateien):** Im August bewusst
   stehengelassen („braucht echte Durchsicht"). War damals 324 GB, ist jetzt
   6,2 GB. Erledigt oder unfertig?
3. **Die 27 GB private Fotos/Videos:** Sollen die gesichert und von der
   Musikplatte herunter — und wohin?
4. **`Ranger_07.26` und `Library`:** Sagen dir die Namen noch etwas?
5. **`R:` als Arbeitslaufwerk:** Wird die Radio-Freigabe überhaupt noch
   benutzt, oder läuft alles über `M:` und die Radio-Bridge?

## Mögliche nächste Schritte — als Optionen, nicht als Plan

Bewusst **keine** Reihenfolge, keine Empfehlung. Erst Wolfs Antworten oben.

- **A — `R:` von der Systemplatte holen.** Der einzige Punkt mit
  Ausfallrisiko für den ganzen Proxmox-Knoten. Entweder Freigabe auf die
  Musikplatte umziehen oder einen echten Datenträger nach `/mnt/musicstick`
  mounten. (Die `sda` mit „982 GB" ist der gefälschte Stick vom 01.08.2026 —
  **nicht** wieder einhängen.)
- **B — Herausfinden, was `Quarantine` füllt.** Messen, nicht löschen.
- **C — `Inbox/yourparty_Libary_R` streichen.** 6,9 GB, als bitgleiche Kopie
  belegt. Ginge erst nach Option A, sonst ist es die einzige zweite Kopie.
- **D — Die 19.364 `.ntfs-3g-*`-Geisterdateien entfernen.** Bringt **0 Byte**
  Platz, macht aber jede künftige Zählung ehrlich.
- **E — `chkdsk` unter Windows** gegen die 26 defekten Dateien.
- **F — Private Fotos/Videos aussortieren** (27 GB).
- **G — `[documents]`-Freigabe reparieren oder entfernen.**
- **H — Ordnernamen in `Master_Library` normalisieren** (426 → handhabbar).
  🔴 Grösster Eingriff: **alle 9.360 Playlist-Symlinks zeigen dorthin** und
  müssten mitgezogen werden. Nur mit Plan und Sicherung.

---

## Nachprüfen

```bash
# Freigaben und ihre echten Pfade
ssh stock-pve "pct exec 120 -- grep -A2 '^\[' /etc/samba/smb.conf | grep -E '^\[|path'"

# Liegt R: immer noch auf der Systemplatte?
ssh stock-pve "mountpoint /mnt/musicstick; df -h /mnt/musicstick"

# Grössen je Wurzel
ssh stock-pve "pct exec 120 -- du -h -d 1 /mnt/music"

# Geisterdateien zählen
ssh stock-pve "pct exec 120 -- find /mnt/music -name '*.ntfs-3g-*' -type f | wc -l"

# Zeigen die Playlisten wirklich alle nach Master_Library?
ssh stock-pve "pct exec 120 -- find /mnt/music/Curated_Playlists -maxdepth 2 -type l -printf '%l\n' | grep -c Master_Library"
```
