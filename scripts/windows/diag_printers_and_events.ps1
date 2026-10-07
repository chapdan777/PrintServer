# Чтение принтеров из реестра (не требует WMI/CIM)
Write-Host "=== ПРИНТЕРЫ ИЗ РЕЕСТРА ==="
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Printers" | ForEach-Object {
    $props = Get-ItemProperty $_.PsPath
    [PSCustomObject]@{
        PrinterName = $_.PSChildName
        Driver = $props."Printer Driver"
        Port = $props.Port
    }
} | Format-Table -AutoSize

Write-Host "`n=== ВСЕ СБОИ ПРИЛОЖЕНИЙ (Event ID 1000) ЗА 30 ДНЕЙ ==="
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000; StartTime=(Get-Date).AddDays(-30)} -MaxEvents 30 -ErrorAction SilentlyContinue |
    ForEach-Object {
        $msg = $_.Message
        $appName = if ($msg -match 'Имя сбойного приложения:\s*([^\r\n,]+)') { $matches[1] } else { 'Unknown' }
        $modName = if ($msg -match 'Имя сбойного модуля:\s*([^\r\n,]+)') { $matches[1] } else { 'Unknown' }
        $code = if ($msg -match 'Код исключения:\s*([^\r\n,]+)') { $matches[1] } else { 'Unknown' }
        [PSCustomObject]@{
            Date = $_.TimeCreated.ToString('dd.MM.yyyy HH:mm')
            Application = $appName
            Module = $modName
            ExceptionCode = $code
        }
    } | Format-Table -AutoSize
