#!/bin/bash
# Быстрый деплой STT-сервиса на VPS

set -e

VPS="root@92.51.36.233"
REMOTE_PATH="/root/hearyou/packages"

echo "🚀 Деплой STT-сервиса на VPS..."

# 1. Синхронизация файлов
echo "📦 Синхронизация файлов..."
rsync -avz --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='uploads/' \
    --exclude='results/' \
    --exclude='temp/' \
    ./ $VPS:$REMOTE_PATH/stt-service/

rsync -avz --exclude='__pycache__' \
    --exclude='*.pyc' \
    ../stt-yandex/ $VPS:$REMOTE_PATH/stt-yandex/

# 2. Пересборка и перезапуск
echo "🔨 Пересборка Docker образа..."
ssh $VPS "cd $REMOTE_PATH && docker-compose -f stt-service/docker-compose.yml down && docker-compose -f stt-service/docker-compose.yml up -d --build"

# 3. Проверка статуса
echo "✅ Проверка статуса..."
sleep 3
ssh $VPS "cd $REMOTE_PATH && docker-compose -f stt-service/docker-compose.yml ps"

# 4. Healthcheck
echo "🔍 Healthcheck..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://92.51.36.233:8000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Деплой успешен! Сервис доступен: http://92.51.36.233:8000"
else
    echo "❌ Ошибка: сервис недоступен (HTTP $HTTP_CODE)"
    ssh $VPS "cd $REMOTE_PATH && docker-compose -f stt-service/docker-compose.yml logs --tail=20"
    exit 1
fi
