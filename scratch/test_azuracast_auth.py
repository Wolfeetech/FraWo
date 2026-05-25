import requests

base_url = "https://funk.frawo-tech.de/api"
email = "wolf@frawo-tech.de"
password = "11Vaudeville!!"
station_id = 1

# Try to get playlists (requires auth)
response = requests.get(f"{base_url}/station/{station_id}/playlists", auth=(email, password))
print(f"Playlists Status Code: {response.status_code}")
if response.status_code == 200:
    print("Playlists:", response.json())
else:
    print(response.text)

# Try getting API keys
response = requests.get(f"{base_url}/admin/api-keys", auth=(email, password))
print(f"API Keys Status Code: {response.status_code}")

