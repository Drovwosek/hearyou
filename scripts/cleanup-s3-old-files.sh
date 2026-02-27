#!/bin/bash
# Очистка старых файлов из Yandex Object Storage

set -e

# Загрузка credentials
if [ -f /root/hearyou/packages/stt-service/.env.yandex ]; then
    source /root/hearyou/packages/stt-service/.env.yandex
else
    echo "❌ Файл .env.yandex не найден"
    exit 1
fi

BUCKET="hearyou-stt-temp"
ENDPOINT="https://storage.yandexcloud.net"

echo "🗑️  Очистка старых файлов из Object Storage..."
echo "📦 Bucket: $BUCKET"
echo ""

# Устанавливаем AWS CLI если нет
if ! command -v aws &> /dev/null; then
    echo "📥 Установка AWS CLI..."
    pip3 install awscli >/dev/null 2>&1
fi

# Настраиваем AWS CLI для Yandex
export AWS_ACCESS_KEY_ID="$YANDEX_S3_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="$YANDEX_S3_SECRET_KEY"

# Список всех файлов
echo "📋 Список файлов:"
aws s3 ls "s3://$BUCKET/" --endpoint-url="$ENDPOINT" | head -20

echo ""
read -p "❓ Удалить ВСЕ файлы из bucket? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Удаление..."
    
    # Удаляем все файлы
    aws s3 rm "s3://$BUCKET/" --recursive --endpoint-url="$ENDPOINT"
    
    echo ""
    echo "✅ Готово!"
    
    # Проверяем результат
    echo ""
    echo "📊 Статистика:"
    COUNT=$(aws s3 ls "s3://$BUCKET/" --endpoint-url="$ENDPOINT" 2>/dev/null | wc -l)
    echo "Осталось файлов: $COUNT"
else
    echo "❌ Отменено"
fi
