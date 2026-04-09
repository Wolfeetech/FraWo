# Professional Network Routing Fix for StudioPC
# Goal: Prioritize WLAN (EasyBox) for Internet and Ethernet (UCG) for Management.

# 1. Identify Interfaces
$wlan = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway.NextHop -eq "192.168.2.1" }
$ethernet = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway.NextHop -eq "10.1.0.1" }

if ($null -eq $wlan -or $null -eq $ethernet) {
    Write-Error "Could not identify both interfaces. Please ensure you are connected to both EasyBox and UCG."
    exit
}

Write-Host "Found WLAN (Index $($wlan.InterfaceIndex)) and Ethernet (Index $($ethernet.InterfaceIndex))."

# 2. Set Metrics (Requires Admin)
Write-Host "Setting WLAN metric to 10 (Highest Priority for Internet)..."
Set-NetIPInterface -InterfaceIndex $wlan.InterfaceIndex -InterfaceMetric 10

Write-Host "Setting Ethernet metric to 40 (Management Priority)..."
Set-NetIPInterface -InterfaceIndex $ethernet.InterfaceIndex -InterfaceMetric 40

# 3. Verify
Write-Host "`nCurrent Routing Table (Default Routes):"
Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Sort-Object Metric

Write-Host "`nTesting Connectivity..."
Test-NetConnection google.com
Test-NetConnection 10.1.0.1
