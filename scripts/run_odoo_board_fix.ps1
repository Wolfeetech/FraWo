$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$pythonScriptPath = Join-Path $PSScriptRoot "odoo_board_fix.py"
$pythonScriptBytes = [System.IO.File]::ReadAllBytes($pythonScriptPath)
$pythonScriptBase64 = [Convert]::ToBase64String($pythonScriptBytes)

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/odoo_board_fix.py").write_bytes(base64.b64decode("$pythonScriptBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http < /tmp/odoo_board_fix.py'
"@

Write-Host "Updating Odoo Board and Language..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Odoo Board Update Complete."
