#!/bin/bash
# Тесты с реальными аудио файлами

BASE_URL="http://92.51.36.233:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

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

function wait_for_task() {
    task_id=$1
    max_wait=120  # 2 минуты
    waited=0
    
    while [ $waited -lt $max_wait ]; do
        status=$(curl -s "$BASE_URL/status/$task_id" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status', 'unknown'))")
        
        if [ "$status" = "completed" ]; then
            return 0
        elif [ "$status" = "failed" ]; then
            return 1
        fi
        
        sleep 2
        ((waited+=2))
    done
    
    return 2  # timeout
}

echo "========================================="
echo "  Audio File Processing Tests"
echo "========================================="
echo ""

# Создаём тестовые аудио файлы с помощью ffmpeg
test_info "Создание тестовых файлов..."

# 1. Генерация тона 440Hz (нота Ля) 5 секунд - MP3
if command -v ffmpeg &> /dev/null; then
    ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame -q:a 4 /tmp/test_tone.mp3 -y &>/dev/null
    if [ -f /tmp/test_tone.mp3 ]; then
        test_pass "Создан тестовый MP3 файл"
        
        # Тест: загрузка MP3
        test_info "Test: Транскрибация MP3 файла"
        RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test_tone.mp3" -F "punctuation=true")
        TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', ''))")
        
        if [ -n "$TASK_ID" ]; then
            test_pass "MP3 файл принят, task_id: $TASK_ID"
            
            # Ожидаем завершения
            if wait_for_task "$TASK_ID"; then
                test_pass "MP3 файл успешно обработан"
                
                # Проверяем результат
                RESULT=$(curl -s "$BASE_URL/result/$TASK_ID" | python3 -c "import sys,json; print(json.load(sys.stdin).get('text', ''))")
                if [ -n "$RESULT" ]; then
                    test_pass "Получен результат транскрибации"
                else
                    test_fail "Результат пустой"
                fi
            else
                test_fail "MP3 файл не обработан (timeout или ошибка)"
            fi
        else
            test_fail "MP3 файл отклонён: $RESPONSE"
        fi
        
        rm /tmp/test_tone.mp3
    fi
    
    # Ждём сброса rate limit
    sleep 61
    
    # 2. WAV файл
    ffmpeg -f lavfi -i "sine=frequency=440:duration=3" /tmp/test_tone.wav -y &>/dev/null
    if [ -f /tmp/test_tone.wav ]; then
        test_pass "Создан тестовый WAV файл"
        
        test_info "Test: Транскрибация WAV файла"
        RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test_tone.wav" -F "punctuation=true")
        TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', ''))")
        
        if [ -n "$TASK_ID" ]; then
            test_pass "WAV файл принят"
            
            if wait_for_task "$TASK_ID"; then
                test_pass "WAV файл успешно обработан"
            else
                test_fail "WAV файл не обработан"
            fi
        else
            test_fail "WAV файл отклонён"
        fi
        
        rm /tmp/test_tone.wav
    fi
    
    sleep 61
    
    # 3. AAC файл (как с диктофона)
    ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -c:a aac /tmp/test_voice.aac -y &>/dev/null
    if [ -f /tmp/test_voice.aac ]; then
        test_pass "Создан тестовый AAC файл"
        
        test_info "Test: Транскрибация AAC файла"
        RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test_voice.aac" -F "punctuation=true")
        TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', ''))")
        
        if [ -n "$TASK_ID" ]; then
            test_pass "AAC файл принят (как с диктофона)"
            
            if wait_for_task "$TASK_ID"; then
                test_pass "AAC файл успешно обработан"
            else
                test_fail "AAC файл не обработан"
            fi
        else
            test_fail "AAC файл отклонён"
        fi
        
        rm /tmp/test_voice.aac
    fi
    
    sleep 61
    
    # 4. MP4 видео (извлечение аудио)
    ffmpeg -f lavfi -i "sine=frequency=440:duration=2" -f lavfi -i "color=c=blue:s=320x240:d=2" \
           -c:v libx264 -c:a aac -shortest /tmp/test_video.mp4 -y &>/dev/null
    if [ -f /tmp/test_video.mp4 ]; then
        test_pass "Создан тестовый MP4 видео файл"
        
        test_info "Test: Извлечение аудио из MP4"
        RESPONSE=$(curl -s -X POST $BASE_URL/transcribe -F "file=@/tmp/test_video.mp4" -F "punctuation=true")
        TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', ''))")
        
        if [ -n "$TASK_ID" ]; then
            test_pass "MP4 видео принято"
            
            if wait_for_task "$TASK_ID"; then
                test_pass "Аудио извлечено и обработано из MP4"
            else
                test_fail "MP4 не обработан"
            fi
        else
            test_fail "MP4 отклонён"
        fi
        
        rm /tmp/test_video.mp4
    fi
    
else
    test_fail "ffmpeg не установлен, пропускаем audio тесты"
fi

# Итоги
echo ""
echo "========================================="
echo "  Результаты"
echo "========================================="
echo -e "${GREEN}Пройдено:${NC} $PASSED"
echo -e "${RED}Провалено:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Все audio тесты пройдены!${NC}"
    exit 0
else
    echo -e "${RED}✗ Некоторые audio тесты провалены${NC}"
    exit 1
fi
