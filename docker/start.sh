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
ADMIN_USER="${CUPS_ADMIN_USER:-admin}"
ADMIN_PASS="${CUPS_ADMIN_PASSWORD:-admin}"

if ! id "$ADMIN_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G lpadmin "$ADMIN_USER"
fi
echo "$ADMIN_USER:$ADMIN_PASS" | chpasswd
usermod -aG lpadmin "$ADMIN_USER"

exec /usr/sbin/cupsd -f
