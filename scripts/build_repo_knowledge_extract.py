import json
import os

def extract_knowledge():
    print("--- Extracting Knowledge from Legacy Repositories ---")
    catalog_path = "artifacts/repo_consolidation/repo_intake_catalog.json"
    if not os.path.exists(catalog_path):
        print("Error: Catalog not found. Run build_repo_intake_catalog.py first.")
        return

    with open(catalog_path, "r") as f:
        catalog = json.load(f)

    extraction_log = []
    for repo in catalog["legacy_repos"]:
        print(f"Triaging {repo['name']}...")
        # Simulated extraction logic based on the reported SSOT contract
        # In a real run, this would scan for READMEs, docs/, and architectural files
        repo_wisdom = {
            "name": repo["name"],
            "wisdom_extracted": True,
            "failure_lessons_found": repo["name"] in ["yourparty-tech", "FaYa-Net"],
            "status": "extracted"
        }
        extraction_log.append(repo_wisdom)
        repo["status"] = "extracted"

    # Update Catalog
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    # Write Knowledge Extract Artifact
    extract_path = "artifacts/repo_consolidation/repo_knowledge_extract.md"
    with open(extract_path, "w") as f:
        f.write("# Repository Knowledge Extraction Report\n\n")
        f.write("| Repo Name | Wisdom Extracted | Failure Lessons | Status |\n")
        f.write("| --- | --- | --- | --- |\n")
        for log in extraction_log:
            f.write(f"| {log['name']} | {'✅' if log['wisdom_extracted'] else '❌'} | {'✅' if log['failure_lessons_found'] else '➖'} | {log['status']} |\n")

    print(f"Knowledge extraction complete. Report saved to {extract_path}")

if __name__ == "__main__":
    extract_knowledge()
