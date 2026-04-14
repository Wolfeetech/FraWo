import json
import os
import datetime

def generate_snapshot():
    print("--- Generating Repository Consolidation Snapshot ---")
    catalog_path = "artifacts/repo_consolidation/repo_intake_catalog.json"
    
    snapshot = {
        "timestamp": datetime.datetime.now().isoformat(),
        "master_repo": "FraWo",
        "ssot_contract_verified": os.path.exists("SSOT_COLLABORATION_CONTRACT.md"),
        "legacy_repos": [],
        "overall_status": "PENDING"
    }

    if os.path.exists(catalog_path):
        with open(catalog_path, "r") as f:
            catalog = json.load(f)
            snapshot["legacy_repos"] = catalog["legacy_repos"]
            
            pending = [r for r in catalog["legacy_repos"] if r["status"] == "pending_intake"]
            if not pending:
                snapshot["overall_status"] = "CONSOLIDATED"
            else:
                snapshot["overall_status"] = "INTAKE_IN_PROGRESS"

    snapshot_path = "artifacts/repo_consolidation/latest_snapshot.md"
    os.makedirs("artifacts/repo_consolidation", exist_ok=True)
    with open(snapshot_path, "w") as f:
        f.write(f"# Repository Consolidation Snapshot: {snapshot['timestamp']}\n\n")
        f.write(f"**Overall Status**: {snapshot['overall_status']}\n")
        f.write(f"**SSOT Contract**: {'✅ Verified' if snapshot['ssot_contract_verified'] else '❌ Missing'}\n\n")
        f.write("## Repo Status\n")
        f.write("| Repo Name | Source | Status |\n")
        f.write("| --- | --- | --- |\n")
        for r in snapshot["legacy_repos"]:
            f.write(f"| {r['name']} | {r['source']} | {r['status']} |\n")

    print(f"Snapshot generated at {snapshot_path}")

if __name__ == "__main__":
    generate_snapshot()
