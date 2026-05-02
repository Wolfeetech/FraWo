import xmlrpc.client

url = 'http://10.1.0.22:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'Wolf2024!Frawo'

def add_wolf_tasks():
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        print("[X] Auth failed")
        return
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Find the project ID for "🚀 Homeserver 2027: Masterplan" (We know it's ID 1)
    project_id = 1
    
    # We also want to assign it to Wolf. UID is Wolf's user ID.
    
    tasks = [
        {
            'name': '[MANUELL] Windows Hosts-Datei bereinigen (DNS Fix)',
            'description': '''<p><strong>Aufgabe:</strong> Die veralteten Tailscale-IPs (100.99.206.128) m&uuml;ssen aus der lokalen Windows hosts-Datei entfernt werden, damit die Namensaufl&ouml;sung (odoo.hs27.internal etc.) wieder korrekt funktioniert.</p>
            <p><strong>Schritte:</strong></p>
            <ol>
                <li>Notepad als Administrator starten.</li>
                <li>Datei <code>C:\\Windows\\System32\\drivers\\etc\\hosts</code> &ouml;ffnen.</li>
                <li>Alle Zeilen, die mit <code>100.99.206.128</code> beginnen, l&ouml;schen oder mit <code>#</code> auskommentieren.</li>
                <li>Speichern und in der Kommandozeile <code>ipconfig /flushdns</code> ausf&uuml;hren.</li>
            </ol>
            <p><strong>Definition of Done (DoD):</strong> <code>ping odoo.hs27.internal</code> auf dem StudioPC l&ouml;st automatisch die korrekte Tailscale-IP (100.82.26.53) oder IPv6 auf.</p>''',
            'project_id': project_id,
            'user_ids': [(4, uid)], # Assign to Wolf
            'stage_id': 37 # Stage: Dringend
        },
        {
            'name': '[MANUELL] AzuraCast Station zu "FraWo Funk" umbenennen',
            'description': '''<p><strong>Aufgabe:</strong> Das finale Rebranding des Radio-Nodes in der AzuraCast Web-UI durchf&uuml;hren, da die Code-Agenten keinen Admin-Zugang zum Webinterface haben.</p>
            <p><strong>Schritte:</strong></p>
            <ol>
                <li>Im Browser <code>https://radio.yourparty.tech</code> &ouml;ffnen und einloggen.</li>
                <li>In die Stations-Verwaltung von "Radio4yourparty" gehen.</li>
                <li>Den Namen offiziell zu "FraWo Funk" &auml;ndern.</li>
                <li>Sicherstellen, dass der Shortcode (falls ver&auml;ndert) mit dem Website-Player synchronisiert wird (aktuell: <code>radio.yourparty</code>).</li>
            </ol>
            <p><strong>Definition of Done (DoD):</strong> Der öffentliche Stream tr&auml;gt den Namen "FraWo Funk" in den Metadaten und spielt nahtlos auf <code>frawo-tech.de</code>.</p>''',
            'project_id': project_id,
            'user_ids': [(4, uid)],
            'stage_id': 8 # Stage: Today
        },
        {
            'name': '[MANUELL] OpenClaw Surface Go Client-Architektur festlegen',
            'description': '''<p><strong>Aufgabe:</strong> Konzeption, wie das Surface Go netzwerkbasiert mit dem zentralen OpenClaw-Agenten kommuniziert.</p>
            <p><strong>Schritte:</strong></p>
            <ol>
                <li>Entscheiden: Nutzt das Surface Go eine SSH-Remote-Session (z.B. VS Code Remote) zum Proxmox-Host/CT100?</li>
                <li>Oder soll eine dedizierte Web-UI (z.B. Open WebUI / lokaler Chatbot-Client) bereitgestellt werden, die API-Calls an den Backend-Agenten schickt?</li>
                <li>Tailscale auf dem Surface Go verifizieren, um die sichere Kommunikation "hinter" der UCG zu gew&auml;hrleisten.</li>
            </ol>
            <p><strong>Definition of Done (DoD):</strong> Die Ziel-Architektur f&uuml;r das Surface Go ist dokumentiert und freigegeben, sodass die Agenten die Backend-Prozesse auf dem Homeserver einrichten k&ouml;nnen.</p>''',
            'project_id': project_id,
            'user_ids': [(4, uid)],
            'stage_id': 8 # Stage: Today
        }
    ]

    for t in tasks:
        new_task = models.execute_kw(db, uid, password, 'project.task', 'create', [t])
        print(f"Created Task ID {new_task} for Wolf: {t['name']}")

if __name__ == "__main__":
    add_wolf_tasks()
