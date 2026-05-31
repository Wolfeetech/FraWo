import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    with open("c:/WORKSPACE/FraWo/scratch/odoo_tasks_output.txt", "r", encoding="utf-16") as f:
        content = f.read()

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        json_str = match.group(0)
        data = json.loads(json_str)
        
        if "out-data" in data and data["out-data"]:
            print("--- STDOUT ---")
            print(data["out-data"])
            
        if "err-data" in data and data["err-data"]:
            print("--- STDERR ---")
            print(data["err-data"])
            
        print(f"\nExit Code: {data.get('exitcode')}")
    else:
        print("No JSON found.")
except Exception as e:
    print(f"Error: {e}")
