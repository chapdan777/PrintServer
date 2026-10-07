#!/usr/bin/env python3
"""
ШАГ 2: Настройка DNS-SD / Avahi внутри Docker-контейнера CUPS на 192.168.2.141.
С полным бэкапом и верификацией cupsd -t и lpstat.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
set -e
cd /home/user/docker/printserver

echo "=== 1. СОЗДАНИЕ РЕЗЕРВНЫХ КОПИЙ ==="
cp Dockerfile Dockerfile.bak-mdns
cp start.sh start.sh.bak-mdns
docker exec printserver-cups cp /etc/cups/cupsd.conf /etc/cups/cupsd.conf.bak-mdns
echo "Бэкапы созданы успешно."

echo ""
echo "=== 2. ОБНОВЛЕНИЕ DOCKERFILE ==="
cat << 'EOF' > Dockerfile
FROM debian:13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    cups \
    cups-client \
    cups-filters \
    ghostscript \
    ca-certificates \
    iputils-ping \
    netcat-openbsd \
    avahi-daemon \
    avahi-utils \
    dbus \
 && rm -rf /var/lib/apt/lists/*

# Слушаем сеть, но разрешаем доступ только из вашей LAN.
RUN sed -ri 's#^Listen localhost:631#Port 631#' /etc/cups/cupsd.conf \
 && sed -ri '/<Location \/>/,/<\/Location>/ s#Order allow,deny#Order allow,deny\n  Allow from 192.168.2.0/24#' /etc/cups/cupsd.conf \
 && sed -ri 's/^Browsing No/Browsing Yes/' /etc/cups/cupsd.conf

COPY start.sh /usr/local/bin/start-printserver
RUN chmod 755 /usr/local/bin/start-printserver

CMD ["/usr/local/bin/start-printserver"]
EOF
echo "Dockerfile обновлен."

echo ""
echo "=== 3. ОБНОВЛЕНИЕ START.SH ==="
cat << 'EOF' > start.sh
#!/bin/sh
mkdir -p /run/dbus /var/run/dbus
rm -f /run/dbus/pid /run/dbus/system_bus_socket /var/run/dbus/pid /var/run/dbus/system_bus_socket
dbus-daemon --system --fork

mkdir -p /run/avahi-daemon /var/run/avahi-daemon
rm -f /run/avahi-daemon/pid /var/run/avahi-daemon/pid
avahi-daemon -D

exec /usr/sbin/cupsd -f
EOF
chmod 755 start.sh
echo "start.sh обновлен."

echo ""
echo "=== 4. НАСТРОЙКА CUPSD.CONF В ТОМЕ cups-config ==="
# Обновляем cupsd.conf в томе
docker exec printserver-cups sed -ri 's/^Browsing .*/Browsing Yes/' /etc/cups/cupsd.conf
if ! docker exec printserver-cups grep -q "BrowseLocalProtocols" /etc/cups/cupsd.conf; then
    docker exec printserver-cups sed -ri '/^Browsing Yes/a BrowseLocalProtocols dnssd' /etc/cups/cupsd.conf
else
    docker exec printserver-cups sed -ri 's/^BrowseLocalProtocols .*/BrowseLocalProtocols dnssd/' /etc/cups/cupsd.conf
fi

if ! docker exec printserver-cups grep -q "BrowseDNSSDSubTypes" /etc/cups/cupsd.conf; then
    docker exec printserver-cups sed -ri '/^BrowseLocalProtocols dnssd/a BrowseDNSSDSubTypes _cups,_print' /etc/cups/cupsd.conf
else
    docker exec printserver-cups sed -ri 's/^BrowseDNSSDSubTypes .*/BrowseDNSSDSubTypes _cups,_print/' /etc/cups/cupsd.conf
fi

echo "Обновленные директивы Browsing в /etc/cups/cupsd.conf:"
docker exec printserver-cups grep -Ei "Browsing|BrowseLocalProtocols|BrowseDNSSDSubTypes" /etc/cups/cupsd.conf

echo ""
echo "=== 5. СБОРКА И ПЕРЕЗАПУСК КОНТЕЙНЕРА CUPS ==="
docker compose build cups
docker compose up -d --no-deps cups

echo ""
echo "=== 6. ОЖИДАНИЕ ЗАПУСКА СЕРВИСОВ (5 сек) ==="
sleep 5

echo ""
echo "=== 7. ВЕРИФИКАЦИЯ: CUPSD -T ==="
docker exec printserver-cups cupsd -t || echo "Ошибка синтаксиса cupsd"

echo ""
echo "=== 8. ВЕРИФИКАЦИЯ: СТАТУС ОЧЕРЕДЕЙ LPSTAT ==="
docker exec printserver-cups lpstat -r
docker exec printserver-cups lpstat -p -d -v

echo ""
echo "=== 9. ВЕРИФИКАЦИЯ: ПРОЦЕССЫ ВНУТРИ КОНТЕЙНЕРА ==="
docker exec printserver-cups ps aux
"""

print(ssh_server(script, timeout=180))
