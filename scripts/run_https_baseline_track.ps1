[CmdletBinding()]
param(
    [string]$PythonCommand = ""
)

$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
$auditScript = Join-Path $PSScriptRoot "run_https_baseline_audit.py"
$gateScript = Join-Path $PSScriptRoot "https_baseline_gate.py"
$auditRoot = Join-Path $rootDir "artifacts\https_baseline_audit"

function Resolve-PythonCommand {
    param(
        [string]$Requested
    )

    if ($Requested) {
        return @{
            FilePath = $Requested
            Arguments = @()
        }
    }

    function Test-Interpreter {
        param(
            [string]$FilePath,
            [string[]]$Arguments = @()
        )

        try {
            & $FilePath @($Arguments + "--version") *> $null
            return ($LASTEXITCODE -eq 0)
        }
        catch {
            return $false
        }
    }

    foreach ($candidate in @("python", "py")) {
        if ((Get-Command $candidate -ErrorAction SilentlyContinue) -and (Test-Interpreter -FilePath $candidate)) {
            return @{
                FilePath = $candidate
                Arguments = @()
            }
        }
    }

    if ((Get-Command "wsl" -ErrorAction SilentlyContinue) -and (Test-Interpreter -FilePath "wsl" -Arguments @("python3"))) {
        return @{
            FilePath = "wsl"
            Arguments = @("python3")
        }
    }

    throw "python_command_not_found"
}

$python = Resolve-PythonCommand -Requested $PythonCommand

function Convert-PathForInterpreter {
    param(
        [string]$Path,
        [hashtable]$Interpreter
    )

    if ($Interpreter.FilePath -ne "wsl") {
        return $Path
    }

    $resolved = Resolve-Path -LiteralPath $Path
    $windowsPath = $resolved.ProviderPath
    if ($windowsPath -match '^([A-Za-z]):\\(.*)$') {
        $drive = $matches[1].ToLowerInvariant()
        $rest = ($matches[2] -replace '\\', '/')
        return "/mnt/$drive/$rest"
    }

    throw "wsl_path_conversion_failed: $windowsPath"
}

Push-Location $rootDir
try {
    $auditScriptPath = Convert-PathForInterpreter -Path $auditScript -Interpreter $python
    & $python.FilePath @($python.Arguments + $auditScriptPath)
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    $latestAuditDir = Get-ChildItem $auditRoot -Directory |
        Where-Object { $_.Name -match '^\d{8}_\d{6}$' } |
        Sort-Object Name |
        Select-Object -Last 1

    if (-not $latestAuditDir) {
        throw "https_baseline_audit_summary_not_found"
    }

    $summaryPath = Join-Path $latestAuditDir.FullName "summary.tsv"
    $gateScriptPath = Convert-PathForInterpreter -Path $gateScript -Interpreter $python
    $summaryInterpreterPath = Convert-PathForInterpreter -Path $summaryPath -Interpreter $python
    & $python.FilePath @($python.Arguments + $gateScriptPath + $summaryInterpreterPath)
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
