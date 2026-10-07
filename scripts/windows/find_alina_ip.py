#!/usr/bin/env python3
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server_cmd

script = r"""
echo "=== SAMBA LOGS (FIND ALINA / IPS) ==="
docker exec printserver-samba grep -in "alina" /var/log/samba/* 2>/dev/null || echo "No alina in logs"
docker exec printserver-samba ls -la /var/log/samba/

echo ""
echo "=== SAMBA LOG FILES WITH IP ==="
docker exec printserver-samba ls -la /var/log/samba/log.192.* 2>/dev/null || echo "No IP logs"

echo ""
echo "=== SAMBA LAST CONNECTED CLIENTS ==="
docker exec printserver-samba smbstatus -b 2>/dev/null || echo "smbstatus not available"

echo ""
echo "=== CUPS LOGS (CLIENT IPS) ==="
docker exec printserver-cups tail -n 20 /var/log/cups/access_log 2>/dev/null || echo "No access_log"
"""

print(ssh_server_cmd(script))
