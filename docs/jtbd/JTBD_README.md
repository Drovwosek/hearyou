# JTBD Analyzer для HearYou

Автоматический анализ транскрипций по фреймворку **Jobs To Be Done** с помощью Claude Sonnet 4.5.

## Что такое JTBD?

**Jobs To Be Done (JTBD)** — фреймворк для понимания потребностей пользователей через призму "работ", которые они хотят выполнить.

### Элементы JTBD:

1. **Jobs (Работы)** — основные цели и задачи пользователя
   - Функциональные (что нужно сделать)
   - Эмоциональные (как хочется себя чувствовать)
   - Социальные (как хочется выглядеть в глазах других)

2. **Pains (Боли)** — проблемы, препятствия, риски
   - Нежелательные результаты
   - Сложности и барьеры
   - Риски и страхи

3. **Gains (Выгоды)** — желаемые результаты
   - Требуемые выгоды (минимум)
   - Ожидаемые выгоды (стандарт)
   - Желаемые выгоды (приятные сюрпризы)
   - Неожиданные выгоды (превышение ожиданий)

4. **Context (Контекст)** — условия и ситуации
   - Когда возникает потребность
   - Где происходит
   - С кем взаимодействует
   - Какие ограничения существуют

5. **Triggers (Триггеры)** — что запускает работу
   - События
   - Моменты переключения
   - Проблемы, требующие решения

---

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install anthropic
```

### 2. Настройка API ключа Claude

Экспортируйте переменную окружения:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Или добавьте в `.env` файл:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 3. Проверка работы

```bash
# Тест анализатора
python core/jtbd_analyzer.py test_transcript.txt

# Или через Python
from core.jtbd_analyzer import JTBDAnalyzer

analyzer = JTBDAnalyzer()
result = analyzer.analyze("Ваш текст транскрипции...")
print(result)
```

---

## Использование через API

### 1. Через Web UI

1. Откройте веб-интерфейс HearYou
2. Загрузите аудио файл
3. **Включите опцию "JTBD Analysis"** (по умолчанию включена)
4. Запустите транскрибацию
5. Результат будет содержать секцию `jtbd` с анализом

### 2. Через REST API

**POST /transcribe**

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@interview.mp3" \
  -F "language=ru-RU" \
  -F "analyze_jtbd=true"
```

**Параметры:**
- `file` — аудио файл
- `language` — язык (ru-RU, en-US и т.д.)
- `analyze_jtbd` — включить JTBD анализ (по умолчанию `true`)
- `clean` — убрать слова-паразиты
- `corrections` — применить исправления
- `speaker_labeling` — определить спикеров

**Ответ:**

```json
{
  "task_id": "abc123def456",
  "status": "queued",
  "message": "Задача добавлена в очередь"
}
```

### 3. Получение результата

**GET /result/{task_id}**

```bash
curl "http://localhost:8000/result/abc123def456"
```

**Ответ:**

См. [JTBD_EXAMPLE.json](./JTBD_EXAMPLE.json) для полного примера результата.

Структура:

```json
{
  "task_id": "...",
  "text": "транскрипция текста",
  "jtbd": {
    "jobs": [...],
    "pains": [...],
    "gains": [...],
    "context": [...],
    "triggers": [...],
    "summary": "краткое резюме",
    "metadata": {
      "model": "claude-sonnet-4-5-20250929",
      "total_elements": 15,
      "input_tokens": 1234,
      "output_tokens": 856
    }
  }
}
```

---

## Использование через Python

### Базовое использование

```python
from core.jtbd_analyzer import JTBDAnalyzer

# Инициализация
analyzer = JTBDAnalyzer()

# Анализ текста
text = """
Мне нужно быстро найти работу,
но я не знаю как правильно написать резюме.
Хочется выделиться среди других кандидатов.
"""

result = analyzer.analyze(text)

# Результат
print(f"Jobs: {len(result['jobs'])}")
print(f"Pains: {len(result['pains'])}")
print(f"Summary: {result['summary']}")
```

### Пакетный анализ

```python
texts = [
    "транскрипция интервью 1...",
    "транскрипция интервью 2...",
    "транскрипция интервью 3...",
]

results = analyzer.analyze_batch(texts)

for i, result in enumerate(results):
    print(f"Interview {i+1}: {result['metadata']['total_elements']} elements")
```

### Форматирование в Markdown

```python
result = analyzer.analyze(text)

# Красивый Markdown вывод
markdown = analyzer.format_as_markdown(result)
print(markdown)

# Сохранение в файл
with open("analysis.md", "w") as f:
    f.write(markdown)
```

---

## Структура данных

### Jobs (Работы)

```json
{
  "text": "Научиться программированию на Python",
  "quote": "Мне нужно быстро освоить Python",
  "type": "functional|emotional|social",
  "confidence": "high|medium|low"
}
```

### Pains (Боли)

```json
{
  "text": "Нехватка времени для обучения",
  "quote": "у меня нет времени на курсы",
  "severity": "critical|high|medium|low",
  "confidence": "high|medium|low"
}
```

