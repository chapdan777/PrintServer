#!/usr/bin/env bash
#
# Скрипт резервного копирования конфигураций и очередей CUPS
# Запуск: ./scripts/backup_config.sh
#

set -e

CONTAINER_NAME="${CONTAINER_NAME:-printserver-cups}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARGET_DIR="${BACKUP_DIR}/cups_backup_${TIMESTAMP}"

mkdir -p "$TARGET_DIR"

echo "=== Создание резервной копии CUPS в $TARGET_DIR ==="

# Копирование конфигураций из контейнера
docker cp "${CONTAINER_NAME}:/etc/cups/cupsd.conf" "${TARGET_DIR}/cupsd.conf" 2>/dev/null || true
docker cp "${CONTAINER_NAME}:/etc/cups/printers.conf" "${TARGET_DIR}/printers.conf" 2>/dev/null || true
docker cp "${CONTAINER_NAME}:/etc/cups/ppd" "${TARGET_DIR}/ppd" 2>/dev/null || true

echo "Создан бэкап:"
ls -la "$TARGET_DIR"
echo "Успешно завершено."
