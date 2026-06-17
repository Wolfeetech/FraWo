# Odoo Shell Script to update task 452 (Surface Go Integration)
task = env['project.task'].browse(452)
if not task.exists():
    print("Error: Task 452 does not exist!")
else:
    task.write({
        'name': '📱 Surface Go: Mobiler Desktop & Steuerung für den Event-Pi',
        'description': """<h2>📱 Surface Go Integration als Mobiler Desktop</h2>
<p><strong>Ziel:</strong> Nutzung des Surface Go als mobiles Bedien- und Kontroll-Panel für den Event-Pi im Koffer (Steuerung von REW, QLC+, Companion und MPD).</p>

<h3>🔌 Verbindung zum Koffer-Netzwerk</h3>
<ol>
  <li>Verbinde das Surface Go per WLAN mit dem Koffer-AP <strong>"FraWo-Event-Net"</strong>.</li>
  <li>Das Surface Go erhält automatisch eine IP per DHCP vom Raspberry Pi (aus dem Bereich <code>192.168.50.x</code>).</li>
</ol>

<h3>🖥️ 1. Zugriff auf den Desktop (VNC / noVNC)</h3>
<p>Da der Pi den Bildschirm `:0` (HDMI) per VNC spiegelt, siehst du auf dem Surface Go exakt das gleiche Bild wie auf dem HDMI-Bildschirm an der Wand. Du kannst den Pi über zwei Wege steuern:</p>
<ul>
  <li><strong>Web-Variante (Ohne Installation - noVNC):</strong><br>
      Öffne einfach einen Webbrowser (z.B. Edge oder Chrome) und gehe auf:<br>
      <a href="http://10.3.0.8:6080/vnc.html" target="_blank"><strong>http://10.3.0.8:6080/vnc.html</strong></a> (bzw. <code>http://192.168.50.1:6080/vnc.html</code> im Koffer-LAN).<br>
      Hier kannst du REW und QLC+ direkt per Touch und Tastatur im Browser steuern.</li>
  <li><strong>Native App-Variante (Bessere Performance &amp; Touch):</strong><br>
      Installiere einen schlanken VNC Viewer auf dem Surface Go (z.B. <strong>TightVNC Viewer</strong> oder <strong>RealVNC Viewer</strong>).<br>
      Verbinde dich mit der Adresse: <strong><code>10.3.0.8:5900</code></strong> (bzw. <code>192.168.50.1:5900</code>).<br>
      Das bietet minimale Latenz und fühlt sich an wie ein nativer lokaler Desktop.</li>
</ul>

<h3>🎵 2. Audio-Wiedergabe &amp; Kuration (MPD Client)</h3>
<p>Um das Surface Go als professionelles Musik-Wiedergabegerät zu nutzen, greifen wir auf den <strong>Music Player Daemon (MPD)</strong> zu:</p>
<ul>
  <li>Installiere das Open-Source-Programm <strong>Cantata</strong> auf dem Surface Go (ein hervorragender, touch-freundlicher MPD-Client für Windows).</li>
  <li>Richte in Cantata eine Verbindung zum Pi ein: Host = <code>10.3.0.8</code> (bzw. <code>192.168.50.1</code>), Port = <code>6600</code>.</li>
  <li>Du kannst nun die gesamte Musikbibliothek auf dem Pi durchsuchen, Playlists erstellen und Songs abspielen. Der Ton wird latenzfrei über die PreSonus Studio 24c ausgegeben.</li>
</ul>

<h3>🎛️ 3. Web-Dienste auf dem Surface Go</h3>
<p>Folgende Web-Links können auf dem Surface Go als Verknüpfung hinterlegt werden:</p>
<table style="width:100%; border-collapse:collapse; font-family:sans-serif; margin-bottom:20px;">
  <thead>
    <tr style="background-color:#1e293b; color:#ffffff; text-align:left;">
      <th style="padding:10px; border:1px solid #cbd5e1;">Dienst</th>
      <th style="padding:10px; border:1px solid #cbd5e1;">Adresse im Koffer-LAN</th>
      <th style="padding:10px; border:1px solid #cbd5e1;">Zweck</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">QLC+ Web-Console</td>
      <td style="padding:10px; border:1px solid #e2e8f0;"><code>http://192.168.50.1:9999</code></td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Webbasierte Schieberegler und Buttons zur Lichtsteuerung (sehr gut für Touch).</td>
    </tr>
    <tr>
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">Bitfocus Companion</td>
      <td style="padding:10px; border:1px solid #e2e8f0;"><code>http://192.168.50.1:8000</code></td>
      <td style="padding:10px; border:1px solid #e2e8f0;">Triggern von System-Befehlen, Stream-Start, Audio-Routing usw.</td>
    </tr>
    <tr style="background-color:#f8fafc;">
      <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">AzuraCast Radio</td>
      <td style="padding:10px; border:1px solid #e2e8f0;"><code>http://192.168.50.1</code></td>
      <td style="padding:10px; border:1px solid #e2e8f0;">DJ-Verwaltung, Musik-Upload und automatische Playlist-Kuration.</td>
    </tr>
  </tbody>
</table>

<p>📝 <i>Status: Diese Integrationsanleitung wurde direkt in Odoo hinterlegt, um den Onboarding-Workflow für das Surface Go zu dokumentieren.</i></p>"""
    })
    print("Task 452 successfully updated!")
