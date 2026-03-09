# Docker Workflow для HearYou STT

## Режимы работы

### Production (docker-compose.yml)
```bash
docker-compose down
docker-compose build
docker-compose up -d
```
- Полная пересборка: ~10 минут
- Стабильный режим для прода

### Development (docker-compose.dev.yml)
```bash
# Первый раз собрать образ
docker-compose -f docker-compose.dev.yml build

# Запуск с live reload
docker-compose -f docker-compose.dev.yml up -d

# Изменения в .py файлах применяются МГНОВЕННО!
# Изменения в static/ применяются МГНОВЕННО!
```

**Преимущества dev режима:**
- ✅ Изменения в Python коде применяются без rebuild (uvicorn --reload)
- ✅ Изменения в static файлах применяются сразу
- ✅ Логи видны в реальном времени: `docker-compose -f docker-compose.dev.yml logs -f`

**Когда нужен rebuild:**
- Изменился `requirements.txt`
- Добавлены новые системные зависимости
- Изменён Dockerfile

## Оптимизация Dockerfile

**Текущая проблема:** `core/` копируется ДО установки requirements  
→ Любое изменение в core/ инвалидирует кеш и torch переустанавливается заново

**Решение:** Использовать `Dockerfile.optimized`
- requirements.txt копируется и устанавливается ПЕРВЫМ
- Код копируется ПОСЛЕ
- При изменении кода: rebuild за 30 секунд (вместо 10 минут!)

```bash
# Переключиться на оптимизированный Dockerfile
mv Dockerfile Dockerfile.old
mv Dockerfile.optimized Dockerfile
docker-compose build  # Быстро!
```

## Чистка

```bash
# Удалить старые образы и слои
docker system prune -af

# Удалить dangling images
docker images -qf dangling=true | xargs -r docker rmi
```
