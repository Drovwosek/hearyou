#!/usr/bin/env python3
"""
HearYou STT Service - FastAPI веб-сервис для транскрибации
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import uvicorn
import asyncio
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import hashlib
import shutil
import re
import logging
import traceback as tb

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорт из общего модуля core
sys.path.insert(0, '/root/hearyou')

from core.yandex_stt import YandexSTT
from core.text_cleaner import TranscriptionCleaner

# JTBD анализатор - опционально (требует anthropic)
try:
    from core.jtbd_analyzer import JTBDAnalyzer
    JTBD_AVAILABLE = True
except ImportError:
    JTBD_AVAILABLE = False
    logger.warning("JTBD Analyzer недоступен: не установлен пакет 'anthropic'")

from ispring_hints import DEFAULT_HINTS
from speaker_diarization_resemblyzer import (
    SpeakerDiarizationResemblyzer,
    merge_transcription_with_speakers,
    format_with_speakers as format_speakers_dialogue
)

app = FastAPI(
    title="HearYou STT Service",
    description="Сервис транскрибации аудио через Yandex SpeechKit",
    version="1.0.0"
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Логируем входящий запрос (минимально)
    logger.info(f"{request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
    # Для POST /transcribe логируем заголовки
    if request.method == "POST" and request.url.path == "/transcribe":
        logger.info(f"🔍 Content-Type: {request.headers.get('content-type')}")
        logger.info(f"🔍 Content-Length: {request.headers.get('content-length')}")
        # НЕ читаем body в middleware - это ломает multipart/form-data парсинг в FastAPI!
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Логируем ответ
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.2f}s)")
        
        # Если 400 на /transcribe - логируем подробности + response body
        if response.status_code >= 400 and request.url.path == "/transcribe":
            logger.error(f"❌ HTTP {response.status_code} on /transcribe")
            logger.error(f"❌ Request took {duration:.2f}s")
            
            # Попытаемся прочитать response body для диагностики
            if hasattr(response, 'body'):
                try:
                    body = response.body.decode('utf-8')[:500]  # первые 500 символов
                    logger.error(f"❌ Response body: {body}")
                except Exception as e:
                    logger.error(f"❌ Could not read response body: {e}")
            
            logger.error(f"❌ This suggests FastAPI rejected the request before reaching the endpoint")
            logger.error(f"❌ Possible causes: invalid Content-Type, missing required fields, or parsing error")
        
        return response
    except Exception as e:
        logger.error(f"{request.method} {request.url.path} failed: {e}")
        logger.error(tb.format_exc())
        raise

# CORS для доступа из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers для детального логирования ошибок
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ VALIDATION ERROR on {request.method} {request.url.path}")
    logger.error(f"❌ Client: {request.client.host if request.client else 'unknown'}")
    logger.error(f"❌ Content-Type: {request.headers.get('content-type')}")
    logger.error(f"❌ Errors count: {len(exc.errors())}")
    
    # Детальный вывод каждой ошибки
    for i, error in enumerate(exc.errors(), 1):
        loc = ' -> '.join(str(x) for x in error.get('loc', []))
        logger.error(f"  ❌ Error {i}:")
        logger.error(f"     Location: {loc}")
        logger.error(f"     Type: {error.get('type')}")
        logger.error(f"     Message: {error.get('msg')}")
        if 'input' in error:
            input_str = str(error.get('input'))[:100]  # первые 100 символов
            logger.error(f"     Input: {input_str}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation failed - check server logs for details"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"❌ HTTP Exception {exc.status_code} on {request.method} {request.url.path}")
    logger.error(f"❌ Detail: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception on {request.method} {request.url.path}: {type(exc).__name__}")
    logger.error(f"❌ Message: {str(exc)}")
    logger.error(f"❌ Traceback:")
    logger.error(tb.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Конфигурация
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
TEMP_DIR = Path("temp")

UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Логи
LOGS_DIR = Path("/app/logs")
LOGS_DIR.mkdir(exist_ok=True)

# Временная директория для chunked uploads
CHUNKS_DIR = Path("/app/chunks")
CHUNKS_DIR.mkdir(exist_ok=True)

# Максимальный размер файла (25 ГБ - для видео, аудио экстрагируется автоматически)
MAX_FILE_SIZE = 25 * 1024 * 1024 * 1024

# Хранилище информации о chunked uploads
chunked_uploads = {}  # {upload_id: {filename, total_chunks, received_chunks, file_path}}

# Whitelist разрешённых расширений (безопасность)
# Валидация форматов отключена - принимаем любые файлы с аудио потоком (проверка через ffprobe)
# Можно вернуть whitelist если потребуется ограничить форматы:
# ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.aac', '.m4a', '.ogg', '.opus', '.flac', ...}

# Инициализация STT (с поддержкой S3 для async API)
stt = YandexSTT(
    s3_access_key=os.getenv('YANDEX_S3_ACCESS_KEY'),
    s3_secret_key=os.getenv('YANDEX_S3_SECRET_KEY'),
    s3_bucket=os.getenv('YANDEX_S3_BUCKET', 'hearyou-stt-temp')
)
cleaner = TranscriptionCleaner()  # Полный пайплайн очистки (звуки + паразиты + артефакты)
diarizer = SpeakerDiarizationResemblyzer()  # Speaker diarization через Resemblyzer

# Инициализация JTBD анализатора (с обработкой ошибок если нет API ключа)
if JTBD_AVAILABLE:
    try:
        jtbd_analyzer = JTBDAnalyzer()
        logger.info("JTBD Analyzer initialized successfully")
    except ValueError as e:
        logger.warning(f"JTBD Analyzer not initialized: {e}")
        jtbd_analyzer = None
else:
    jtbd_analyzer = None
    logger.info("JTBD Analyzer disabled (anthropic package not installed)")


def format_with_speakers(result_data: dict) -> str:
    """
    Форматировать транскрипцию с разделением по спикерам
    
    Args:
        result_data: Результат от Yandex API с speakerLabeling
        
    Returns:
        Отформатированный текст с разделением по спикерам
    """
    chunks = result_data.get('chunks', [])
    
    if not chunks:
        # Если нет chunks, вернуть обычный result
        return result_data.get('result', '')
    
    # Собираем все слова с метаданными
    all_words = []
    
    for chunk in chunks:
        for alt in chunk.get('alternatives', []):
            for word_data in alt.get('words', []):
                speaker_tag = word_data.get('speakerTag')
                if speaker_tag is not None:  # Есть информация о спикере
                    word = word_data.get('word', '')
                    start_time = word_data.get('startTime', '0s')
                    all_words.append({
                        'word': word,
                        'speaker': speaker_tag,
                        'time': start_time
                    })
    
    # Если нет информации о спикерах, вернуть обычный текст
    if not all_words:
        return result_data.get('result', '')
    
    # Подсчитываем уникальных спикеров
    unique_speakers = set(w['speaker'] for w in all_words)
    if len(unique_speakers) <= 1:
        # Только один спикер - вернуть обычный текст
        return result_data.get('result', '')
    
    # Группируем последовательно по спикерам (диалог)
    dialog = []
    current_speaker = None
    current_text = []
    
    for word_info in all_words:
        speaker = word_info['speaker']
        word = word_info['word']
        
        if speaker != current_speaker:
            # Сменился спикер - сохранить предыдущую реплику
            if current_speaker is not None and current_text:
                text = ' '.join(current_text)
                dialog.append(f"Спикер {current_speaker}: {text}")
            
            # Начать новую реплику
            current_speaker = speaker
            current_text = [word]
        else:
            # Тот же спикер - добавить слово
            current_text.append(word)
    
    # Добавить последнюю реплику
    if current_speaker is not None and current_text:
        text = ' '.join(current_text)
        dialog.append(f"Спикер {current_speaker}: {text}")
    
    return '\n\n'.join(dialog)


# Очередь задач
task_queue = asyncio.Queue()
tasks_status = {}  # {task_id: {status, progress, result}}

# Rate limiting (простая защита от спама)
from collections import defaultdict
import time

request_counts = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
RATE_LIMIT_WINDOW = 60  # 60 секунд
RATE_LIMIT_MAX_REQUESTS = 10  # Максимум 10 запросов в минуту

# Простая авторизация
VALID_TOKENS = {
    "artem_token": "Artem",
    "test_token": "Test User",
}

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Проверка токена авторизации"""
    if not authorization:
        # В dev режиме разрешаем без токена
        return "anonymous"
    
    token = authorization.replace("Bearer ", "")
    if token in VALID_TOKENS:
        return VALID_TOKENS[token]
    
    raise HTTPException(status_code=401, detail="Invalid token")


