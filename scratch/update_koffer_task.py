# Odoo Shell Script to update task 243
task = env['project.task'].browse(243)
if not task.exists():
    print("Error: Task 243 does not exist!")
else:
    task.write({
        'name': '[🤖+👤] 📻 Mobile Streaming-Station (VT-Koffer) — Setup & Einkaufsliste',
        'description': """<h2>📦 Mobile Streaming-Station (VT-Koffer)</h2>
<p><strong>Ziel:</strong> Portables, hochverfügbares Streaming- und Steuerungs-Setup in einem robusten Transportkoffer mit Raspberry Pi 4 als zentralem Hub (Ansible-gesteuert).</p>

<h3>🛠️ System-Architektur &amp; Features</h3>
<ul>
  <li><strong>LAN-Gateway &amp; Routing:</strong> Der Pi fungiert als DHCP- und DNS-Server im Koffer (IP 192.168.50.1).</li>
  <li><strong>VPN-Konnektivität:</strong> Automatischer Tailscale-Tunnel zurück zu CT 130 (100.x.x.x) für Remote-Zugriff und Audio-Relay.</li>
  <li><strong>Mess- &amp; Audiotechnik:</strong> Room EQ Wizard (REW) und MPD über PipeWire/xvfb/noVNC im Webbrowser.</li>
  <li><strong>Lichtsteuerung &amp; Video:</strong> QLC+ (DMX über Art-Net Node) und Bitfocus Companion (Stream Deck Steuerung).</li>
</ul>

<h3>🛒 Hardware-Einkaufsliste (Shopping List)</h3>
<p>Die Einkaufsliste ist nach Odoo Best Practice gegliedert und enthält alle notwendigen Add-ons zur Realisierung des Koffers:</p>

<table style="width:100%; border-collapse:collapse; font-family:sans-serif; margin-bottom:20px;">
  <thead>
    <tr style="background-color:#1e293b; color:#ffffff; text-align:left;">
      <th style="padding:10px; border:1px solid #cbd5e1;">Bereich</th>
      <th style="padding:10px; border:1px solid #cbd5e1;">Komponente / Bezeichnung</th>
      <th style="padding:10px; border:1px solid #cbd5e1;">Zweck / Details</th>
      <th style="padding:10px; border:1px solid #cbd5e1; text-align:center;">Status</th>
    </tr>
  </thead>
  <tbody>
    <!-- Core -->
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Core &amp; Power</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Raspberry Pi 4 Model B (8 GB RAM)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Zentrale Recheneinheit &amp; Gateway für alle Dienste.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#16a34a; font-weight:bold; text-align:center;">Vorhanden</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Core &amp; Power</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Raspberry Pi PoE+ HAT</td>
      <td style="padding:10px; border:1px solid #e2e8f0;"><b>Wichtig!</b> Ermöglicht die Stromversorgung des Pi direkt über den PoE-Switch im Koffer (spart Kabel &amp; Netzteile). Mit dem RPi 4 und diesem HAT läuft die Versorgung via Switch problemlos!</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Core &amp; Power</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Anker Nano II 45W / 65W USB-C</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Redundante / optionale Stromversorgung außerhalb des PoE-Betriebs.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Core &amp; Power</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">SanDisk Extreme Pro 64GB microSD</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Langlebiges &amp; schnelles OS-Medium (Ubuntu Server 24.04 LTS/26.04 LTS).</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    
    <!-- Network -->
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Network</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">TP-Link AC750 Travel Router (TL-WR902AC)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Dient als kompakter Access Point im AP-Modus für das Koffer-WLAN.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Network</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Managed Gigabit PoE+ Switch (z.B. Netgear GS305EP)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Speist Pi (via Hat) und DMX-Node; verbindet alle Netzwerk-Komponenten.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Network</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Neutrik EtherCON Chassis RJ45 (NE8FDP)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Robuster Netzwerk-Außenanschluss für Kabel-Verbindung zum Switch.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Network</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Cat.6a S/FTP Patchkabel (0.25m - 0.5m)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Kompakte, flexible Verkabelung aller Komponenten im Koffer.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>

    <!-- Audio -->
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Audio</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">PreSonus Studio 24c USB-C Interface</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">2x2 Audio-Interface für System-Messungen (REW) und Zuspieler.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#16a34a; font-weight:bold; text-align:center;">Vorhanden</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Audio</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">PreSonus Eris E3.5 Active Monitors</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Kompaktes Monitor-Paar für den Soundcheck und lokales Abhören.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Audio</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Fostex PC-1e(B) Volume Controller</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Passiver Lautstärkeregler zur schnellen Lautstärkekontrolle der Boxen.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Audio</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Line-Out Klinke auf XLR/Cinch Kabel-Set</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Verbindung von Interface zu Fostex Regler und Eris Boxen.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>

    <!-- DMX -->
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">DMX / Licht</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Wolfmix W1 DMX-Controller</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Standalone-Lichtsteuerung (wird per USB an Pi gekoppelt).</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#16a34a; font-weight:bold; text-align:center;">Vorhanden</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">DMX / Licht</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Art-Net / sACN DMX-Node (z.B. eDMX2 PRO)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Ethernet-zu-DMX Interface zur drahtgebundenen DMX-Verteilung.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">DMX / Licht</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Neutrik XLR 3-Pin / 5-Pin Chassis Connectors</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Robuste Außenbuchsen am Koffer für DMX-Out.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>

    <!-- Control & Video -->
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Control &amp; Video</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Elgato Stream Deck MK.2 (15 Tasten)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Hardware-Controller für Bitfocus Companion zur Steuerung aller Koffer-Dienste.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Control &amp; Video</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Elgato Cam Link 4K (USB HDMI Grabber)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">HDMI-Videoeingang zum Livestreamen von Kamerasignalen.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Control &amp; Video</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">HDMI &amp; Toslink Audio Extractor</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">HDMI Audio-Splitter zur separaten Audio-Verarbeitung.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>

    <!-- Case -->
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Case &amp; Mech</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Flightcase (z.B. Thomann Mix-Case)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Stabiles Transport-Case für die gesamte Technik.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Case &amp; Mech</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Maßgeschneidertes Hartschaum-Inlay (LD45)</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Gefräster Schaumstoff zur sicheren, rutschfesten Fixierung aller Geräte.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Case &amp; Mech</td>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:semibold; color:#2563eb;">Neutrik PowerCON Chassis Connector (Blue) + Kabel</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Verriegelbare 230V Koffer-Netzbuchse zur zentralen Stromzufuhr.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Case &amp; Mech</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Kompakte 4-fach Steckdosenleiste</td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Interne 230V Stromverteilung für Router/Switch/Boxen-Netzteile.</td>
      <td style="padding:10px; border:1px solid #e2e8f0; color:#ea580c; font-weight:bold; text-align:center;">Zu Kaufen</td>
    </tr>
  </tbody>
</table>

<p>📝 <i>Hinweis: Diese Liste wurde vollautomatisch nach Odoo Best Practice direkt im ERP-System hinterlegt.</i></p>"""
    })
    print("Task 243 successfully updated!")
