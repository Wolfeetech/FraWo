[CmdletBinding()]
param(
    [string]$BootstrapPath = "$env:LOCALAPPDATA\Homeserver2027\bootstrap\vaultwarden_admin_token.txt",
    [switch]$ReuseExistingToken
)

$ErrorActionPreference = "Stop"

function New-RandomToken {
    $json = python -c "import json, secrets; print(json.dumps({'token': secrets.token_urlsafe(32)}))"
    return (ConvertFrom-Json $json).token
}

function New-Argon2Hash {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Token
    )

    $json = python -c "import json, sys; from argon2 import PasswordHasher, Type; token = sys.argv[1]; ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16, type=Type.ID); print(json.dumps({'hash': ph.hash(token)}))" -- $Token
    return (ConvertFrom-Json $json).hash
}

$token = ""
if ($ReuseExistingToken -and (Test-Path $BootstrapPath)) {
    $token = (Get-Content -Path $BootstrapPath -Raw).Trim()
}
if ([string]::IsNullOrWhiteSpace($token)) {
    $token = New-RandomToken
}

$argon2Hash = New-Argon2Hash -Token $token

$bootstrapDir = Split-Path -Parent $BootstrapPath
if (-not (Test-Path $bootstrapDir)) {
    New-Item -ItemType Directory -Path $bootstrapDir -Force | Out-Null
}
Set-Content -Path $BootstrapPath -Value $token -NoNewline -Encoding utf8

$hashB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($argon2Hash))
$updatePython = @'
import base64
import os
import pathlib
import shutil
import time

path = pathlib.Path("/opt/homeserver2027/stacks/vaultwarden/.env")
backup = path.with_name(f"{path.name}.bak.{int(time.time())}")
hashed_token = base64.b64decode(os.environ["VW_ADMIN_TOKEN_HASH_B64"]).decode()

original_lines = path.read_text(encoding="utf-8").splitlines()
shutil.copy2(path, backup)

result = []
replaced = False
for raw in original_lines:
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or "=" not in raw:
        result.append(raw)
        continue
    key, _value = raw.split("=", 1)
    if key == "ADMIN_TOKEN":
        result.append(f"ADMIN_TOKEN={hashed_token}")
        replaced = True
        continue
    result.append(raw)

if not replaced:
    result.append(f"ADMIN_TOKEN={hashed_token}")

path.write_text("\n".join(result).rstrip() + "\n", encoding="utf-8")
print(f"vaultwarden_env_backup={backup}")
print("vaultwarden_admin_token_mode=hashed")
'@
$updatePythonB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($updatePython))

$remoteCommand = @"
set -euo pipefail
export VW_ADMIN_TOKEN_HASH_B64='$hashB64'
export VW_UPDATE_SCRIPT_B64='$updatePythonB64'
pct exec 120 -- sh -lc 'echo "`$VW_UPDATE_SCRIPT_B64" | base64 -d >/tmp/vaultwarden_admin_token_update.py && python3 /tmp/vaultwarden_admin_token_update.py && rm -f /tmp/vaultwarden_admin_token_update.py'
pct exec 120 -- sh -lc 'cd /opt/homeserver2027/stacks/vaultwarden && if docker compose version >/dev/null 2>&1; then docker compose up -d >/dev/null; else docker-compose up -d >/dev/null; fi'
pct exec 120 -- sh -lc 'sleep 2; for i in `$(seq 1 60); do status=`$(docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" vaultwarden 2>/dev/null || true); echo vaultwarden_health=`${status}; if [ "`${status}" = "healthy" ] || [ "`${status}" = "running" ]; then exit 0; fi; sleep 2; done; exit 1'
pct exec 120 -- sh -lc 'docker logs --tail 40 vaultwarden 2>&1'
"@

& "$PSScriptRoot\proxmox_windows_ssh_exec.ps1" -RemoteCommand $remoteCommand
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Output "bootstrap_path=$BootstrapPath"
Write-Output "vaultwarden_admin_token_plaintext_saved=yes"