def check_rate_limit(client_ip: str) -> None:
    """
    Проверка rate limit для защиты от спама
    Максимум 10 запросов в минуту с одного IP
    """
    now = time.time()
    
    # Очистка старых записей
    request_counts[client_ip] = [
        ts for ts in request_counts[client_ip] 
        if now - ts < RATE_LIMIT_WINDOW
    ]
    
    # Проверка лимита
    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Слишком много запросов. Максимум {RATE_LIMIT_MAX_REQUESTS} запросов в минуту."
        )
    
    # Добавление текущего запроса
    request_counts[client_ip].append(now)


def sanitize_filename(filename: str) -> str:
    """
    Санитизация имени файла для защиты от инъекций
    - Удаляет опасные символы
    - Ограничивает длину
    - Сохраняет только безопасные символы
    - НИКОГДА не падает — всегда возвращает валидное имя
    """
    try:
        # Берём только имя файла (без пути)
        filename = str(filename)  # Явное приведение к строке
        filename = Path(filename).name
        
        # Удаляем нулевые байты
        filename = filename.replace('\x00', '')
        
        # Если пустое имя после очистки
        if not filename or filename.strip() == '':
            return 'file.mp3'
        
        # Разделяем на имя и расширение (безопасно)
        parts = filename.rsplit('.', 1)
        
        if len(parts) == 2:
            name, extension = parts[0], parts[1]
            ext = '.' + extension.lower() if extension else '.mp3'
        else:
            name = parts[0]
            ext = '.mp3'  # Дефолтное расширение если не указано
        
        # Оставляем только безопасные символы:
        # буквы (латиница + кириллица), цифры, дефис, подчёркивание, пробелы
        name = re.sub(r'[^\w\s\-а-яА-ЯёЁ]', '_', name, flags=re.UNICODE)
        
        # Убираем множественные пробелы и подчёркивания
        name = re.sub(r'[\s_]+', '_', name)
        
        # Убираем начальные/конечные спецсимволы
        name = name.strip('_-. ')
        
        # Ограничиваем длину (макс 200 символов)
        if len(name) > 200:
            name = name[:200]
        
        # Если имя стало пустым после очистки
        if not name or name == '':
            name = 'file'
        
        result = name + ext
        
        # Финальная проверка валидности
        if not result or result == '' or result == '.':
            return 'file.mp3'
        
        return result
        
    except Exception as e:
        # Если что-то пошло не так — возвращаем безопасное имя
        logger.warning(f"Filename sanitization exception: {e}, using fallback")
        return 'file.mp3'


