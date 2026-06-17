#!/bin/bash
# Скрипт для быстрого запуска сервиса

echo "🚀 Запуск HearYou STT Service..."
echo

echo "✅ Yandex credentials не нужны: используется локальный Whisper"
echo "   WHISPER_MODEL=${WHISPER_MODEL:-small}"
echo

# Запуск через docker-compose
docker-compose up -d

echo
echo "✅ Сервис запущен!"
echo "📍 Веб-интерфейс: http://localhost:8000"
echo "📚 API документация: http://localhost:8000/docs"
echo
echo "Команды:"
echo "  Логи:        docker-compose logs -f"
echo "  Остановить:  docker-compose down"
echo "  Перезапуск:  docker-compose restart"
