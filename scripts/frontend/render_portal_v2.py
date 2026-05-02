import jinja2
import json
import os

# Paths
TEMPLATE_FILE = "ansible/templates/frontend/surface-go-portal/index.html.j2"
ACTIONS_FILE = "manifests/control_surface/actions.json"
OUTPUT_FILE = "artifacts/surface_index_v2_with_nowplaying.html"

# Meta data for actions
ACTION_META = {
    "radio_player_special": {"icon": "📻", "note": "Radio4yourparty"},
    "stockenweiler_home_assistant": {"icon": "🏠", "note": "HA Eltern"},
    "homeserver_home_assistant": {"icon": "⚡", "note": "HA Homeserver"},
    "frawo_odoo": {"icon": "💼", "note": "FraWo Odoo"},
    "proxmox_ve": {"icon": "🖥️", "note": "Proxmox VE"}
}

def render():
    with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
        actions_data = json.load(f)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    template = env.get_template(TEMPLATE_FILE)
    
    # Provide ALL variables the template might expect
    context = {
        "surface_go_actions_manifest": actions_data,
        "accent_primary": "#00ffa3",
        "bg_dark": "#03070a",
        "surface_go_target_hostname": "surface-go-frontend",
        "surface_go_status": "CONNECTED (LAN)"
    }
    
    html = template.render(**context)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully rendered to {OUTPUT_FILE}")

if __name__ == "__main__":
    render()
