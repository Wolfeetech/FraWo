import requests
import json

base_url = "https://funk.frawo-tech.de/api"
api_key = "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c"
station_id = 1

# Try both X-API-Key and Authorization headers just to be sure
headers = {
    "X-API-Key": api_key
}

print(f"Testing API Key on {base_url}/station/{station_id}/playlists...")
try:
    response = requests.get(f"{base_url}/station/{station_id}/playlists", headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("🎉 SUCCESS! Playlists retrieved:")
        for pl in response.json():
            print(f"- ID: {pl.get('id')}, Name: {pl.get('name')}, Type: {pl.get('type')}, Enabled: {pl.get('is_enabled')}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"💥 Error making API request: {str(e)}")
