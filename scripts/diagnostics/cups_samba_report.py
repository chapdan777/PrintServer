#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== [1.1] CUPS VERSION & QUEUES ==="
docker exec printserver-cups dpkg -l cups | grep -E '^ii'
docker exec printserver-cups lpstat -r
docker exec printserver-cups lpstat -p -d -v

echo ""
echo "=== [1.2] CUPS SHARING (cupsd.conf) ==="
docker exec printserver-cups grep -Ei "Browsing|Browse|Share|Listen|Port|Order|Allow" /etc/cups/cupsd.conf | grep -v '^#'

echo ""
echo "=== [1.3] CUPS IPP ATTRIBUTES (HP_M428_241) ==="
# Запрос ключевых атрибутов
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
docker exec printserver-cups ipptool -t -v ipp://localhost:631/printers/HP_M428_241 /tmp/get-attrs.test 2>&1

echo ""
echo "=== [1.4] AVAHI / MDNS / DNS-SD ==="
ps aux | grep -i avahi | grep -v grep || echo "Avahi НЕ запущен на хосте"
docker exec printserver-cups ps aux | grep -iE "avahi|dbus" || echo "Avahi/DBus НЕ запущен в CUPS контейнере"
ss -ulpn | grep 5353 || echo "Порт 5353 НЕ слушается"

echo ""
echo "=== [1.5] SAMBA PRINTERS & RPC ==="
docker exec printserver-samba smbd -V
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumprinters 2'
docker exec printserver-samba rpcclient -U '%' localhost -c 'enumdrivers 8' 2>&1 | head -n 15
"""

print(ssh_server(script))
