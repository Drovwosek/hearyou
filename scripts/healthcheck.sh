#!/bin/bash

# HearYou - Health Check
# Проверяет все компоненты сервиса

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "=== HearYou Health Check ==="
echo ""

# 1. Nginx
echo -n "Проверка Nginx... "
if systemctl is-active --quiet nginx; then
    check_ok "Nginx запущен"
else
    check_fail "Nginx не запущен!"
    exit 1
fi

# 2. Docker контейнер FastAPI
echo -n "Проверка FastAPI контейнера... "
if docker ps | grep -q hearyou-stt; then
    check_ok "FastAPI работает"
else
    check_fail "FastAPI контейнер не запущен!"
    exit 1
fi

# 3. Redis
echo -n "Проверка Redis... "
if docker exec hearyou_redis_1 redis-cli ping 2>/dev/null | grep -q PONG; then
    check_ok "Redis отвечает"
else
    check_fail "Redis не отвечает!"
    exit 1
fi

# 4. PostgreSQL
echo -n "Проверка PostgreSQL... "
if docker exec hearyou_postgres_1 pg_isready -U postgres >/dev/null 2>&1; then
    check_ok "PostgreSQL работает"
else
    check_fail "PostgreSQL не отвечает!"
    exit 1
fi

# 5. HTTPS endpoint
echo -n "Проверка HTTPS доступности... "
if curl -k -s https://92.51.36.233/ | grep -q "HearYou"; then
    check_ok "HTTPS доступен"
else
    check_fail "HTTPS недоступен!"
    exit 1
fi

# 6. Yandex API
echo -n "Проверка Yandex SpeechKit API... "
API_KEY=$(docker exec hearyou-stt cat /app/.env.yandex 2>/dev/null | grep YANDEX_API_KEY | cut -d'=' -f2)
if [ -n "$API_KEY" ]; then
    if curl -s -H "Authorization: Api-Key $API_KEY" \
         "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize" \
         2>&1 | grep -q "model"; then
        check_ok "Yandex API доступен"
    else
        check_warn "Yandex API не отвечает (возможно проблемы сети)"
    fi
else
    check_warn "API ключ не найден в .env.yandex"
fi

# 7. Использование ресурсов
echo ""
echo "=== Ресурсы ==="

# RAM
RAM_USAGE=$(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
RAM_VALUE=$(echo $RAM_USAGE | sed 's/%//')
echo -n "RAM: $RAM_USAGE "
if (( $(echo "$RAM_VALUE > 80" | bc -l) )); then
    check_warn "Высокая нагрузка"
else
    check_ok ""
fi

# Disk
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}')
DISK_VALUE=$(echo $DISK_USAGE | sed 's/%//')
echo -n "Disk: $DISK_USAGE "
if [ "$DISK_VALUE" -gt 70 ]; then
    check_warn "Нужна очистка"
else
    check_ok ""
fi

# Load Average
LOAD=$(uptime | grep -oP 'load average: \K.*' | cut -d',' -f1 | xargs)
echo "Load: $LOAD"

# 8. Статистика файлов
echo ""
echo "=== Файлы ==="
UPLOADS=$(find /root/hearyou/packages/stt-service/uploads/ -type f 2>/dev/null | wc -l)
RESULTS=$(find /root/hearyou/packages/stt-service/results/ -type f 2>/dev/null | wc -l)
UPLOADS_SIZE=$(du -sh /root/hearyou/packages/stt-service/uploads/ 2>/dev/null | cut -f1)
RESULTS_SIZE=$(du -sh /root/hearyou/packages/stt-service/results/ 2>/dev/null | cut -f1)

echo "Uploads: $UPLOADS файлов ($UPLOADS_SIZE)"
echo "Results: $RESULTS файлов ($RESULTS_SIZE)"

# 9. Последние задачи
echo ""
echo "=== Последние задачи ==="
docker exec hearyou_postgres_1 psql -U postgres -d hearyou_db -t -c \
    "SELECT 
        status, 
        COUNT(*) as count,
        ROUND(AVG(EXTRACT(EPOCH FROM (updated_at - created_at))), 1) as avg_sec
     FROM tasks 
     WHERE created_at > NOW() - INTERVAL '24 hours'
     GROUP BY status;" 2>/dev/null | grep -v "^$" | while read line; do
    echo "$line"
done || echo "(нет данных)"

echo ""
echo "=== Лимиты ==="
echo "Max file size: 25 GB"
echo "Max timeout: 2 hours"
echo "Supported: Audio + Video (auto audio extraction)"

echo ""
echo -e "${GREEN}=== Все проверки пройдены ===${NC}"
