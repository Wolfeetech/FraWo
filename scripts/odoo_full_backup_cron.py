#!/usr/bin/env python3
"""
Automated Odoo 19 Full Backup Script (PostgreSQL DB + Filestore)
For FraWo GbR Odoo Instance (FraWo_GbR)
"""

import os
import sys
import time
import shutil
import urllib.request
import urllib.parse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = os.getenv("ODOO_URL", "http://10.1.0.112:8069")
ODOO_DB = os.getenv("ODOO_DB", "FraWo_GbR")
MASTER_PWD = os.getenv("ODOO_MASTER_PASSWD", "FrawoWolf2026!")
BACKUP_DIR = os.getenv("BACKUP_DIR", r"C:\Users\StudioPC\FraWo\_BACKUPS_ODOO")
SAMBA_SHARE = os.getenv("SAMBA_SHARE", r"\\10.1.0.94\music\_BACKUPS_ODOO")
RETENTION_DAYS = 30


def ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(os.path.dirname(SAMBA_SHARE)):
        try:
            os.makedirs(SAMBA_SHARE, exist_ok=True)
        except Exception as e:
            print(f"[WARN] Could not create Samba backup dir: {e}")


def perform_odoo_backup():
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file_name = f"odoo_backup_{ODOO_DB}_{timestamp}.zip"
    target_local_path = os.path.join(BACKUP_DIR, backup_file_name)

    print(f"[{datetime.now().isoformat()}] Starting Odoo Backup for '{ODOO_DB}'...")
    print(f"Target local: {target_local_path}")

    backup_url = f"{ODOO_URL}/web/database/backup"
    data = urllib.parse.urlencode({
        "master_pwd": MASTER_PWD,
        "name": ODOO_DB,
        "backup_format": "zip"
    }).encode("utf-8")

    req = urllib.request.Request(backup_url, data=data, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            with open(target_local_path, "wb") as f:
                shutil.copyfileobj(response, f)
        
        file_size_mb = os.path.getsize(target_local_path) / (1024 * 1024)
        print(f"✅ Local backup successful! Size: {file_size_mb:.2f} MB")

        # Copy to Samba share if accessible
        if os.path.exists(SAMBA_SHARE):
            samba_path = os.path.join(SAMBA_SHARE, backup_file_name)
            shutil.copy2(target_local_path, samba_path)
            print(f"✅ Synced to Samba share: {samba_path}")

        # Retention Cleanup
        cleanup_old_backups(BACKUP_DIR)
        if os.path.exists(SAMBA_SHARE):
            cleanup_old_backups(SAMBA_SHARE)

        return True, target_local_path
    except Exception as e:
        print(f"❌ Backup failed: {e}", file=sys.stderr)
        return False, str(e)


def cleanup_old_backups(directory):
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)
    for fname in os.listdir(directory):
        if fname.startswith("odoo_backup_") and fname.endswith(".zip"):
            fpath = os.path.join(directory, fname)
            if os.path.getmtime(fpath) < cutoff:
                try:
                    os.remove(fpath)
                    print(f"🗑️ Cleaned up old backup: {fname}")
                except Exception as e:
                    print(f"[WARN] Failed to delete old backup {fname}: {e}")


if __name__ == "__main__":
    success, result = perform_odoo_backup()
    sys.exit(0 if success else 1)
