#!/bin/bash

# HearYou - Автоматическая очистка старых файлов
# Запускать через cron раз в день

set -e

UPLOAD_DIR="/root/hearyou/packages/stt-service/uploads"
RESULTS_DIR="/root/hearyou/packages/stt-service/results"
LOG_FILE="/var/log/hearyou-cleanup.log"

# Создать лог если не существует
touch "$LOG_FILE"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Начало очистки ==="

# Подсчитать текущее использование диска
DISK_USAGE_BEFORE=$(df -h / | awk 'NR==2 {print $5}')
log "Использование диска до очистки: $DISK_USAGE_BEFORE"

# Подсчитать количество файлов
UPLOADS_COUNT_BEFORE=$(find "$UPLOAD_DIR" -type f 2>/dev/null | wc -l)
RESULTS_COUNT_BEFORE=$(find "$RESULTS_DIR" -type f 2>/dev/null | wc -l)

log "Файлов в uploads до очистки: $UPLOADS_COUNT_BEFORE"
log "Файлов в results до очистки: $RESULTS_COUNT_BEFORE"

# Удалить загрузки старше 3 дней
log "Удаление файлов из uploads старше 3 дней..."
DELETED_UPLOADS=$(find "$UPLOAD_DIR" -type f -mtime +3 -delete -print | wc -l)
log "Удалено из uploads: $DELETED_UPLOADS файлов"

# Удалить результаты старше 90 дней
log "Удаление файлов из results старше 90 дней..."
DELETED_RESULTS=$(find "$RESULTS_DIR" -type f -mtime +90 -delete -print | wc -l)
log "Удалено из results: $DELETED_RESULTS файлов"

# Подсчитать после очистки
UPLOADS_COUNT_AFTER=$(find "$UPLOAD_DIR" -type f 2>/dev/null | wc -l)
RESULTS_COUNT_AFTER=$(find "$RESULTS_DIR" -type f 2>/dev/null | wc -l)
DISK_USAGE_AFTER=$(df -h / | awk 'NR==2 {print $5}')

log "Файлов в uploads после очистки: $UPLOADS_COUNT_AFTER"
log "Файлов в results после очистки: $RESULTS_COUNT_AFTER"
log "Использование диска после очистки: $DISK_USAGE_AFTER"

# Очистить старые логи Docker (оставить последние 10000 строк)
log "Ротация логов Docker..."
docker logs hearyou-stt --tail 10000 > /tmp/hearyou-stt.log 2>&1 || true
if [ -f /tmp/hearyou-stt.log ]; then
    log "Логи сохранены в /tmp/hearyou-stt.log"
fi

log "=== Очистка завершена ==="
log ""
