#!/usr/bin/env python3
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server_cmd, win_ps_cmd

script = r"""
echo "=== SAMBA LOG.ALINA ==="
docker exec printserver-samba cat /var/log/samba/log.alina

echo ""
echo "=== PING 192.168.2.74 FROM SERVER ==="
ping -c 2 192.168.2.74 || echo "Ping failed"

echo ""
echo "=== CHECK PORTS ON 192.168.2.74 (NC/NMAP/CURL) ==="
nc -zv -w 2 192.168.2.74 22 2>/dev/null && echo "Port 22 OPEN" || echo "Port 22 CLOSED"
nc -zv -w 2 192.168.2.74 5985 2>/dev/null && echo "Port 5985 (WinRM) OPEN" || echo "Port 5985 CLOSED"
nc -zv -w 2 192.168.2.74 445 2>/dev/null && echo "Port 445 (SMB) OPEN" || echo "Port 445 CLOSED"
"""

print(ssh_server_cmd(script))
