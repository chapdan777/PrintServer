#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
docker exec printserver-cups ipptool -t -v ipp://localhost:631/printers/HP_M428_241 /usr/share/cups/ipptool/get-printer-attributes.test 2>&1 | grep -iE "printer-name|printer-is-shared|document-format|sides-supported|printer-make-and-model|color-supported|ipp-versions" | head -n 35
"""

print(ssh_server(script))
