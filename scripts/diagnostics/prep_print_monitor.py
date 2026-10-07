#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== 1. ПРОВЕРКА TCPDUMP НА СЕРВЕРЕ ==="
which tcpdump || docker exec printserver-cups which tcpdump || echo "tcpdump не установлен"

echo ""
echo "=== 2. ПОСЛЕДНИЕ ЗАПИСИ CUPS ACCESS_LOG ДО ТЕСТА ==="
docker exec printserver-cups tail -n 5 /var/log/cups/access_log 2>/dev/null || echo "access_log пуст"

echo ""
echo "=== 3. ТЕКУЩИЕ ЗАДАНИЯ В ОЧЕРЕДИ HP_M428_241 ==="
docker exec printserver-cups lpstat -W all -o HP_M428_241
"""

print(ssh_server(script, timeout=30))
