# StudioPC Smart-Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Touchscreen (stock-pve, Aufgabe #1039) und Wolfs Surface Go zeigen zusätzlich zum Dashboard einen unabhängigen virtuellen zweiten Monitor des StudioPC an, den beide gleichzeitig ansehen/bedienen können — ohne den Fernseher (Monitor 1) zu beeinflussen.

**Architecture:** UltraVNC (aktiv gepflegt, hat eingebaute Unterstützung für virtuelle Displays über die eigene DDEngine/Mirror-Driver-Komponente — keine zusätzliche Dritt-Treiber nötig) läuft als Windows-Dienst auf dem StudioPC, teilt ausschließlich den virtuellen Monitor, lauscht nur auf der Tailscale-IP. Touchscreen bekommt einen zusätzlichen noVNC-Reiter im bestehenden Chromium-Kiosk. Surface Go nutzt den TigerVNC-Viewer (Client-seitig aktiv gepflegt, im Unterschied zum unmaintainten winvnc-Server).

**Tech Stack:** UltraVNC Server 1.4+ (Windows), TigerVNC Viewer (Windows-Client), noVNC (HTML5, im Chromium-Kiosk).

**Spec:** `DOCS/superpowers/specs/2026-08-27-studiopc-smartscreen-design.md`

## Global Constraints

