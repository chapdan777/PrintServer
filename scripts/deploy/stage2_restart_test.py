#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
set -e
cd /home/user/docker/printserver

echo "=== 1. ПРОВЕРКА СИНТАКСИСА CUPSD.CONF ==="
docker exec printserver-cups cupsd -t

echo ""
echo "=== 2. CONTROLLED RESTART: DOCKER COMPOSE RESTART CUPS ==="
docker compose restart cups

echo ""
echo "=== 3. ОЖИДАНИЕ ИНИЦИАЛИЗАЦИИ СЛУЖБ (6 сек) ==="
sleep 6

echo ""
echo "=== 4. ПРОВЕРКА ПРОЦЕССОВ ВНУТРИ КОНТЕЙНЕРА ==="
docker exec printserver-cups ps aux

echo ""
echo "=== 5. ПРОВЕРКА СТАТУСА ОЧЕРЕДЕЙ LPSTAT ==="
docker exec printserver-cups lpstat -r
docker exec printserver-cups lpstat -p -d -v

echo ""
echo "=== 6. ПРОВЕРКА ВОССТАНОВЛЕНИЯ DNS-SD АНОНСОВ ==="
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t 2>&1 | grep -E "HP LaserJet Pro MFP M428fdn @ servvm|HP LaserJet Pro MFP M428fdw @ servvm" -A 4
"""

out = ssh_server(script, timeout=60)
print(out)
