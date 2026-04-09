param(
    [string]$SurfaceEvidence = "",
    [string]$IphoneEvidence = "",
    [switch]$SkipGate,
    [switch]$SkipHandoff
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = "python"
$updateScript = Join-Path $repoRoot "scripts\update_release_mvp_manual_check.py"
$gateScript = Join-Path $repoRoot "scripts\release_mvp_gate.py"
$handoffScript = Join-Path $repoRoot "scripts\generate_ai_server_handoff.py"
$latestGatePath = Join-Path $repoRoot "artifacts\release_mvp_gate\latest_release_mvp_gate.md"
$handoffPath = Join-Path $repoRoot "AI_SERVER_HANDOFF.md"

function Invoke-PythonCapture {
    param(
        [string[]]$Arguments
    )

    $output = & $pythonExe @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    return @{
        Output = @($output)
        ExitCode = $exitCode
    }
}

if (-not (Test-Path $updateScript)) {
    throw "Update script missing: $updateScript"
}

if (-not (Test-Path $gateScript)) {
    throw "Gate script missing: $gateScript"
}

if (-not (Test-Path $handoffScript)) {
    throw "Handoff script missing: $handoffScript"
}

if (-not $SurfaceEvidence) {
    if ([Console]::IsInputRedirected) {
        throw "surface_evidence_required: pass -SurfaceEvidence or run interactively."
    }
    $SurfaceEvidence = Read-Host -Prompt "Visible evidence for Franz Surface Laptop rollout"
}

if (-not $IphoneEvidence) {
    if ([Console]::IsInputRedirected) {
        throw "iphone_evidence_required: pass -IphoneEvidence or run interactively."
    }
    $IphoneEvidence = Read-Host -Prompt "Visible evidence for Franz iPhone rollout"
}

if (-not $SurfaceEvidence) {
    throw "No Surface Laptop evidence entered."
}

if (-not $IphoneEvidence) {
    throw "No iPhone evidence entered."
}

$today = Get-Date -Format "yyyy-MM-dd"
$evidence = "Visible device rollout proof ${today}: Surface Laptop: $SurfaceEvidence iPhone: $IphoneEvidence This closes the visible Franz device rollout for the current MVP."

$updateResult = Invoke-PythonCapture -Arguments @(
    $updateScript,
    "--id", "device_rollout_verified",
    "--status", "passed",
    "--last-verified", $today,
    "--evidence", $evidence
)

$updateResult.Output | ForEach-Object { $_ }

if ($updateResult.ExitCode -ne 0) {
    throw "Manual check update failed."
}

if (-not $SkipGate) {
    $gateResult = Invoke-PythonCapture -Arguments @($gateScript)
    $gateResult.Output | ForEach-Object { $_ }
    if ($gateResult.ExitCode -ne 0) {
        Write-Host "Gate remains blocked for other reasons. Latest gate file: $latestGatePath"
    }
    else {
        Write-Host "Gate is now MVP_READY. Latest gate file: $latestGatePath"
    }
}

if (-not $SkipHandoff) {
    $handoffResult = Invoke-PythonCapture -Arguments @($handoffScript)
    $handoffResult.Output | ForEach-Object { $_ }
    if ($handoffResult.ExitCode -ne 0) {
        throw "AI handoff refresh failed."
    }
    Write-Host "Updated AI handoff: $handoffPath"
}
