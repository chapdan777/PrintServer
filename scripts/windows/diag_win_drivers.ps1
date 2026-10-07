$ErrorActionPreference = "Continue"

Write-Host "=== HOST INFO ==="
Write-Host "ComputerName: $env:COMPUTERNAME"
Write-Host "User: $env:USERNAME"
[System.Environment]::OSVersion.VersionString
Write-Host "Is64BitOS: $([System.Environment]::Is64BitOperatingSystem)"

Write-Host "`n=== REGISTRY PRINT DRIVERS (x86) ==="
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows NT x86\Drivers" -ErrorAction SilentlyContinue | ForEach-Object {
    $ver = $_.PSChildName
    Get-ChildItem $_.PSPath | ForEach-Object {
        [PSCustomObject]@{
            Environment = "Windows NT x86"
            Version = $ver
            DriverName = $_.PSChildName
        }
    }
} | Format-Table -AutoSize

Write-Host "`n=== REGISTRY PRINT DRIVERS (x64) ==="
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Drivers" -ErrorAction SilentlyContinue | ForEach-Object {
    $ver = $_.PSChildName
    Get-ChildItem $_.PSPath | ForEach-Object {
        [PSCustomObject]@{
            Environment = "Windows x64"
            Version = $ver
            DriverName = $_.PSChildName
        }
    }
} | Format-Table -AutoSize

Write-Host "`n=== PNPUTIL ENUM-DRIVERS (FILTER PRINTERS / PCL / IPP) ==="
& pnputil.exe /enum-drivers | Select-String -Pattern "prn|print|pcl|ipp|hp" -Context 1,3

Write-Host "`n=== DRIVERSTORE INF FILES FOR PCL6 / IPP ==="
Get-ChildItem -Path "C:\Windows\System32\DriverStore\FileRepository" -Filter "*prn*.inf" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
