import jinja2
import json
import os

# Paths
TEMPLATE_FILE = "ansible/templates/frontend/surface-go-portal/index.html.j2"
ACTIONS_FILE = "manifests/control_surface/actions.json"
OUTPUT_FILE = "manifests/control_surface/index.html"

# Meta data for actions
ACTION_META = {
    "radio_player_special": {"icon": "📻", "note": "Radio4yourparty"},
    "stockenweiler_home_assistant": {"icon": "🏠", "note": "HA Eltern"},
    "homeserver_home_assistant": {"icon": "⚡", "note": "HA Homeserver"},
    "frawo_odoo": {"icon": "💼", "note": "FraWo Odoo"},
    "proxmox_ve": {"icon": "🖥️", "note": "Proxmox VE"}
}

def render():
    with open(ACTIONS_FILE, "r") as f:
        actions_data = json.load(f)

    # Mocking the Ansible variables used in the template
    group_actions = []
    for action_id in actions_data["actions"]:
        target_url = "#"
        if action_id == "stockenweiler_home_assistant": target_url = "http://192.168.178.179:8123"
        elif action_id == "homeserver_home_assistant": target_url = "http://haos.hs27.internal:8123"
        elif action_id == "frawo_odoo": target_url = "https://odoo.frawo-tech.de"
        elif action_id == "proxmox_ve": target_url = "http://proxmox.hs27.internal:8006"
        
        group_actions.append({"id": action_id, "target_url": target_url})

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    template = env.get_template(TEMPLATE_FILE)
    
    # Provide ALL variables the template might expect
    context = {
        "surface_go_actions_manifest": actions_data,
        "group_actions": group_actions,
        "action_meta": ACTION_META,
        "accent_primary": "#10b981",
        "bg_dark": "#0a0a0a",
        "surface_go_target_hostname": "surface-go-frontend",
        "surface_go_status": "online"
    }
    
    html = template.render(**context)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully rendered to {OUTPUT_FILE}")

if __name__ == "__main__":
    render()
