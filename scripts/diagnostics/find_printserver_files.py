#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server_cmd

script = r"""
echo "=== FIND PRINTSERVER REPO / COMPOSE ON 192.168.2.141 ==="
find /home/user /opt -maxdepth 4 -name "*print*" -o -name "*samba*" -o -name "*cups*" 2>/dev/null

echo ""
echo "=== DOCKER INSPECT PRINTSERVER-SAMBA MOUNTS ==="
docker inspect printserver-samba --format '{{json .Mounts}}' | jq . || docker inspect printserver-samba --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'

echo ""
echo "=== DOCKER INSPECT PRINTSERVER-CUPS MOUNTS ==="
docker inspect printserver-cups --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
"""

print(ssh_server_cmd(script))
