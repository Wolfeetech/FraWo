param(
    [string]$Root = "C:\Users\Admin\Documents",
    [int]$MaxDepth = 4
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "--- Repository Discovery: Local Workstation ---" -ForegroundColor Cyan

function Find-GitRepos {
    param($Path, $Depth)
    if ($Depth -gt $MaxDepth) { return }
    
    # Use -Force to see hidden .git folders
    $items = Get-ChildItem -Path $Path -Force
    foreach ($item in $items) {
        if ($item.Name -eq ".git") {
            $repoPath = Split-Path $item.FullName -Parent
            $remoteUrl = "Unknown"
            try {
                # Try to get remote origin URL if git is available
                if (Get-Command git -ErrorAction SilentlyContinue) {
                    $remoteUrl = (git -C $repoPath remote get-url origin) 2>$null
                }
            } catch {}
            
            Write-Host "[FOUND] $repoPath ($remoteUrl)" -ForegroundColor Green
            [PSCustomObject]@{
                Path = $repoPath
                Remote = $remoteUrl
                Type = "Local"
                Node = $env:COMPUTERNAME
            } | Export-Csv -Path "artifacts/repo_consolidation/local_discovery_$($env:COMPUTERNAME).csv" -Append -NoTypeInformation
        } else {
            Find-GitRepos -Path $item.FullName -Depth ($Depth + 1)
        }
    }
}

# Ensure directory exists
if (-not (Test-Path "artifacts/repo_consolidation")) {
    New-Item -ItemType Directory -Path "artifacts/repo_consolidation"
}

# Start Discovery
Find-GitRepos -Path $Root -Depth 0
Write-Host "Discovery Complete." -ForegroundColor Cyan
