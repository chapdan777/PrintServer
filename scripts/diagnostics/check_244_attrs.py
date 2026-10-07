#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
docker exec printserver-cups ipptool -t -v ipp://localhost:631/printers/HP_M428_244 /usr/share/cups/ipptool/get-printer-attributes.test 2>&1 | grep -iE "printer-name|printer-is-shared|document-format|sides-supported|media-source-supported|printer-make-and-model|printer-resolution-supported|printer-dns-sd-name" | head -n 35
"""

out = ssh_server(script, timeout=30)
print(out)