def sanitize_language_code(lang: str) -> str:
    """
    Валидация языкового кода
    Разрешены только стандартные коды вида: xx-XX
    """
    # Whitelist языков поддерживаемых Yandex
    allowed_languages = {
        'ru-RU', 'en-US', 'tr-TR', 'uk-UK', 'uz-UZ', 
        'kk-KK', 'de-DE', 'fr-FR', 'es-ES'
    }
    
    if lang in allowed_languages:
        return lang
    
    # Если передан неизвестный код, используем ru-RU по умолчанию
    return 'ru-RU'


def validate_file_security(filename: str, file_path: Path) -> None:
    """Проверка безопасности загруженного файла"""
    import subprocess
    
    # Единственная проверка: ffprobe валидация (принимаем любые форматы с аудио потоком)
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',  # Только ошибки
            '-show_entries', 'stream=codec_type',
            '-of', 'json',
            str(file_path)
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise ValueError("Файл повреждён или имеет неподдерживаемый формат")
        
        probe_data = json.loads(result.stdout)
        streams = probe_data.get('streams', [])
        
        # Проверяем наличие хотя бы одного аудио потока
        has_audio = any(s.get('codec_type') == 'audio' for s in streams)
        if not has_audio:
            raise ValueError("Файл не содержит аудио дорожки")
            
    except subprocess.TimeoutExpired:
        raise ValueError("Превышено время анализа файла")
    except json.JSONDecodeError:
        raise ValueError("Ошибка при анализе файла")


def probe_media_file(file_path: Path) -> dict:
    """Получение информации о медиа-файле через ffprobe"""
    import subprocess
    
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ], capture_output=True, text=True, check=True, timeout=10)
        
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise ValueError("Превышено время анализа файла")
    except Exception as e:
        raise ValueError(f"Не удалось прочитать файл: {e}")


