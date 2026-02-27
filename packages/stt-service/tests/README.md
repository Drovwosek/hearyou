# Testing Suite - README

Комплексная структура тестирования для HearYou STT Service.

## Структура директории

```
tests/
├── README.md (этот файл)
├── TEST_CASES.md              # 15 детальных тест-кейсов
├── PERFORMANCE_TESTS.md       # Performance & load testing
├── SECURITY_CHECKLIST.md      # Security audit checklist
├── UX_TEST_SCENARIOS.md       # UX & usability testing
└── fixtures/                  # Тестовые данные (создать при необходимости)
    ├── audio/
    │   ├── test_1mb.mp3
    │   ├── test_10mb.mp3
    │   └── corrupted.mp3
    └── malicious/
        ├── xss_filename.mp3
        └── path_traversal.mp3
```

## Типы тестов

### 1. Функциональные тесты (TEST_CASES.md)
**Что:** Проверка основного функционала  
**Когда:** При каждом изменении кода  
**Автоматизация:** ✅ Да (test_service.sh, test_audio_files.sh)  
**Приоритет:** Критичный

**Покрытие:**
- ✅ Базовые операции (загрузка, обработка, результат)
- ✅ Валидация форматов
- ✅ Обработка ошибок
- ✅ Edge cases

### 2. Performance тесты (PERFORMANCE_TESTS.md)
**Что:** Скорость, нагрузка, ресурсы  
**Когда:** Перед релизом, при оптимизации  
**Автоматизация:** ⚠️ Частично  
**Приоритет:** Высокий

**Покрытие:**
- Baseline metrics
- Concurrent requests (3, 10, 50)
- Upload speed & ETA
- Memory & disk usage
- Long-running tasks

### 3. Security тесты (SECURITY_CHECKLIST.md)
**Что:** Защита от атак и уязвимостей  
**Когда:** Ежемесячно + перед production  
**Автоматизация:** ⚠️ Частично  
**Приоритет:** Критичный

**Покрытие:**
- XSS, SQL/Command injection
- Path traversal
- Rate limiting
- Data security
- Infrastructure hardening

### 4. UX тесты (UX_TEST_SCENARIOS.md)
**Что:** Удобство использования  
**Когда:** При изменении UI  
**Автоматизация:** ❌ Ручные  
**Приоритет:** Средний

**Покрытие:**
- First-time user journey
- Error recovery
- Mobile experience
- Accessibility
- Trust & credibility

## Быстрый старт

### Запуск базовых тестов (2 минуты)
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service
./test_service.sh
```

**Проверяет:**
- API доступность
- Endpoints работают
- Валидация форматов
- Security (XSS, path traversal)
- Rate limiting

### Запуск audio тестов (5-10 минут)
```bash
./test_audio_files.sh
```

**Требует:** ffmpeg  
**Проверяет:**
- Реальная обработка MP3, WAV, AAC, MP4
- Полный цикл: загрузка → конвертация → STT → результат

### Manual testing
```bash
# Откройте браузер
open http://92.51.36.233:8000

# Загрузите тестовые файлы из tests/fixtures/
# Следуйте сценариям из UX_TEST_SCENARIOS.md
```

## Тестовые данные

### Создание fixtures

```bash
# Создать директорию
mkdir -p tests/fixtures/audio tests/fixtures/malicious

# Сгенерировать тестовые аудио (требует ffmpeg)
cd tests/fixtures/audio

# 1 МБ MP3 (тон 440Hz, 30 секунд)
ffmpeg -f lavfi -i "sine=frequency=440:duration=30" \
  -c:a libmp3lame -b:a 256k test_1mb.mp3

# 10 МБ MP3 (5 минут)
ffmpeg -f lavfi -i "sine=frequency=440:duration=300" \
  -c:a libmp3lame -b:a 256k test_10mb.mp3

# Битый файл
dd if=/dev/urandom of=corrupted.mp3 bs=1024 count=100

# XSS filename
touch "<script>alert('XSS')</script>.mp3"

