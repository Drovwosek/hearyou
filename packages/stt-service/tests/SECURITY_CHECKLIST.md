# Security Testing Checklist

## Injection Attacks

### SQL Injection
- [ ] **Status:** N/A (не используется SQL база данных)
- [ ] NoSQL injection в параметрах (если добавится БД)

### Command Injection
- [x] Имена файлов не передаются в shell напрямую
- [x] subprocess использует массивы аргументов (не shell=True)
- [x] ffmpeg команды параметризированы
- [ ] **Test:** Попробовать загрузить файл с именем `; rm -rf /`
- [ ] **Expected:** Имя санитизируется, команда не выполняется

### Path Traversal
- [x] Имена файлов санитизируются (удаление `../`, `/`, `\`)
- [x] Файлы сохраняются только в UPLOAD_DIR
- [ ] **Test:** Файл с именем `../../etc/passwd.mp3`
- [ ] **Expected:** Сохраняется в `/app/uploads/` с безопасным именем

### XSS (Cross-Site Scripting)
- [x] HTML escaping всех пользовательских данных
- [x] Имена файлов экранируются перед отображением
- [x] Ошибки экранируются
- [ ] **Test:** Файл `<script>alert(1)</script>.mp3`
- [ ] **Expected:** Отображается как текст, не выполняется

### Template Injection
- [ ] **Status:** N/A (нет template engine с user input)

---

## Authentication & Authorization

### Authentication
- [ ] **Status:** Нет авторизации (сервис публичный)
- [ ] **Future:** Basic Auth или API ключи для production

### Authorization
- [ ] Users не могут видеть чужие результаты
- [ ] **Test:** Попробовать `GET /result/{другой_task_id}`
- [ ] **Current:** Task IDs генерируются случайно (MD5 hash)
- [ ] **Improvement:** Привязка task к IP или session

### Rate Limiting
- [x] 10 запросов в минуту на /transcribe
- [x] IP-based tracking
- [ ] **Test:** 11 запросов подряд → 11-й отклоняется
- [ ] **Future:** Per-user limits (когда будет auth)

---

## File Upload Security

### File Type Validation
- [x] Whitelist расширений (30+ аудио/видео форматов)
- [x] MIME type проверка через `file` command
- [x] FFprobe валидация (глубокая проверка)
- [ ] **Test:** Переименовать `virus.exe` в `virus.mp3`
- [ ] **Expected:** Отклоняется на этапе MIME или ffprobe

### File Size Limits
- [x] Максимум 500 МБ
- [x] Проверка размера перед сохранением
- [ ] **Test:** Попытка загрузить файл 501 МБ
- [ ] **Expected:** HTTP 413 "Файл слишком большой"

### Malicious File Content
- [x] Битые файлы обрабатываются gracefully
- [x] Ffmpeg ограничен timeout (10s)
- [ ] **Test:** Zip bomb (файл который разархивируется в огромный размер)
- [ ] **Expected:** Ffmpeg fails, задача помечается "failed"

### Filename Sanitization
- [x] Ограничение длины (200 символов)
- [x] Удаление опасных символов
- [x] Null byte protection
- [x] Unicode normalization
- [ ] **Test:** Файл с именем 500 символов
- [ ] **Expected:** Обрезается до 200, расширение сохраняется

---

## Network Security

### HTTPS/TLS
- [ ] **Status:** HTTP только (development)
- [ ] **Production:** Должен быть HTTPS через Nginx + Let's Encrypt
- [ ] Certificate validation
- [ ] Strong ciphers only (TLS 1.2+)

### CORS
- [x] CORS настроен (allow_origins=["*"])
- [ ] **Production:** Ограничить origins до конкретных доменов
- [ ] Проверить OPTIONS requests

### Rate Limiting
- [x] Application-level (10 req/min)
- [ ] **Future:** Nginx rate limiting (дополнительная защита)
- [ ] DDoS protection через CDN (Cloudflare)

---

## Data Security

### Data at Rest
- [ ] Uploaded files хранятся в `/app/uploads`
- [ ] **Improvement:** Шифрование диска
- [ ] Автоочистка старых файлов (> 7 дней)
- [ ] Результаты транскрибации в `/app/results`

### Data in Transit
- [ ] **Current:** HTTP (незащищено)
- [ ] **Production:** HTTPS обязательно
- [ ] Yandex API использует HTTPS ✅

### Sensitive Data
- [ ] API ключи в environment variables (не в коде) ✅
- [ ] Логи не содержат API ключи ✅
- [ ] Логи не содержат полный текст транскрибации ✅
- [ ] **Check:** Grep логов на наличие YANDEX_API_KEY

### Data Retention
- [ ] Uploaded files: cleanup через 7 дней
- [ ] Results: cleanup через 7 дней
- [ ] Logs: ротация (не безлимитный рост)
- [ ] **Test:** Вызвать `DELETE /cleanup?days=7`

---

## API Security

### Input Validation
- [x] Filename sanitization
- [x] Language code whitelist
- [x] File size validation
- [x] File type validation
- [ ] **Test:** Передать language=`<script>`
- [ ] **Expected:** Sanitized to ru-RU (default)

### Error Messages
- [x] Не раскрывают internal paths
- [x] Не раскрывают версии библиотек
- [x] Не раскрывают stack traces пользователю
- [ ] **Check:** Stack traces только в логах, не в HTTP response

### Headers Security
- [ ] X-Frame-Options: DENY (защита от clickjacking)
- [ ] X-Content-Type-Options: nosniff
- [ ] Content-Security-Policy
- [ ] **Current:** Не настроены (нужно добавить)

---

## Infrastructure Security

### Docker Security
- [x] Non-root user внутри контейнера ❌ (сейчас root)
- [ ] **Improvement:** Создать отдельного пользователя
- [ ] Read-only filesystem где возможно
- [ ] Ограничение ресурсов (--memory, --cpus)
- [ ] Network isolation

### Dependencies
- [x] Python 3.11 (latest stable)
- [x] FastAPI, uvicorn (актуальные версии)
- [ ] **Regular:** Проверка CVE для зависимостей
- [ ] Dependabot для автоматических обновлений

### Secrets Management
- [x] API ключи в `.env.yandex`
- [x] `.env.yandex` в .gitignore
- [ ] **Production:** Использовать Docker secrets или vault
- [ ] Ротация ключей каждые 90 дней

### Logging
- [x] Все запросы логируются с IP
- [x] Ошибки логируются с traceback
- [ ] Логи доступны через /logs endpoint
- [ ] **Security:** /logs должен требовать auth

---

## Compliance & Privacy

### GDPR (если применимо)
- [ ] Сбор данных: только uploaded files + IP
- [ ] Право на удаление: пользователь может запросить удаление
- [ ] Срок хранения: 7 дней (автоочистка)
- [ ] Privacy policy на сайте

### Audio Content
- [ ] Транскрибация через Yandex (third-party)
- [ ] Аудио отправляется в Yandex Cloud
- [ ] **Privacy:** Уведомить пользователей что данные уходят в Yandex
- [ ] Опция: локальный STT для чувствительных данных

---

## Vulnerability Testing

### Automated Scans
- [ ] OWASP ZAP scan
- [ ] Nikto web scanner
- [ ] SQLMap (хотя SQL нет)
- [ ] **Run monthly**

### Manual Testing
- [x] Basic penetration testing выполнено (XSS, path traversal)
- [ ] Full pentest от security специалиста
- [ ] Bug bounty program (опционально)

### Known Vulnerabilities
- [ ] Check https://cve.mitre.org для используемых библиотек
- [ ] Subscribe to security advisories (FastAPI, Python, ffmpeg)

---

## Incident Response

### Monitoring
- [x] Логирование всех запросов
- [ ] Alert при подозрительной активности:
  - Много failed requests с одного IP
  - Rate limit violations
  - Попытки path traversal
- [ ] Интеграция с SIEM (если есть)

### Response Plan
- [ ] Documented incident response plan
- [ ] Кто отвечает за security
- [ ] Процедура при обнаружении breach
- [ ] Контакты для security reports

---

## Security Checklist Summary

**Critical (must fix):**
- [ ] Переход на HTTPS в production
- [ ] Авторизация для /logs endpoint
- [ ] Non-root Docker user
- [ ] Security headers (CSP, X-Frame-Options)

**High:**
- [ ] Ограничить CORS origins
- [ ] Task ID привязка к session/IP
- [ ] Secrets в vault (не в .env)

**Medium:**
- [ ] Автоочистка старых uploads
- [ ] Privacy policy
- [ ] Regular security scans
- [ ] Dependency updates

**Low:**
- [ ] Bug bounty program
- [ ] Full pentest
- [ ] GDPR compliance docs

---

## Security Testing Schedule

- **Daily:** Automated code scans (if CI/CD)
- **Weekly:** Review logs for anomalies
- **Monthly:** Dependency updates, OWASP ZAP scan
- **Quarterly:** Manual penetration testing
- **Yearly:** Full security audit, update response plan
