# 🔧 HearYou - Admin Guide

## Архитектура

```
┌─────────────┐      HTTPS (443)      ┌──────────┐
│   Browser   │ ←──────────────────→  │  Nginx   │
└─────────────┘                        └────┬─────┘
                                            │ proxy_pass
                                            ↓
                                    ┌───────────────┐
                                    │ FastAPI       │
                                    │ (port 8000)   │
                                    │ Docker        │
                                    └───────┬───────┘
                                            │
                    ┌───────────────────────┼───────────────┐
                    ↓                       ↓               ↓
            ┌───────────────┐       ┌──────────┐    ┌──────────┐
            │ Yandex STT    │       │  Redis   │    │ Postgres │
            │ (async API)   │       │  Queue   │    │   DB     │
            └───────────────┘       └──────────┘    └──────────┘
```

## Компоненты

### 1. Nginx (Reverse Proxy)
- **Конфиг:** `/etc/nginx/sites-available/hearyou`
- **Порт:** 443 (HTTPS)
- **SSL:** Самоподписанный `/etc/nginx/ssl/hearyou.{crt,key}`
- **Функции:** 
  - Терминация SSL
  - Reverse proxy к FastAPI
  - Лимиты: 1100MB upload, 30min timeout

**Управление:**
```bash
# Проверить конфиг
sudo nginx -t

# Перезапустить
sudo systemctl reload nginx

# Логи
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. FastAPI Application (Docker)
- **Контейнер:** `hearyou-stt`
- **Image:** `stt-service_stt-service`
- **Порт внутри:** 8000
- **Код:** `/root/hearyou/packages/stt-service/`

**Управление:**
```bash
# Статус
docker ps | grep hearyou

# Логи (real-time)
docker logs -f hearyou-stt

# Логи (последние 50 строк)
docker logs --tail 50 hearyou-stt

# Перезапуск
docker restart hearyou-stt

# Остановить
docker stop hearyou-stt

# Запустить заново
docker start hearyou-stt

# Пересобрать после изменений
cd /root/hearyou/packages/stt-service
docker-compose up -d --build
```

### 3. Redis (Очередь задач)
- **Контейнер:** `hearyou_redis_1`
- **Порт:** 6379
- **Функция:** Background task queue

**Проверка:**
```bash
# Статус
docker exec hearyou_redis_1 redis-cli ping
# Должно вернуть: PONG

# Количество задач в очереди
docker exec hearyou_redis_1 redis-cli llen transcription_queue
```

### 4. PostgreSQL (База данных)
- **Контейнер:** `hearyou_postgres_1`
- **Порт:** 5432
- **База:** `hearyou_db`
- **Функция:** Хранение метаданных задач

**Проверка:**
```bash
# Подключиться к БД
docker exec -it hearyou_postgres_1 psql -U postgres -d hearyou_db

# Список таблиц
\dt

# Последние задачи
SELECT task_id, status, filename, created_at FROM tasks ORDER BY created_at DESC LIMIT 10;

# Выход
\q
```

## Мониторинг

### Проверка здоровья сервиса

```bash
# 1. Все контейнеры запущены?
docker ps | grep hearyou

# 2. Nginx работает?
sudo systemctl status nginx

# 3. Сервис отвечает?
curl -k https://92.51.36.233/ | head -5

# 4. API доступен?
curl -k https://92.51.36.233/health
```

### Логи приложения

```bash
# Ошибки последнего часа
docker logs --since 1h hearyou-stt 2>&1 | grep ERROR

# Статистика обработки
docker logs --tail 100 hearyou-stt | grep "POST /transcribe"
```

### Использование ресурсов

```bash
# Память и CPU
docker stats hearyou-stt --no-stream

# Размер логов
docker inspect -f '{{.LogPath}}' hearyou-stt | xargs ls -lh

# Занятое место загрузками
du -sh /root/hearyou/packages/stt-service/uploads/

# Занятое место результатами
du -sh /root/hearyou/packages/stt-service/results/
```

## Обслуживание

### Автоматическая очистка старых файлов

**Статус:** ✅ Настроена автоматическая очистка через cron

**Расписание:** Каждые 6 часов (00:00, 06:00, 12:00, 18:00)

**Скрипт:** `/root/hearyou/scripts/cleanup.sh`

**Параметры очистки:**
- `uploads/` - файлы старше **3 дней** удаляются
- `results/` - файлы старше **90 дней** удаляются
- Логи: `/var/log/hearyou-cleanup.log`

**Проверка работы:**
```bash
# Посмотреть логи последней очистки
tail -30 /var/log/hearyou-cleanup.log

# Проверить расписание cron
crontab -l | grep cleanup

# Запустить вручную (для теста)
/root/hearyou/scripts/cleanup.sh

