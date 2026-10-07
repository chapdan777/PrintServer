# Проверка журнала событий на падения приложений (Event ID 1000, 1001, 1002) за последние 7 дней
Write-Host "=== ЖУРНАЛ СБОЕВ ПРИЛОЖЕНИЙ (Application Error / Hang) ==="
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000,1001,1002; StartTime=(Get-Date).AddDays(-7)} -MaxEvents 15 -ErrorAction SilentlyContinue | 
    Select-Object TimeCreated, Id, @{N='Message'; E={$_.Message.Split("`n")[0..3] -join " | "}} | Format-Table -Wrap

Write-Host "`n=== ЖУРНАЛ НЕХВАТКИ ПАМЯТИ (Resource-Exhaustion-Detector / Event 2004) ==="
Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004; StartTime=(Get-Date).AddDays(-14)} -MaxEvents 5 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, Id, @{N='Message'; E={$_.Message.Split("`n")[0..2] -join " "}} | Format-Table -Wrap

Write-Host "`n=== СЛУЖБА ДИСПЕТЧЕРА ПЕЧАТИ (Spooler) И СБОИ СИСТЕМЫ ==="
Get-Service spooler | Select-Object Name, Status, StartType | Format-Table
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Service Control Manager'; Id=7031,7034; StartTime=(Get-Date).AddDays(-7)} -MaxEvents 10 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, Id, Message | Format-Table -Wrap

Write-Host "`n=== ПРИНТЕРЫ И ОЧЕРЕДИ ПЕЧАТИ ==="
Get-Printer | Select-Object Name, DriverName, PortName, PrinterStatus, JobCount | Format-Table -AutoSize
Get-PrintJob -PrinterName * -ErrorAction SilentlyContinue | Select-Object PrinterName, Id, DocumentName, JobStatus, Size | Format-Table -AutoSize

Write-Host "`n=== ФАЙЛЫ В ОЧЕРЕДИ ПЕЧАТИ (SPOOL) ==="
Get-ChildItem -Path "C:\Windows\System32\spool\PRINTERS" -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
