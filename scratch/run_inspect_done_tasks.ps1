$ErrorActionPreference = "Stop"

$scriptsDir = Join-Path "c:\WORKSPACE\FraWo" "scripts"
$proxmoxExec = Join-Path $scriptsDir "proxmox_windows_ssh_exec.ps1"

$pythonScriptPath = Join-Path "c:\WORKSPACE\FraWo" "scratch\inspect_done_tasks.py"
$pythonScriptBytes = [System.IO.File]::ReadAllBytes($pythonScriptPath)
$pythonScriptBase64 = [Convert]::ToBase64String($pythonScriptBytes)

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/inspect_done_tasks.py").write_bytes(base64.b64decode("$pythonScriptBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/inspect_done_tasks.py'
"@

$responseString = & $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve" | Out-String
Write-Output $responseString