async def process_audio_file(
    file_path: Path,
    task_id: str,
    options: dict
):
    """Обработка аудио файла"""
    try:
        tasks_status[task_id]["status"] = "processing"
        tasks_status[task_id]["progress"] = 10
        tasks_status[task_id]["message"] = "Подготовка к конвертации..."
        
        import subprocess
        
        # Конвертация в OGG Opus (всегда, для гарантии совместимости)
        tasks_status[task_id]["progress"] = 20
        tasks_status[task_id]["message"] = "Конвертация в OGG Opus..."
        
        temp_file = TEMP_DIR / f"{task_id}.ogg"
        
        try:
            subprocess.run([
                'ffmpeg',
                '-i', str(file_path),
                '-vn',  # Игнорировать видео
                '-c:a', 'libopus',
                '-b:a', '48k',
                '-ar', '48000',
                '-ac', '1',  # Моно - быстрее
                str(temp_file),
                '-y'
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg conversion failed for {task_id}: {error_msg}")
            
            # Упрощённое сообщение для пользователя
            if "Could not find codec parameters" in error_msg or "Invalid data" in error_msg:
                raise ValueError(
                    "Файл повреждён или имеет нестандартный формат. "
                    "Попробуйте пересохранить файл или использовать другой."
                )
            else:
                raise ValueError(f"Не удалось обработать аудио файл. Попробуйте другой формат.")
        
        audio_to_send = temp_file
        
        tasks_status[task_id]["progress"] = 50
        tasks_status[task_id]["message"] = "Загрузка в облако..."
        
        # Асинхронная транскрибация (поддержка больших файлов)
        logger.info(f"Starting async transcription for task {task_id}")
        
        # Запускаем Yandex STT
        # speaker_labeling не поддерживается в transcribe_async - используем Resemblyzer отдельно
        operation_id = stt.transcribe_async(
            str(audio_to_send),
            language=options.get("language", "ru-RU"),
            punctuation=options.get("punctuation", True),
            literature_text=options.get("literature", False),
            auto_upload=True,
            # hints=DEFAULT_HINTS,  # Не поддерживается в async API
        )
        
        logger.info(f"Task {task_id}: operation_id = {operation_id}")
        
        # Если нужна диаризация - запускаем Resemblyzer параллельно
        speaker_segments = None
        if options.get("speaker_labeling", False):
            tasks_status[task_id]["message"] = "Транскрипция + определение спикеров..."
            tasks_status[task_id]["progress"] = 60
            
            # Запускаем Resemblyzer диаризацию параллельно с Yandex
            async def run_diarization():
                try:
                    logger.info(f"Task {task_id}: starting Resemblyzer diarization")
                    return diarizer.diarize(str(audio_to_send), num_speakers=2)
                except Exception as e:
                    logger.error(f"Task {task_id}: diarization failed: {e}")
                    return None
            
            # Запускаем оба процесса параллельно
            diarization_task = asyncio.create_task(run_diarization())
            
            # Ждём Yandex
            tasks_status[task_id]["progress"] = 70
            result = stt.wait_for_completion(operation_id, timeout=7200, poll_interval=5)
            
            # Ждём диаризацию
            tasks_status[task_id]["message"] = "Объединение результатов..."
            tasks_status[task_id]["progress"] = 75
            speaker_segments = await diarization_task
            
        else:
            # Без диаризации - просто ждём транскрипцию
            tasks_status[task_id]["message"] = "Транскрибация (ожидание результата)..."
            tasks_status[task_id]["progress"] = 60
            result = stt.wait_for_completion(operation_id, timeout=7200, poll_interval=5)
        
        # Удаляем временный файл из Object Storage
        try:
            object_name = Path(audio_to_send).name
            stt.delete_from_storage(object_name)
            logger.info(f"Task {task_id}: cleaned up S3 file {object_name}")
        except Exception as e:
            logger.warning(f"Task {task_id}: failed to cleanup S3 file: {e}")
        
        # Форматирование результата
        if speaker_segments:
            # Объединяем транскрипцию со спикерами
            try:
                # Извлекаем слова из chunks Yandex
                all_words = []
                for chunk in result.get('chunks', []):
                    for alt in chunk.get('alternatives', []):
                        all_words.extend(alt.get('words', []))
                
                # Объединяем с диаризацией
                words_with_speakers = merge_transcription_with_speakers(all_words, speaker_segments)
                
                # Форматируем как диалог
                text = format_speakers_dialogue(words_with_speakers)
                
                # Сохраняем enriched data
                result['words_with_speakers'] = words_with_speakers
                result['speaker_segments'] = speaker_segments
                
                logger.info(f"Task {task_id}: merged {len(words_with_speakers)} words with {len(set(s['speaker'] for s in speaker_segments))} speakers")
            except Exception as e:
                logger.error(f"Task {task_id}: failed to merge speakers: {e}")
                text = result.get('result', '')
        else:
            text = result.get('result', '')
        
        # Очистка из S3
        try:
            object_name = Path(audio_to_send).name
            stt.delete_from_storage(object_name)
            logger.info(f"Task {task_id}: cleaned up S3 object {object_name}")
        except Exception as e:
            logger.warning(f"Task {task_id}: failed to delete from S3: {e}")
        
        tasks_status[task_id]["progress"] = 70
        
        # Полная очистка текста (звуки + паразиты + артефакты)
        if options.get("clean", False) or options.get("corrections", True):
            tasks_status[task_id]["message"] = "Улучшение качества текста..."
            text = cleaner.clean(
                text,
                remove_filler_sounds=True,  # Всегда убираем лишние звуки (эээ, ммм, бе, ме)
                remove_filler_words=options.get("clean", False),  # Слова-паразиты (по запросу)
                fix_artifacts=options.get("corrections", True),  # Артефакты (иишка → ИИшка)
            )
        
        tasks_status[task_id]["progress"] = 90
        
        # JTBD анализ (если включен)
        jtbd_result = None
        if options.get("analyze_jtbd", True) and jtbd_analyzer:
            try:
                tasks_status[task_id]["message"] = "JTBD анализ..."
                tasks_status[task_id]["progress"] = 92
                
                logger.info(f"Task {task_id}: starting JTBD analysis")
                jtbd_result = jtbd_analyzer.analyze(text)
                
                logger.info(
                    f"Task {task_id}: JTBD analysis completed, "
                    f"{jtbd_result['metadata']['total_elements']} elements found"
                )
            except Exception as e:
                logger.error(f"Task {task_id}: JTBD analysis failed: {e}")
                jtbd_result = {
                    "error": str(e),
                    "jobs": [], "pains": [], "gains": [], "context": [], "triggers": [],
                    "summary": f"Ошибка анализа: {str(e)}"
                }
        
        tasks_status[task_id]["progress"] = 95
        
        # Сохранение результата
        result_file = RESULTS_DIR / f"{task_id}.json"
        result_data = {
            "task_id": task_id,
            "text": text,
            "original_filename": tasks_status[task_id]["filename"],
            "timestamp": datetime.now().isoformat(),
            "options": options,
            "raw_result": result,
            "jtbd": jtbd_result,
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # Очистка временных файлов
        if audio_to_send != file_path:
            audio_to_send.unlink(missing_ok=True)
        
        tasks_status[task_id]["status"] = "completed"
        tasks_status[task_id]["progress"] = 100
        tasks_status[task_id]["result"] = text
        tasks_status[task_id]["result_file"] = str(result_file)
        
    except Exception as e:
        error_msg = str(e)
        error_trace = tb.format_exc()
        
        logger.error(f"Task {task_id} failed: {error_msg}")
        logger.debug(f"Task {task_id} traceback:\n{error_trace}")
        
        tasks_status[task_id]["status"] = "failed"
        tasks_status[task_id]["error"] = error_msg
        tasks_status[task_id]["traceback"] = error_trace


async def worker():
    """Воркер для обработки очереди"""
    while True:
        task = await task_queue.get()
        await process_audio_file(
            task["file_path"],
            task["task_id"],
            task["options"]
        )
        task_queue.task_done()


@app.on_event("startup")
async def startup_event():
    """Запуск воркеров при старте"""
    # 3 параллельных воркера
    for _ in range(3):
        asyncio.create_task(worker())


@app.get("/favicon.ico")
async def favicon():
    """Favicon для браузера"""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с веб-интерфейсом"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding='utf-8')
    
    # Простейший HTML если файла нет
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HearYou STT Service</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>HearYou STT Service</h1>
        <p>API работает! Используйте /docs для Swagger UI</p>
    </body>
    </html>
    """


@app.post("/upload-chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    chunk: UploadFile = File(...),
    x_forwarded_for: str = Header(None, alias="X-Forwarded-For"),
    x_real_ip: str = Header(None, alias="X-Real-IP")
):
    """
    Загрузка файла по частям (chunked upload)
    
    - **upload_id**: уникальный ID загрузки
    - **chunk_index**: номер части (0-based)
    - **total_chunks**: общее количество частей
    - **filename**: имя файла
    - **chunk**: данные части
    """
    
    # Rate limiting
    client_ip = x_forwarded_for or x_real_ip or "direct"
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    logger.info(f"Chunk upload from {client_ip}: {upload_id} [{chunk_index+1}/{total_chunks}]")
    
    # Инициализация upload если первый чанк
    if upload_id not in chunked_uploads:
        safe_filename = sanitize_filename(filename)
        chunked_uploads[upload_id] = {
            "filename": safe_filename,
            "total_chunks": total_chunks,
            "received_chunks": set(),
            "chunk_dir": CHUNKS_DIR / upload_id,
            "started_at": datetime.now().isoformat()
        }
        chunked_uploads[upload_id]["chunk_dir"].mkdir(exist_ok=True)
        logger.info(f"Started chunked upload: {upload_id} for {safe_filename}")
    
    upload_info = chunked_uploads[upload_id]
    
    # Сохранение чанка
    chunk_path = upload_info["chunk_dir"] / f"chunk_{chunk_index}"
    with open(chunk_path, "wb") as f:
        shutil.copyfileobj(chunk.file, f)
    
    upload_info["received_chunks"].add(chunk_index)
    received_count = len(upload_info["received_chunks"])
    
    logger.debug(f"Chunk {chunk_index} saved, progress: {received_count}/{total_chunks}")
    
    # Проверка завершения
    is_complete = received_count == total_chunks
    
    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "received": received_count,
        "total": total_chunks,
        "complete": is_complete,
        "progress": round((received_count / total_chunks) * 100, 1)
    }


@app.post("/complete-upload")
async def complete_upload(
    upload_id: str = Form(...),
    language: str = Form("ru-RU"),
    punctuation: bool = Form(True),
    literature: bool = Form(False),
    clean: bool = Form(False),
    corrections: bool = Form(True),
    analyze_jtbd: bool = Form(False)  # JTBD отключен по умолчанию
):
    """
    Завершение chunked upload и запуск транскрибации
    """
    
    if upload_id not in chunked_uploads:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    upload_info = chunked_uploads[upload_id]
    
    # Проверка что все чанки получены
    if len(upload_info["received_chunks"]) != upload_info["total_chunks"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Incomplete upload: {len(upload_info['received_chunks'])}/{upload_info['total_chunks']} chunks"
        )
    
    logger.info(f"Assembling chunked upload: {upload_id}")
    
    # Объединение чанков
    task_id = hashlib.md5(f"{upload_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    final_path = UPLOAD_DIR / f"{task_id}_{upload_info['filename']}"
    
    with open(final_path, "wb") as final_file:
        for i in range(upload_info["total_chunks"]):
            chunk_path = upload_info["chunk_dir"] / f"chunk_{i}"
            with open(chunk_path, "rb") as chunk_file:
                shutil.copyfileobj(chunk_file, final_file)
    
    logger.info(f"Assembled file: {final_path}, size: {final_path.stat().st_size}")
    
    # Проверка размера
    if final_path.stat().st_size > MAX_FILE_SIZE:
        final_path.unlink()
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой: {final_path.stat().st_size // (1024*1024)} МБ"
        )
    
    # Валидация файла
    try:
        validate_file_security(upload_info['filename'], final_path)
    except ValueError as e:
        final_path.unlink()
        raise HTTPException(status_code=400, detail=str(e))
    
    # Очистка чанков
    shutil.rmtree(upload_info["chunk_dir"], ignore_errors=True)
    del chunked_uploads[upload_id]
    
    # Создание задачи на транскрибацию
    safe_language = sanitize_language_code(language)
    
    options = {
        "language": safe_language,
        "punctuation": punctuation,
        "literature": literature,
        "clean": clean,
        "corrections": corrections,
        "analyze_jtbd": analyze_jtbd,
    }
    
    tasks_status[task_id] = {
        "status": "queued",
        "progress": 0,
        "filename": upload_info["filename"],
        "created_at": datetime.now().isoformat(),
        "user": "chunked_upload",
    }
    
    await task_queue.put({
        "file_path": final_path,
        "task_id": task_id,
        "options": options,
    })
    
    logger.info(f"Chunked upload completed and queued: {task_id}")
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Файл загружен и добавлен в очередь"
    }


@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Минимальный тест - принимает только файл"""
    logger.info(f"🧪 TEST: Received file={file.filename}, size={file.size}, content_type={file.content_type}")
    return {"status": "ok", "filename": file.filename, "content_type": file.content_type}

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form("ru-RU"),
    punctuation: bool = Form(True),
    literature: bool = Form(False),
    clean: bool = Form(False),
    corrections: bool = Form(True),
    speaker_labeling: bool = Form(False),
    analyze_jtbd: bool = Form(False),  # JTBD отключен по умолчанию
    user: str = Header(None, alias="X-User"),
    x_forwarded_for: str = Header(None, alias="X-Forwarded-For"),
    x_real_ip: str = Header(None, alias="X-Real-IP")
):
    """
    Транскрибация аудио файла
    
    - **file**: аудио файл (MP3, WAV, AAC, OGG и т.д.)
    - **language**: язык (ru-RU, en-US, etc.)
    - **speaker_labeling**: определять спикеров (кто говорит)
    - **punctuation**: расставлять пунктуацию
    - **literature**: литературный текст (Yandex фильтр)
    - **clean**: убрать слова-паразиты
    - **corrections**: применять исправления
    - **analyze_jtbd**: анализировать по JTBD фреймворку (Jobs To Be Done)
    """
    
    # 🔍 STEP 1: Получили параметры
    logger.info(f"📥 STEP 1: Received params - file={file.filename}, language={language}, punctuation={punctuation}, literature={literature}, clean={clean}, corrections={corrections}, speaker_labeling={speaker_labeling}, analyze_jtbd={analyze_jtbd}")
    
    # Rate limiting (защита от спама)
    # Получаем IP из headers (если за прокси) или используем заглушку
    client_ip = x_forwarded_for or x_real_ip or "direct"
    logger.info(f"📍 STEP 2: Client IP = {client_ip}")
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()  # Первый IP из списка
    
    logger.info(f"Upload request from {client_ip}: {file.filename} ({file.content_type})")
    
    logger.info("⏱️ STEP 3: Checking rate limit...")
    try:
        check_rate_limit(client_ip)
        logger.info("✅ STEP 3: Rate limit OK")
    except HTTPException as e:
        logger.warning(f"❌ STEP 3: Rate limit exceeded for {client_ip}")
        raise
    
    # Генерация task_id
    logger.info("🔑 STEP 4: Generating task_id...")
    task_id = hashlib.md5(
        f"{file.filename}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]
    logger.info(f"✅ STEP 4: task_id = {task_id}")
    
    # Санитизация имени файла (защита от инъекций)
    logger.info("🧹 STEP 5: Sanitizing filename...")
    safe_filename = sanitize_filename(file.filename)
    if file.filename != safe_filename:
        logger.info(f"⚠️  Sanitized filename: '{file.filename}' -> '{safe_filename}'")
    logger.info(f"✅ STEP 5: safe_filename = {safe_filename}")
    
    # Санитизация языкового кода
    logger.info("🌍 STEP 6: Sanitizing language code...")
    safe_language = sanitize_language_code(language)
    logger.info(f"✅ STEP 6: safe_language = {safe_language}")
    
    # Проверка размера файла
    logger.info("📏 STEP 7: Checking file size...")
    file.file.seek(0, 2)  # Переместиться в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Вернуться в начало
    logger.info(f"✅ STEP 7: file_size = {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)} МБ, загружено: {file_size // (1024*1024)} МБ"
        )
    
    if file_size == 0:
        logger.error("❌ STEP 7: File is empty")
        raise HTTPException(status_code=400, detail="Файл пустой")
    
    # Сохранение файла
    logger.info(f"💾 STEP 8: Saving file to {UPLOAD_DIR}...")
    file_path = UPLOAD_DIR / f"{task_id}_{safe_filename}"
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"✅ STEP 8: File saved to {file_path}")
    except Exception as e:
        logger.error(f"❌ STEP 8: Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {e}")
    
    # Проверка безопасности файла
    logger.info(f"🔒 STEP 9: Validating file security...")
    try:
        validate_file_security(safe_filename, file_path)
        logger.info(f"✅ STEP 9: File validated successfully: {safe_filename}")
    except ValueError as e:
        # Удаляем небезопасный файл
        logger.error(f"❌ STEP 9: File validation failed: {safe_filename}, reason: {e}")
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    
    # Опции (используем санитизированный язык)
    logger.info("⚙️ STEP 10: Creating options...")
    options = {
        "language": safe_language,
        "punctuation": punctuation,
        "literature": literature,
        "clean": clean,
        "corrections": corrections,
        "speaker_labeling": speaker_labeling,
        "analyze_jtbd": analyze_jtbd,
    }
    logger.info(f"✅ STEP 10: options = {options}")
    
    # Создание задачи (используем санитизированное имя для отображения)
    logger.info("📋 STEP 11: Creating task status...")
    tasks_status[task_id] = {
        "status": "queued",
        "progress": 0,
        "filename": safe_filename,  # Санитизированное имя для безопасного отображения
        "created_at": datetime.now().isoformat(),
        "user": user or "anonymous",
    }
    logger.info(f"✅ STEP 11: Task status created for {task_id}")
    
    # Добавление в очередь
    logger.info("📤 STEP 12: Adding task to queue...")
    await task_queue.put({
        "file_path": file_path,
        "task_id": task_id,
        "options": options,
    })
    logger.info(f"✅ STEP 12: Task {task_id} added to queue")
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Задача добавлена в очередь"
    }


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Получить статус задачи"""
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_status[task_id]



@app.get("/status/{task_id}/stream")
async def stream_status(task_id: str):
    """SSE endpoint для получения обновлений статуса в реальном времени"""
    async def event_generator():
        while True:
            if task_id not in tasks_status:
                yield f"data: {{\"error\": \"Task not found\"}}\n\n"
                break
            
            task = tasks_status[task_id]
            
            data = {
                "status": task["status"],
                "progress": task.get("progress", 0),
                "message": task.get("message", ""),
                "filename": task.get("filename", "")
            }
            
            if task["status"] == "completed":
                if task.get("result"):
                    data["result"] = task["result"]
                elif task.get("result_file"):
                    result_path = RESULTS_DIR / f"{task_id}.json"
                    if result_path.exists():
                        with open(result_path, "r", encoding="utf-8") as f:
                            result_data = json.load(f)
                            data["result"] = result_data.get("text", "")
            
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            if task["status"] in ["completed", "failed", "error"]:
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Получить результат транскрибации"""
    # Сначала проверяем файл на диске (persists across restarts)
    result_file = RESULTS_DIR / f"{task_id}.json"
    
    if result_file.exists():
        # Файл есть - возвращаем результат
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Файла нет - проверяем in-memory статус
    if task_id not in tasks_status:
        raise HTTPException(
            status_code=404, 
            detail="Результат не найден. Возможно файл был удалён или срок хранения истёк."
        )
    
    status = tasks_status[task_id]
    
    if status["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка обработки: {status.get('error', 'Неизвестная ошибка')}"
        )
    
    if status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Задача ещё обрабатывается. Статус: {status['status']}"
        )
    
    # Статус completed, но файла нет
    raise HTTPException(
        status_code=404, 
        detail="Файл результата был удалён. Попробуйте обработать файл заново."
    )


