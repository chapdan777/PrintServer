#!/usr/bin/env python3
"""
Диагностика драйверов на Windows-клиенте ALINA (192.168.2.74).
Строго READ-ONLY.
"""
import sys
import base64
import subprocess

ps_script = r"""
$ErrorActionPreference = "Continue"

Write-Host "=== 1. ПРОВЕРКА ТОЧНЫХ ИМЕН ДРАЙВЕРОВ В SPOOLER ==="
$d1 = Get-PrinterDriver -Name "Microsoft PCL6 Class Driver" -ErrorAction SilentlyContinue
$d2 = Get-PrinterDriver -Name "Microsoft IPP Class Driver" -ErrorAction SilentlyContinue

Write-Host "Поиск 'Microsoft PCL6 Class Driver':"
if ($d1) { $d1 | Select-Object Name, MajorVersion, PrinterEnvironment | Format-List } else { Write-Host "НЕ НАЙДЕН в Get-PrinterDriver" }

Write-Host "Поиск 'Microsoft IPP Class Driver':"
if ($d2) { $d2 | Select-Object Name, MajorVersion, PrinterEnvironment | Format-List } else { Write-Host "НЕ НАЙДЕН в Get-PrinterDriver" }

Write-Host "`n=== 2. ВСЕ УСТАНОВЛЕННЫЕ ДРАЙВЕРЫ ПЕЧАТИ (Get-PrinterDriver) ==="
try {
    Get-PrinterDriver | Select-Object Name, MajorVersion, PrinterEnvironment | Format-Table -AutoSize
} catch {
    Write-Host "Ошибка Get-PrinterDriver: $_"
}

Write-Host "`n=== 3. РЕГИСТРАЦИЯ ДРАЙВЕРОВ В РЕЕСТРЕ (Print Environments) ==="
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows NT x86\Drivers" -ErrorAction SilentlyContinue | ForEach-Object {
    $ver = $_.PSChildName
    Get-ChildItem $_.PsPath | ForEach-Object {
        [PSCustomObject]@{
            Environment = "Windows NT x86"
            Version = $ver
            DriverName = $_.PSChildName
        }
    }
} | Format-Table -AutoSize

Write-Host "`n=== 4. PNPUTIL /ENUM-DRIVERS (ПРИНТЕРНЫЕ ПАКЕТЫ) ==="
& pnputil.exe /enum-drivers | Select-String -Pattern "prn|print|pcl|ipp|hp" -Context 1,2

Write-Host "`n=== 5. IN-BOX INF В DRIVERSTORE (C:\Windows\System32\DriverStore\FileRepository\prnms*.inf) ==="
$infs = Get-ChildItem -Path "C:\Windows\System32\DriverStore\FileRepository" -Filter "prnms*.inf" -Recurse -ErrorAction SilentlyContinue
foreach ($inf in $infs) {
    Write-Host "Файл: $($inf.FullName)"
    $content = Get-Content $inf.FullName -ErrorAction SilentlyContinue
    $classDrivers = $content | Select-String -Pattern 'Class Driver|PCL6|IPP'
    if ($classDrivers) {
        $classDrivers | Select-Object -First 5 | ForEach-Object { Write-Host "    $($_.Line.Trim())" }
    }
}
"""

b64 = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')

expect_script = f"""#!/usr/bin/expect -f
set timeout 60
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Alina@192.168.2.74 powershell -NoProfile -EncodedCommand {b64}
expect {{
    "yes/no" {{
        send "yes\\r"
        exp_continue
    }}
    "password:" {{
        send "1\\r"
    }}
    timeout {{
        puts "Timeout connecting to 192.168.2.74"
        exit 1
    }}
    eof {{
        puts "Connection closed"
        exit 1
    }}
}}
expect {{
    timeout {{
        puts "Timeout waiting for command output"
        exit 1
    }}
    eof
}}
"""

proc = subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)
print(proc.stdout)
if proc.stderr:
    print("STDERR:", proc.stderr, file=sys.stderr)
