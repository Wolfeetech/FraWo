import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    r = requests.get('https://10.1.0.1', verify=False, timeout=5)
    print(f"HTTPS Status: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"HTTPS Error: {e}")
