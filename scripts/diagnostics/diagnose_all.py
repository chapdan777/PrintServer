#!/usr/bin/env python3
"""
Комплексная диагностика:
1. ALINA (Windows 10 LTSC x86) через SSH (проверяем 192.168.2.74 и 192.168.2.72)
2. Samba 4.22.11 на 192.168.2.141
3. CUPS на 192.168.2.141
Все проверки СТРОГО READ-ONLY.
"""
import os
import sys
import base64
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common_env

SERVER_HOST = os.getenv("LOCAL_SERVER_HOST", "192.168.2.141")
SERVER_USER = os.getenv("LOCAL_SERVER_USER", "user")
SERVER_PASSWORD = os.getenv("LOCAL_SERVER_PASSWORD", "1")

def ssh_server(cmd, timeout=60):
    expect_script = f"""#!/usr/bin/expect -f
set timeout {timeout}
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {SERVER_USER}@{SERVER_HOST} {{ {cmd} }}
expect {{
    "yes/no" {{ send "yes\\r"; exp_continue }}
    "password:" {{ send "{SERVER_PASSWORD}\\r" }}
    timeout {{ puts "Timeout connecting to {SERVER_HOST}"; exit 1 }}
    eof {{ puts "Connection closed"; exit 1 }}
}}
expect {{
    timeout {{ puts "Timeout waiting for server output"; exit 1 }}
    eof
}}
"""
    proc = subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)
    return proc.stdout

def win_ps(ps_code, host="192.168.2.72", user="ssh", password="ssh", timeout=60):
    b64 = base64.b64encode(ps_code.encode('utf-16le')).decode('ascii')
    expect_script = f"""#!/usr/bin/expect -f
set timeout {timeout}
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {user}@{host} powershell -NoProfile -EncodedCommand {b64}
expect {{
    "yes/no" {{ send "yes\\r"; exp_continue }}
    "password:" {{ send "{password}\\r" }}
    timeout {{ puts "Timeout connecting to {host}"; exit 1 }}
    eof {{ puts "EOF on connect"; exit 1 }}
}}
expect {{
    timeout {{ puts "Timeout waiting for Win result"; exit 1 }}
    eof
}}
"""
    proc = subprocess.run(["expect", "-c", expect_script], capture_output=True, text=True)
    return proc.stdout

def main():
    print("================================================================")
    print("1. ДИАГНОСТИКА SAMBA 4.22.11 И CUPS НА 192.168.2.141")
    print("================================================================")
    
    server_cmd = r"""
echo "--- [1.1] CUPS ВЕРСИЯ И СТАТУС ---"
docker exec printserver-cups cupsd --version 2>/dev/null || docker exec printserver-cups dpkg -l cups | grep cups
docker exec printserver-cups lpstat -r
docker exec printserver-cups lpstat -p -d -v

echo ""
echo "--- [1.2] CUPS SHARING И КОНФИГУРАЦИЯ (cupsd.conf) ---"
docker exec printserver-cups grep -Ei "Browsing|Browse|Share|Listen|Port|Order|Allow" /etc/cups/cupsd.conf | grep -v '^#'

echo ""
echo "--- [1.3] CUPS IPP ATTRIBUTES ДЛЯ HP_M428_241 ---"
# Проверка IPP атрибутов через ipptool
docker exec printserver-cups which ipptool >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "ipptool найден, запрашиваем атрибуты..."
    cat << 'EOF' > /tmp/get-attrs.test
{
    OPERATION Get-Printer-Attributes
    GROUP operation-attributes-tag
    ATTR charset attributes-charset utf-8
    ATTR natural-language attributes-natural-language en
    ATTR uri printer-uri ipp://localhost:631/printers/HP_M428_241
    STATUS successful-ok
    DISPLAY printer-name
    DISPLAY printer-make-and-model
    DISPLAY printer-is-shared
    DISPLAY color-supported
    DISPLAY sides-supported
    DISPLAY document-format-supported
    DISPLAY ipp-versions-supported
}
EOF
    docker cp /tmp/get-attrs.test printserver-cups:/tmp/get-attrs.test
    docker exec printserver-cups ipptool -t -v ipp://localhost:631/printers/HP_M428_241 /tmp/get-attrs.test 2>&1 | head -n 30
else
    echo "ipptool не установлен в контейнере CUPS, опрашиваем через curl/HTTP..."
    docker exec printserver-cups curl -s http://localhost:631/printers/HP_M428_241 | grep -iE "driver|description|status|make" | head -n 20
fi

echo ""
echo "--- [1.4] DNS-SD / mDNS АНОНСЫ (AVAHI / IPP EVERYWHERE) ---"
ps aux | grep -i avahi | grep -v grep || echo "Avahi не запущен на хосте"
docker exec printserver-cups ps aux | grep -iE "avahi|dbus" || echo "Avahi/DBus в контейнере CUPS не запущен"
ss -tulpn | grep 5353 || echo "Порт UDP 5353 (mDNS) не слушается"

echo ""
echo "--- [1.5] SAMBA 4.22.11 SPOOLSS / RPC / TYPE 4 ДРАЙВЕРЫ ---"
docker exec printserver-samba smbd -V
echo "Текущие принтеры в Samba:"
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumprinters 2'

echo ""
echo "Текущие зарегистрированные драйверы в Samba (Level 1, 2, 3):"
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumdrivers 2'
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumdrivers 3'

echo ""
echo "Поддерживает ли Samba enumdrivers 8 (Type 4 v4 driver info)?"
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumdrivers 8' 2>&1

echo ""
echo "--- [1.6] SAMBA SMB.CONF ---"
docker exec printserver-samba cat /etc/samba/smb.conf
"""
    out_server = ssh_server(server_cmd)
    print(out_server)

if __name__ == "__main__":
    main()
