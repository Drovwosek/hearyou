#!/bin/bash
# Скрипт для быстрого запуска сервиса

echo "🚀 Запуск HearYou STT Service..."
echo

# Проверка .env.yandex
if [ ! -f ".env.yandex" ]; then
    echo "❌ Файл .env.yandex не найден!"
    echo "Создайте его из .env.example и добавьте API ключи"
    exit 1
fi

echo "✅ Конфигурация найдена"
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
