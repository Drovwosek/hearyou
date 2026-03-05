# Настройка pyannote.audio для speaker diarization

Pyannote.audio - это state-of-the-art решение для определения "кто когда говорит". Значительно точнее resemblyzer.

## Шаг 1: Получите HuggingFace токен

1. Зарегистрируйтесь на **https://huggingface.co** (если ещё не зарегистрированы)

2. Создайте токен доступа:
   - Перейдите в https://huggingface.co/settings/tokens
   - Нажмите **New token**
   - Тип токена: **Read** (только чтение)
   - Скопируйте созданный токен

3. Примите условия использования моделей:
   - https://huggingface.co/pyannote/speaker-diarization-3.1 — нажмите **Agree and access repository**
   - https://huggingface.co/pyannote/segmentation-3.0 — нажмите **Agree and access repository**

## Шаг 2: Создайте файл .env.huggingface

```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service
cp .env.huggingface.example .env.huggingface
nano .env.huggingface  # или vim
```

Вставьте свой токен:

```bash
HUGGINGFACE_TOKEN=hf_ваш_токен_здесь
```

Сохраните файл (Ctrl+O, Enter, Ctrl+X).

## Шаг 3: Пересоберите Docker образ

```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service

# Пересборка с обновлёнными зависимостями
docker-compose build --no-cache

# Перезапуск
docker-compose down && docker-compose up -d
```

## Шаг 4: Проверьте логи

```bash
docker logs hearyou-stt -f
```

Вы должны увидеть:
```
✅ Используется pyannote.audio для speaker diarization
```

Если видите:
```
⚠️ Не удалось загрузить pyannote, используется fallback
```

Значит проблема с токеном или моделями.

## Шаг 5: Протестируйте

Загрузите аудио с включённой опцией "🎭 Определить спикеров" через https://92.51.36.233/

Теперь диаризация должна работать **значительно точнее**:
- ✅ Определяет короткие реплики
- ✅ Работает с перебиваниями
- ✅ Точные границы между спикерами
- ✅ Автоматическое определение количества спикеров

## Troubleshooting

### "Требуется HuggingFace токен"
- Убедитесь что файл `.env.huggingface` существует
- Проверьте что токен записан без лишних пробелов
- Перезапустите контейнер: `docker-compose restart`

### "403 Forbidden" при загрузке модели
- Вы не приняли условия использования моделей (Шаг 1, пункт 3)
- Зайдите на страницы моделей и нажмите "Agree"

### "CUDA out of memory" (если есть GPU)
- Модель требует ~2GB VRAM
- Если недостаточно памяти, pyannote автоматически переключится на CPU

### Fallback на resemblyzer
- Если pyannote не работает, сервис автоматически использует старый resemblyzer
- Функциональность сохраняется, но точность ниже
