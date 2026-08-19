import requests

base_url = "https://funk.frawo-tech.de/api"
email = "wolf@frawo-tech.de"
password = "__ROTATED_SECRET__"

session = requests.Session()

# In AzuraCast, login usually happens via POST /api/frontend/account/login
payload = {
    "username": email,
    "password": password
}
response = session.post(f"{base_url}/frontend/account/login", json=payload)
print(f"Login Status Code: {response.status_code}")
if response.status_code == 200:
    print("Login success:", response.json())
    
    # Now that we have a session, let's try getting playlists
    station_id = 1
    pl_resp = session.get(f"{base_url}/station/{station_id}/playlists")
    print(f"Playlists Status Code: {pl_resp.status_code}")
    if pl_resp.status_code == 200:
        print("Playlists:", pl_resp.json())
        
    # Get API keys
    ak_resp = session.get(f"{base_url}/admin/api-keys")
    print(f"API Keys Status Code: {ak_resp.status_code}")
    if ak_resp.status_code == 200:
        print("API Keys:", ak_resp.json())
        
    # Create an API key
    key_payload = {
        "comment": "FraWo Odoo Sync"
    }
    create_resp = session.post(f"{base_url}/admin/api-keys", json=key_payload)
    print(f"Create API Key Status Code: {create_resp.status_code}")
    if create_resp.status_code == 200:
        print("Created Key:", create_resp.json())
else:
    print(response.text)
