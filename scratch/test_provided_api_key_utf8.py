import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

base_url = "https://funk.frawo-tech.de/api"
api_key = "b9a8e51be992498c:c55ea5c67b8ff16bffbed39004b056b1"
station_id = 1

# Method 1: X-API-Key
print("--- Method 1: X-API-Key ---")
headers_x = {
    "X-API-Key": api_key,
    "Accept": "application/json"
}
try:
    response = requests.get(f"{base_url}/station/{station_id}/playlists", headers=headers_x, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Authorization Bearer
print("\n--- Method 2: Authorization Bearer ---")
headers_bearer = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}
try:
    response = requests.get(f"{base_url}/station/{station_id}/playlists", headers=headers_bearer, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
