#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== ЧИСЛО СТРАНИЦ В PDF ЗАДАНИИ 711 ==="
docker exec printserver-cups grep -c "/Type /Page" /var/spool/cups/d00711-001 || echo "Не удалось подсчитать"
docker exec printserver-cups pdfinfo /var/spool/cups/d00711-001 2>/dev/null || echo "pdfinfo отсутствует"
"""

print(ssh_server(script, timeout=30))
