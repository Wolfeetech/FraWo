import json
import os
import subprocess
import sys

def get_github_repos(owner):
    print(f"--- Discovering GitHub Repositories for {owner} ---")
    try:
        # Use curl to get public repos if no token is provided
        cmd = ["curl", "-s", f"https://api.github.com/users/{owner}/repos"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        repos = json.loads(result.stdout)
        
        if not isinstance(repos, list):
            print(f"Error fetching repos: {repos}")
            return []
            
        repo_list = []
        for repo in repos:
            repo_list.append({
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo["description"],
                "updated_at": repo["updated_at"]
            })
            print(f"[FOUND] {repo['name']} - {repo['html_url']}")
        return repo_list
    except Exception as e:
        print(f"Discovery failed: {e}")
        return []

def main():
    owner = "Wolfeetech"
    repos = get_github_repos(owner)
    
    # Write to artifacts
    os.makedirs("artifacts/repo_consolidation", exist_ok=True)
    with open("artifacts/repo_consolidation/github_discovery.json", "w") as f:
        json.dump(repos, f, indent=2)
    
    with open("artifacts/repo_consolidation/github_discovery.md", "w") as f:
        f.write(f"# GitHub Discovery: {owner}\n\n")
        f.write("| Name | Description | URL | Last Update |\n")
        f.write("| --- | --- | --- | --- |\n")
        for r in repos:
            f.write(f"| {r['name']} | {r['description']} | [link]({r['url']}) | {r['updated_at']} |\n")

if __name__ == "__main__":
    main()
