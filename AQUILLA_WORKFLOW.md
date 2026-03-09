# HearYou Workflow - Правила для Аквиллы 🦅

## ⚠️ ВАЖНО: Source of Truth

**Рабочая директория:** `/root/.openclaw/workspace/hearyou/`  
**Оригинал (backup):** `/root/hearyou/`

Все изменения делаю **ТОЛЬКО** в workspace, затем синхронизирую в оригинал.

## 📁 Структура

```
/root/.openclaw/workspace/hearyou/
├── packages/
│   └── stt-service/
│       ├── app.py              # Python backend
│       ├── docker-compose.yml  # Docker конфигурация
│       ├── Dockerfile          # Сборка образа
│       ├── static/
│       │   ├── index.html      # Фронтенд (volume → контейнер)
│       │   └── favicon.ico
│       ├── uploads/            # Загруженные файлы (volume)
│       ├── results/            # Результаты (volume)
│       └── .env.yandex         # API ключи (volume, read-only)
└── core/                       # Общие модули (внутри образа)
```

## 🔄 Volumes (Live Updates)

**Настроено в docker-compose.yml:**
```yaml
volumes:
  - ./static:/app/static:ro     # Frontend - изменения применяются МГНОВЕННО
  - ./uploads:/app/uploads       # User uploads
  - ./results:/app/results       # Transcription results
  - ./.env.yandex:/app/.env.yandex:ro
```

## ✏️ Workflow для изменений

### Фронтенд (HTML/CSS/JS)

1. **Править:** `/root/.openclaw/workspace/hearyou/packages/stt-service/static/index.html`
2. **Применяется:** МГНОВЕННО (volume mount)
3. **Синхронизировать в backup:**
   ```bash
   rsync -av --delete /root/.openclaw/workspace/hearyou/packages/stt-service/static/ /root/hearyou/packages/stt-service/static/
   ```
4. Пользователь делает Ctrl+Shift+R для очистки кэша

### Backend (Python)

1. **Править:** `/root/.openclaw/workspace/hearyou/packages/stt-service/app.py`
2. **Rebuild образа:**
   ```bash
   cd /root/.openclaw/workspace/hearyou/packages/stt-service
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```
3. **Синхронизировать:**
   ```bash
   rsync -av /root/.openclaw/workspace/hearyou/packages/stt-service/app.py /root/hearyou/packages/stt-service/app.py
   ```

### Docker конфигурация

1. **Править:** `/root/.openclaw/workspace/hearyou/packages/stt-service/docker-compose.yml`
2. **Применить:**
   ```bash
   cd /root/.openclaw/workspace/hearyou/packages/stt-service
   docker-compose down
   docker-compose up -d
   ```
3. **Синхронизировать:**
   ```bash
   rsync -av /root/.openclaw/workspace/hearyou/packages/stt-service/docker-compose.yml /root/hearyou/packages/stt-service/docker-compose.yml
   ```

## 🚫 НЕ делать

- ❌ **НЕ** использовать `docker cp` - изменения пропадут при rebuild
- ❌ **НЕ** править файлы внутри контейнера (`docker exec ... vim`)
- ❌ **НЕ** править `/root/hearyou/` напрямую (только через sync из workspace)

## ✅ Проверка изменений

```bash
# Frontend изменения видны сразу
curl -s http://localhost:8000/ | grep "твоё изменение"

# Проверить что volume смонтирован
docker inspect hearyou-stt | grep -A 5 "Mounts"

# Проверить логи
docker logs hearyou-stt -f
```

## 📊 Текущее состояние

- **Контейнер:** hearyou-stt (running)
- **Порты:** 8000 (Docker) → 443 (Nginx HTTPS)
- **URL:** https://92.51.36.233/
- **Лимиты:** 1 ГБ (uvicorn) / 25 ГБ (nginx)
- **Static:** Live updates через volume ✅

## 🎭 Speaker Diarization (pyannote.audio)

**State-of-the-art алгоритм** для определения "кто когда говорит" - заменил слабый resemblyzer.

**Преимущества pyannote:**
- ✅ Точное определение границ реплик
- ✅ Работает с перебиваниями
- ✅ Короткие фразы определяет корректно
- ✅ Автоопределение количества спикеров

**Требуется:** HuggingFace токен (бесплатный)

**Setup:**
1. Следуй инструкциям: `PYANNOTE_SETUP.md`
2. Создай `.env.huggingface` с токеном
3. Пересобери образ: `docker-compose build --no-cache`
4. Перезапусти: `docker-compose down && docker-compose up -d`

**Fallback:** Если pyannote недоступен, автоматически используется resemblyzer (старый алгоритм).

**Файлы:**
- `speaker_diarization_pyannote.py` — новый (основной)
- `speaker_diarization_resemblyzer.py` — старый (fallback)
- `.env.huggingface.example` — шаблон для токена

## 📝 После каждого изменения

1. Сделать изменение в workspace
2. Проверить что работает
3. Синхронизировать в backup
4. Обновить `memory/YYYY-MM-DD.md`

---

**Принцип:** Workspace → Тест → Backup → Документация
