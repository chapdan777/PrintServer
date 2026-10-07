#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
set -e

echo "=== 1. ОБНОВЛЕНИЕ /home/user/docker/printserver/start.sh ==="
cat << 'EOF' > /home/user/docker/printserver/start.sh
#!/bin/sh
mkdir -p /run/dbus /var/run/dbus
rm -f /run/dbus/pid /run/dbus/system_bus_socket /var/run/dbus/pid /var/run/dbus/system_bus_socket
dbus-daemon --system --fork

# Строгая привязка Avahi только к физическому интерфейсу LAN (eth0) и только IPv4
sed -i 's/^#*use-ipv6=.*/use-ipv6=no/' /etc/avahi/avahi-daemon.conf
sed -i 's/^#*allow-interfaces=.*/allow-interfaces=eth0/' /etc/avahi/avahi-daemon.conf

mkdir -p /run/avahi-daemon /var/run/avahi-daemon
rm -f /run/avahi-daemon/pid /var/run/avahi-daemon/pid
avahi-daemon -D

exec /usr/sbin/cupsd -f
EOF
chmod +x /home/user/docker/printserver/start.sh

echo "=== 2. СБОРКА И ПЕРЕЗАПУСК КОНТЕЙНЕРА CUPS ==="
cd /home/user/docker/printserver
docker compose build cups
docker compose up -d cups

echo "=== 3. ОЖИДАНИЕ ИНИЦИАЛИЗАЦИИ СЛУЖБ (5 сек) ==="
sleep 5

echo "=== 4. ПРОВЕРКА /etc/avahi/avahi-daemon.conf В КОНТЕЙНЕРЕ ==="
docker exec printserver-cups grep -E "use-ipv6|allow-interfaces" /etc/avahi/avahi-daemon.conf

echo "=== 5. ПРОВЕРКА СТАТУСА CUPS И АНОНСОВ AVAHI ==="
docker exec printserver-cups lpstat -r
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t 2>&1
"""

print(ssh_server(script, timeout=120))
