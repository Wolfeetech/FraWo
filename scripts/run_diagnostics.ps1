$ErrorActionPreference = "Continue"

Write-Host "Running Diagnostics..."
$sshConfig = "Codex/ssh_config"

$ramOutput = ssh -F $sshConfig pve-anker "free -h; echo '---'; qm list" 2>&1
$ramOutput | Out-File -FilePath "scratch/ram_check.txt" -Encoding utf8

$nfsOutput = ssh -F $sshConfig pve-anker "mount | grep nfs; cat /etc/pve/storage.cfg" 2>&1
$nfsOutput | Out-File -FilePath "scratch/nfs_check.txt" -Encoding utf8

$pbsOutput = ssh -F $sshConfig pve-anker "qm status 240" 2>&1
$pbsOutput | Out-File -FilePath "scratch/pbs_check.txt" -Encoding utf8

$dnsOutput = nslookup funk.frawo-tech.de 1.1.1.1 2>&1
$dnsOutput | Out-File -FilePath "scratch/dns_check.txt" -Encoding utf8

$radioOutput = ssh -F $sshConfig pve-anker "pct exec 130 -- docker ps | grep azuracast" 2>&1
$radioOutput | Out-File -FilePath "scratch/radio_check.txt" -Encoding utf8

Write-Host "Diagnostics complete."
