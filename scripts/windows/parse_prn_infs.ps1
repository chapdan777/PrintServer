$infs = Get-ChildItem -Path "C:\Windows\System32\DriverStore\FileRepository" -Filter "prnms*.inf" -Recurse -ErrorAction SilentlyContinue

foreach ($inf in $infs) {
    $content = Get-Content $inf.FullName -ErrorAction SilentlyContinue
    $lines = $content | Select-String -Pattern '\[Strings\]' -Context 0, 50
    $driverNames = $content | Select-String -Pattern '^\s*".*Class Driver.*"'
    Write-Host "FILE: $($inf.Name)"
    $driverNames | ForEach-Object { Write-Host "  Driver: $($_.Line.Trim())" }
}

Write-Host "`n=== PRINT ENVIRONMENTS ==="
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments" | ForEach-Object {
    Write-Host "ENV: $($_.PSChildName)"
    Get-ChildItem $_.PsPath | ForEach-Object {
        Write-Host "  SUB: $($_.PSChildName)"
        Get-ChildItem $_.PsPath | ForEach-Object {
            Write-Host "    ENTRY: $($_.PSChildName)"
        }
    }
}
