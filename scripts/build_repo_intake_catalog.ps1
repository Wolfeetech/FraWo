Write-Host "--- Building Repository Intake Catalog (PS) ---" -ForegroundColor Cyan

$catalogPath = "artifacts/repo_consolidation/repo_intake_catalog.json"
$githubPath = "artifacts/repo_consolidation/github_discovery.csv"

$catalog = @{
    master_ssot = "FraWo"
    legacy_repos = @()
}

# Load GitHub Discovery
if (Test-Path $githubPath) {
    $githubRepos = Import-Csv -Path $githubPath
    foreach ($repo in $githubRepos) {
        if ($repo.name -ne $catalog.master_ssot) {
            $catalog.legacy_repos += @{
                name = $repo.name
                source = "github"
                url = $repo.html_url
                status = "pending_intake"
            }
        }
    }
}

# Update Register MD
$registerPath = "REPO_CONSOLIDATION_REGISTER.md"
# (Logic to update the MD if needed)

$catalog | ConvertTo-Json -Depth 10 | Out-File -FilePath $catalogPath
Write-Host "Catalog built with $($catalog.legacy_repos.Count) legacy repositories." -ForegroundColor Green
