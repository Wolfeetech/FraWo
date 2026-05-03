import sys
import re
from pathlib import Path

def parse_masterplan(content):
    lanes = []
    current_lane = None
    
    lines = content.splitlines()
    for line in lines:
        if line.startswith("### Lane "):
            # Extract Lane Name and Status
            match = re.search(r"Lane ([A-E]): (.*) - \[STATUS: (.*)\]", line)
            if match:
                current_lane = {
                    "lane": match.group(1),
                    "name": match.group(2),
                    "status": match.group(3),
                    "tasks": []
                }
                lanes.append(current_lane)
        elif current_lane and line.strip().startswith("- "):
            current_lane["tasks"].append(line.strip()[2:])
            
    return lanes

def generate_odoo_tasks(lanes):
    odoo_tasks = []
    for lane in lanes:
        task_name = f"[Lane {lane['lane']}] {lane['name']} ({lane['status']})"
        description = "<ul>"
        for t in lane['tasks']:
            description += f"<li>{t}</li>"
        description += "</ul>"
        
        odoo_tasks.append({
            "name": task_name,
            "description": description
        })
    return odoo_tasks

if __name__ == "__main__":
    masterplan_path = Path("MASTERPLAN.md")
    if not masterplan_path.exists():
        print("MASTERPLAN.md not found")
        sys.exit(1)
        
    content = masterplan_path.read_text(encoding="utf-8")
    lanes = parse_masterplan(content)
    tasks = generate_odoo_tasks(lanes)
    
    print(f"Parsed {len(tasks)} tasks from Masterplan.")
    for t in tasks:
        print(f"Task: {t['name']}")
