#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
set -e
cd /home/user/docker/printserver

TS=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/user/docker/printserver/backup_${TS}"
mkdir -p "$BACKUP_DIR"

echo "=== 1. СОХРАНЕНИЕ КОНФИГУРАЦИОННЫХ ФАЙЛОВ В $BACKUP_DIR ==="
cp docker-compose.yml "$BACKUP_DIR/"
cp Dockerfile "$BACKUP_DIR/"
cp start.sh "$BACKUP_DIR/"
if [ -d samba ]; then
    cp -r samba "$BACKUP_DIR/"
fi

# Копирование из контейнера CUPS (volume cups-config)
docker cp printserver-cups:/etc/cups/cupsd.conf "$BACKUP_DIR/cupsd.conf"
docker cp printserver-cups:/etc/cups/printers.conf "$BACKUP_DIR/printers.conf" 2>/dev/null || touch "$BACKUP_DIR/printers.conf"
docker cp printserver-cups:/etc/cups/ppd "$BACKUP_DIR/ppd" 2>/dev/null || mkdir -p "$BACKUP_DIR/ppd"

echo "Содержимое резервной копии:"
ls -la "$BACKUP_DIR"
ls -la "$BACKUP_DIR/ppd" 2>/dev/null || true

echo ""
echo "=== 2. DOCKER COMPOSE PS ==="
docker compose ps

echo ""
echo "=== 3. CUPS LPSTAT -T ==="
docker exec printserver-cups lpstat -t

echo ""
echo "=== 4. CUPS LPOPTIONS (HP_M428_241) ==="
docker exec printserver-cups lpoptions -p HP_M428_241 -l

echo ""
echo "=== 5. CUPS LPOPTIONS (HP_M428_244) ==="
docker exec printserver-cups lpoptions -p HP_M428_244 -l

echo ""
echo "=== 6. AVAHI-BROWSE _IPP._TCP ==="
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t 2>&1

echo ""
echo "=== 7. AVAHI-BROWSE _IPPS._TCP ==="
docker exec printserver-cups avahi-browse -rt _ipps._tcp -t 2>&1
"""

out = ssh_server(script, timeout=60)
print(out)

# Сохранение локального отчета BEFORE
report_path = Path(__file__).resolve().parent.parent / "reports" / "printserver_before_rollout.txt"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(out)
print(f"\n[OK] Полный отчёт сохранён в {report_path}")
