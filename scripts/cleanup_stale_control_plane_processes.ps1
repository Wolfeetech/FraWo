param()

$threshold = (Get-Date).AddHours(-1)

$staleSsh = Get-Process -Name ssh -ErrorAction SilentlyContinue |
  Where-Object {
    try {
      $_.StartTime -lt $threshold
    } catch {
      $false
    }
  } |
  ForEach-Object {
    Get-CimInstance Win32_Process -Filter ("ProcessId = " + $_.Id)
  }

$stalePwsh = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq 'powershell.exe' -and
    $_.CommandLine -match 'prove_strato_mail_model\.ps1'
  }

$targets = @()
if ($staleSsh) {
  $targets += @($staleSsh)
}
if ($stalePwsh) {
  $targets += @($stalePwsh)
}
$targets = @($targets | Where-Object { $_ } | Sort-Object ProcessId -Unique)

foreach ($proc in $targets) {
  try {
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
  } catch {
  }
}

$killed = @($targets | Select-Object -ExpandProperty ProcessId)
Write-Output ("killed_count={0}" -f $killed.Count)
if ($killed.Count -gt 0) {
  Write-Output ("killed_ids={0}" -f ($killed -join ','))
}
