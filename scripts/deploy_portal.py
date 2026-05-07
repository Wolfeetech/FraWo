import os
import subprocess
import jinja2
import json
import time

ROOT = r"C:\WORKSPACE\FraWo"
TARGET_HOST = "100.106.67.127"
TARGET_USER = "frawo"
TARGET_PASS = "anker"
MANIFEST_PATH = os.path.join(ROOT, "manifests", "control_surface", "actions.json")
TEMPLATE_PATH = os.path.join(ROOT, "ansible", "templates", "frontend", "surface-go-portal", "index.html.j2")
OUTPUT_PATH = os.path.join(ROOT, "rendered_index.html")

def render():
    print("Rendering portal...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_content = f.read()
    env = jinja2.Environment()
    template = env.from_string(template_content)
    context = {"surface_go_actions_manifest": manifest, "playbook_dir": "/home/frawo/ansible"}
    output = template.render(**context)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Rendered to {OUTPUT_PATH}")

def deploy():
    print(f"Deploying to {TARGET_HOST}...")
    # Upload to /tmp first
    try:
        subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", OUTPUT_PATH, f"{TARGET_USER}@{TARGET_HOST}:/tmp/index.html"], check=True)
        print("Upload to /tmp successful.")
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e}")
        return

    # Move to final destination with sudo
    print("Installing portal and restarting Firefox...")
    install_cmd = f"echo {TARGET_PASS} | sudo -S bash -c 'cp /tmp/index.html /home/frontend/homeserver2027-portal/index.html && chown frontend:frontend /home/frontend/homeserver2027-portal/index.html && pkill -u frontend firefox'"
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", f"{TARGET_USER}@{TARGET_HOST}", install_cmd])
    print("Done.")

if __name__ == "__main__":
    render()
    deploy()
