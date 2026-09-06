import base64
import subprocess
import os

FILES_TO_SYNC = [
    "addons/frawo_agent/models/it_equipment.py",
    "addons/frawo_agent/models/mail_message.py",
    "addons/frawo_agent/models/radio_vote.py",
    "addons/frawo_agent/models/__init__.py",
    "addons/frawo_agent/views/it_equipment_views.xml",
    "addons/frawo_agent/views/radio_page.xml",
    "addons/frawo_agent/__manifest__.py",
    "addons/frawo_agent/controllers/main.py",
    "addons/frawo_agent/controllers/anker_tracker.py",
    "addons/frawo_agent/controllers/radio_votes.py",
]

for rel_path in FILES_TO_SYNC:
    with open(rel_path, "rb") as f:
        content = f.read()

    b64_content = base64.b64encode(content).decode("ascii")
    clean_rel = rel_path.replace("addons/", "")
    remote_dest = f"/opt/frawotech/extra-addons/{clean_rel}"

    print(f"Syncing {rel_path} -> CT140:{remote_dest}...")

    # Write file inside CT140 via python
    py_code = f"""import base64, os
dest = '{remote_dest}'
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, 'wb') as f:
    f.write(base64.b64decode('{b64_content}'))
print('Wrote', dest)
"""
    cmd = [
        "ssh", "-o", "BatchMode=yes", "root@10.1.0.128",
        "pct exec 140 -- python3 -"
    ]
    res = subprocess.run(cmd, input=py_code, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0:
        print("  [OK] Success")
    else:
        print(f"  [ERROR] Error: {res.stderr}")

print("=== All files synced to CT140! ===")
