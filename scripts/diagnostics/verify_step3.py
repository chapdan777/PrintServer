#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== 1. SCAN _IPP._TCP (avahi-browse -rt _ipp._tcp) ==="
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t 2>&1

echo ""
echo "=== 2. SCAN _IPPS._TCP (avahi-browse -rt _ipps._tcp) ==="
docker exec printserver-cups avahi-browse -rt _ipps._tcp -t 2>&1

echo ""
echo "=== 3. CUPS IPP ATTRIBUTES (printer-dns-sd-name) ==="
docker exec printserver-cups ipptool -t -v ipp://localhost:631/printers/HP_M428_241 /usr/share/cups/ipptool/get-printer-attributes.test 2>&1 | grep -iE "printer-dns-sd-name|printer-name|printer-info"
"""

print(ssh_server(script, timeout=60))
