# HearYou STT Tests

Автоматические тесты для проекта HearYou STT (Speech-to-Text).

## 📋 Структура

```
tests/
├── __init__.py
├── conftest.py          # Общие fixtures
├── unit/                # Unit-тесты (быстрые, без внешних зависимостей)
│   ├── test_yandex_stt.py       # Тесты Yandex STT клиента
│   ├── test_corrections.py      # Тесты модуля исправлений
│   └── test_filler_words.py     # Тесты фильтра слов-паразитов
└── integration/         # Integration-тесты (требуют сервисов)
    └── test_api.py              # Тесты FastAPI приложения
```

## 🚀 Запуск тестов

### Все тесты
```bash
cd /root/hearyou
pytest
```

### Только unit-тесты (быстрые)
```bash
pytest tests/unit/ -v
```

### Только integration-тесты
```bash
pytest tests/integration/ -v
```

### С покрытием кода
```bash
pytest --cov=core --cov-report=html
```

Отчёт будет в `htmlcov/index.html`

### Конкретный тест
```bash
pytest tests/unit/test_yandex_stt.py::TestYandexSTTInit::test_init_with_env_vars -v
```

## 📊 Coverage Report

После запуска тестов с `--cov`, откройте отчёт:

```bash
python3 -m http.server 8080 -d htmlcov
# Откройте http://localhost:8080
```

**Цель:** минимум 50% code coverage для критичных модулей.

## ✅ Что покрыто тестами

### `core/yandex_stt.py`
- ✅ Инициализация с env vars
- ✅ Синхронная транскрипция (sync API)
- ✅ Асинхронная транскрипция (async API)
- ✅ Загрузка в S3 Object Storage
- ✅ Удаление из S3
- ✅ Ожидание завершения операции
- ✅ Обработка ошибок API
- ✅ Таймауты

### `core/stt_corrections.py`
- ✅ Базовые исправления (словарь)
- ✅ Фонетические паттерны (regex)
- ✅ Сохранение пунктуации
- ✅ Case-insensitive исправления
- ✅ Добавление кастомных исправлений
- ✅ Граничные случаи (пустой текст, unicode)

### `core/filler_words_filter.py`
- ✅ Удаление русских слов-паразитов
- ✅ Удаление английских слов-паразитов
- ✅ Удаление звуков (эээ, ммм)
- ✅ Удаление повторов (я я, и и)
- ✅ Нормализация пробелов
- ✅ Агрессивная очистка
- ✅ Сохранение смыслового содержания

### `packages/stt-service/app.py` (Integration)
- ✅ Health endpoints
- ✅ Stats endpoint
- ✅ Formats endpoint
- ✅ History endpoint
- ⚠️ Upload endpoint (частично, требует моков)
- ⚠️ Status/Result endpoints (требуют завершённых задач)

## 🔧 Fixtures

В `conftest.py` доступны следующие fixtures:

- `mock_env_vars` - mock переменных окружения
- `mock_yandex_api` - mock Yandex STT API
- `mock_s3_client` - mock boto3 S3 client
- `test_audio_file` - тестовый WAV файл
- `test_text_with_fillers` - текст со словами-паразитами
- `test_corrections_dict` - словарь исправлений
- `app_client` - FastAPI TestClient

## 📝 Написание новых тестов

### Unit-тест
```python
def test_my_function(mock_env_vars, mocker):
    """Описание теста"""
    # Arrange
    stt = YandexSTT()
    
    # Act
    result = stt.some_method()
    
    # Assert
    assert result == expected
```

### Integration-тест
```python
def test_api_endpoint(app_client):
    """Тест API endpoint"""
    response = app_client.get("/endpoint")
    
    assert response.status_code == 200
    assert "key" in response.json()
```

## 🎯 Принципы тестирования

1. **Быстрые тесты**: unit-тесты должны выполняться <30 секунд все вместе
2. **Изоляция**: используем моки для внешних API (Yandex, S3)
3. **Не требуем credentials**: тесты работают без реальных API ключей
4. **AAA паттерн**: Arrange, Act, Assert
5. **Один тест = одна проверка**: не смешиваем логику

## 🔒 Безопасность

- ✅ Все тесты используют моки для внешних сервисов
- ✅ Не требуют реальных API ключей
- ✅ Временные файлы автоматически удаляются
- ✅ Нет утечек credentials в логах

## 🐛 Дебаггинг тестов

### Запуск с подробным выводом
```bash
pytest -vv -s tests/unit/test_yandex_stt.py
```

### Только упавшие тесты
```bash
pytest --lf
```

### Только медленные тесты
```bash
pytest --durations=10
```

### С pdb debugger
```bash
pytest --pdb
```

## 🔄 CI/CD Integration

Для GitHub Actions создайте `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 📈 Метрики качества

**Текущее покрытие:** (запустите `pytest --cov` для обновления)

- `core/yandex_stt.py`: ~70%
- `core/stt_corrections.py`: ~80%
- `core/filler_words_filter.py`: ~85%
- `packages/stt-service/app.py`: ~40% (integration тесты требуют моков)

**Цель:** 50%+ для критичных модулей

## 🤝 Contributing

При добавлении новой функциональности:

1. Напишите unit-тесты первым (TDD)
2. Убедитесь что покрытие ≥50%
3. Все тесты проходят: `pytest`
4. Проверьте линтер: `pytest --flake8` (если настроен)

## 📚 Ресурсы

- [Pytest документация](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Создано:** 2026-02-27  
**Последнее обновление:** 2026-02-27
