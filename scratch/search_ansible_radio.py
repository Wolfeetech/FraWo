import os

def search_text(folder, query):
    print(f"Searching for '{query}' in {folder}...")
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(('.yml', '.yaml', '.conf', '.cfg', '.j2', '.sh', '.py', '.txt')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        for i, line in enumerate(file, 1):
                            if query in line:
                                print(f"  {os.path.relpath(path, folder)}:{i} | {line.strip()}")
                except Exception:
                    pass

search_text(r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\ansible", "radio")