### Gains (Выгоды)

```json
{
  "text": "Быстрое освоение навыка",
  "quote": "быстро освоить Python",
  "type": "required|expected|desired|unexpected",
  "confidence": "high|medium|low"
}
```

### Context (Контекст)

```json
{
  "text": "Необходимость совмещать с работой",
  "quote": "нет времени на курсы",
  "dimension": "when|where|who|constraints",
  "confidence": "high|medium|low"
}
```

### Triggers (Триггеры)

```json
{
  "text": "Потребность в навыках для работы",
  "quote": "научиться программировать",
  "type": "event|problem|switching_moment",
  "confidence": "high|medium|low"
}
```

---

## Примеры использования

### 1. Анализ интервью с клиентами

```python
from core.jtbd_analyzer import JTBDAnalyzer

analyzer = JTBDAnalyzer()

# Транскрипция интервью
interview = open("customer_interview.txt").read()

# Анализ
result = analyzer.analyze(interview)

# Ключевые инсайты
print(f"Главная работа: {result['jobs'][0]['text']}")
print(f"Главная боль: {result['pains'][0]['text']}")
print(f"Главная выгода: {result['gains'][0]['text']}")
```

### 2. Анализ нескольких интервью

```python
import json
from pathlib import Path

analyzer = JTBDAnalyzer()

# Анализ всех транскрипций в папке
interviews = Path("interviews/").glob("*.txt")

all_results = []
for file in interviews:
    text = file.read_text()
    result = analyzer.analyze(text)
    all_results.append({
        "filename": file.name,
        "jtbd": result
    })

# Сохранение агрегированных результатов
with open("all_interviews_jtbd.json", "w") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
```

### 3. Автоматическая обработка через STT сервис

```python
import requests

# Загрузка и транскрибация с JTBD анализом
files = {"file": open("interview.mp3", "rb")}
data = {
    "language": "ru-RU",
    "analyze_jtbd": True,  # Включить JTBD
    "clean": True,
}

response = requests.post("http://localhost:8000/transcribe", files=files, data=data)
task_id = response.json()["task_id"]

# Получение результата
import time
while True:
    result = requests.get(f"http://localhost:8000/result/{task_id}").json()
    if "jtbd" in result:
        print(f"Jobs: {result['jtbd']['jobs']}")
        break
    time.sleep(5)
```

---

## Стоимость

**Claude Sonnet 4.5:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**Пример для 1000 слов транскрипции:**
- Input: ~1500 tokens (~$0.0045)
- Output: ~800 tokens (~$0.012)
- **Итого: ~$0.017 за анализ**

Для 100 интервью: ~$1.70

---

## Отключение JTBD анализа

Если API ключ Claude не настроен или нужно отключить анализ:

### Через API:

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "analyze_jtbd=false"
```

### Через код:

```python
# Проверка доступности анализатора
from core.jtbd_analyzer import JTBDAnalyzer

try:
    analyzer = JTBDAnalyzer()
    print("JTBD Analyzer доступен")
except ValueError:
    print("JTBD Analyzer не настроен (нет API ключа)")
```

---

## Логирование

Анализатор пишет логи в стандартный logger:

```python
import logging

logging.basicConfig(level=logging.INFO)

# Будут видны логи типа:
# INFO: JTBDAnalyzer initialized with model: claude-sonnet-4-5-20250929
# INFO: Starting JTBD analysis (1234 chars)
# INFO: JTBD analysis completed: 15 elements, 1247 in / 856 out tokens
```

---

## Troubleshooting

### Ошибка: "ANTHROPIC_API_KEY не найден"

**Решение:** Установите переменную окружения:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Ошибка: "Failed to parse JSON from Claude"

**Причина:** Claude вернул невалидный JSON (редко).

**Решение:** Проверьте логи, анализатор пытается извлечь JSON из markdown блоков автоматически.

### Пустые результаты

**Причина:** Текст слишком короткий или не содержит JTBD элементов.

**Решение:** Убедитесь что транскрипция содержит информацию о целях, проблемах или желаемых результатах.

---

## Best Practices

1. **Качественные транскрипции**
   - Используйте `clean=True` для удаления слов-паразитов
   - Включайте `punctuation=True` для корректной расстановки знаков

2. **Объединение нескольких интервью**
   - Анализируйте каждое интервью отдельно
   - Агрегируйте результаты на уровне приложения

3. **Кастомизация промпта**
   - Отредактируйте `_build_prompt()` для специфичных доменов
   - Добавьте примеры в промпт для улучшения качества

4. **Валидация результатов**
   - Проверяйте `confidence` уровень
   - Используйте `quote` для верификации цитат

---

## Примеры кейсов

### Customer Development

Анализ интервью с потенциальными клиентами для валидации гипотез продукта.

### User Research

Понимание потребностей пользователей для дизайна новых фич.

### Market Research

Выявление болей и выгод целевой аудитории для позиционирования.

### Sales Intelligence

Анализ звонков продавцов для понимания возражений и триггеров покупки.

---

## Лицензия

Часть проекта HearYou. MIT License.
