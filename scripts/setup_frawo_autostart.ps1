# Combined Autostart Setup for FraWo OpenClaw Agent & Telegram Bridge
# Registers Windows Task Scheduler tasks to start these services automatically at logon.

$WorkDir    = "c:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo"
$PythonExe  = "C:\Python313\python.exe"

# Task 1: OpenClaw Agent
$AgentTaskName   = "OpenClaw-Agent"
$AgentScript     = "$WorkDir\openclaw_web_server.py"

Write-Host "Setting up OpenClaw Agent Autostart..."
if (Get-ScheduledTask -TaskName $AgentTaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $AgentTaskName -Confirm:$false
    Write-Host "  Removed existing agent task."
}
$AgentAction = New-ScheduledTaskAction -Execute $PythonExe -Argument $AgentScript -WorkingDirectory $WorkDir
$AgentTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$AgentSettings = New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartInterval (New-TimeSpan -Minutes 1) -RestartCount 5 -StartWhenAvailable
$AgentPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$AgentTask = New-ScheduledTask -Action $AgentAction -Trigger $AgentTrigger -Settings $AgentSettings -Principal $AgentPrincipal -Description "OpenClaw AI Agent (Port 5555)"
Register-ScheduledTask -TaskName $AgentTaskName -InputObject $AgentTask -Force | Out-Null
Write-Host "✅ Task '$AgentTaskName' registered successfully!"

# Task 2: Telegram Bridge
$BridgeTaskName  = "OpenClaw-Telegram-Bridge"
$BridgeScript    = "$WorkDir\scripts\business\telegram_openclaw_bridge.py"

Write-Host "Setting up Telegram Bridge Autostart..."
if (Get-ScheduledTask -TaskName $BridgeTaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $BridgeTaskName -Confirm:$false
    Write-Host "  Removed existing bridge task."
}
$BridgeAction = New-ScheduledTaskAction -Execute $PythonExe -Argument $BridgeScript -WorkingDirectory $WorkDir
$BridgeTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$BridgeSettings = New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartInterval (New-TimeSpan -Minutes 1) -RestartCount 5 -StartWhenAvailable
$BridgePrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$BridgeTask = New-ScheduledTask -Action $BridgeAction -Trigger $BridgeTrigger -Settings $BridgeSettings -Principal $BridgePrincipal -Description "OpenClaw Telegram-to-Agent Bridge"
Register-ScheduledTask -TaskName $BridgeTaskName -InputObject $BridgeTask -Force | Out-Null
Write-Host "✅ Task '$BridgeTaskName' registered successfully!"

Write-Host ""
Write-Host "All tasks set up successfully!"
Get-ScheduledTask -TaskName "OpenClaw-*" | Select-Object TaskName, State, Description