@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """Скачать результат как текстовый файл"""
    # Сначала проверяем файл на диске
    result_file = RESULTS_DIR / f"{task_id}.json"
    
    if not result_file.exists():
        raise HTTPException(
            status_code=404, 
            detail="Результат не найден. Возможно файл был удалён или срок хранения истёк."
        )
    
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создать TXT файл
    txt_file = TEMP_DIR / f"{task_id}.txt"
    txt_file.write_text(data["text"], encoding='utf-8')
    
    # Имя файла из результата или из in-memory статуса
    filename = data.get("original_filename", "transcript.txt")
    if not filename.endswith('.txt'):
        filename = filename.rsplit('.', 1)[0] + '.txt'
    
    return FileResponse(
        txt_file,
        media_type='text/plain',
        filename=filename
    )


@app.get("/history")
async def get_history(limit: int = 50):
    """Получить историю транскрибаций"""
    history = []
    
    for task_id, status in sorted(
        tasks_status.items(),
        key=lambda x: x[1].get("created_at", ""),
        reverse=True
    )[:limit]:
        history.append({
            "task_id": task_id,
            "filename": status.get("filename"),
            "status": status.get("status"),
            "created_at": status.get("created_at"),
            "user": status.get("user", "anonymous"),
        })
    
    return history


