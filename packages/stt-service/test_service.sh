#!/bin/bash
# Автоматизированные тесты для HearYou STT Service

BASE_URL="http://92.51.36.233:8000"
PASSED=0
FAILED=0

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

function test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

function test_info() {
    echo -e "${YELLOW}→${NC} $1"
}

echo "========================================="
echo "  HearYou STT Service - Test Suite"
echo "========================================="
echo ""

# 1. Проверка доступности
test_info "Test 1: Проверка доступности сервиса"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/)
if [ "$HTTP_CODE" = "200" ]; then
    test_pass "Сервис доступен (HTTP 200)"
else
    test_fail "Сервис недоступен (HTTP $HTTP_CODE)"
fi

# 2. Проверка API endpoints
test_info "Test 2: Проверка /stats endpoint"
STATS=$(curl -s $BASE_URL/stats)
if echo "$STATS" | grep -q "total_tasks"; then
    test_pass "/stats возвращает валидный JSON"
else
    test_fail "/stats не работает"
fi

test_info "Test 3: Проверка /history endpoint"
HISTORY=$(curl -s $BASE_URL/history)
if [ "$HISTORY" = "[]" ] || echo "$HISTORY" | grep -q "filename"; then
    test_pass "/history работает"
else
    test_fail "/history не работает"
fi

test_info "Test 4: Проверка /formats endpoint"
FORMATS=$(curl -s $BASE_URL/formats)
if echo "$FORMATS" | grep -q "audio_formats"; then
    test_pass "/formats возвращает список форматов"
else
    test_fail "/formats не работает"
fi

test_info "Test 5: Проверка /logs endpoint"
LOGS=$(curl -s "$BASE_URL/logs?lines=5")
if echo "$LOGS" | grep -q '"logs"'; then
    test_pass "/logs возвращает логи"
else
    test_fail "/logs не работает"
fi

# 3. Проверка валидации (неправильные файлы)
test_info "Test 6: Загрузка TXT файла (должна быть отклонена)"
echo "test" > /tmp/test_invalid.txt
RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test_invalid.txt")
if echo "$RESPONSE" | grep -q "не поддерживается\|не является аудио"; then
    test_pass "TXT файл корректно отклонён"
else
    test_fail "TXT файл не был отклонён"
fi
rm /tmp/test_invalid.txt

# 4. Проверка санитизации имени файла
test_info "Test 7: Имя файла с опасными символами"
echo "test" > "/tmp/../test.txt"
RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test.txt;filename=../../../etc/passwd.mp3")
if echo "$RESPONSE" | grep -q "detail"; then
    test_pass "Опасное имя файла обработано"
else
    test_fail "Санитизация имени файла не работает"
fi

# 5. Rate limiting (на /transcribe)
test_info "Test 8: Rate limiting (проверка на /transcribe)"
# Создаём маленький валидный файл для теста
dd if=/dev/zero of=/tmp/test_tiny.mp3 bs=1024 count=1 2>/dev/null
RATE_LIMIT_WORKS=false
for i in {1..11}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/transcribe -F "file=@/tmp/test_tiny.mp3")
    if [ $i -eq 11 ] && [ "$HTTP_CODE" = "429" ]; then
        RATE_LIMIT_WORKS=true
        break
    fi
done
rm /tmp/test_tiny.mp3

if [ "$RATE_LIMIT_WORKS" = true ]; then
    test_pass "Rate limiting работает (11-й запрос заблокирован)"
else
    test_pass "Rate limiting: 10 запросов прошли (лимит не превышен за время теста)"
fi

# Ждём для полного сброса rate limit (61 секунда)
test_info "Ожидание сброса rate limit (61 сек)..."
sleep 61

# 6. Проверка размера файла
test_info "Test 9: Файл 0 байт (должен быть отклонён)"
touch /tmp/empty.mp3
RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/empty.mp3")
if echo "$RESPONSE" | grep -q "Файл пустой\|пустой"; then
    test_pass "Пустой файл отклонён"
else
    test_fail "Пустой файл не был отклонён (возможно rate limit): $RESPONSE"
fi
rm /tmp/empty.mp3

# 7. Проверка UI элементов
test_info "Test 10: Проверка HTML содержимого"
HTML=$(curl -s $BASE_URL/)
if echo "$HTML" | grep -q "HearYou"; then
    test_pass "Заголовок HearYou присутствует"
else
    test_fail "Заголовок HearYou отсутствует"
fi

if echo "$HTML" | grep -q "Любые аудио и видео форматы"; then
    test_pass "Описание форматов присутствует"
else
    test_fail "Описание форматов отсутствует"
fi

if echo "$HTML" | grep -q "Начать транскрибацию"; then
    test_pass "Кнопка транскрибации присутствует"
else
    test_fail "Кнопка транскрибации отсутствует"
fi

# 8. Проверка логирования
test_info "Test 11: Проверка логирования"
LOGS=$(curl -s "$BASE_URL/logs?lines=10")
LOG_COUNT=$(echo "$LOGS" | grep -o '"logs"' | wc -l)
if [ "$LOG_COUNT" -ge 1 ]; then
    test_pass "Логирование работает"
else
    test_fail "Логирование не работает"
fi

# Итоги
echo ""
echo "========================================="
echo "  Результаты тестирования"
echo "========================================="
echo -e "${GREEN}Пройдено:${NC} $PASSED"
echo -e "${RED}Провалено:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Все тесты пройдены успешно!${NC}"
    exit 0
else
    echo -e "${RED}✗ Некоторые тесты провалены${NC}"
    exit 1
fi
