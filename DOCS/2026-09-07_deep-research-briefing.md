# Briefing für eine unabhängige Infrastruktur-Analyse (Stand: 07.09.2026)

## Was ich von dir will

Ich betreibe als Kleinunternehmer (FraWo GbR, Deutschland, §19 UStG) eine selbstgebaute
IT-Landschaft aus zwei gebrauchten Mini-PCs. Sie ist über etwa ein halbes Jahr organisch
gewachsen — ein Dienst nach dem anderen, ohne Gesamtplan. Heute ist einer der beiden
Rechner hardwareseitig gestorben, und dabei ist sichtbar geworden, wie viele
Abhängigkeiten wir übersehen haben.

**Analysiere die folgende Landschaft und beantworte:**

1. Welche **Konstruktionsfehler** stecken in diesem Aufbau — insbesondere versteckte
   Abhängigkeiten, die erst bei einem Ausfall sichtbar werden?
2. Was wäre **professioneller Standard** für einen Betrieb dieser Größe (1–2 aktive
   Personen, ein paar Kunden, öffentliche Website und ein Webradio)? Wo sind wir davon
   entfernt, und wo ist der Abstand vertretbar, weil professioneller Standard hier
   überzogen wäre?
3. Welche **nächsten Schritte** würdest du in welcher Reihenfolge empfehlen? Bitte
   priorisiert nach Risiko und Aufwand, nicht nach technischer Eleganz.
4. Wie hole ich das **Maximum aus vorhandener Hardware**, statt neue zu kaufen?
5. Konkret: Ein **Dell OptiPlex 7050** steht als Ersatz bereit. Wie sollte er sinnvoll
   in diese Landschaft eingebunden werden — als Eins-zu-eins-Ersatz des toten Rechners
   oder als Anlass, die Aufteilung neu zu schneiden?

Sei kritisch. Ich suche keine Bestätigung, sondern die Fehler, die ich selbst nicht mehr
sehe.

---

## 1. Rahmen und Beteiligte

- **FraWo GbR** — Kleinstunternehmen, Veranstaltungstechnik (Licht/Ton für Konzerte und
  Events), Technikverleih, dazu ein Webradio als Marken- und Hobbyprojekt.
- **Zwei Gesellschafter**, davon einer (ich) mit der IT befasst — **ohne
  IT-Ausbildung**. Alles ist mit Hilfe von KI-Assistenten gebaut worden.
- **Erklärtes Ziel:** Die eigene Infrastruktur ist Prototyp. Wenn sie stabil und
  betreubar ist, soll dieselbe Bauweise **gewerblich als Dienstleistung** angeboten
  werden (kleine Betriebe, Smart Home, Vereinsräume). Maßstab an jede Lösung ist deshalb:
  *reproduzierbar? dokumentiert? von jemand anderem betreubar?*
- **Drei KI-Agenten** arbeiten mit an der Infrastruktur (Details in Abschnitt 10).

## 2. Standorte

Wichtig, weil Namen in die Irre führen:

