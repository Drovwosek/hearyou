# Yandex SpeechKit - Настройка завершена ✅

## 🎯 Что настроено

- ✅ API-ключ создан и сохранён
- ✅ Folder ID настроен
- ✅ Авторизация протестирована
- ✅ Python-обёртка готова к использованию

## 📁 Файлы

- `.env.yandex` - конфигурация (API ключ + Folder ID)
- `yandex_stt.py` - основная библиотека
- `test_yandex_stt.py` - тестовый скрипт

## 🚀 Быстрый старт

### Вариант 1: Простая транскрибация

```python
from yandex_stt import YandexSTT

# Инициализация (читает креды из .env.yandex)
stt = YandexSTT()

# Транскрибация (для файлов до 1 минуты)
result = stt.transcribe_sync(
    "audio.mp3",           # Путь к файлу
    language="ru-RU",      # Язык
    punctuation=True       # Пунктуация
)

# Получить текст
text = result.get('result', '')
print(text)
```

### Вариант 2: Из командной строки

```bash
# Создай простой CLI скрипт
python3 -c "
from yandex_stt import YandexSTT
import sys
stt = YandexSTT()
result = stt.transcribe_sync(sys.argv[1])
print(result.get('result', ''))
" audio.mp3
```

## 📊 Форматы аудио

Поддерживаются:
- **MP3** (рекомендуется)
- **OGG Opus**
- **WAV** (PCM 16-bit)
- **FLAC**

## ⚙️ Параметры

### Языки
- `ru-RU` - русский (по умолчанию)
- `en-US` - английский
- `tr-TR` - турецкий
- и другие (полный список в документации Yandex)

### Дополнительные опции
- `punctuation=True` - автоматическая пунктуация
- `profanity_filter=True` - фильтр мата
- `format="auto"` - автоопределение формата (или lpcm, oggopus, mp3)

## 📝 Ограничения синхронного API

- ⏱️ Длительность: **до 1 минуты**
- 📦 Размер: **до 1 МБ**
- 🎤 Для более длинных файлов используй async API (требует Object Storage)

## 💰 Стоимость

- ~1.2₽ за минуту аудио
- 100 часов ≈ 7200₽ (~$75)

## 🔧 Устранение проблем

### "Missing YANDEX_API_KEY"
Проверь файл `.env.yandex` - должен содержать ключ

### "API Error 401"
Неверный API-ключ, создай новый в консоли

### "API Error 400"
- Проверь формат файла (должен быть audio)
- Файл не должен превышать 1 минуту/1 МБ

## 🎓 Примеры использования

### Пример 1: Транскрибация с обработкой ошибок

```python
from yandex_stt import YandexSTT

stt = YandexSTT()

try:
    result = stt.transcribe_sync("recording.mp3")
    
    if 'result' in result:
        print("✅ Транскрипция:")
        print(result['result'])
    else:
        print("⚠️ Ничего не распознано")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
```

### Пример 2: Пакетная обработка

```python
from yandex_stt import YandexSTT
from pathlib import Path

stt = YandexSTT()

# Обработать все MP3 в папке
audio_files = Path("audio_files").glob("*.mp3")

for audio_file in audio_files:
    print(f"Обработка: {audio_file.name}...")
    
    try:
        result = stt.transcribe_sync(str(audio_file))
        text = result.get('result', '')
        
        # Сохранить транскрипцию
        output_file = audio_file.with_suffix('.txt')
        output_file.write_text(text, encoding='utf-8')
        
        print(f"  ✅ Готово: {output_file.name}")
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
```

### Пример 3: Разные языки

```python
from yandex_stt import YandexSTT

stt = YandexSTT()

# Английский
result_en = stt.transcribe_sync("english.mp3", language="en-US")
print("English:", result_en.get('result'))

# Русский
result_ru = stt.transcribe_sync("russian.mp3", language="ru-RU")
print("Русский:", result_ru.get('result'))
```

## 📚 Дополнительно

- [Документация Yandex SpeechKit](https://cloud.yandex.ru/docs/speechkit/)
- [Поддерживаемые языки](https://cloud.yandex.ru/docs/speechkit/stt/models)
- [Примеры кода](https://cloud.yandex.ru/docs/speechkit/quickstart)

---

**Настроено:** 26.02.2026 by Aquilla 🦅  
**Статус:** ✅ Полностью рабочий