@app.get("/stats")
async def get_stats():
    """Статистика сервиса"""
    total = len(tasks_status)
    completed = sum(1 for s in tasks_status.values() if s["status"] == "completed")
    failed = sum(1 for s in tasks_status.values() if s["status"] == "failed")
    queued = sum(1 for s in tasks_status.values() if s["status"] == "queued")
    processing = sum(1 for s in tasks_status.values() if s["status"] == "processing")
    
    return {
        "total_tasks": total,
        "completed": completed,
        "failed": failed,
        "queued": queued,
        "processing": processing,
        "queue_size": task_queue.qsize(),
    }


@app.get("/formats")
async def get_supported_formats():
    """Список поддерживаемых форматов"""
    return {
        "supported": "Любые файлы с аудио потоком",
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "validation": "ffprobe проверяет наличие аудио потока",
        "note": "Поддерживаются все форматы, которые понимает FFmpeg (любые аудио и видео). Из видео извлекается аудио.",
        "examples": "MP3, WAV, AAC, M4A, OGG, FLAC, MP4, MKV, AVI, WebM, и сотни других форматов"
    }


@app.get("/logs")
async def get_logs(lines: int = 100):
    """
    Получить последние строки логов
    - **lines**: количество последних строк (по умолчанию 100, макс 1000)
    """
    lines = min(lines, 1000)  # Ограничение
    
    log_file = LOGS_DIR / "app.log"
    if not log_file.exists():
        return {"logs": [], "message": "Логи пока пусты"}
    
    try:
        # Читаем последние N строк
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in last_lines],
            "total_lines": len(all_lines),
            "showing": len(last_lines)
        }
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка чтения логов: {e}")


@app.delete("/cleanup")
async def cleanup_old_files(days: int = 7):
    """Очистка старых файлов"""
    import time
    
    cutoff = time.time() - (days * 86400)
    cleaned = 0
    
    for dir in [UPLOAD_DIR, RESULTS_DIR, TEMP_DIR]:
        for file in dir.iterdir():
            if file.stat().st_mtime < cutoff:
                file.unlink()
                cleaned += 1
    
    return {"cleaned_files": cleaned}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
