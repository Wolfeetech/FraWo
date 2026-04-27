import jinja2
import json
import os

# Paths
ROOT = r"C:\WORKSPACE\FraWo"
MANIFEST_PATH = os.path.join(ROOT, "manifests", "control_surface", "actions.json")
TEMPLATE_PATH = os.path.join(ROOT, "ansible", "templates", "frontend", "surface-go-portal", "index.html.j2")
OUTPUT_PATH = os.path.join(ROOT, "rendered_index.html")

def render():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    env = jinja2.Environment()
    template = env.from_string(template_content)
    
    # Mocking Ansible-like context
    context = {
        "surface_go_actions_manifest": manifest,
        "playbook_dir": os.path.join(ROOT, "ansible", "playbooks")
    }
    
    output = template.render(**context)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output)
    
    print(f"Rendered template to {OUTPUT_PATH}")

if __name__ == "__main__":
    render()
