#!/bin/bash
# Настройка Lifecycle Policy для автоудаления файлов из Object Storage

set -e

# Загрузка переменных
source /root/hearyou/packages/stt-service/.env.yandex

BUCKET="hearyou-stt-temp"
LIFECYCLE_FILE="/tmp/lifecycle-policy.json"

echo "🗑️  Настройка автоудаления файлов в Object Storage..."

# Создаём Lifecycle Policy
cat > "$LIFECYCLE_FILE" << 'EOF'
{
  "Rules": [
    {
      "ID": "DeleteTempFiles",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "Expiration": {
        "Days": 1
      }
    }
  ]
}
EOF

echo "📄 Lifecycle Policy:"
cat "$LIFECYCLE_FILE"

# Применяем через AWS CLI (совместимый с Yandex S3)
echo ""
echo "🔧 Применение policy..."

aws s3api put-bucket-lifecycle-configuration \
  --bucket "$BUCKET" \
  --lifecycle-configuration file://"$LIFECYCLE_FILE" \
  --endpoint-url=https://storage.yandexcloud.net \
  --profile yandex

if [ $? -eq 0 ]; then
    echo "✅ Lifecycle Policy применён!"
    echo ""
    echo "Файлы старше 1 дня будут автоматически удаляться"
else
    echo "❌ Ошибка применения policy"
    echo ""
    echo "Ручная настройка через веб-интерфейс:"
    echo "1. Открыть https://console.cloud.yandex.ru/folders/..."
    echo "2. Object Storage → Бакеты → hearyou-stt-temp"
    echo "3. Настройки → Lifecycle → Добавить правило"
    echo "4. Удаление объектов через: 1 день"
fi

rm "$LIFECYCLE_FILE"
