import requests

base_url = "https://funk.frawo-tech.de/api"
email = "wolf@frawo-tech.de"
password = "11Vaudeville!!"

# In AzuraCast, there isn't a simple username/password auth for the REST API (you usually need an API key).
# BUT, we can try to get an API key or see if there is an auth endpoint.
# Actually, the user login endpoint is often /api/internal/auth or we can just try to scrape the CSRF token.
# Let's try basic auth on the stations endpoint just in case it supports it (unlikely).
try:
    response = requests.get(f"{base_url}/stations", auth=(email, password))
    print(f"Auth Test Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Stations:", response.json())
except Exception as e:
    print("Error:", e)
