#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== 1. UPTIME СЕРВЕРА ==="
uptime

echo ""
echo "=== 2. DOCKER CONTAINERS STATUS ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== 3. ПРОЦЕССЫ ВНУТРИ ПРИНТСЕРВЕРА CUPS ==="
docker exec printserver-cups ps aux

echo ""
echo "=== 4. СТАТУС ОЧЕРЕДЕЙ CUPS И БЭКЕНДЫ ==="
docker exec printserver-cups lpstat -r
docker exec printserver-cups lpstat -p -d -v

echo ""
echo "=== 5. АВТОМАТИЧЕСКИЕ АНОНСЫ DNS-SD (AVAHI-BROWSE) ==="
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t 2>&1 | grep -E "HP LaserJet Pro MFP M428fdn @ servvm|HP LaserJet Pro MFP M428fdw @ servvm" -A 4
"""

out = ssh_server(script, timeout=60)
print(out)
