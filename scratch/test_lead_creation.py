import requests
import re
import sys

BASE_URL = "https://www.frawo-tech.de"

print(f"[*] Making GET request to {BASE_URL}/contactus to obtain CSRF token and session cookie...")
session = requests.Session()
try:
    res = session.get(f"{BASE_URL}/contactus", verify=True)
except Exception as e:
    print(f"[FAIL] GET failed: {e}")
    sys.exit(1)

if res.status_code != 200:
    print(f"[FAIL] GET /contactus failed with status code {res.status_code}")
    sys.exit(1)

# Extract CSRF token using regex
csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.text)
if not csrf_match:
    # Try alternate formatting
    csrf_match = re.search(r'value="([^"]+)"\s+name="csrf_token"', res.text)

if not csrf_match:
    print("[FAIL] CSRF token not found in the HTML!")
    # Save a snippet to check
    with open("contactus_raw.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("Saved contactus_raw.html for inspection.")
    sys.exit(1)

csrf_token = csrf_match.group(1)
print(f"[OK] Found CSRF Token: {csrf_token}")

headers = {
    "Referer": f"{BASE_URL}/contactus",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "X-Requested-With": "XMLHttpRequest" # Some controllers expect this for website forms
}

# 1. Test Standard Fields
print("\n[*] Attempting form submission with STANDARD fields only...")
# Odoo website forms expects a model name in data attribute, and standard POST
# But wait! In Odoo 17, website forms controller endpoint /website/form/
# actually expects the data to be posted to /website/form/
# and the form itself should define the model:
data_standard = {
    "csrf_token": csrf_token,
    "contact_name": "Testbot Antigravity Standard",
    "email_from": "antigravity-std@frawo-tech.de",
    "phone": "+49123456789",
    "name": "Smart Home Integration Test Standard",
    "description": "This is a test lead created programmatically by Antigravity."
}

# In Odoo website forms, the model name is passed as part of the POST or URL
# For `/website/form/`, it requires model_name inside the POST data if it's not in the URL path, or it looks for the referrer's form data!
# Actually, Odoo's website form controller expects 'model_name': 'crm.lead' in the POST parameters!
data_standard["model_name"] = "crm.lead"

res_post = session.post(f"{BASE_URL}/website/form/", data=data_standard, headers=headers)
print(f"Status Code: {res_post.status_code}")
print(f"Response URL: {res_post.url}")
print(f"Response text:\n{res_post.text}")

# 2. Test Custom Fields
print("\n[*] Attempting form submission WITH non-standard fields ('timeline' and 'privacy')...")
data_with_custom = {
    "csrf_token": csrf_token,
    "model_name": "crm.lead",
    "contact_name": "Testbot Antigravity Custom",
    "email_from": "antigravity-custom@frawo-tech.de",
    "phone": "+49123456789",
    "name": "Smart Home Custom Fields Test",
    "timeline": "Juli 2026",
    "description": "Testing if custom fields crash the submission.",
    "privacy": "on"
}

res_post_custom = session.post(f"{BASE_URL}/website/form/", data=data_with_custom, headers=headers)
print(f"Status Code with custom fields: {res_post_custom.status_code}")
print(f"Response text:\n{res_post_custom.text}")
