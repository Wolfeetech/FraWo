import requests
import re
from bs4 import BeautifulSoup

base_url = "https://funk.frawo-tech.de"
email = "wolf@frawo-tech.de"
password = "__ROTATED_SECRET__"

session = requests.Session()

# 1. Get the login page to extract CSRF token
login_page = session.get(f"{base_url}/login")
soup = BeautifulSoup(login_page.text, 'html.parser')

# In AzuraCast, CSRF is usually in a hidden input named 'csrf' or similar, or in the JS
csrf_input = soup.find("input", {"name": "csrf"})
if csrf_input:
    csrf_token = csrf_input["value"]
else:
    # Try to find any input hidden
    inputs = soup.find_all("input", type="hidden")
    print("Hidden inputs:", inputs)
    csrf_token = inputs[0]["value"] if inputs else None

if not csrf_token:
    print("Could not find CSRF token.")
else:
    print(f"Found CSRF: {csrf_token}")
    
    # 2. Post login
    payload = {
        "username": email,
        "password": password,
        "csrf": csrf_token
    }
    # AzuraCast login is at /login
    login_resp = session.post(f"{base_url}/login", data=payload, allow_redirects=False)
    print(f"Login Response: {login_resp.status_code}")
    
    if login_resp.status_code in [302, 303]: # Redirect means success
        print("Login successful! Redirected to", login_resp.headers.get('Location'))
        
        # 3. Access API to get keys
        # We need to hit /api/admin/api-keys using the session
        # But wait, the API requires the CSRF token in headers if using session auth?
        # Actually, AzuraCast uses a session cookie for the web UI which also authenticates the API
        
        station_id = 1
        pl_resp = session.get(f"{base_url}/api/station/{station_id}/playlists")
        print(f"Playlists API: {pl_resp.status_code}")
        if pl_resp.status_code == 200:
            print("Playlists:", pl_resp.json())
            
        # Try to create API key directly
        # First, we might need a CSRF token for the API. AzuraCast handles this via the frontend API
        # Often the easiest way to generate an API key if we have SSH is via the CLI.
    else:
        print("Login failed.")
        print(login_resp.text)
