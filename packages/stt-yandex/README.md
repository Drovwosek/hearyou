# Yandex SpeechKit STT Integration

Интеграция Yandex SpeechKit для транскрибации аудио с максимальным качеством для русского языка.

## ✨ Возможности

- 🎯 **Лучшее качество для русского** (WER 5-8%)
- 🔄 **Автоматическая конвертация** форматов (AAC/MP3/WAV → OGG Opus)
- 🧹 **Фильтрация слов-паразитов** ("эээ", "ммм", "ну", "вот")
- ✅ **Исправление специфичных слов** (словарь замен)
- 📝 **CLI + Python API**
- 💰 **Экономично** (~1.2₽/минута)

## 🚀 Быстрый старт

### Установка

```bash
cd packages/stt-yandex
pip install -r requirements.txt
```

### Конфигурация

Создай файл `.env.yandex`:

```bash
YANDEX_API_KEY=your_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here
```

### Использование

```bash
# Простая транскрибация
python3 transcribe.py audio.mp3

# С фильтрацией паразитов и исправлениями
python3 transcribe.py audio.mp3 --literature --clean -v
```

## 📚 Документация

- [QUICKSTART.md](./QUICKSTART.md) - быстрый старт
- [YANDEX_STT_README.md](./YANDEX_STT_README.md) - полное руководство
- [ACCURACY_GUIDE.md](./ACCURACY_GUIDE.md) - улучшение точности
- [FILLER_WORDS_GUIDE.md](./FILLER_WORDS_GUIDE.md) - фильтрация паразитов
- [FINAL_REPORT.md](./FINAL_REPORT.md) - отчёт о тестировании

## 🎯 Пример

```python
from yandex_stt import YandexSTT
from filler_words_filter import FillerWordsFilter

# Инициализация
stt = YandexSTT()
filler_filter = FillerWordsFilter()

# Транскрибация
result = stt.transcribe_sync("audio.mp3", 
                             format='oggopus',
                             literature_text=True)

# Очистка
text = filler_filter.clean(result['result'])
print(text)
```

## 📦 Интеграция с HearYou

Этот пакет можно использовать как STT провайдер для HearYou:

```javascript
// packages/api/src/stt/providers/yandex.ts
import { exec } from 'child_process';

async function transcribeYandex(audioPath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    exec(
      `python3 packages/stt-yandex/transcribe.py ${audioPath} --literature --clean`,
      (error, stdout) => {
        if (error) reject(error);
        resolve(stdout.trim());
      }
    );
  });
}
```

## 🔑 API-ключ

Получить API-ключ: https://console.cloud.yandex.ru/

1. Создать сервисный аккаунт
2. Выдать роль `ai.speechkit-stt.user`
3. Создать API-ключ
4. Скопировать в `.env.yandex`

---

**Настроено by Aquilla 🦅**
