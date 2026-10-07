# Print Server Session Notes & Handoff

## 2026-10-07 — Реорганизация репозитория, Web GUI и фиксация Production

### Сделано (Done)
- [x] Проект принт-сервера полностью изолирован в подкаталоге `printserver/` с симлинком `targets/printserver`.
- [x] Синхронизированы актуальные конфигурации Docker с сервера `192.168.2.141` (`docker-compose.yml`, `Dockerfile`, `start.sh`, `samba/`).
- [x] Перенесены все скрипты развертывания, диагностики и PowerShell клиентов из `scratch/` в `printserver/scripts/`.
- [x] Включен Web GUI CUPS Administration (`http://192.168.2.141:631/admin`), создана учетная запись `admin:admin` в группе `lpadmin`.
- [x] Создано исчерпывающее руководство администратора: [`docs/ADMIN_GUIDE.md`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docs/ADMIN_GUIDE.md).
- [x] Создана памятка пользователя: [`docs/PRINTSERVER_GUIDE.md`](file:///Users/mironocean/Documents/Программирование/SSH/printserver/docs/PRINTSERVER_GUIDE.md).
- [x] Сформированы материалы для синхронизации с базой знаний LoreBase (`~/vault`).

### Следующие шаги (Next Steps)
1. Подключить обе очереди (`M428fdn` и `M428fdw`) на остальных рабочих станциях Windows в локальной сети (например, ПК `VIKA` `192.168.2.72`).
2. При добавлении новых или старых принтеров использовать Web GUI CUPS (`admin:admin`).

### Обнаруженные грабли (Gotchas)
- По умолчанию Avahi в Docker `network_mode: host` рассылает анонсы по всем интерфейсам и по IPv6, что приводило к потере анонсов второй очереди на клиентах Windows. Решено директивами `allow-interfaces=eth0` и `use-ipv6=no`.
- Доступ к `/admin` в CUPS по умолчанию закрыт для внешних IP и требует `DefaultEncryption Never` в локальной доверенной сети для предотвращения ошибок с самоподписанными SSL-сертификатами.

---

## 2026-10-06 — Production Rollout драйверлесс CUPS IPP Everywhere

### Сделано (Done)
- [x] Создан полный timestamped-бэкап на сервере: `/home/user/docker/printserver/backup_20261006_203600/`.
- [x] Проверен холодный перезапуск сервера `192.168.2.141` (`reboot`): все контейнеры и службы (D-Bus, Avahi, CUPS) поднялись автоматически.
- [x] Обе очереди (`HP_M428_241` и `HP_M428_244`) проверены на клиенте Windows 10 LTSC 1809 x86 (`ALINA`):
  - Драйвер: `Microsoft IPP Class Driver` (Type 4 in-box);
  - Двусторонняя печать: PASS на обоих принтерах;
  - Лотки 1, 2 и автовыбор: PASS;
  - Трафик строго через сервер CUPS (PDF 1.7), прямого обхода нет.
- [x] Устаревшие очереди Local Port и Samba удалены с тестового клиента.

---

## 2026-10-06 — Аудит Samba/CUPS Print Server и отказ от HP UPD

### Сделано (Done)
- [x] Исследована возможность раздачи HP UPD через Samba 4.22 Spoolss.
- [x] Выявлен фундаментальный блокер: ошибка `0x80070bcb` из-за отсутствия Package Point-and-Print (MS-PAR) в Samba и ограничений Microsoft PrintNightmare.
- [x] Принято архитектурное решение: переход на нативный стандарт CUPS IPP Everywhere.
