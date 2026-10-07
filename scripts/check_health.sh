#!/usr/bin/env bash
#
# Скрипт комплексной проверки здоровья сервера печати CUPS
# Запуск: ./scripts/check_health.sh
#

set -e

CONTAINER_NAME="${CONTAINER_NAME:-printserver-cups}"

echo "============================================================"
echo "  ПРОВЕРКА ЗДОРОВЬЯ ПРИНТ-СЕРВЕРА ($CONTAINER_NAME)"
echo "============================================================"

# 1. Проверка статуса контейнера Docker
echo ""
echo "[1/4] Статус контейнера Docker:"
if docker ps --format '{{.Names}} ({{.Status}})' | grep -q "$CONTAINER_NAME"; then
    echo "  [OK] Контейнер $CONTAINER_NAME запущен:"
    docker ps --filter "name=$CONTAINER_NAME" --format "       ID: {{.ID}} | Image: {{.Image}} | Status: {{.Status}}"
else
    echo "  [FAIL] Контейнер $CONTAINER_NAME не запущен!"
    exit 1
fi

# 2. Проверка планировщика CUPS
echo ""
echo "[2/4] Статус планировщика CUPS:"
if docker exec "$CONTAINER_NAME" lpstat -r 2>&1 | grep -q "scheduler is running"; then
    echo "  [OK] Планировщик CUPS активен и обрабатывает задания."
else
    echo "  [FAIL] Планировщик CUPS остановлен!"
    exit 1
fi

# 3. Список очередей печати
echo ""
echo "[3/4] Состояние очередей печати:"
docker exec "$CONTAINER_NAME" lpstat -p -d

# 4. Проверка анонсов mDNS / DNS-SD в локальной сети
echo ""
echo "[4/4] Анонсы очередей через Avahi (mDNS / IPP):"
docker exec "$CONTAINER_NAME" avahi-browse -rt _ipp._tcp -t 2>&1 | grep -E "^\+.*servvm|^=.*servvm|hostname =|address =|port =" || true

echo ""
echo "============================================================"
echo "  ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО"
echo "============================================================"
