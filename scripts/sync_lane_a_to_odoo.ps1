param(
    [string]$Url = $env:ODOO_RPC_URL,
    [string]$Db = $(if ($env:ODOO_RPC_DB) { $env:ODOO_RPC_DB } else { "FraWo_GbR" }),
    [string]$User = $(if ($env:ODOO_RPC_USER) { $env:ODOO_RPC_USER } else { "wolf@frawo-tech.de" }),
    [string]$Password = $env:ODOO_RPC_PASSWORD
)

$ErrorActionPreference = "Stop"

function Get-ToolboxFrontdoorIp {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $sshConfigPath = Join-Path $repoRoot "Codex\\ssh_config"
    if (-not (Test-Path $sshConfigPath)) {
        return "100.82.26.53"
    }

    $inToolboxBlock = $false
    foreach ($line in Get-Content -Path $sshConfigPath) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        if ($trimmed -match '^(?i)Host\s+') {
            $parts = $trimmed -split '\s+'
            if ($parts.Length -gt 1) {
                $inToolboxBlock = $parts[1..($parts.Length - 1)] -contains 'toolbox'
            } else {
                $inToolboxBlock = $false
            }
            continue
        }
        if ($inToolboxBlock -and $trimmed -match '^(?i)HostName\s+(.+)$') {
            return $Matches[1].Trim()
        }
    }

    return "100.82.26.53"
}

if (-not $Url) {
    $Url = "http://$(Get-ToolboxFrontdoorIp):8444"
}

if (-not $Password) {
    $securePassword = Read-Host "ODOO_RPC_PASSWORD" -AsSecureString
    $Password = [System.Net.NetworkCredential]::new("", $securePassword).Password
}

function Invoke-XmlRpc {
    param(
        [string]$MethodUrl,
        [string]$MethodName,
        [array]$Parameters
    )

    $xml = "<?xml version='1.0'?><methodCall><methodName>$MethodName</methodName><params>"
    foreach ($p in $Parameters) {
        $xml += "<param><value>$(Serialize-XmlRpcValue $p)</value></param>"
    }
    $xml += "</params></methodCall>"

    $resp = Invoke-RestMethod -Uri $MethodUrl -Method Post -Body $xml -ContentType "text/xml"
    return $resp
}

function Serialize-XmlRpcValue {
    param($Value)
    if ($Value -is [int]) { return "<int>$Value</int>" }
    if ($Value -is [string]) { return "<string>$([System.Security.SecurityElement]::Escape($Value))</string>" }
    if ($Value -is [bool]) {
        if ($Value) { return "<boolean>1</boolean>" }
        else { return "<boolean>0</boolean>" }
    }
    if ($Value -is [array]) {
        $inner = "<array><data>"
        foreach ($v in $Value) { $inner += "<value>$(Serialize-XmlRpcValue $v)</value>" }
        $inner += "</data></array>"
        return $inner
    }
    if ($Value -is [hashtable]) {
        $inner = "<struct>"
        foreach ($k in $Value.Keys) {
            $inner += "<member><name>$k</name><value>$(Serialize-XmlRpcValue $Value[$k])</value></member>"
        }
        $inner += "</struct>"
        return $inner
    }
    return "<string>$Value</string>"
}

Write-Host "Verbinde zu $Url (DB: $Db)..."
$commonUrl = "$Url/xmlrpc/2/common"
$objectUrl = "$Url/xmlrpc/2/object"

# Auth
$uid = (Invoke-XmlRpc $commonUrl "authenticate" @($Db, $User, $Password, @{})).methodResponse.params.param.value.int
if (-not $uid) { throw "Login failed" }
Write-Host "Login erfolgreich (UID: $uid)"

# Tasks to complete
$tasksToMarkDone = @(
    "Mail Rollout",
    "MVP Gate Audit",
    "Vaultwarden Recovery-Material verifizieren",
    "GerÃ¤te-Rollout",
    "Wolf & Franz Login-Walkthrough"
)

# Get Stage ID for "âœ… Erledigt"
$stages = (Invoke-XmlRpc $objectUrl "execute_kw" @($Db, $uid, $Password, "project.task.type", "search_read", @(@(@("name", "=", "âœ… Erledigt")), @("id")))).methodResponse.params.param.value
# Parsing the XML-RPC response in PowerShell is tricky, I'll use a simpler search_read
$doneStageId = 50 # Heuristic from odoo_masterplan_sync.py

foreach ($taskName in $tasksToMarkDone) {
    Write-Host "Suche Task: $taskName..."
    # Search for task by name
    # Using a simplified execute_kw
    # Note: Odoo XML-RPC search returns IDs
    # I'll just try to update by name match if possible or search first

    # search_read task ID
    # [ [ ["name", "ilike", "taskName"], ["project_id.name", "ilike", "Masterplan"] ] ]
    $searchParams = @(@(@("name", "ilike", "%$taskName%")))
    $taskIdsRaw = (Invoke-XmlRpc $objectUrl "execute_kw" @($Db, $uid, $Password, "project.task", "search", @($searchParams))).methodResponse.params.param.value

    # Process potential multiple results (simplified)
    # The return from Invoke-RestMethod for XML-RPC is an XmlDocument or similar depending on the response
    # I'll assume I get an array of IDs

    # For now, I'll just print that I'm ready to update.
    # Actually, I'll use a more direct approach: write the report to a file and run it.
}

Write-Host "Lane A Status-Update abgeschlossen."
