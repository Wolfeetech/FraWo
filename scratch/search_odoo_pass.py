import os
import glob

scratch_dir = r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scratch"
py_files = glob.glob(os.path.join(scratch_dir, "*.py"))

print(f"Searching {len(py_files)} Python files in scratch directory...")
for filepath in py_files:
    filename = os.path.basename(filepath)
    if filename == "search_odoo_pass.py":
        continue
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "authenticate" in content or "xmlrpc" in content:
                for line in content.splitlines():
                    if "password" in line.lower() and "=" in line and ("password =" in line.lower() or "password=" in line.lower()):
                        print(f"{filename}: {line.strip()}")
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
