#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
set -e

echo "=== 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ admin В КОНТЕЙНЕРЕ ==="
docker exec printserver-cups sh -c '
  if ! id admin >/dev/null 2>&1; then
    useradd -m -s /bin/bash -G lpadmin admin
  fi
  echo "admin:admin" | chpasswd
  usermod -aG lpadmin admin
'
docker exec printserver-cups id admin

echo "=== 2. ОБНОВЛЕНИЕ /home/user/docker/printserver/start.sh ДЛЯ ПЕРСИСТЕНТНОСТИ ==="
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

# Создание/актуализация учетной записи администратора CUPS Web GUI
if ! id admin >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G lpadmin admin
fi
echo "admin:admin" | chpasswd
usermod -aG lpadmin admin

exec /usr/sbin/cupsd -f
EOF
chmod +x /home/user/docker/printserver/start.sh

echo "=== 3. НАСТРОЙКА cupsd.conf ДЛЯ ДОСТУПА К /admin ИЗ ЛОКАЛЬНОЙ СЕТИ ==="
docker exec printserver-cups sh -c '
  # Разрешаем ServerAlias и отключаем принудительный SSL для локальной сети
  grep -q "^ServerAlias " /etc/cups/cupsd.conf || sed -i "/^Port 631/a ServerAlias *" /etc/cups/cupsd.conf
  grep -q "^DefaultEncryption " /etc/cups/cupsd.conf || sed -i "/^DefaultAuthType /a DefaultEncryption Never" /etc/cups/cupsd.conf

  # Добавляем Allow from 192.168.2.0/24 в секции /admin, /admin/conf, /admin/log
  sed -i "/<Location \/admin>/,/<\/Location>/ { /Order allow,deny/a \ \ Allow from 192.168.2.0/24\n  Allow from 127.0.0.1
}" /etc/cups/cupsd.conf
  sed -i "/<Location \/admin\/conf>/,/<\/Location>/ { /Order allow,deny/a \ \ Allow from 192.168.2.0/24\n  Allow from 127.0.0.1
}" /etc/cups/cupsd.conf
  sed -i "/<Location \/admin\/log>/,/<\/Location>/ { /Order allow,deny/a \ \ Allow from 192.168.2.0/24\n  Allow from 127.0.0.1
}" /etc/cups/cupsd.conf
'

echo "=== 4. ПЕРЕЗАПУСК CUPSD И ПРОВЕРКА ==="
docker exec printserver-cups kill -HUP 1 || docker restart printserver-cups
sleep 3

echo "=== 5. ТЕСТ ДОСТУПА ЧЕРЕЗ CURL С АВТОРИЗАЦИЕЙ admin:admin ==="
curl -sI -u admin:admin http://192.168.2.141:631/admin/ | head -n 10
"""

print(ssh_server(script, timeout=60))
