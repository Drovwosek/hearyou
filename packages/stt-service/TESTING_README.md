# Тестирование HearYou STT Service

## Доступные тесты

### 1. Базовые тесты (`test_service.sh`)

Проверяет основной функционал без реальной транскрибации:

```bash
./test_service.sh
```

**Что тестирует:**
- ✅ Доступность сервиса
- ✅ API endpoints (/stats, /history, /formats, /logs)
- ✅ Валидация форматов (отклонение TXT, PDF)
- ✅ Санитизация имён файлов
- ✅ Rate limiting (10 запросов/минуту)
- ✅ Проверка пустых файлов
- ✅ UI элементы
- ✅ Логирование

**Время выполнения:** ~2 минуты (из-за ожидания rate limit reset)

### 2. Тесты с реальными аудио (`test_audio_files.sh`)

Генерирует тестовые аудиофайлы и проверяет полный цикл транскрибации:

```bash
./test_audio_files.sh
```

**Требования:** ffmpeg должен быть установлен

**Что тестирует:**
- ✅ MP3 файл → конвертация → транскрибация → результат
- ✅ WAV файл → обработка
- ✅ AAC файл (имитация диктофона) → обработка
- ✅ MP4 видео → извлечение аудио → транскрибация

**Время выполнения:** ~5-10 минут (реальная обработка через Yandex API)

**Примечание:** Использует rate limit, поэтому между тестами паузы 61 секунда

### 3. Полный тест-план (`TEST_PLAN.md`)

Документ с детальным описанием всех тест-кейсов:
- 80+ пунктов проверки
- UI/UX тесты
- Security тесты
- Performance тесты
- Edge cases

## Быстрый запуск всех тестов

```bash
# Базовые тесты
./test_service.sh

# Если всё ОК, запускаем audio тесты
./test_audio_files.sh
```

## CI/CD Integration

Базовые тесты можно добавить в GitHub Actions:

```yaml
- name: Run tests
  run: |
    cd packages/stt-service
    ./test_service.sh
```

Audio тесты лучше запускать отдельно (требуют больше времени).

## Результаты

**Текущий статус:** ✅ 13/13 базовых тестов пройдены

**Последний запуск:**
```
=========================================
  Результаты тестирования
=========================================
Пройдено: 13
Провалено: 0

✓ Все тесты пройдены успешно!
```

## Troubleshooting

### Rate Limit Errors
Если тесты падают с "Слишком много запросов":
- Подождите 61 секунду
- Или увеличьте лимит в `app.py` (RATE_LIMIT_MAX_REQUESTS)

### ffmpeg Not Found
Для audio тестов нужен ffmpeg:
```bash
# Ubuntu/Debian
apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Timeout во время транскрибации
Если audio тесты падают по timeout:
- Проверьте доступность Yandex API
- Проверьте логи: `curl http://92.51.36.233:8000/logs?lines=50`
- Увеличьте `max_wait` в `test_audio_files.sh`

## Добавление новых тестов

### Базовый тест

```bash
# В test_service.sh добавьте:
test_info "Test X: Описание"
RESPONSE=$(curl -s $BASE_URL/endpoint)
if echo "$RESPONSE" | grep -q "expected"; then
    test_pass "Тест пройден"
else
    test_fail "Тест провален"
fi
```

### Audio тест

```bash
# В test_audio_files.sh добавьте:
ffmpeg -i input.mp3 output.wav -y &>/dev/null
RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@output.wav")
TASK_ID=$(echo "$RESPONSE" | python3 -c "...")
wait_for_task "$TASK_ID"
```

## Мониторинг в production

Рекомендуется запускать базовые тесты:
- Раз в час (healthcheck)
- После каждого деплоя
- При получении алертов от пользователей

```bash
# Cron job для healthcheck
*/60 * * * * cd /path/to/stt-service && ./test_service.sh || mail -s "STT Tests Failed" admin@example.com
```
