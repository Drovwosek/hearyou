# HearYou Core

**Общие модули для всех сервисов HearYou**

## Назначение

Этот модуль устраняет дублирование кода между `stt-service` и `stt-yandex`, содержа общую логику работы с Yandex SpeechKit STT.

## Содержимое

### 1. `yandex_stt.py`
Клиент для Yandex SpeechKit API:
- Синхронный STT (до 1 МБ)
- Асинхронный STT (до 1 ГБ через Object Storage)
- Поддержка speaker diarization
- Автоматический выбор API

### 2. `filler_words_filter.py`
Фильтр слов-паразитов для русского языка:
- Базовый список слов-паразитов
- Режим "литературный текст" (более агрессивная фильтрация)
- Сохранение структуры текста

### 3. `stt_corrections.py`
Пост-обработка транскрипции:
- Исправление частых ошибок STT
- Загрузка пользовательских словарей из JSON
- Фонетические замены
- Поддержка доменных терминов

### 4. `transcribe.py`
CLI утилита для транскрибации:
- Простой интерфейс командной строки
- Поддержка всех опций Yandex STT
- Интеграция с фильтрами и исправлениями

## Использование

### В Python коде

```python
import sys
sys.path.insert(0, '/root/hearyou')

from core.yandex_stt import YandexSTT
from core.filler_words_filter import FillerWordsFilter
from core.stt_corrections import correct_transcription

# Транскрибация
stt = YandexSTT()
result = stt.transcribe_sync("audio.mp3", literature_text=True)

# Фильтрация
filter = FillerWordsFilter()
clean_text = filter.filter(result['result'], mode='literature')

# Исправления
final_text = correct_transcription(clean_text)
```

### В Docker

Добавьте volume в `docker-compose.yml`:

```yaml
services:
  stt-service:
    volumes:
      - /root/hearyou/core:/app/core:ro
```

## Миграция

### Было (дублирование):
```
packages/stt-service/yandex_stt.py
packages/stt-yandex/yandex_stt.py
```

### Стало (единый источник):
```
core/yandex_stt.py
```

### Обновление импортов:

**Старый код:**
```python
from yandex_stt import YandexSTT
```

**Новый код:**
```python
import sys
sys.path.insert(0, '/root/hearyou')
from core.yandex_stt import YandexSTT
```

## Преимущества

✅ **Устранено ~1000 строк дублирования**  
✅ **Один источник правды** - изменения в одном месте  
✅ **Легче поддержка** - фиксы применяются ко всем сервисам  
✅ **Единые тесты** - один набор тестов для всех  

## История

**2026-02-27**: Создан общий модуль, устранено 30% дублирования кода между сервисами
