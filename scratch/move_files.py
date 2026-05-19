import os
import shutil

src_dir = r"C:\Users\StudioPC"
dest_dir = r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\deployments\cloudflare-security-headers"

os.makedirs(dest_dir, exist_ok=True)

files = [
    "START_HERE.md",
    "DEPLOYMENT_CHECKLIST.md",
    "IMPLEMENTATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "README_SECURITY_IMPLEMENTATION.md",
    "frawo-tech_security_audit_2026-05-16.md",
    "cloudflare-security-headers-config.json",
    "caddy-security-config.caddyfile",
    "odoo-security-config.conf",
    "cloudflare-deploy-security-headers.ps1",
    "cloudflare-deploy-security-headers.sh",
    "verify-security-headers.ps1",
    "verify-security-headers.sh",
    "CLOUDFLARE_SETUP_NOW.md"
]

moved_count = 0
for f in files:
    src_path = os.path.join(src_dir, f)
    dest_path = os.path.join(dest_dir, f)
    if os.path.exists(src_path):
        try:
            shutil.move(src_path, dest_path)
            print(f"Moved: {f}")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {f}: {e}")
    else:
        print(f"Not found: {f}")

print(f"Done. Moved {moved_count} files.")