# Проверить текущий размер папок
du -sh /root/hearyou/packages/stt-service/uploads/
du -sh /root/hearyou/packages/stt-service/results/
```

**Мониторинг размера uploads:**
```bash
# Проверить не превышен ли порог 1GB
/root/hearyou/scripts/check-disk-usage.sh
```

**Ручная очистка (если нужна срочная):**
```bash
# Удалить загрузки старше 3 дней
find /root/hearyou/packages/stt-service/uploads/ -type f -mtime +3 -delete

# Удалить результаты старше 90 дней
find /root/hearyou/packages/stt-service/results/ -type f -mtime +90 -delete

# Очистить логи Docker (освободить место)
docker logs hearyou-stt --tail 0 > /dev/null 2>&1
```

### Обновление кода

```bash
cd /root/hearyou/packages/stt-service

# 1. Backup текущей версии
docker commit hearyou-stt hearyou-stt-backup-$(date +%Y%m%d)

# 2. Изменить код (например, app.py)
nano app.py

# 3. Пересобрать и перезапустить
docker-compose up -d --build

# 4. Проверить логи
docker logs -f hearyou-stt
```

### Обновление SSL сертификата

```bash
# Генерация нового самоподписанного (срок 365 дней)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/hearyou.key \
  -out /etc/nginx/ssl/hearyou.crt \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=iSpring/CN=92.51.36.233"

# Перезапустить Nginx
sudo systemctl reload nginx
```

### Миграция на Let's Encrypt (если появится домен)

```bash
# 1. Установить certbot
sudo apt install certbot python3-certbot-nginx

# 2. Получить сертификат
sudo certbot --nginx -d yourdomain.com

# 3. Автообновление (уже настроено)
sudo systemctl status certbot.timer
```

## Настройка Yandex SpeechKit

**Креды:** `/root/hearyou/packages/stt-service/.env.yandex`

```bash
YANDEX_API_KEY=YOUR_YANDEX_API_KEY_HERE
YANDEX_FOLDER_ID=b1gabj97m2134sfj5pn0
```

**Проверка доступа:**
```bash
docker exec hearyou-stt python3 -c "
from yandex_stt import YandexSTT
stt = YandexSTT()
print('API доступен:', stt.check_auth())
"
```

## Troubleshooting

### Проблема: Файл не загружается (413 Request Entity Too Large)

**Причина:** Недостаточный лимит в Nginx
**Решение:**
```bash
# Проверить лимит
grep client_max_body_size /etc/nginx/sites-available/hearyou

# Должно быть: client_max_body_size 1100M;
# Если нет - добавить и перезапустить
sudo systemctl reload nginx
```

### Проблема: SSE не работает / результат не появляется

**Причина:** Nginx буферизует SSE
**Решение:** Проверить в конфиге Nginx:
```nginx
proxy_buffering off;
proxy_cache off;
```

### Проблема: Docker контейнер не запускается

```bash
# Посмотреть почему упал
docker logs hearyou-stt

# Проверить порты
sudo netstat -tulpn | grep 8000

# Пересоздать с нуля
cd /root/hearyou/packages/stt-service
docker-compose down
docker-compose up -d
```

### Проблема: Yandex API ошибки (401/403)

```bash
# Проверить креды
docker exec hearyou-stt cat /app/.env.yandex

# Проверить доступ к API
curl -H "Authorization: Api-Key YOUR_YANDEX_API_KEY_HERE" \
     "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
```

## Бэкапы

### Что бэкапить

1. **База данных:**
```bash
docker exec hearyou_postgres_1 pg_dump -U postgres hearyou_db > backup_$(date +%Y%m%d).sql
```

2. **Конфигурация:**
```bash
tar -czf hearyou_config_$(date +%Y%m%d).tar.gz \
  /etc/nginx/sites-available/hearyou \
  /etc/nginx/ssl/hearyou.* \
  /root/hearyou/packages/stt-service/.env* \
  /root/hearyou/packages/stt-service/docker-compose.yml
```

3. **Важные файлы (если нужно):**
```bash
# Только файлы меньше 7 дней
find /root/hearyou/packages/stt-service/uploads/ -type f -mtime -7 -exec tar -czf uploads_backup.tar.gz {} +
```

## Метрики и статистика

```bash
# Количество обработанных файлов за сегодня
docker exec hearyou_postgres_1 psql -U postgres -d hearyou_db -c \
  "SELECT COUNT(*) FROM tasks WHERE DATE(created_at) = CURRENT_DATE;"

# Средняя длительность обработки
docker exec hearyou_postgres_1 psql -U postgres -d hearyou_db -c \
  "SELECT AVG(processing_time_sec) FROM tasks WHERE status='completed';"

# Топ самых больших файлов
docker exec hearyou_postgres_1 psql -U postgres -d hearyou_db -c \
  "SELECT filename, file_size_mb FROM tasks ORDER BY file_size_mb DESC LIMIT 10;"
```

## Контакты

**Администратор:** Артём (Product Manager, iSpring)
**Сервер:** 92.51.36.233
**Yandex Cloud:** Folder ID `b1gabj97m2134sfj5pn0`

---

**Last updated:** 2026-02-27
