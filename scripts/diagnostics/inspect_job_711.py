#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== ТИП ФАЙЛА ДАННЫХ d00711-001 ==="
docker exec printserver-cups file /var/spool/cups/d00711-001 || docker exec printserver-cups head -c 16 /var/spool/cups/d00711-001

echo ""
echo "=== СОДЕРЖИМОЕ CONTROL FILE c00711 ==="
docker exec printserver-cups strings /var/spool/cups/c00711
"""

print(ssh_server(script, timeout=30))
