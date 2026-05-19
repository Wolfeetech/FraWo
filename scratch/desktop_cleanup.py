import os
import shutil

desktop_dir = r"C:\Users\StudioPC\Desktop"
archive_dir = r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\archive\desktop_cleanup_2026-05-19"
test_init_dir = r"C:\Users\StudioPC\test-init"

os.makedirs(archive_dir, exist_ok=True)

# List of files to move (excluding desktop.ini and shortcuts)
extensions_to_move = [".md", ".py", ".bat", ".txt", ".ps1", ".jpg"]

moved_count = 0
errors = []

for f in os.listdir(desktop_dir):
    src_path = os.path.join(desktop_dir, f)
    if os.path.isdir(src_path):
        continue
    
    if f.lower() == "desktop.ini":
        continue
        
    _, ext = os.path.splitext(f)
    if ext.lower() in extensions_to_move:
        dest_path = os.path.join(archive_dir, f)
        try:
            shutil.move(src_path, dest_path)
            print(f"Moved to archive: {f}")
            moved_count += 1
        except Exception as e:
            errors.append((f, str(e)))

# Clean up empty test-init folder
if os.path.exists(test_init_dir):
    try:
        shutil.rmtree(test_init_dir)
        print("Deleted empty folder: test-init")
    except Exception as e:
        errors.append(("test-init", str(e)))

print(f"\nCleanup completed. Moved {moved_count} files to {archive_dir}.")
if errors:
    print("\nErrors encountered:")
    for f, err in errors:
        print(f" - {f}: {err}")
