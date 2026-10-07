<#
.SYNOPSIS
    Проверка установленных очередей CUPS IPP Everywhere и статуса дуплекса на клиенте Windows.
.DESCRIPTION
    Скрипт проверяет наличие очередей с драйвером Microsoft IPP Class Driver,
    состояние портов WSD и параметры двусторонней печати.
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ПРОВЕРКА ОЧЕРЕДЕЙ ПРИНТ-СЕРВЕРА НА WINDOWS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Поиск очередей, подключенных через servvm / IPP
$printers = Get-Printer | Where-Object { $_.Name -like "*servvm*" -or $_.DriverName -like "*IPP*" }

if ($printers.Count -eq 0) {
    Write-Host "`n[!] Очереди принт-сервера servvm не найдены на данном ПК." -ForegroundColor Yellow
    Write-Host "    Для подключения откройте: Параметры -> Устройства -> Принтеры и сканеры -> Добавить устройство.`n"
    exit 0
}

Write-Host "`n[+] Найденные очереди принт-сервера:" -ForegroundColor Green
$printers | Select-Object Name, DriverName, PortName, Shared | Format-Table -AutoSize

# 2. Детальная проверка конфигурации каждой очереди
foreach ($p in $printers) {
    Write-Host "`n--- Свойства принтера: $($p.Name) ---" -ForegroundColor Cyan
    try {
        $config = Get-PrintConfiguration -PrinterName $p.Name -ErrorAction Stop
        Write-Host "  Двусторонняя печать (DuplexingMode): $($config.DuplexingMode)"
        Write-Host "  Ориентация бумаги (PaperSize):      $($config.PaperSize)"
    } catch {
        Write-Host "  Не удалось получить параметры печати: $_" -ForegroundColor DarkGray
    }
}

Write-Host "`nПроверка завершена.`n" -ForegroundColor Green
