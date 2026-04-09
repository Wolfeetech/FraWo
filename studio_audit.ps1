
$audit = @{
    LargeFiles = Get-ChildItem -Path $HOME -Recurse -File -ErrorAction SilentlyContinue | Where-Object {$_.Length -gt 500MB} | Sort-Object Length -Descending | Select-Object FullName, @{N='SizeGB';E={[math]::Round($_.Length / 1GB, 2)}}, LastWriteTime
    FolderSizes = Get-ChildItem -Path $HOME -Directory | ForEach-Object { $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; [pscustomobject]@{ Name = $_.Name; SizeGB = [math]::Round($size / 1GB, 4) } } | Sort-Object SizeGB -Descending
    NonMSProcesses = Get-Process | Where-Object {$_.Company -notmatch 'Microsoft' -and $_.Company -ne $null} | Select-Object Name, Company, @{N='WS_MB';E={[math]::Round($_.WorkingSet / 1MB, 2)}} | Sort-Object WS_MB -Descending | Select-Object -First 20
    StartupItems = Get-CimInstance -ClassName Win32_StartupCommand | Select-Object Name, Command, LocationUser
    RunningServices = Get-Service | Where-Object {$_.Status -eq 'Running' -and $_.DisplayName -notmatch 'Microsoft'} | Select-Object DisplayName, Status
}

"--- ARTIFACT: LARGE FILES ---"
$audit.LargeFiles | Format-Table -AutoSize
"--- ARTIFACT: FOLDER SIZES ---"
$audit.FolderSizes | Format-Table -AutoSize
"--- ARTIFACT: NON-MS PROCESSES ---"
$audit.NonMSProcesses | Format-Table -AutoSize
"--- ARTIFACT: STARTUP ITEMS ---"
$audit.StartupItems | Format-Table -AutoSize
"--- ARTIFACT: NON-MS SERVICES ---"
$audit.RunningServices | Format-Table -AutoSize
