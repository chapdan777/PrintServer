#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_all import ssh_server

script = r"""
docker run --rm --net=host debian:13-slim sh -c '
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq >/dev/null 2>&1
  apt-get install -y -qq avahi-daemon avahi-utils dbus >/dev/null 2>&1
  mkdir -p /run/dbus
  dbus-daemon --system --fork 2>/dev/null
  avahi-daemon -D 2>/dev/null
  sleep 3
  echo "=== 1. ВСЕ DNS-SD СЕРВИСЫ В LAN (avahi-browse -art) ==="
  avahi-browse -art -t 2>&1
  echo ""
  echo "=== 2. IPP СЕРВИСЫ (avahi-browse -rt _ipp._tcp) ==="
  avahi-browse -rt _ipp._tcp -t 2>&1
  echo ""
  echo "=== 3. IPPS СЕРВИСЫ (avahi-browse -rt _ipps._tcp) ==="
  avahi-browse -rt _ipps._tcp -t 2>&1
'
"""

print(ssh_server(script, timeout=120))
