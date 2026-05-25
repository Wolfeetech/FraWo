import requests
import re

base_url = "https://funk.frawo-tech.de"
email = "wolf@frawo-tech.de"
password = "11Vaudeville!!"

session = requests.Session()

# 1. Get the login page to extract CSRF token
print("1. Fetching login page...")
login_page = session.get(f"{base_url}/login")
print(f"Status: {login_page.status_code}")

# Find CSRF token using regex
csrf_match = re.search(r'name=["\']csrf["\']\s+value=["\']([^"\']+)["\']', login_page.text)
if not csrf_match:
    # Try another pattern
    csrf_match = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']csrf["\']', login_page.text)

if not csrf_match:
    print("Could not find CSRF token using regex. Page snippet:")
    print(login_page.text[:1000])
    csrf_token = None
else:
    csrf_token = csrf_match.group(1)
    print(f"Found CSRF: {csrf_token}")

if csrf_token:
    # 2. Post login
    payload = {
        "username": email,
        "password": password,
        "csrf": csrf_token
    }
    print("2. Attempting login...")
    login_resp = session.post(f"{base_url}/login", data=payload, allow_redirects=False)
    print(f"Login Response Status: {login_resp.status_code}")
    print(f"Headers: {dict(login_resp.headers)}")
    
    if login_resp.status_code in [302, 303]:
        redirect_url = login_resp.headers.get('Location')
        print(f"Login successful! Redirected to {redirect_url}")
        
        # Follow the redirect to establish session properly
        dashboard = session.get(redirect_url if redirect_url.startswith('http') else f"{base_url}{redirect_url}")
        print(f"Dashboard status: {dashboard.status_code}")
        
        # 3. Access API to get playlists
        station_id = 1
        pl_resp = session.get(f"{base_url}/api/station/{station_id}/playlists")
        print(f"Playlists API: {pl_resp.status_code}")
        if pl_resp.status_code == 200:
            print("Playlists:")
            for pl in pl_resp.json():
                print(f"- ID: {pl.get('id')}, Name: {pl.get('name')}, Type: {pl.get('type')}, Enabled: {pl.get('is_enabled')}")
        else:
            print("Playlists API response:", pl_resp.text)
            
        # Try to retrieve existing API keys
        ak_resp = session.get(f"{base_url}/api/admin/api-keys")
        print(f"Admin API keys status: {ak_resp.status_code}")
        
        # Let's see if we can create a token!
        # In AzuraCast, we can generate a new token via POST /api/admin/api-key or /api/admin/api-keys
        # Let's check if there is an endpoint like POST /api/admin/api-keys
        # Wait, let's try POST to create a key
        create_payload = {
            "comment": "FraWo Odoo Sync Auto"
        }
        create_resp = session.post(f"{base_url}/api/admin/api-keys", json=create_payload)
        print(f"Create API Key Status: {create_resp.status_code}")
        if create_resp.status_code in [200, 201]:
            print("Created Key Successfully:")
            print(create_resp.json())
        else:
            print("Create Key failed:", create_resp.text)
    else:
        print("Login failed. Status code not redirect.")
        print(login_resp.text[:1000])
