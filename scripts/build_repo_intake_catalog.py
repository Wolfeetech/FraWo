import json
import os
import glob

def build_catalog():
    print("--- Building Repository Intake Catalog ---")
    catalog = {
        "master_ssot": "FraWo",
        "legacy_repos": [],
        "last_updated": ""
    }
    
    # Load GitHub Discovery
    github_file = "artifacts/repo_consolidation/github_discovery.json"
    if os.path.exists(github_file):
        with open(github_file, "r") as f:
            github_repos = json.load(f)
            for r in github_repos:
                if r["name"] != catalog["master_ssot"]:
                    catalog["legacy_repos"].append({
                        "name": r["name"],
                        "source": "github",
                        "url": r["url"],
                        "status": "pending_intake"
                    })
    
    # Load Local Discovery
    local_files = glob.glob("artifacts/repo_consolidation/local_discovery_*.json")
    for lf in local_files:
        with open(lf, "r") as f:
            local_repos = json.load(f)
            for r in local_repos:
                name = os.path.basename(r["path"])
                if name != catalog["master_ssot"]:
                    # Check if already cataloged from GitHub
                    existing = next((x for x in catalog["legacy_repos"] if x["name"] == name), None)
                    if existing:
                        existing["local_path"] = r["path"]
                    else:
                        catalog["legacy_repos"].append({
                            "name": name,
                            "source": "local",
                            "local_path": r["path"],
                            "status": "pending_intake"
                        })

    os.makedirs("artifacts/repo_consolidation", exist_ok=True)
    catalog_path = "artifacts/repo_consolidation/repo_intake_catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Catalog built with {len(catalog['legacy_repos'])} legacy repositories.")
    return catalog_path

if __name__ == "__main__":
    build_catalog()