| Standort | Was dort steht | Netz |
|---|---|---|
| **Rothkreuz 22(a)** | beide Server, Werkstatt, Studio, Arbeitsplatz | eigenes VLAN-Netz (siehe unten) |
| **Rothkreuz 14** („die Villa") | **Unternehmensstandort**, derzeit Baustelle — hierhin soll die Anlage langfristig ziehen | „Franznetz", getrennt. **Kein Kabelanschluss: WAN nur per Richtfunk, 100 Mbit** |
| **Stockenweiler 3, Hergensweiler** | Grundstück der Eltern, dort ein FraWo-Außenposten (Container: Lager/Technik) | FRITZ!Box-Netz `192.168.178.0/24`, per WireGuard an Rothkreuz angebunden |

**Falle:** Der eine Server heißt aus historischen Gründen `stockenweiler-pve`, steht aber
in **Rothkreuz**. Dasselbe gilt für eine Home-Assistant-Instanz namens „Stockenweiler",
die physisch als VM auf diesem Rothkreuz-Server läuft und nur die Geräte der Eltern
steuert.

In Stockenweiler sind drei Parteien mit getrennten Stromkreisen (Eltern, eine Mieterin,
der FraWo-Container) — abgegrenzt über Shelly-Pro-4PM-Zähler.

## 3. Netzwerk

**Gateway:** UniFi Cloud Gateway Ultra (10.1.0.1), dazu ein WLAN-Access-Point (U7 Mesh).
Segmentiert in VLANs:

| VLAN | Subnetz | Zweck |
|---|---|---|
| 1 | 192.168.1.0/24 | Default (Rest) |
| 100 | 10.0.0.0/24 | Anker-LAN |
| **101** | **10.1.0.0/24** | **Server — hier läuft alles Wesentliche** |
| 102 | 10.2.0.0/24 | DMZ |
| 103 | 10.3.0.0/24 | DMZ Radio |
| **104** | **10.4.0.0/24** | **IoT (Shellys, Kameras, Smart Home)** |
| 105 | 10.5.0.0/24 | Gäste-WLAN, L2-isoliert |
| 110/111 | 10.10/10.11.0.0/24 | für den Standort Stockenweiler vorgesehen |

**Firewall-Regeln zwischen den VLANs:** IoT→Server und Gast→Server sind blockiert,
Server→IoT ist erlaubt. Ausnahmen für DNS, NTP und die Überwachungs-Ports (Prometheus).

**Bekannte Falle, die uns Stunden gekostet hat:** Eine Erlaubnis-Regel für den Hinweg
reicht bei dieser Firewall nicht. Ohne eine zusätzliche Regel für „established/related"
verwirft die Blockier-Regel die Antwortpakete — sämtliche IoT-Geräte wirken dann tot,
obwohl sie erreichbar sind.

**DNS:** Zwei AdGuard-Home-Instanzen, ein Master und eine Replica, die kontinuierlich
synchronisiert wird. **Der Master lief auf dem heute ausgefallenen Rechner.**
Nebenbefund: Mein Arbeitsplatzrechner benutzt gar nicht den internen DNS, sondern direkt
1.1.1.1 — die Filterung greift dort also überhaupt nicht.

## 4. Hardware

| Rolle | Gerät | CPU | RAM | Zustand |
|---|---|---|---|---|
| Knoten A („ProDesk", `stockenweiler-pve`) | HP ProDesk 600 G4 | i7-7700T, 8 Threads | ? | **heute gestorben** |
| Knoten B („Anker", `proxmox-anker`) | Lenovo ThinkCentre | i5-8500T, 6 Kerne | 16 GB | läuft |
| Ersatz (bereitgestellt) | **Dell OptiPlex 7050** | ? | ? | noch nicht eingebunden |

Beide Knoten laufen **Proxmox VE 8**, aber **nicht als Cluster** — zwei völlig
eigenständige Installationen ohne gemeinsame Verwaltung, ohne Live-Migration, ohne
gemeinsamen Speicher.

**Speicher:** LVM-Thin-Pools auf lokalen Platten. Der Anker hat 157 GB Thin-Pool
(derzeit 61 % belegt) und ist **überbucht** — die Summe der zugewiesenen virtuellen
Platten übersteigt den Pool. Zusätzlich ein ZFS-Pool von 1,9 TB (fast leer) und zwei
über USB angeschlossene externe Festplatten am toten Knoten (1 TB für Sicherungen, 2 TB
für Musik).

Die LXC-Container liefen lange **ohne `discard`**, wodurch gelöschte Daten dauerhaft im
Thin-Pool belegt blieben und dieser schleichend volllief. Inzwischen läuft wöchentlich
ein `fstrim`-Skript.

## 5. Was wo läuft

**Auf dem toten Knoten A lief:**

| Dienst | Zweck |
|---|---|
| Odoo 19 Community + Website | ERP, Kundenverwaltung, Rechnungen, Aufgaben, öffentliche Website |
| Vaultwarden | **Passwort-Tresor — Ablageort sämtlicher Zugangsdaten** |
| Paperless-ngx + n8n | Dokumentenarchiv (154 Dokumente), Automatisierungen |
| Prometheus + Grafana + Alertmanager | **Überwachung und Alarmierung der gesamten Landschaft** |
| AdGuard Home (Master) | primärer DNS |
| WireGuard | VPN zum Standort Stockenweiler |
| Samba/NFS-Fileserver | Musik- und Datenfreigaben |
| AzuraCast (VM) | **das Webradio** |
| Home Assistant (VM) | Smart Home der Eltern |

**Auf Knoten B (Anker) läuft:**

| Dienst | Zweck |
|---|---|
| AdGuard Home (Replica) | sekundärer DNS |
| OpenClaw | KI-Agent „Jarvis", Telegram-Anbindung, 24/7 |
| Radio-Backend (FastAPI + Postgres + Redis) | fertig gebaut, **aber nie verdrahtet** |
| Home Assistant (VM) | Smart Home Rothkreuz |
| Proxmox Backup Server (VM) | Sicherungsziel |
| Nextcloud (VM) | Dateien |
| *seit heute zusätzlich* | Odoo+Website, Vaultwarden, Paperless+n8n (aus Sicherungen) |

## 6. Zugang von außen

- **Keine einzige Portweiterleitung** am Gateway. Alles läuft über
  **Cloudflare-Tunnel**, die von innen aufgebaut werden, plus **Tailscale** als
  Fernwartungsnetz.
- Öffentlich erreichbar: die Website (`frawo.tech`), der Passwort-Tresor
  (`vault.frawo-tech.de`), das Radio (`funk.frawo-tech.de`), Paperless.
- **Konstruktionsfehler, heute sichtbar geworden:** Der Cloudflare-Tunnel läuft im
  selben Container wie Odoo und die Website. Fällt der aus, sind **auch Radio und
  Passwort-Tresor von außen weg**, obwohl sie eigene Dienste sind. Das erklärt, warum
  heute Fehler 530 statt 502 kam — es war nicht das Ziel, das fehlte, sondern der
  Tunnel selbst.
- Zwei Domains parallel im Einsatz: `frawo.tech` und `frawo-tech.de`. Kein erkennbares
  System dahinter, historisch gewachsen.

## 7. Datensicherung

| Was | Wohin | Takt |
|---|---|---|
| Container von Knoten A | Proxmox Backup Server (VM auf Knoten B) | täglich 04:00 |
| Gäste von Knoten B | Google Drive (via rclone) | täglich 04:00, 3 Generationen |
| VMs von Knoten A | Google Drive, eigener Ordner | wöchentlich |
| Musik | Google Drive | stündlich |

Ein Prüfskript („Backup-TÜV", täglich 08:00) prüft **12 Ergebnisse**, nicht Vorgänge:
Ist eine Datei da, groß genug, jung genug, **und lesbar**? Sonntags läuft zusätzlich ein
echter Wiederherstellungstest der Odoo-Datenbank in eine Wegwerf-Datenbank.

**Historie, die zu diesem Aufbau geführt hat:** Es gab zwei längere Phasen, in denen
Sicherungen **still ins Leere liefen** — einmal wochenlang 0-Byte-Dumps, einmal 14 Tage
gar nichts, weil ein Formatfehler in der Crontab sämtliche Cron-Jobs lahmgelegt hatte.
Beides fiel erst auf, als jemand zufällig nachsah.

**Heute aufgefallen:** Die Sicherungen haben funktioniert und waren 1,5 Stunden vor dem
Ausfall aktuell. Aber ich musste erst herausfinden, dass die Sicherungen von Knoten A in
einem getrennten Namensraum des Backup-Servers liegen, den Knoten B gar nicht kannte —
er musste erst als Speicher eingebunden werden, bevor eine Wiederherstellung möglich war.

## 8. Überwachung

Prometheus, Grafana, Alertmanager, Blackbox-Exporter mit 39 Alarmregeln und 16
Überwachungszielen. Zwei Alarmwege: Telegram an mich, und ein Webhook an den KI-Agenten.

**Der zentrale Konstruktionsfehler:** Das alles lief auf Knoten A. Als Knoten A starb,
starb die Alarmierung mit. **Der Ausfall blieb vier Stunden lang unbemerkt.** Niemand
wurde benachrichtigt — auch der KI-Agent nicht, weil er seine Meldungen von genau dieser
Alarmierung bekommt.

Zusätzlich: Der Mailversand von Knoten B ist seit unbekannter Zeit defekt (die
Zugangsdatei für den Mail-Relay fehlt komplett). Auch dieser Weg hätte nicht funktioniert.

## 9. Das Radio

- **AzuraCast** als VM auf Knoten A, öffentlich als `funk.frawo-tech.de`.
- Ein zweites, komplett eigenständiges **Radio-Backend** (FastAPI, eigene Datenbank,
  Redis) läuft auf Knoten B — es wurde fertig gebaut, ist aber **an nichts angeschlossen**.
  Es existiert seit Wochen und tut nichts.
- Eine Funktion „Kanal-Demokratie" ist live: Zuschauer stimmen ab, ein zeitgesteuerter
  Job rechnet daraus Gewichtungen und schreibt sie über die AzuraCast-Schnittstelle in
  die Playlisten.
- **Bekannte Fallen:** Die Wiederholsperre von AzuraCast arbeitet pro *Datei*, nicht pro
  *Titel* — derselbe Song lief zweimal pro Stunde, bis wir die Playlisten entdoppelten.
  Eine Datenbankspalte heißt anders als vermutet, wodurch eine Abfrage stillschweigend
  beide Speicherorte vermischte.
- Bei einer früheren Migration blieb eine **gestoppte Zwillings-VM mit identischer
  MAC-Adresse** und aktiviertem Autostart zurück. Beim nächsten Neustart wäre sie
  gestartet — doppelte MAC im selben Netz, Radioausfall mit sehr schwer auffindbarem
  Fehlerbild. Rein zufällig entdeckt.
- Die als Rückfallebene gedachte Kopie dieser Radio-VM lag auf einer Netzwerkfreigabe
  **des Rechners, der heute gestorben ist**. Sie war damit im Ernstfall wertlos.

## 10. Die KI-Agenten (und warum sie Ärger machen)

Drei Agenten arbeiten an derselben Infrastruktur:

- **„Jarvis"** — OpenClaw, läuft dauerhaft auf Knoten B, per Telegram erreichbar,
  Koordinator und Empfänger der Alarme.
- **Claude Code** — im Terminal, zustandslos, für Code und größere Umbauten.
- **Antigravity** — in der Entwicklungsumgebung, für lokale und Netzwerk-Aufgaben.

Als Single Source of Truth für Aufgaben dient **Odoo**. Es gibt ein schriftliches
Protokoll: vorher ankündigen, Aufgabe übernehmen (das ist die Sperre gegen Doppelarbeit),
hinterher Ergebnis belegen, Vier-Augen-Prinzip vor „Erledigt".

**Warum das immer wieder scheitert:**

- Ein Agent hat einmal Ergebnisse **frei erfunden** und Aufgaben als erledigt gemeldet,
  ohne sie bearbeitet zu haben. Das Protokoll existierte da schon — es wurde nur nicht
  gelesen.
- Es gab eine automatische Abfrage, die Agenten-Sitzungen auslöste und Aufgaben selbsttätig
  bearbeitete. Ergebnis waren Schein-Erledigungen. Seither sind eigene Cron- oder
  Polling-Jobs, die Agenten triggern, ausdrücklich verboten.
- Ein Webhook ohne sofortige Empfangsbestätigung und ohne Dubletten-Erkennung führte zu
  **Alarm-Spam** — derselbe Alarm fünfmal.
- Zwei Agenten haben dieselbe Aufgabe komplett doppelt bearbeitet, weil keiner sie vorher
  übernommen hatte.
- OpenClaw selbst ist störanfällig: Aussetzer durch nicht funktionierendes IPv6,
  Authentifizierungsfehler, die als Netzwerk-Zeitüberschreitung erschienen, ein
  Konfigurationsbefehl, der unbemerkt das gesamte Modell mitumstellt, und eine
  Kostenexplosion durch eine Einstellung, die bei jedem Aufruf den vollen Kontext
  mitschickte (Verhältnis Eingabe zu Ausgabe 500:1).
- Ein Webhook-Handler ist seit Tagen defekt und offen.

**Ehrliche Einschätzung:** Die Agenten erledigen viel, aber die Kontrollmechanismen sind
nachträglich um Vorfälle herumgebaut worden, nicht vorher entworfen.

## 11. Fallstudie: der Ausfall heute

**Zeitleiste:**

| Zeit | Ereignis |
|---|---|
| gestern 18:20 | erste Aussetzer der Dateifreigabe von Knoten A, vereinzelt |
| gestern 19:00 | fünf Aussetzer in einer Stunde |
| nachts | 1–4 Aussetzer pro Stunde |
| 04:11 | die nächtliche Sicherung läuft **vollständig und sauber** durch |
| ca. 05:55 | Stromaufnahme fällt von 195 auf 87 Watt — der Rechner ist aus |
| ab 06:00 | über 300 Fehlermeldungen pro Stunde: endgültig weg |
| 10:01 | **Knoten B startet sich selbst unsauber neu** (eigener Vorfall) |
| ~10:00 | Ausfall wird zufällig bemerkt, vier Stunden zu spät |

**Diagnose:** Der Strom lag durchgehend an — eine Shelly-Steckdose hat die ganze Nacht
gemessen, stabil zwischen 185 und 197 Watt. Kein Stromausfall, kein langsam sterbendes
Netzteil (das hätte man an unruhiger Aufnahme gesehen). Der Rechner reagiert auch nicht
mehr auf den Einschaltknopf und nicht auf Wake-on-LAN. Ein Gerät, das gar nicht mehr
anspringt, hat kein Software- und kein Festplattenproblem — es ist Netzteil oder
Mainboard. Ein Ersatznetzteil ist für 13 € bestellt.

**Wiederherstellung:** Odoo und Website waren nach 6,5 Minuten wieder online, danach
Passwort-Tresor und Paperless. Alles aus den Sicherungen von 04:11 Uhr, praktisch ohne
Datenverlust.

**Was der Ausfall offengelegt hat:**

1. Die **Alarmierung lag auf dem überwachten Rechner** und schwieg.
2. Der **Passwort-Tresor lag auf demselben Rechner** — im Störungsfall kam ich an keine
   einzige Zugangsdatei, unter anderem nicht an die, die zur Reparatur des Mailversands
   nötig gewesen wäre.
3. Die **Rückfallkopie des Radios** lag auf einer Freigabe des ausgefallenen Rechners.
4. Der zweite Knoten kannte die Sicherungen des ersten **gar nicht** — sie mussten erst
   eingebunden werden.
5. **Wake-on-LAN war nie aktiviert**, also gab es keine Möglichkeit der Ferndiagnose.
6. Die Infrastrukturdokumentation enthielt **falsche IP-Adressen** für mindestens zwei
   Dienste.
7. Ein toter Hilfsdienst startete sich seit Monaten **alle fünf Sekunden** neu
   (Restart-Zähler über 162.000) — er versuchte, einen seit einem Monat abgeschalteten
   Server zu erreichen. Niemandem war es aufgefallen.

## 12. Karteileichen und Inaktives

- Der genannte Neustart-Dienst, der ins Leere lief (inzwischen abgeschaltet).
- Ein **dritter Server eines früheren Mitstreiters** ist endgültig weg. Darauf liefen
  Nextcloud, eine zweite AzuraCast-Instanz, eine ältere Automatisierungsplattform, ein
  lokales Sprachmodell und eine Vektordatenbank. Ob davon etwas wieder gebraucht wird,
  ist nie geklärt worden.
- **Uptime-Kuma** läuft irgendwo, seit Monaten steht die Entscheidung aus, ob aufräumen
  oder abschalten.
- Das fertige Radio-Backend ohne Anschluss (siehe Abschnitt 9).
- Ein früher stark überzogener NFS-Export: eine Freigabe war für das gesamte Netz lesbar,
  inklusive einer Passwortdatei mit Rechten 777. Inzwischen behoben.
- **13 alte Zugangsdaten liegen im öffentlichen Git-Repository** in der Historie. Ein
  Scanner läuft inzwischen in der CI, aber die Altlast ist nicht bereinigt und die
  Passwörter sind nicht rotiert.
- Im ERP: doppelte Kundendatensätze, mehrfach vorhandene Schlagworte, Dutzende
  archivierter Testeinträge im Kalender.
- Eine gefälschte USB-Festplatte (meldet 982 GB, hat real 64 GB) lag monatelang im
  Bestand und hat Sicherungen aufgenommen, die nie gespeichert wurden.

## 13. Was jetzt zu entscheiden ist

Der Ersatzrechner (**Dell OptiPlex 7050**) steht bereit. Am Gateway ist der Port des
toten Rechners frei geworden, ein Switch ist also nicht nötig. Die beiden externen
USB-Festplatten (Sicherungen, Musik) hängen noch am toten Gerät und können umgesteckt
werden.

**Die Versuchung ist, den OptiPlex genau so aufzusetzen wie den toten Rechner und alles
zurückzuschieben.** Genau davor möchte ich gewarnt oder darin bestätigt werden.

Offene Fragen, zu denen ich eine begründete Empfehlung brauche:

- **Aufteilung:** Was gehört auf welchen Knoten, damit der Ausfall eines Knotens nicht
  wieder die Alarmierung, den Passwort-Tresor und die Sicherungskenntnis mitreißt?
- **Cluster oder nicht?** Zwei eigenständige Proxmox-Installationen bedeuten keine
  Live-Migration. Ein Zwei-Knoten-Cluster braucht aber einen dritten Stimmgeber
  (QDevice). Lohnt das in dieser Größenordnung?
- **Alarmierung:** Wie überwacht man eine Zwei-Knoten-Landschaft so, dass der Ausfall
  eines beliebigen Knotens sicher gemeldet wird — ohne einen dritten Rechner nur dafür
  zu kaufen? Reicht ein externer Dienst?
- **Trennung der Zugangswege:** Der Cloudflare-Tunnel für alle Dienste in einem Container
  ist offensichtlich falsch. Was ist der saubere Schnitt?
- **Speicher:** Externe USB-Platten für Sicherungen und Mediendaten — vertretbar oder
  Zeitbombe? Was wäre die nächstbessere Stufe ohne großes Budget?
- **Dokumentation und Reproduzierbarkeit:** Ein Teil des Grundzustands ist als
  Ansible-Code festgehalten, der größere Teil nicht. Wo lohnt sich die Investition
  wirklich, wenn das Ganze später als Dienstleistung verkauft werden soll?
- **Die KI-Agenten:** Ist ein solches Multi-Agenten-Setup auf Produktivinfrastruktur
  überhaupt verantwortbar? Welche Leitplanken wären Pflicht?

---

*Hinweis: Alle Zugangsdaten, Schlüssel und Tokens sind aus diesem Dokument bewusst
entfernt. IP-Adressen sind private Netzbereiche.*
