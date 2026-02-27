#!/bin/bash
# Пример полного pipeline транскрибации с максимальным качеством

echo "🎯 Пример полного pipeline Yandex STT"
echo

# Файл для обработки
AUDIO_FILE="${1:-test_audio.ogg}"

echo "📁 Файл: $AUDIO_FILE"
echo

# Шаг 1: Базовая транскрибация
echo "1️⃣ Базовая транскрибация (без фильтров):"
python3 transcribe.py "$AUDIO_FILE" --no-corrections
echo

# Шаг 2: С фильтром слов-паразитов
echo "2️⃣ С фильтром слов-паразитов (--clean):"
python3 transcribe.py "$AUDIO_FILE" --clean --no-corrections
echo

# Шаг 3: С API фильтром (literature_text)
echo "3️⃣ С Yandex фильтром (--literature):"
python3 transcribe.py "$AUDIO_FILE" --literature --no-corrections
echo

# Шаг 4: С исправлениями
echo "4️⃣ С исправлениями специфичных слов:"
python3 transcribe.py "$AUDIO_FILE"
echo

# Шаг 5: Максимальное качество (всё вместе)
echo "5️⃣ МАКСИМАЛЬНОЕ КАЧЕСТВО (всё вместе):"
python3 transcribe.py "$AUDIO_FILE" --literature --clean -v
echo

echo "✅ Готово! Сравни результаты выше."
