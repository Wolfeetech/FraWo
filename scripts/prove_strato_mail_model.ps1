param(
    [string]$Username = "franz@frawo-tech.de",
    [string]$Subject = "HS27 noreply SMTP proof 2026-03-30 23:37",
    [string]$PasswordPlaintext = "",
    [switch]$SkipGate
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = "python"
$proofScript = Join-Path $repoRoot "scripts\check_strato_inbox_for_subject.py"
$updateScript = Join-Path $repoRoot "scripts\update_release_mvp_manual_check.py"
$gateScript = Join-Path $repoRoot "scripts\release_mvp_gate.py"
$latestGatePath = Join-Path $repoRoot "artifacts\release_mvp_gate\latest_release_mvp_gate.md"

function Convert-SecureStringToPlainText {
    param([Security.SecureString]$SecureValue)

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

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

if (-not (Test-Path $proofScript)) {
    throw "Proof script missing: $proofScript"
}

if (-not (Test-Path $updateScript)) {
    throw "Update script missing: $updateScript"
}

if (-not (Test-Path $gateScript)) {
    throw "Gate script missing: $gateScript"
}

$hadPreviousEnv = [bool]$env:HS27_MAILBOX_PASSWORD
$previousEnv = $env:HS27_MAILBOX_PASSWORD

try {
    if (-not $env:HS27_MAILBOX_PASSWORD -and $PasswordPlaintext) {
        $env:HS27_MAILBOX_PASSWORD = $PasswordPlaintext
    }

    if (-not $env:HS27_MAILBOX_PASSWORD) {
        if ([Console]::IsInputRedirected) {
            throw "mailbox_password_required: set HS27_MAILBOX_PASSWORD or pass -PasswordPlaintext."
        }
        $securePassword = Read-Host -Prompt "Franz mailbox password for $Username" -AsSecureString
        $plainPassword = Convert-SecureStringToPlainText -SecureValue $securePassword
        if (-not $plainPassword) {
            throw "No mailbox password entered."
        }
        $env:HS27_MAILBOX_PASSWORD = $plainPassword
    }

    $proofResult = Invoke-PythonCapture -Arguments @(
        $proofScript,
        "--username", $Username,
        "--subject", $Subject
    )

    $proofResult.Output | ForEach-Object { $_ }

    if ($proofResult.ExitCode -ne 0) {
        throw "Inbox proof failed."
    }

    $parsed = @{}
    foreach ($line in $proofResult.Output) {
        $text = [string]$line
        if ($text -match "^[A-Za-z0-9_]+=") {
            $parts = $text -split "=", 2
            $parsed[$parts[0]] = $parts[1]
        }
    }

    if ($parsed["inbox_proof"] -ne "yes") {
        throw "Inbox proof did not return inbox_proof=yes."
    }

    $today = Get-Date -Format "yyyy-MM-dd"
    $latestFrom = $parsed["latest_from"]
    $latestDate = $parsed["latest_date"]
    $evidence = "Read-only IMAP proof ${today}: $Username INBOX contains subject '$Subject'. Latest matching header shows From=$latestFrom, Date=$latestDate. This closes the visible Franz inbox proof for the noreply SMTP path."

    $updateResult = Invoke-PythonCapture -Arguments @(
        $updateScript,
        "--id", "strato_mail_model_verified",
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
}
finally {
    if ($hadPreviousEnv) {
        $env:HS27_MAILBOX_PASSWORD = $previousEnv
    }
    else {
        Remove-Item Env:HS27_MAILBOX_PASSWORD -ErrorAction SilentlyContinue
    }
}
