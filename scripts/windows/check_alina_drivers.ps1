$env:COMPUTERNAME
Get-PrinterDriver | Select-Object Name, MajorVersion, PrinterEnvironment | Format-Table -AutoSize
