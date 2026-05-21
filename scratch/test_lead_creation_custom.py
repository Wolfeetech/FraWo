import requests
import re
import sys

BASE_URL = "https://www.frawo-tech.de"

print(f"[*] Making GET request to {BASE_URL}/contactus to obtain CSRF token...")
session = requests.Session()
try:
    res = session.get(f"{BASE_URL}/contactus", verify=True)
except Exception as e:
    print(f"[FAIL] GET failed: {e}")
    sys.exit(1)

csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.text)
if not csrf_match:
    csrf_match = re.search(r'value="([^"]+)"\s+name="csrf_token"', res.text)

if not csrf_match:
    print("[FAIL] CSRF token not found in the HTML!")
    sys.exit(1)

csrf_token = csrf_match.group(1)
print(f"[OK] Found CSRF Token: {csrf_token}")

headers = {
    "Referer": f"{BASE_URL}/contactus",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "X-Requested-With": "XMLHttpRequest"
}

print("\n[*] Posting to /website/form/crm.lead WITH custom fields ('timeline' and 'privacy')...")
data_with_custom = {
    "csrf_token": csrf_token,
    "contact_name": "Testbot Antigravity Custom (Direct)",
    "email_from": "antigravity-custom@frawo-tech.de",
    "phone": "+49123456789",
    "name": "Smart Home Custom Fields Test (Direct)",
    "timeline": "Juli 2026",
    "description": "Testing if custom fields crash the submission.",
    "privacy": "on"
}

res_post = session.post(f"{BASE_URL}/website/form/crm.lead", data=data_with_custom, headers=headers)
print(f"Status Code: {res_post.status_code}")
print(f"Response text:\n{res_post.text}")
