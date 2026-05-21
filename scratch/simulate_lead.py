import requests
import re

def submit_test_lead():
    print("Starte Lead-Simulation...")
    session = requests.Session()
    response = session.get('https://www.frawo-tech.de/contactus')
    
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    csrf_token = match.group(1) if match else None
    
    if not csrf_token:
        print("[FAIL] Konnte keinen CSRF-Token auf der Seite finden.")
        return
        
    print(f"[OK] CSRF-Token gefunden: {csrf_token[:10]}...")
    
    data = {
        'csrf_token': csrf_token,
        'contact_name': 'Anna Testkunde (Automatischer Test)',
        'phone': '0151 98765432',
        'email_from': 'anna.testkunde@example.com',
        'name': 'Firmenjubilaeum 2026 - Kompletttechnik',
        'description': 'TIMELINE: Oktober 2026\nPRIVACY: Zugestimmt\n\nHallo liebes FraWo-Team!\nWir benoetigen fuer unser Jubilaeum eine grosse Buehne, Licht und Tontechnik fuer ca. 300 Personen im Zelt.\nViele Gruesse!',
    }
    
    print("[*] Sende POST Request an /website/form/crm.lead...")
    post_resp = session.post('https://www.frawo-tech.de/website/form/crm.lead', data=data)
    
    print(f"[STATUS] {post_resp.status_code}")
    if post_resp.status_code == 200:
        print("[OK] Formular erfolgreich abgeschickt! JSON: " + post_resp.text)
    else:
        print(f"[FAIL] Fehler beim Senden: {post_resp.text[:200]}")

if __name__ == '__main__':
    submit_test_lead()
