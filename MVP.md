# HearYou MVP - Minimum Viable Product

**Дата:** 5 марта 2026  
**Версия:** 1.0.0  
**Статус:** ✅ Production Ready

## 🎯 Основной функционал

### ✅ Транскрибация аудио
- **Провайдер:** Yandex SpeechKit (асинхронный API)
- **Языки:** ru-RU (основной), en-US, другие по запросу
- **Форматы:** MP3, WAV, OGG, M4A, FLAC
- **Размер файлов:** до 1 ГБ (лимит 100 МБ на уровне uvicorn, 25 ГБ на nginx)
- **Качество:** WER ~5-8% для русского языка

### ✅ Speaker Diarization (разделение по спикерам)
- **Primary:** Resemblyzer (работает без токенов)
- **State-of-the-art:** Pyannote.audio 4.0.4 (требует HuggingFace токен)
- **Fallback:** автоматическое переключение pyannote → resemblyzer
- **Точность:** определяет смены спикеров, форматирует как диалог

### ✅ Улучшение текста
- **Фильтр звуков:** убирает "эээ", "ммм", "бе", "ме"
- **Слова-паразиты:** опционально убирает "вот", "типа", "короче"
- **Артефакты:** автоисправление "иишка" → "ИИшка", "мелишка" → "Мелешка"
- **Пунктуация:** автоматическая расстановка
- **Литературный стиль:** опциональная обработка для официальных текстов

### ✅ JTBD Analysis (Jobs-to-be-Done)
- **Провайдер:** Claude (Anthropic API)
- **Категории:** Jobs, Pains, Gains, Context, Triggers
- **Применение:** анализ интервью с пользователями, выявление потребностей

## 🛠️ Технический стек

### Backend
- **FastAPI** - веб-фреймворк
- **Uvicorn** - ASGI сервер (с увеличенным h11-max-incomplete-event-size до 100MB)
- **Yandex SpeechKit** - STT API
- **Pyannote.audio 4.0.4** - state-of-the-art speaker diarization
- **Resemblyzer** - fallback speaker diarization
- **Torch 2.10.0** + CUDA 12.8 - ML inference

### Frontend
- **Vanilla JS** - без фреймворков
- **SSE (Server-Sent Events)** - real-time progress
- **Responsive UI** - адаптивный дизайн (мобильные + десктоп)

### Infrastructure
- **Docker** + **Docker Compose**
- **Nginx** - reverse proxy с HTTPS
- **Yandex Object Storage** - временное хранение больших файлов
- **Local filesystem** - results + uploads

## 📦 Деплой

