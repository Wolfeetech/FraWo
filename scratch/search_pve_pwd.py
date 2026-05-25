import os
import glob

dirs = [
    r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo",
    r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scripts",
    r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scratch"
]

print("Searching for HOMESERVER_PROXMOX_ROOT_PASSWORD...")
for d in dirs:
    files = glob.glob(os.path.join(d, "*.py")) + glob.glob(os.path.join(d, "*.ps1")) + glob.glob(os.path.join(d, "*.sh")) + glob.glob(os.path.join(d, ".env*"))
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "HOMESERVER_PROXMOX_ROOT_PASSWORD" in content or "proxmox_host" in content.lower():
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if "HOMESERVER_PROXMOX_ROOT_PASSWORD" in line or "proxmox_host" in line.lower() or "pve_host" in line.lower():
                            print(f"{filename}:{line_num}: {line.strip()}")
        except Exception as e:
            pass
