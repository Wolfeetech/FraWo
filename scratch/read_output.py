import sys
try:
    with open("c:/WORKSPACE/FraWo/scratch/odoo_tasks_output.txt", "r", encoding="utf-16-le") as f:
        content = f.read()
    print("--- CONTENT ---")
    print(content)
except Exception as e:
    print(f"Error: {e}")
