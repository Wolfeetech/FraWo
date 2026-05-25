import os
import glob

dirs = [
    r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scratch",
    r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scripts"
]

print("Searching files for 'franz'...")
for d in dirs:
    py_files = glob.glob(os.path.join(d, "*.py")) + glob.glob(os.path.join(d, "*.ps1")) + glob.glob(os.path.join(d, "*.sh"))
    for filepath in py_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "franz" in content.lower():
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if "franz" in line.lower():
                            print(f"{filename}:{line_num}: {line.strip()}")
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
