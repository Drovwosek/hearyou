# Deployment Guide

## Автоматический деплой (CI/CD)

### GitHub Actions

При каждом push в `main` запускается CI. Если workflow `Tests` завершился успешно,
workflow `Deploy to Production` фиксирует успешный handoff, а VPS сам забирает
последний SHA с успешным `Tests` и деплоит его через `hearyou-pull-deploy.timer`.

**Настройка (один раз):**

1. На VPS включен systemd timer `hearyou-pull-deploy.timer`.
2. Timer проверяет последний успешный `Tests` run на `main`.
3. Если SHA изменился, сервер делает `git reset`, обновляет venv-зависимости и
   перезапускает `hearyou-stt.service`.

**Ручной запуск:**

```bash
ssh root@72.56.8.201 'systemctl start hearyou-pull-deploy.service'
```

---

## Ручной деплой

```bash
ssh root@72.56.8.201
systemctl start hearyou-pull-deploy.service
journalctl -u hearyou-pull-deploy.service -f
```

Скрипт автоматически:
1. Берет последний SHA с успешным `Tests`.
2. Обновляет `/root/hearyou`.
3. Обновляет `/opt/hearyou-venv`.
4. Перезапускает `hearyou-stt.service`.
5. Проверяет `/stats`.

---

## Управление на VPS

```bash
# SSH
ssh root@72.56.8.201

# Статус
systemctl status hearyou-stt.service
systemctl status hearyou-pull-deploy.timer

# Логи
journalctl -u hearyou-stt.service -f
journalctl -u hearyou-pull-deploy.service -f

# Рестарт
systemctl restart hearyou-stt.service

# Остановка
systemctl stop hearyou-stt.service

# Текущий задеплоенный SHA
cat /var/lib/hearyou-deploy/deployed.sha
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

**Production:** http://72.56.8.201:8000

**API Docs:** http://72.56.8.201:8000/docs
