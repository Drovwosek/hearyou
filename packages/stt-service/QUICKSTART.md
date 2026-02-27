# 🚀 Yandex SpeechKit - Быстрый старт

## Одна команда для транскрибации:

```bash
cd /root/.openclaw/workspace
python3 transcribe.py audio.mp3
```

**Поддерживает:** MP3, AAC, WAV, FLAC, M4A, OGG - любые форматы!

---

## Примеры:

```bash
# Простая транскрибация
python3 transcribe.py voice.aac

# С сохранением в файл
python3 transcribe.py recording.mp3 -o result.txt

# Подробный вывод
python3 transcribe.py audio.wav -v

# Английский язык
python3 transcribe.py english.mp3 --lang en-US

# Убрать слова-паразиты ("эээ", "ммм", "ну")
python3 transcribe.py audio.mp3 --clean --literature

# Максимальная точность (с исправлениями + без паразитов)
python3 transcribe.py audio.mp3 --corrections my.json --clean --literature -v

# Помощь
python3 transcribe.py --help
```

---

## Python код:

```python
from yandex_stt import YandexSTT

stt = YandexSTT()
result = stt.transcribe_sync("audio.mp3", format='oggopus')
print(result['result'])
```

---

## Файлы:

- `.env.yandex` - креденшелы (не коммитить!)
- `yandex_stt.py` - библиотека
- `transcribe.py` - CLI утилита

## Документация:

- `FINAL_REPORT.md` - полный отчёт и тесты
- `YANDEX_STT_README.md` - детальная документация
- `SETUP_COMPLETE.md` - руководство по настройке

---

## Ограничения:

- ⏱️ До 1 минуты (для sync API)
- 📦 До 1 МБ
- 💰 ~1.2₽ за минуту

---

**Всё работает! Просто запускай! 🎉**
