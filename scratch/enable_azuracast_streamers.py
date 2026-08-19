import requests
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

AC_API_KEY = os.getenv('AZURACAST_API_KEY', '__ROTATED_SECRET__')
AC_URL = os.getenv('AZURACAST_URL', 'https://funk.frawo-tech.de').rstrip('/')
if AC_URL.endswith('/api'):
    AC_URL = AC_URL[:-4]
    
STATION_ID = 1
HEADERS = {"X-API-Key": AC_API_KEY}

# Hole aktuelle Config
r = requests.get(f"{AC_URL}/api/admin/stations", headers=HEADERS)
stations = r.json()
station = stations[0]

# Ändere den Wert
station['enable_streamers'] = True

# Speichern
r_put = requests.put(f"{AC_URL}/api/admin/stations/{STATION_ID}", headers=HEADERS, json=station)
if r_put.status_code in [200, 201]:
    print("Streamer/DJs erfolgreich für die Station aktiviert!")
else:
    print(f"Fehler: {r_put.status_code} - {r_put.text}")
    # Fallback endpoint try
    r_put2 = requests.put(f"{AC_URL}/api/admin/station/{STATION_ID}", headers=HEADERS, json=station)
    if r_put2.status_code in [200, 201]:
         print("Streamer/DJs erfolgreich für die Station aktiviert (Fallback-Endpoint)!")
    else:
         print(f"Fehler 2: {r_put2.status_code} - {r_put2.text}")