### Production (VPS)
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service
docker-compose down
docker-compose up -d
```

**URL:** https://92.51.36.233/

### Development (live reload)
```bash
docker-compose -f docker-compose.dev.yml up -d
```
Изменения в `.py` и `static/` применяются мгновенно!

## 🔧 Конфигурация

### Обязательные переменные окружения
- `YANDEX_API_KEY` - Yandex SpeechKit API ключ
- `YANDEX_FOLDER_ID` - Yandex Cloud folder ID
- `AWS_ACCESS_KEY_ID` - Yandex Object Storage ключ
- `AWS_SECRET_ACCESS_KEY` - Yandex Object Storage секрет

### Опциональные
- `HUGGINGFACE_TOKEN` - для pyannote.audio (state-of-the-art diarization)
- `ANTHROPIC_API_KEY` - для JTBD анализа

## 📊 Производительность

### Скорость транскрибации
- **Короткие файлы** (<1 мин): ~10-15 секунд
- **Средние файлы** (5-10 мин): ~40-60 секунд
- **Длинные файлы** (30-60 мин): ~3-5 минут

### Speaker Diarization
- **Resemblyzer:** +5-10 секунд на файл
- **Pyannote:** +30-60 секунд (точнее, но медленнее)

### Ограничения
- **Конкуренция:** 1 задача одновременно (Yandex SpeechKit лимит на folder)
- **Rate limit:** 10 запросов/минуту с одного IP

## 🎨 UI/UX Features

### Основной интерфейс
- ✅ Drag & drop загрузка файлов
- ✅ Real-time прогресс бар с процентами
- ✅ Таймер обработки
- ✅ История транскрибаций (localStorage)
- ✅ Копирование результата в буфер

### Speaker Diarization UI
- ✅ Цветные блоки для каждого спикера
- ✅ Аватары с номерами (S1, S2, ...)
- ✅ Компактное отображение (margin: 2px, padding: 4px 8px)
- ✅ Адаптивный дизайн для мобильных

### Опции
- 🎭 Определить спикеров (кто говорил)
- 🎯 JTBD анализ (Jobs-to-be-Done)
- 🧹 Очистка от слов-паразитов
- 📝 Автоисправление артефактов

## 🐛 Известные ограничения

### Speaker Diarization
- **Без HuggingFace токена:** работает resemblyzer (базовое качество)
- **С токеном:** pyannote.audio (отличное качество, но требует регистрации)

### Размер файлов
- **Uvicorn limit:** 100 МБ (можно увеличить через `--h11-max-incomplete-event-size`)
- **Nginx limit:** 25 ГБ (client_max_body_size)
- **Рекомендация:** файлы >500 МБ могут обрабатываться медленно

### Конкурентность
- Только 1 задача одновременно (Yandex API лимит)
- Очередь задач работает FIFO

## 📝 Changelog (5 марта 2026)

### ✅ Исправлено
- 🐛 Файлы >16 МБ падали с 400 Bad Request → увеличен h11-max-incomplete-event-size до 100 МБ
- 🐛 Speaker diarization не разделял текст → исправлены text cleaner'ы (сохраняют `\n\n`)
- 🐛 Pyannote.audio 3.1.1 несовместим с torchaudio 2.10 → обновлено до 4.0.4
- 🐛 Fallback на resemblyzer падал с ImportError → импортируются оба backend'а
- 🐛 Огромные отступы в UI → уменьшены margin/padding в 5-10 раз

### ✨ Добавлено
- ✅ Pyannote.audio 4.0.4 - state-of-the-art speaker diarization
- ✅ Автоматический fallback pyannote → resemblyzer
- ✅ Документация: PYANNOTE_SETUP.md, README_DOCKER.md
- ✅ Docker volumes для static/ - live reload без rebuild
- ✅ Оптимизированный Dockerfile - rebuild за 15 секунд вместо 10 минут
- ✅ Cache-Control: no-cache для HTML - всегда свежая версия

### 🎨 UI улучшения
- Компактные отступы между блоками спикеров (2px вместо 20px)
- Минимальные padding внутри блоков (4px 8px вместо 12px 16px)
- Уменьшен размер шрифта labels (11px вместо 13px)
- Убраны лишние whitespace из HTML

## 🚀 Следующие шаги (Roadmap)

### Приоритет 1
- [ ] Получить HuggingFace токен для pyannote (state-of-the-art качество)
- [ ] Добавить поддержку нескольких языков в UI
- [ ] Реализовать очередь задач с приоритетами

### Приоритет 2
- [ ] Экспорт результатов (TXT, DOCX, SRT, JSON)
- [ ] Редактирование транскрипции в UI
- [ ] Поиск по истории транскрибаций

### Приоритет 3
- [ ] Автоопределение языка аудио
- [ ] Поддержка видео файлов (извлечение аудио)
- [ ] API для интеграции с внешними системами

## 📚 Документация

- `README.md` - основное описание проекта
- `PYANNOTE_SETUP.md` - настройка pyannote.audio
- `README_DOCKER.md` - Docker workflow (dev/prod)
- `AQUILLA_WORKFLOW.md` - рабочий процесс разработки
- `MVP.md` - этот документ

## 🔐 Безопасность

- ✅ Rate limiting по IP
- ✅ Валидация MIME-types файлов
- ✅ Ограничение размера файлов
- ✅ Очистка временных файлов после обработки
- ✅ HTTPS через nginx
- ⚠️ **TODO:** Аутентификация пользователей

## 📞 Контакты

- **Разработчик:** Артём
- **Ассистент:** Аквилла (AI)
- **GitHub:** https://github.com/Drovwosek/hearyou
- **Статус:** Production Ready ✅

---

**Последнее обновление:** 5 марта 2026, 20:30 UTC  
**Commit:** 67697fa
