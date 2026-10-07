# Project Context & Map: Print Server (CUPS IPP Everywhere)

## 1. What this is
Выделенный модуль управления, диагностики, автоматизации и мониторинга централизованного бездрайверного принт-сервера CUPS IPP Everywhere для клиентов Windows 10/11 в сети `192.168.2.0/24`.

---

## 2. Infrastructure & Topology
- **Print Server Host**: `192.168.2.141` (Debian 13, Docker, пользователь `user`).
- **CUPS Container**: `printserver-cups` (`network_mode: host`, автозапуск `restart: unless-stopped`).
- **Web GUI Administration**: `http://192.168.2.141:631/admin` (HTTP Basic: `admin` / `admin`).
- **Target MFDs (Физические МФУ)**:
  - `HP LaserJet Pro MFP M428fdn`: `192.168.2.241:631` (Очередь: `HP_M428_241`)
  - `HP LaserJet Pro MFP M428fdw`: `192.168.2.244:631` (Очередь: `HP_M428_244`)
- **Clients**: Windows 10 Enterprise LTSC (x86 & x64), например ПК `ALINA` (`192.168.2.74`).

---

## 3. Directory Map (Карта подкаталогов)
* [`docker/`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docker) — live конфигурации сервисов (`docker-compose.yml`, `Dockerfile`, `start.sh`, `samba/`).
* [`scripts/deploy/`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/scripts/deploy) — скрипты применения настроек, Avahi интерфейсов, создания админа и бэкапов.
* [`scripts/diagnostics/`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/scripts/diagnostics) — скрипты опроса IPP-атрибутов, mDNS анонсов, логов заданий и доступа.
* [`scripts/windows/`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/scripts/windows) — PowerShell и скрипты проверки клиентов Windows 10.
* [`docs/`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docs) — документация модуля:
  - 📖 [`ADMIN_GUIDE.md`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docs/ADMIN_GUIDE.md) — полное руководство системного администратора.
  - 🖨️ [`PRINTSERVER_GUIDE.md`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docs/PRINTSERVER_GUIDE.md) — инструкция для пользователей и дежурных администраторов.
* [`NOTES.md`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/NOTES.md) — журнал сессий и Handoff принт-сервера.

---

## 4. Key Commands (Ключевые команды)
```bash
# Проверка планировщика CUPS
docker exec printserver-cups lpstat -r

# Просмотр очередей и их статуса
docker exec printserver-cups lpstat -p -d

# Проверка mDNS анонсов Avahi на eth0
docker exec printserver-cups avahi-browse -rt _ipp._tcp -t

# Просмотр лога страниц печати
docker exec printserver-cups tail -n 20 /var/log/cups/page_log
```

---

## 5. Critical Rules & Constraints
1. **Zero-Touch Driverless**: Все клиенты Windows подключаются строго через встроенный `Microsoft IPP Class Driver` (Type 4). Никаких ручных установок INF или вендорного ПО HP UPD на клиентах.
2. **Samba Spoolss Retired**: Классический Point-and-Print через Samba отключен из-за блокировок `0x80070bcb`.
3. **Avahi Interface Binding**: В `avahi-daemon.conf` обязательны директивы `allow-interfaces=eth0` и `use-ipv6=no`, чтобы не засорять сеть анонсами через мосты Docker.
4. **Volume Persistence**: Изменения очередей сохраняются в томе `cups-config` (`/etc/cups`). При пересборке образов volumes не удалять.
