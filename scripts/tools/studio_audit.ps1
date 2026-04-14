
function Get-DirSize {
    param([string]$path)
    try {
        $files = Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue
        if ($null -eq $files) { return 0 }
        $size = ($files | Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1GB, 4)
    } catch {
        return -1
    }
}

$userHome = $HOME
$dirs = Get-ChildItem -Path $userHome -Directory

"--- FOLDER SIZES ---"
foreach ($d in $dirs) {
    $size = Get-DirSize $d.FullName
    "$size GB : $($d.Name)"
}

"--- TOP 20 LARGE FILES (>250MB) ---"
Get-ChildItem -Path $userHome -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -gt 250MB } | 
    Sort-Object Length -Descending | 
    Select-Object FullName, @{N='SizeGB';E={[math]::Round($_.Length / 1GB, 3)}}, LastWriteTime | 
    Select-Object -First 20 | Format-Table -AutoSize

"--- NON-MS PROCESSES ---"
Get-Process | Where-Object { $_.Company -notmatch 'Microsoft' -and $null -ne $_.Company } | 
    Select-Object Name, Company, @{N='WS_MB';E={[math]::Round($_.WorkingSet / 1MB, 2)}} | 
    Sort-Object WS_MB -Descending | Select-Object -First 20 | Format-Table -AutoSize

"--- RUNNING NON-MS SERVICES ---"
Get-Service | Where-Object { $_.Status -eq 'Running' -and $_.DisplayName -notmatch 'Microsoft' } | 
    Select-Object DisplayName, Status | Format-Table -AutoSize
