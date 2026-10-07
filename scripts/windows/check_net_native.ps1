# Стандартные утилиты Windows (не зависящие от WMI)
Write-Host "=== IPCONFIG /ALL ==="
ipconfig /all

Write-Host "`n=== PING SHLYUZ (192.168.2.1) ==="
ping 192.168.2.1 -n 4

Write-Host "`n=== PING INTERNET (8.8.8.8) ==="
ping 8.8.8.8 -n 4
