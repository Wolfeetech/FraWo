#!/usr/bin/env python3
import urllib.request
import ssl

def verify_website():
    url = "https://www.frawo-tech.de/"
    print(f"[*] Fetching website: {url}")
    
    # Custom User-Agent to bypass potential cloudflare or custom blocks
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityRadioProber/1.0'}
    )
    
    # Bypass SSL verification if internal DNS/SSL has any issues (though it should be fine)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            status = response.status
            body = response.read().decode('utf-8')
            
        print(f"[OK] Response status: {status}")
        
        # Check elements
        has_player = "frawo-radio-player" in body
        has_canvas = "fw-visualizer-canvas" in body
        has_script = "FraWo Live Player active & initializing" in body
        has_stream = "funk.frawo-tech.de/listen/frawo_funk/radio.mp3" in body

        print(f"[*] Analysis:")
        print(f"    - Has player container: {'YES' if has_player else 'NO'}")
        print(f"    - Has canvas:           {'YES' if has_canvas else 'NO'}")
        print(f"    - Has live script tag:  {'YES' if has_script else 'NO'}")
        print(f"    - Has stream URL:       {'YES' if has_stream else 'NO'}")

        if has_player and has_canvas and has_script and has_stream:
            print("[SUCCESS] All radio player elements are successfully live on the website!")
            return 0
        else:
            print("[FAIL] Missing crucial player elements in the HTML body!")
            return 1
            
    except Exception as e:
        print(f"[FAIL] Error contacting website: {e}")
        return 1

if __name__ == "__main__":
    exit(verify_website())
