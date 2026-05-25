import os
import xmlrpc.client
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("=== FraWo Funk: Odoo -> AzuraCast DJ Sync ===")
    
    # 1. Konfiguration laden
    env_path = Path.home() / '.ai-tools-shared' / '.env'
    load_dotenv(env_path)

    ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
    ODOO_DB = 'FraWo_GbR'
    ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

    ac_url_raw = os.getenv('AZURACAST_URL', 'https://funk.frawo-tech.de').rstrip('/')
    if ac_url_raw.endswith('/api'):
        ac_url_raw = ac_url_raw[:-4]
        
    AC_URL = ac_url_raw
    AC_API_KEY = os.getenv('AZURACAST_API_KEY', 'b9a8e51be992498c:c55ea5c67b8ff16bffbed39004b056b1')
    STATION_ID = 1
    AC_HEADERS = {"X-API-Key": AC_API_KEY}

    print("Verbinde mit Odoo...")
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        odoo_users = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'search_read', 
            [[('share', '=', False)]], 
            {'fields': ['id', 'name', 'login']}
        )
        print(f"{len(odoo_users)} interne Benutzer in Odoo gefunden.")
    except Exception as e:
        print(f"Fehler bei der Odoo-Verbindung: {e}")
        return

    print("Verbinde mit AzuraCast...")
    try:
        r = requests.get(f"{AC_URL}/api/station/{STATION_ID}/streamers", headers=AC_HEADERS, timeout=10)
        r.raise_for_status()
        ac_streamers = r.json()
        ac_usernames = [s['streamer_username'] for s in ac_streamers]
        print(f"{len(ac_streamers)} existierende DJ-Accounts in AzuraCast gefunden.")
    except Exception as e:
        print(f"Fehler bei der AzuraCast-Verbindung: {e}")
        return

    print("\nStarte Synchronisation...")
    for user in odoo_users:
        name = user['name']
        email = user['login']
        
        # Zeichensatz-Probleme (z.B. Emojis in Odoo Namen) bei der Ausgabe ignorieren
        safe_name = name.encode('ascii', 'ignore').decode('ascii')
        
        dj_username = email.split('@')[0].lower()
        dj_username = "".join(c for c in dj_username if c.isalnum())
        
        if dj_username == 'admin' or not dj_username:
            continue
            
        dj_password = "FrawoDJ2026!"
        
        if dj_username in ac_usernames:
            print(f" [SKIP] DJ '{dj_username}' existiert bereits in AzuraCast.")
        else:
            print(f" [CREATE] Lege DJ '{dj_username}' ({safe_name}) in AzuraCast an...")
            
            # Um den "station_id must not be accessed before initialization" Fehler zu fixen,
            # senden wir die ID direkt im Body mit, wie es manche AzuraCast-Versionen fordern.
            payload = {
                "streamer_username": dj_username,
                "streamer_password": dj_password,
                "display_name": name,
                "is_active": True,
                "station_id": STATION_ID
            }
            
            r = requests.post(f"{AC_URL}/api/station/{STATION_ID}/streamers", headers=AC_HEADERS, json=payload, timeout=10)
            if r.status_code in [200, 201]:
                print(f"    -> Erfolgreich angelegt!")
            else:
                print(f"    -> Fehler beim Anlegen: {r.status_code} - {r.text}")

    print("\nSynchronisation abgeschlossen!")

if __name__ == "__main__":
    main()