# Path traversal
touch "../../../etc/passwd.mp3"
```

### Использование в тестах

```bash
# В test_service.sh или вручную
curl -X POST http://92.51.36.233:8000/transcribe \
  -F "file=@tests/fixtures/audio/test_1mb.mp3"
```

## CI/CD Integration

### GitHub Actions (example)

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start service
        run: |
          cd packages/stt-service
          docker-compose up -d
          sleep 10
      
      - name: Run basic tests
        run: |
          cd packages/stt-service
          ./test_service.sh
      
      - name: Run audio tests
        run: |
          cd packages/stt-service
          ./test_audio_files.sh
      
      - name: Collect logs
        if: failure()
        run: |
          curl http://localhost:8000/logs?lines=100
```

## Test Coverage Matrix

| Category | Total Tests | Automated | Manual | Status |
|---|---|---|---|---|
| Functional | 15 | 10 | 5 | ✅ 85% pass |
| Performance | 9 | 3 | 6 | ⚪ Not run |
| Security | 25+ checks | 8 | 17 | ✅ Critical pass |
| UX | 12 scenarios | 0 | 12 | ⚪ Not run |
| **Total** | **60+** | **21** | **40** | **🟡 35% pass** |

## Regression Testing

**Перед каждым релизом запустить:**

1. ✅ test_service.sh (basic + security)
2. ✅ test_audio_files.sh (full cycle)
3. ⚠️ Manual smoke test (загрузить 3 разных файла)
4. ⚠️ Performance baseline check (1 файл 10 МБ)
5. ⚠️ Security scan (OWASP ZAP)

**После релиза:**
- Monitor logs for errors
- Check user feedback
- Track success rate metrics

## Known Issues & Limitations

### Current Test Gaps
- [ ] No automated UI tests (Playwright/Selenium)
- [ ] No load testing in CI
- [ ] No integration tests for Yandex API (mock needed)
- [ ] No accessibility automation (axe-core)

### Flaky Tests
- Audio tests могут падать если Yandex API недоступен
- Rate limit tests зависят от timing (wait 61s)

### Test Environment
- Tests run against **production** (92.51.36.233:8000)
- ⚠️ Нужен staging environment для безопасного тестирования
- Rate limiting может блокировать тесты

## Contribution Guidelines

### Добавление нового теста

1. **Определить тип:**
   - Functional → добавить в TEST_CASES.md + test_service.sh
   - Performance → добавить в PERFORMANCE_TESTS.md
   - Security → добавить в SECURITY_CHECKLIST.md
   - UX → добавить в UX_TEST_SCENARIOS.md

2. **Написать тест-кейс:**
```markdown
## TC-XXX: Название

**Приоритет:** Высокий/Средний/Низкий
**Тип:** Функциональный/Негативный/Performance/...

**Шаги:**
1. ...
2. ...

**Ожидаемый результат:**
- ...

**Критерии прохождения:**
- ...
```

3. **Автоматизировать (если возможно):**
```bash
# В test_service.sh добавить:
test_info "Test XXX: Описание"
RESULT=$(curl ...)
if echo "$RESULT" | grep -q "expected"; then
    test_pass "Test passed"
else
    test_fail "Test failed"
fi
```

4. **Обновить coverage matrix** в этом README

## Useful Commands

```bash
# Проверка сервиса
curl -s http://92.51.36.233:8000/stats | jq

# Логи
curl -s "http://92.51.36.233:8000/logs?lines=50" | jq

# Мониторинг ресурсов
ssh root@92.51.36.233 "docker stats hearyou-stt --no-stream"

# Очистка старых файлов
curl -X DELETE "http://92.51.36.233:8000/cleanup?days=1"

# Проверка health
curl -I http://92.51.36.233:8000/
```

## Contact

**Вопросы по тестам:** @Drovwosek  
**Bug reports:** GitHub Issues  
**Security issues:** Приватно в Telegram

## Resources

- [Testing Documentation](../TESTING_README.md)
- [Test Plan](../TEST_PLAN.md)
- [API Documentation](http://92.51.36.233:8000/docs)
- [Deployment Guide](../DEPLOYMENT.md)

---

**Last updated:** 2026-02-26  
**Test suite version:** 1.0  
**Service version:** 1.0.0
