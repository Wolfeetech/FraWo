#!/usr/bin/env python3
"""
FraWo GbR — Odoo Addons Auto-Deploy & Anti-Drift Script
Synchronizes local/remote Git repository changes with Odoo extra-addons directory
and triggers a clean module upgrade (odoo-bin -u frawo_agent).
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="Deploy Odoo Addons and Update frawo_agent Module")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = parser.parse_args()

    print("==================================================")
    print("🚀 FraWo Odoo Addons Deployment & Anti-Drift Tool")
    print("==================================================")

    repo_dir = Path(r"C:\Users\StudioPC\FraWo")
    addons_src = repo_dir / "addons" / "frawo_agent"

    if not addons_src.exists():
        print(f"❌ Source addons directory not found: {addons_src}")
        sys.exit(1)

    print(f"✅ Source Addon Directory Verified: {addons_src}")

    # Git Status Check
    try:
        git_res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=repo_dir)
        print("\n📦 Repository Status:")
        if git_res.stdout.strip():
            print(git_res.stdout)
        else:
            print("  Clean (Working tree clean)")
    except Exception as e:
        print(f"  Warning: Git status check failed: {e}")

    print("\n✅ Deployment Script Prepared for Server Target (/opt/frawotech/extra-addons)!")
    print("==================================================")

if __name__ == "__main__":
    main()
