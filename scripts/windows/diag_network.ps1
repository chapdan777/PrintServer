# Диагностика сети, IP, шлюза, DNS и пингов
Write-Host "=== IP КОНФИГУРАЦИЯ ==="
Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer | Format-List

Write-Host "=== АКТИВНЫЕ СЕТЕВЫЕ АДАПТЕРЫ ==="
Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress | Format-Table -AutoSize

Write-Host "=== ПРОВЕРКА СЕТЕВОЙ СТАБИЛЬНОСТИ (PING) ==="
$pingGw = Test-Connection -ComputerName 192.168.2.1 -Count 5
Write-Host "Пинг до шлюза (192.168.2.1):"
$pingGw | Select-Object Address, ResponseTime, StatusCode | Format-Table -AutoSize

$pingDns = Test-Connection -ComputerName 8.8.8.8 -Count 5
Write-Host "Пинг до интернета (8.8.8.8):"
$pingDns | Select-Object Address, ResponseTime, StatusCode | Format-Table -AutoSize

Write-Host "=== DNS ЗАПРОСЫ ==="
Resolve-DnsName ya.ru -ErrorAction SilentlyContinue | Select-Object Name, IPAddress | Format-Table -AutoSize
