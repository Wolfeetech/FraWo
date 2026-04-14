import os
import json
import socket
import datetime

def discover_repos(root_dir, max_depth=4):
    found_repos = []
    print(f"--- Discovery started on {socket.gethostname()} at {root_dir} ---")
    
    for root, dirs, files in os.walk(root_dir):
        depth = root[len(root_dir):].count(os.sep)
        if depth > max_depth:
            dirs[:] = [] # Stop recursion
            continue
            
        if '.git' in dirs:
            repo_path = os.path.abspath(root)
            print(f"[FOUND] {repo_path}")
            found_repos.append({
                "path": repo_path,
                "node": socket.gethostname(),
                "discovered_at": datetime.datetime.now().isoformat()
            })
            dirs.remove('.git') # Don't dive into .git
            
    return found_repos

if __name__ == "__main__":
    results = discover_repos("C:\\Users\\Admin\\Documents", max_depth=3)
    os.makedirs("artifacts/repo_consolidation", exist_ok=True)
    with open(f"artifacts/repo_consolidation/local_discovery_{socket.gethostname()}.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Discovery complete. Result saved to artifacts/repo_consolidation/local_discovery_{socket.gethostname()}.json")
