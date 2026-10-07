#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
echo "=== 1. DOCKER-COMPOSE & STRUCTURE IN /home/user/docker/printserver ==="
ls -la /home/user/docker/printserver/
if [ -f /home/user/docker/printserver/docker-compose.yml ]; then
    cat /home/user/docker/printserver/docker-compose.yml
elif [ -f /home/user/docker/printserver/compose.yaml ]; then
    cat /home/user/docker/printserver/compose.yaml
else
    echo "docker-compose.yml не найден, поиск *.yml или *.yaml:"
    find /home/user/docker/printserver/ -name "*.yml" -o -name "*.yaml"
fi

echo ""
echo "=== 2. CUPS CONTAINER AVAHI / DBUS PACKAGES ==="
docker exec printserver-cups dpkg -l | grep -iE "avahi|dbus" || echo "Пакеты avahi/dbus не найдены в printserver-cups"

echo ""
echo "=== 3. HOST D-BUS STATUS & SOCKET ==="
ps aux | grep -i dbus | grep -v grep || echo "D-Bus не найден в процессах хоста"
ls -la /var/run/dbus/system_bus_socket 2>/dev/null || echo "Сокет /var/run/dbus/system_bus_socket отсутствует"

echo ""
echo "=== 4. HOST AVAHI STATUS ==="
systemctl status avahi-daemon 2>&1 | head -n 15 || ps aux | grep -i avahi

echo ""
echo "=== 5. CHECK AVAHI-BROWSE ON HOST ==="
which avahi-browse || echo "avahi-browse отсутствует на хосте"
which python3 && python3 -c "import zeroconf; print('zeroconf available')" 2>/dev/null || echo "zeroconf module not installed"
"""

print(ssh_server(script))
