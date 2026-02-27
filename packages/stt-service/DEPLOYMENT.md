# Deployment Guide

## Автоматический деплой (CI/CD)

### GitHub Actions

При каждом push в `main` автоматически деплоится на VPS.

**Настройка (один раз):**

1. Добавь SSH ключ в GitHub Secrets:
   ```bash
   # На этой машине:
   cat ~/.ssh/id_ed25519
   ```

2. GitHub → Settings → Secrets and variables → Actions → New secret
   - Name: `SSH_PRIVATE_KEY`
   - Value: *содержимое приватного ключа*

3. Готово! Теперь при push в main автоматически обновляется сервис.

**Ручной запуск:**
- GitHub → Actions → Deploy STT Service → Run workflow

---

## Ручной деплой

```bash
cd packages/stt-service
./deploy.sh
```

Скрипт автоматически:
1. Синхронизирует файлы на VPS
2. Пересобирает Docker образ
3. Перезапускает сервис
4. Проверяет доступность

---

## Управление на VPS

```bash
# SSH
ssh root@92.51.36.233

# Статус
cd /root/hearyou/packages
docker-compose -f stt-service/docker-compose.yml ps

# Логи
docker-compose -f stt-service/docker-compose.yml logs -f

# Рестарт
docker-compose -f stt-service/docker-compose.yml restart

# Остановка
docker-compose -f stt-service/docker-compose.yml down

# Пересборка
docker-compose -f stt-service/docker-compose.yml up -d --build
```

---

## Мониторинг

Автоматическая проверка каждые 6-8 часов через OpenClaw heartbeat:

```bash
/root/.openclaw/workspace/scripts/check-stt-service.sh
```

Проверяет:
- SSH подключение
- Docker контейнер
- HTTP доступность
- API endpoints
- Ресурсы VPS

При проблемах автоматически пытается исправить и сообщает.

---

## URL

**Production:** http://92.51.36.233:8000

**API Docs:** http://92.51.36.233:8000/docs