- Kein neuer offener Port am Router — Erreichbarkeit ausschließlich über Tailscale (100.98.31.60), passt zur bestehenden FraWo-Sicherheitslinie.
- Fernseher (Monitor 1, physische Ausgabe) darf durch keinen Schritt beeinflusst werden.
- Beide Geräte (Touchscreen, Surface Go) müssen gleichzeitig verbunden sein können und denselben Inhalt sehen (geteilte Sitzung, nicht zwei getrennte virtuelle Displays).
- Nur quelloffene Software (UltraVNC: GPL, TigerVNC: GPL, noVNC: MPL-2.0).
- VNC-Passwort geht in Vaultwarden, nicht ins Repo (analog #815-Konvention).

---

### Task 1: UltraVNC-Server mit virtuellem Display auf StudioPC installieren

**Wer führt aus:** Wolf (Windows-Treiberinstallation braucht Admin-Rechte/UAC-Bestätigung — das kann die Sitzung hier nicht per Fernzugriff klicken).

**Dateien:** keine (Systeminstallation, kein Repo-Bezug)

- [ ] **Schritt 1: UltraVNC herunterladen und installieren**

  Wolf öffnet https://uvnc.com/downloads/ultravnc.html, lädt die aktuelle 64-Bit-Version (mind. 1.4.x) herunter und startet den Installer. Bei der Komponentenauswahl **"MS-Logon"** NICHT aktivieren (unnötig komplex für diesen Anwendungsfall), aber **"Register as Service"** UND die **DDEngine/Mirror-Driver-Komponente** für virtuelle Displays aktivieren (Installer nennt das ggf. "Virtual Display Driver" oder "DDEngine" in der Komponentenliste).

- [ ] **Schritt 2: Installation bestätigen**

  Nach der Installation prüft die Session hier per PowerShell, ob der Dienst existiert:
  ```powershell
  Get-Service -Name "uvnc_service" -ErrorAction SilentlyContinue
  ```
  Erwartet: Dienst vorhanden (Status kann `Stopped` sein, das ist ok — Konfiguration folgt in Task 2).

- [ ] **Schritt 3: Commit**

  Kein Commit nötig (reine Systeminstallation, keine Repo-Datei betroffen).

---

### Task 2: UltraVNC konfigurieren — nur virtuelles Display, nur Tailscale, Passwort

**Wer führt aus:** Die Session hier (Textdatei bearbeiten braucht keine Admin-Rechte), Wolf startet danach den Dienst neu (Dienst-Neustart braucht Admin-Rechte).

**Dateien:**
- Modify: `C:\Program Files\uvnc bvba\UltraVNC\ultravnc.ini`

**Interfaces:**
- Konsumiert: nichts (erster Konfigurationsschritt)
- Erzeugt: laufender UltraVNC-Dienst, erreichbar auf `100.98.31.60:5900`, teilt nur das virtuelle Display

- [ ] **Schritt 1: Aktuelle Tailscale-IP bestätigen**

  ```powershell
  (Get-NetIPAddress -InterfaceAlias "Tailscale*").IPAddress
  ```
  Erwartet: `100.98.31.60` (aus NOW.md bekannt — falls abweichend, in den folgenden Schritten die tatsächliche IP verwenden).

- [ ] **Schritt 2: `ultravnc.ini` anpassen**

  Folgende Werte setzen (Datei mit dem Edit-Tool bearbeiten, nicht händisch — Tippfehler in dieser Datei führen zu einem VNC-Server, der lautlos falsch lauscht):
  ```ini
  [admin]
  passwd=<wird in Schritt 3 über den VNC-Passwort-Dialog gesetzt, nicht hier im Klartext>
  [ultravnc]
  UseDsmPlugin=0
  DDEngineDriver=1
  UseVirtualDisplay=1
  DisableTrayIcon=0
  QuerySetting=0
  LoopbackOnly=0
  AllowLoopback=1
  BlockRemoteInput=0
  BlockLocalInput=0
  ; Nur an die Tailscale-Karte binden, nicht an alle Netzwerkkarten:
  Interface=100.98.31.60
  PortNumber=5900
  ```
  Die genauen Schlüsselnamen können je UltraVNC-Version leicht abweichen (`Interface=` bzw. `AllowedHosts=100.98.31.60/32` ist die Alternative, falls `Interface=` in der installierten Version nicht existiert — beides einmal gegenprüfen, siehe Schritt 4).

- [ ] **Schritt 3: VNC-Passwort setzen**

  Wolf öffnet den UltraVNC-Server-Eigenschaften-Dialog (Systray-Symbol → "Admin Properties"), setzt unter "VNC Password" ein neues, nirgends sonst verwendetes Passwort, trägt es danach in Vaultwarden ein (nicht ins Repo, nicht in den Chat).

- [ ] **Schritt 4: Dienst neu starten und Bindung prüfen**

  Wolf (braucht Admin-Rechte):
  ```powershell
  Restart-Service uvnc_service
  ```
  Die Session hier prüft danach, dass NUR die Tailscale-IP lauscht, nicht 0.0.0.0:
  ```powershell
  Get-NetTCPConnection -LocalPort 5900 -State Listen | Select-Object LocalAddress
  ```
  Erwartet: `100.98.31.60`, NICHT `0.0.0.0` oder die normale LAN-IP. Falls doch `0.0.0.0` erscheint, existiert der `Interface=`-Schlüssel in dieser UltraVNC-Version nicht — dann stattdessen `AllowedHosts=100.98.31.60/32;100.1.0.128/32` in der ini setzen (IP-basierte Zugriffsbeschränkung statt Interface-Bindung) und Schritt 4 wiederholen.

- [ ] **Schritt 5: Virtuelles Display bestätigen**

  Wolf prüft in den Windows-Anzeigeeinstellungen (Rechtsklick Desktop → Anzeigeeinstellungen), dass ein zusätzlicher Monitor 2 erscheint, sobald sich ein Viewer verbindet (UltraVNC mit `UseVirtualDisplay=1` erzeugt ihn bedarfsweise) — Monitor 1 (Fernseher) bleibt unverändert in Auflösung/Ausgabe.

---

### Task 3: "StudioPC"-Reiter im bestehenden Touchscreen-Kiosk (noVNC)

**Wer führt aus:** Die Session hier, per SSH auf stock-pve (etabliertes Muster aus dieser Sitzung).

**Dateien:**
- Auf stock-pve suchen und ändern: die Kiosk-Startseite/das Lovelace- bzw. Kiosk-HTML, das Aufgabe #1039 bereits anzeigt (Pfad zuerst mit `find` ermitteln, nicht raten).

- [ ] **Schritt 1: Bestehende Kiosk-Konfiguration finden**

  ```bash
  ssh root@10.1.0.128 "grep -rl 'kiosk-frawo\|chromium.*kiosk' /etc /home /root 2>/dev/null | head -10"
  ```
  Ziel: die Datei/den Dienst finden, der Chromium mit welcher URL startet (systemd-Unit oder Autostart-Skript des `kiosk`-Users).

- [ ] **Schritt 2: noVNC als statische Dateien + websockify bereitstellen**

  Kein Docker-Image verwenden (die meisten fertigen `novnc`-Images bündeln einen eigenen VNC-Server, den wir nicht brauchen und der mit UltraVNC kollidieren würde). Stattdessen **noVNC direkt als statische Dateien**: das offizielle `novnc/noVNC`-Repository enthält `vnc.html`, das sich mit `?host=localhost&port=6080` aufrufen lässt und selbst nur einen WebSocket-Proxy (`websockify`) braucht, keinen eigenen VNC-Server.

  Der Touchscreen läuft laut NOW.md direkt auf dem stock-pve-Host selbst (nicht in einem Container) — Installation direkt dort:
  ```bash
  ssh root@10.1.0.128 "apt-get install -y git python3-pip && pip3 install websockify && git clone --depth 1 https://github.com/novnc/noVNC.git /opt/novnc"
  ```
  Falls Schritt 1 stattdessen einen Container als Kiosk-Träger ergibt, denselben Befehl per `pct exec <CT_ID> -- bash -c '...'` in diesem Container ausführen statt direkt auf dem Host.

- [ ] **Schritt 3: websockify-Dienst einrichten**

  systemd-Unit anlegen, die `websockify` dauerhaft von einem lokalen Port (z. B. 6080) zu `100.98.31.60:5900` weiterleitet:
  ```ini
  [Unit]
  Description=noVNC websockify Bruecke zum StudioPC
  After=network-online.target

  [Service]
  ExecStart=/usr/local/bin/websockify 6080 100.98.31.60:5900
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```
  Als `/etc/systemd/system/novnc-studiopc-bridge.service` anlegen, dann:
  ```bash
  ssh root@10.1.0.128 "systemctl daemon-reload && systemctl enable --now novnc-studiopc-bridge.service && systemctl is-active novnc-studiopc-bridge.service"
  ```
  Erwartet: `active`.

- [ ] **Schritt 4: Kiosk-Seite um "StudioPC"-Reiter erweitern**

  Die in Schritt 1 gefundene Kiosk-Startseite bekommt einen zusätzlichen Knopf/Link zu `http://localhost:6080/vnc.html?host=localhost&port=6080&autoconnect=true&resize=scale`. Genaue Änderung hängt vom in Schritt 1 gefundenen Aufbau ab (eigenes HTML vs. Home-Assistant-Dashboard-Karte) — bei Home-Assistant-Dashboard: eine `iframe`-Karte mit dieser URL zur bestehenden `kiosk-frawo`-Übersicht hinzufügen; bei eigenem HTML: einen zweiten `<a>`/Tab analog zum bestehenden Muster einfügen.

- [ ] **Schritt 5: Verifizieren**

  Am physischen Touchscreen (oder per Screenshot-Beschreibung von Wolf) bestätigen: neuer Reiter sichtbar, Tippen darauf zeigt den virtuellen StudioPC-Monitor, Tippen/Wischen bewegt den Mauszeiger dort.

- [ ] **Schritt 6: Commit**

  ```bash
  cd "/c/Users/StudioPC/FraWo" && git add DOCS/OPERATIONS/ 2>/dev/null; git status --short
  ```
  Falls die Kiosk-Konfiguration NICHT im Repo liegt (reine Server-Konfiguration), stattdessen einen kurzen Vermerk in `NOW.md` unter der Touchscreen-Kiosk-Zeile ergänzen und committen.

---

### Task 4: TigerVNC-Viewer auf dem Surface Go einrichten

**Wer führt aus:** Wolf (eigenständiges Gerät, kein Fernzugriff von dieser Sitzung aus möglich).

- [ ] **Schritt 1: TigerVNC-Viewer herunterladen**

  Wolf lädt auf dem Surface Go die portable Windows-Version von https://github.com/TigerVNC/tigervnc/releases (aktuelle Version, `*.exe`-Installer oder portable `vncviewer.exe`) herunter — kein Repo-Bezug, keine Installation von dieser Sitzung aus möglich.

- [ ] **Schritt 2: Verbindung einrichten**

  Wolf startet `vncviewer.exe`, trägt `100.98.31.60:5900` als Ziel ein, beim ersten Verbinden das in Task 2 Schritt 3 gesetzte Passwort eingeben, "Verbindung speichern" für künftige Starts.

- [ ] **Schritt 3: Verifizieren**

  Wolf bestätigt: Surface Go zeigt denselben virtuellen Monitor wie der Touchscreen, Berührung/Maus funktioniert.

---

### Task 5: Gleichzeitigkeit end-to-end prüfen

**Wer führt aus:** Wolf, mit Unterstützung der Session hier für serverseitige Prüfungen.

- [ ] **Schritt 1: Beide Geräte gleichzeitig verbinden**

  Touchscreen UND Surface Go gleichzeitig mit dem virtuellen Monitor verbinden. Erwartet laut Spec: beide sehen denselben Inhalt in Echtzeit (nicht zwei getrennte virtuelle Displays).

- [ ] **Schritt 2: Falls getrennte Displays entstehen — korrigieren**

  Falls jedes Gerät sein eigenes virtuelles Display bekommt (UltraVNCs Standardverhalten bei `UseVirtualDisplay=1` kann das je nach Version tun), in `ultravnc.ini` `NumberOfVirtualDisplays=1` setzen bzw. `PortNumber`/`Multiviewer`-Einstellung so anpassen, dass sich neue Verbindungen an die BESTEHENDE Sitzung anhängen statt eine neue zu erzeugen. Nach jeder Änderung Task 2 Schritt 4 (Dienst neu starten, Bindung prüfen) wiederholen.

- [ ] **Schritt 3: Von außerhalb des Tailnets testen (negative Probe)**

  Ein Gerät ohne Tailscale-Zugehörigkeit (z. B. normales Heim-WLAN) versucht `100.98.31.60:5900` zu erreichen — erwartet: **kein** Verbindungsaufbau. Bestätigt, dass nicht versehentlich auf allen Netzwerkkarten gelauscht wird (Falle aus Task 2 Schritt 4).

- [ ] **Schritt 4: PC-Neustart-Test**

  StudioPC neu starten, prüfen dass `uvnc_service` automatisch wieder läuft, ohne dass Wolf manuell eingreifen muss.

- [ ] **Schritt 5: Odoo aktualisieren**

  Aufgabe zum StudioPC-Smart-Screen in Odoo (Projekt 105) anlegen/aktualisieren, Stage auf "Erledigt" setzen sobald alle Schritte bestätigt sind.
