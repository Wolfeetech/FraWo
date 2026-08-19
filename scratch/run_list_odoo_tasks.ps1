$ErrorActionPreference = "Stop"

$scriptsDir = Join-Path "c:\WORKSPACE\FraWo" "scripts"
$proxmoxExec = Join-Path $scriptsDir "proxmox_windows_ssh_exec.ps1"

$pythonScriptPath = Join-Path "c:\WORKSPACE\FraWo" "scratch\list_odoo_tasks.py"
$pythonScriptBytes = [System.IO.File]::ReadAllBytes($pythonScriptPath)
$pythonScriptBase64 = [Convert]::ToBase64String($pythonScriptBytes)

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/list_odoo_tasks.py").write_bytes(base64.b64decode("$pythonScriptBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/list_odoo_tasks.py'
"@

$responseString = & $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve" | Out-String
try {
    $json = $responseString | ConvertFrom-Json
    if ($null -ne $json -and $null -ne $json.exited) {
        if ($json.'out-data') {
            $out = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($json.'out-data'))
            Write-Output "--- STDOUT ---"
            Write-Output $out
        }
        if ($json.'err-data') {
            $err = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($json.'err-data'))
            Write-Output "--- STDERR ---"
            Write-Output $err
        }
        if ($json.exitcode -ne 0) {
            Write-Error "Command exited with code $($json.exitcode)"
        }
    } else {
        Write-Output "Raw response is not guest-exec JSON:"
        Write-Output $responseString
    }
} catch {
    Write-Output "Failed to parse response as JSON. Raw response:"
    Write-Output $responseString
}

