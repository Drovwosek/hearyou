# 🎯 JTBD UI - Quick Start

## TL;DR

✅ **Frontend готов!** UI для JTBD анализа полностью реализован.  
⏳ **Ждём backend** - нужен анализатор, который вернёт JSON с JTBD данными.

## 🚀 Что сделано

- ✅ Чекбокс для включения JTBD анализа
- ✅ Красивый UI с 5 категориями (Jobs, Pains, Gains, Context, Triggers)
- ✅ Визуализация уверенности (confidence bars)
- ✅ Адаптивный дизайн (mobile + desktop)
- ✅ Интеграция с историей загрузок
- ✅ Копирование результатов

## 📁 Файлы

| Файл | Что внутри |
|------|------------|
| `packages/stt-service/static/index.html` | **Изменён** - добавлен JTBD UI |
| `JTBD_UI_PREVIEW.html` | **Preview** - откройте в браузере для демо |
| `JTBD_UI_DOCUMENTATION.md` | **Документация** - полное описание |
| `JTBD_FRONTEND_REPORT.md` | **Отчёт** - что сделано |

## 👀 Посмотреть дизайн

```bash
# Откройте в браузере:
open hearyou/JTBD_UI_PREVIEW.html

# Или:
firefox hearyou/JTBD_UI_PREVIEW.html
```

## 🔌 Что нужно от Backend

Backend должен вернуть JSON в таком формате:

```json
{
  "result": "текст транскрипции...",
  "jtbd": {
    "jobs": [
      {"text": "Описание работы", "confidence": 0.85}
    ],
    "pains": [
      {"text": "Описание боли", "confidence": 0.72}
    ],
    "gains": [
      {"text": "Описание выгоды", "confidence": 0.91}
    ],
    "context": [
      {"text": "Контекст", "confidence": 0.68}
    ],
    "triggers": [
      {"text": "Триггер", "confidence": 0.79}
    ]
  }
}
```

**Где:**
- `confidence` - float от 0.0 до 1.0
- `text` - строка с описанием

## 🎨 Как выглядит

### Desktop (≥1200px)
```
┌─────────────────┬──────────────────┐
│  Транскрипция   │   JTBD Анализ   │
│                 │                  │
│  [текст...]     │  🎯 Jobs    [3] │
│                 │  😖 Pains   [2] │
│                 │  🎁 Gains   [4] │
│                 │  📍 Context [2] │
│                 │  ⚡ Triggers[2] │
└─────────────────┴──────────────────┘
```

### Mobile
```
┌──────────────────────────┐
│    Транскрипция          │
│    [текст...]            │
└──────────────────────────┘
┌──────────────────────────┐
│    JTBD Анализ           │
│    🎯 Jobs    [3]        │
│    😖 Pains   [2]        │
│    ...                   │
└──────────────────────────┘
```

## 🎯 Категории и цвета

| Emoji | Категория | Цвет |
|-------|-----------|------|
| 🎯 | Jobs (Работы) | Синий |
| 😖 | Pains (Боли) | Красный |
| 🎁 | Gains (Выгоды) | Зелёный |
| 📍 | Context (Контекст) | Жёлтый |
| ⚡ | Triggers (Триггеры) | Фиолетовый |

## ⚙️ Как включить

1. Загрузите файл в HearYou
2. Включите чекбокс **"🎯 JTBD анализ"**
3. Нажмите "Загрузить и транскрибировать"
4. Дождитесь результата
5. Увидите транскрипцию + JTBD справа (или снизу на мобильном)

## 🔧 Для разработчиков

### API endpoint

```javascript
// Frontend отправляет:
POST /transcribe
FormData:
  file: <audio file>
  jtbd_analysis: true  // ← новый параметр

// Backend должен вернуть:
{
  "task_id": "abc123",
  ...
}

// Потом в SSE stream:
{
  "status": "completed",
  "result": "текст транскрипции",
  "jtbd": { ... }  // ← новое поле
}
```

### Тестирование

```javascript
// Имитация JTBD данных для теста:
const mockJTBD = {
  jobs: [
    {text: "Тестовая работа", confidence: 0.85}
  ],
  pains: [
    {text: "Тестовая боль", confidence: 0.72}
  ],
  gains: [
    {text: "Тестовая выгода", confidence: 0.91}
  ],
  context: [],
  triggers: []
};

// Вызов функции:
showJTBD(mockJTBD);
```

## 📞 Частые вопросы

**Q: Где код UI?**  
A: Всё в `packages/stt-service/static/index.html` (CSS + JS встроены)

**Q: Нужны ли зависимости?**  
A: Нет, всё на vanilla JS + CSS

**Q: Работает ли на мобильных?**  
A: Да, адаптивный дизайн

**Q: Что если backend не вернёт JTBD?**  
A: JTBD секция просто не покажется

**Q: Можно ли добавить новые категории?**  
A: Да, см. `JTBD_UI_DOCUMENTATION.md` → "Расширение"

## 🎉 Next Steps

1. **Backend субагент** создаёт JTBD анализатор
2. Интегрируем backend + frontend
3. Тестируем на реальных данных
4. 🚀 Profit!

---

**Статус:** ✅ Frontend готов, ждёт backend интеграции  
**Автор:** jtbd-frontend субагент  
**Дата:** 2026-02-28
