import requests
r = requests.get("https://funk.frawo-tech.de/login")
with open("scratch/login_page.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved to scratch/login_page.html")
