#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== 1. CUPS PAGE_LOG ==="
docker exec printserver-cups cat /var/log/cups/page_log 2>/dev/null || echo "page_log пуст"

echo ""
echo "=== 2. ПОСЛЕДНИЕ ЗАПИСИ ACCESS_LOG ==="
docker exec printserver-cups tail -n 15 /var/log/cups/access_log 2>/dev/null

echo ""
echo "=== 3. ПОСЛЕДНИЕ ЗАПИСИ ERROR_LOG ==="
docker exec printserver-cups tail -n 25 /var/log/cups/error_log 2>/dev/null

echo ""
echo "=== 4. АТРИБУТЫ ПОСЛЕДНЕГО ЗАДАНИЯ В SPOOL ==="
docker exec printserver-cups ls -lt /var/spool/cups/ | head -n 10
LAST_JOB=$(docker exec printserver-cups ls -t /var/spool/cups/c* 2>/dev/null | head -n 1)
if [ -n "$LAST_JOB" ]; then
    echo "Анализ файла задания $LAST_JOB:"
    docker exec printserver-cups strings "$LAST_JOB" | grep -iE "sides|duplex|pages|media|source|format" | head -n 20
fi
"""

print(ssh_server(script, timeout=30))
