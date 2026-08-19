$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$pythonScriptPath = Join-Path $PSScriptRoot "odoo_shell_deploy.py"
$pythonScriptBytes = [System.IO.File]::ReadAllBytes($pythonScriptPath)
$pythonScriptBase64 = [Convert]::ToBase64String($pythonScriptBytes)

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/odoo_shell_deploy.py").write_bytes(base64.b64decode("$pythonScriptBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/odoo_shell_deploy.py
docker-compose restart web'
"@

Write-Host "Deploying v3 Website via Odoo Shell..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Deployment complete."
