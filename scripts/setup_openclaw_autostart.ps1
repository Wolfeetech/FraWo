# OpenClaw Autostart - Windows Task Scheduler
# Startet openclaw_web_server.py automatisch beim Windows-Login
# Aufruf: .\setup_openclaw_autostart.ps1

$TaskName   = "OpenClaw-Agent"
$WorkDir    = "c:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo"
$Script     = "$WorkDir\openclaw_web_server.py"
$LogFile    = "$WorkDir\openclaw_server.log"
$ErrFile    = "$WorkDir\openclaw_server_error.log"
$PythonExe  = (Get-Command python).Source

Write-Host "Setting up OpenClaw autostart task..."
Write-Host "  Python: $PythonExe"
Write-Host "  Script: $Script"
Write-Host "  WorkDir: $WorkDir"

# Remove existing task if present
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "  Removed existing task."
}

# Build the action: python openclaw_web_server.py > logs
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $Script `
    -WorkingDirectory $WorkDir

# Trigger: At logon of current user
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Settings: restart on failure, hidden window
$Settings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 5 `
    -StartWhenAvailable

# Principal: run as current user
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

$Task = New-ScheduledTask `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "OpenClaw AI Agent - FraWo Homeserver 2027 Control Plane (Port 5555)"

Register-ScheduledTask -TaskName $TaskName -InputObject $Task -Force | Out-Null

Write-Host ""
Write-Host "✅ Task '$TaskName' registered successfully!"
Write-Host "   Starts automatically at logon for user: $env:USERNAME"
Write-Host "   To test: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "   To stop:  Stop-ScheduledTask -TaskName '$TaskName'"
Write-Host "   To view:  Get-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "Status check after registration:"
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, Description
