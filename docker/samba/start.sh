#!/bin/sh
set -e

# Samba runtime
mkdir -p /run/samba
mkdir -p /var/cache/samba
mkdir -p /var/spool/samba
mkdir -p /var/lib/samba/private

chmod 0755 /run/samba
chmod 0755 /var/cache/samba
chmod 1777 /var/spool/samba
chmod 0700 /var/lib/samba/private

# Windows Point and Print driver repository
mkdir -p /var/lib/samba/printers/x64
mkdir -p /var/lib/samba/printers/W32X86

# printadmin должен физически иметь право записи в print$
chown -R root:printadmin /var/lib/samba/printers
chmod -R g+rwX /var/lib/samba/printers

# Новые каталоги наследуют группу printadmin
find /var/lib/samba/printers -type d -exec chmod g+s {} \;

testparm -s >/dev/null

exec /usr/sbin/smbd --foreground --no-process-group
