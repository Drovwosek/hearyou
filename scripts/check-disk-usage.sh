#!/bin/bash
# HearYou - Мониторинг размера папки uploads
# Предупреждает если размер превышает порог

UPLOADS_DIR="/root/hearyou/packages/stt-service/uploads"
THRESHOLD=1000  # 1GB в MB
LOG_FILE="/var/log/hearyou-cleanup.log"

# Получить размер в MB
UPLOADS_SIZE=$(du -sm "$UPLOADS_DIR" 2>/dev/null | awk '{print $1}')

if [ -z "$UPLOADS_SIZE" ]; then
    echo "Ошибка: не удалось получить размер $UPLOADS_DIR"
    exit 1
fi

# Проверить порог
if [ "$UPLOADS_SIZE" -gt "$THRESHOLD" ]; then
    MESSAGE="⚠️ Warning: uploads/ > 1GB (текущий размер: $UPLOADS_SIZE MB)"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $MESSAGE" | tee -a "$LOG_FILE"
    
    # TODO: Добавить отправку уведомления (например, через Telegram)
    # curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    #   -d "chat_id=<CHAT_ID>" \
    #   -d "text=$MESSAGE"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Размер uploads: $UPLOADS_SIZE MB (норма)" | tee -a "$LOG_FILE"
fi
