# PrintServer: Централизованный Driverless принт-сервер (CUPS IPP Everywhere)

Промышленное решение для централизованной сетевой печати в гетерогенной корпоративной сети Windows 10/11 без необходимости ручной установки драйверов на рабочих станциях (**Zero-Touch**).

Решение полностью исключает зависимость от Samba Spoolss, классического Point-and-Print и вендорных пакетов драйверов (HP Universal Print Driver), защищая инфраструктуру от уязвимостей класса **PrintNightmare** (ошибки `0x80070bcb`).

---

## 🏗 Архитектура решения

```mermaid
flowchart TD
    subgraph Clients["Клиенты Windows 10 / 11 (x86 & x64)"]
        W10["Клиент (например, ALINA 192.168.2.74)"]
        W10_Driver["Microsoft IPP Class Driver (Type 4 in-box)"]
        W10 --> W10_Driver
    end

    subgraph Server["Сервер печати (Debian 13, 192.168.2.141)"]
        subgraph Docker["Docker Container: printserver-cups (network_mode: host)"]
            Avahi["Avahi Daemon (mDNS, UDP 5353, eth0 IPv4)"]
            CUPS["CUPS 2.4.x (Scheduler, TCP 631)"]
            WebGUI["CUPS Web Administration (HTTP basic: admin/admin)"]
            Queues["Очереди печати:\n• HP_M428_241\n• HP_M428_244"]
            
            Avahi -.->|mDNS анонсы очередей| W10
            CUPS --- Queues
            WebGUI --- CUPS
        end
    end

    subgraph Printers["Физические МФУ HP LaserJet Pro"]
        HP241["HP LaserJet Pro MFP M428fdn\n(192.168.2.241:631 IPP)"]
        HP244["HP LaserJet Pro MFP M428fdw\n(192.168.2.244:631 IPP)"]
    end

    W10_Driver ==>|Документ PDF 1.7 / IPP (TCP 631)| CUPS
    Queues ==>|IPP Print (TCP 631)| HP241
    Queues ==>|IPP Print (TCP 631)| HP244
```

### Ключевые особенности:
1. **Zero-Touch на клиентах**: Windows использует встроенный системный драйвер **`Microsoft IPP Class Driver`** (Type 4). Не требуются права локального администратора.
2. **Полный аппаратный функционал**:
   - Двусторонняя печать (**Duplex / 2-Sided Printing**);
   - Управление лотками подачи (**Tray 1, Tray 2, Auto Select**);
   - Автоматическое считывание формата бумаги (**A4**).
3. **Безопасность и изоляция**: Клиенты не имеют прямого доступа к физическим МФУ — весь трафик централизован и логируется на сервере CUPS.
4. **Универсальность**: Сервер принимает PDF от Windows и может отправлять задания как на современные IPP-принтеры, так и на старые аппараты через AppSocket/JetDirect (RAW port 9100).

---

## 🚀 Быстрый старт

### 1. Требования
- Docker Engine 24+ & Docker Compose v2+
- Физический сетевой интерфейс `eth0` на хосте
- Открытые порты в локальной сети: UDP 5353 (mDNS), TCP 631 (IPP/HTTP)

### 2. Клонирование и запуск
```bash
git clone https://github.com/chapdan777/PrintServer.git
cd PrintServer/docker

# Запуск контейнера сервера печати
docker compose up -d cups
```

---

## 🖥 Web GUI администрирования CUPS

Сервер оснащен веб-панелью для управления очередями, добавления новых принтеров и назначения PPD-драйверов:

- **Адрес панели:** `http://192.168.2.141:631/admin`
- **Логин:** `admin`
- **Пароль:** `admin` *(настраивается через `CUPS_ADMIN_PASSWORD` в `.env`)*

---

## 👥 Подключение принтеров на Windows 10/11 (3 клика)

1. Откройте **Параметры** (`Win + I`) ➔ **Устройства** ➔ **Принтеры и сканеры**.
2. Нажмите **`+ Добавить принтер или сканер`**.
3. В появившемся списке выберите нужный принтер:
   - `HP LaserJet Pro MFP M428fdn @ servvm` (МФУ .241)
   - `HP LaserJet Pro MFP M428fdw @ servvm` (МФУ .244)
4. Нажмите **`Добавить устройство`** ➔ готово к работе через 10 секунд.

---

## 📂 Структура репозитория

```
PrintServer/
├── README.md                   # Главное описание проекта
├── .env                        # Конфигурация локального окружения
├── .env.example                # Шаблон конфигурации
├── .gitignore                  # Исключения Git
├── AGENTS.md                   # Контекстная карта для ИИ-агентов
├── NOTES.md                    # История сессий и Handoff
├── docs/                       # Документация проекта
│   ├── ADMIN_GUIDE.md          # Полное руководство системного администратора
│   └── PRINTSERVER_GUIDE.md    # Памятка по эксплуатации и подключению
├── docker/                     # Конфигурации контейнеров Docker
│   ├── docker-compose.yml      # Спецификация сервисов CUPS и Samba
│   ├── Dockerfile              # Сборка образа на Debian 13
│   ├── start.sh                # Скрипт инициализации D-Bus, Avahi и CUPS
│   └── samba/                  # Legacy-модуль Samba (опционально)
└── scripts/                    # Инструменты автоматизации и диагностики
    ├── deploy/                 # Скрипты развертывания и привязки интерфейсов
    ├── diagnostics/            # Проверка IPP, mDNS, логов и очередей
    └── windows/                # PowerShell-скрипты диагностики клиентов
```

---

## 📚 Документация

- 📖 [**Руководство администратора (ADMIN_GUIDE.md)**](docs/ADMIN_GUIDE.md) — подробный разбор архитектуры, обоснование отказа от HP UPD / Samba Spoolss, инструкция по Web GUI и устранению неполадок.
- 🖨️ [**Руководство пользователя (PRINTSERVER_GUIDE.md)**](docs/PRINTSERVER_GUIDE.md) — памятка по подключению принтеров на рабочих местах.
