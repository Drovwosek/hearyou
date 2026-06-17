#!/usr/bin/env python3
"""
Pytest fixtures для HearYou STT тестов
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import json
import wave

PROJECT_ROOT = Path(__file__).parent.parent

# Добавляем путь к core модулям и FastAPI сервису
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "core"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "stt-service"))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables для локального Whisper runtime."""
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)
    monkeypatch.delenv("YANDEX_S3_ACCESS_KEY", raising=False)
    monkeypatch.delenv("YANDEX_S3_SECRET_KEY", raising=False)
    monkeypatch.delenv("YANDEX_S3_BUCKET", raising=False)
    monkeypatch.setenv("WHISPER_MODEL", "tiny")
    monkeypatch.setenv("WHISPER_DEVICE", "cpu")
    monkeypatch.setenv("WHISPER_COMPUTE_TYPE", "int8")


@pytest.fixture
def mock_local_stt(mocker):
    """Mock локального STT-провайдера."""
    mock_response = {
        "result": "Тестовая транскрипция текста"
    }

    mock_transcribe = mocker.patch("core.local_whisper_stt.LocalWhisperSTT.transcribe_sync")
    mock_transcribe.return_value = mock_response

    return mock_transcribe


@pytest.fixture
def mock_yandex_api(mock_local_stt):
    """Legacy alias для старых пропущенных тестов."""
    return mock_local_stt


@pytest.fixture
def mock_s3_client(mocker):
    """Legacy no-op S3 client mock для старых пропущенных тестов."""
    mock_client = MagicMock()
    mock_client.upload_file.return_value = None
    mock_client.delete_object.return_value = None
    return mock_client


@pytest.fixture
def test_audio_file():
    """Создать тестовый WAV файл"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        # Создать простейший WAV файл (1 секунда тишины)
        with wave.open(f.name, 'wb') as wav:
            wav.setnchannels(1)  # Моно
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(16000)  # 16kHz
            wav.writeframes(b'\x00' * 32000)  # 1 секунда тишины
        
        yield f.name
        
        # Cleanup
        try:
            os.unlink(f.name)
        except:
            pass


@pytest.fixture
def test_text_with_fillers():
    """Пример текста со словами-паразитами"""
    return "Эээ ну вот я думаю что эээ это хорошо короче типа"


@pytest.fixture
def test_text_with_errors():
    """Пример текста с частыми ошибками транскрипции"""
    return "иришка мелишка свита"


@pytest.fixture
def test_corrections_dict():
    """Словарь тестовых исправлений"""
    return {
        "иришка": "ИИшка",
        "мелишка": "милишка",
        "свита": "свит"
    }


@pytest.fixture
def test_corrections_file():
    """Создать временный JSON файл с исправлениями"""
    corrections = {
        "test_words": {
            "тест": "TEST",
            "пример": "EXAMPLE"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False, encoding='utf-8') as f:
        json.dump(corrections, f, ensure_ascii=False)
        yield f.name
        
    # Cleanup
    try:
        os.unlink(f.name)
    except:
        pass


@pytest.fixture
def mock_async_operation(mocker):
    """Mock асинхронной операции локального STT."""
    operation_id = "test_operation_123"
    mock_check = mocker.patch("core.local_whisper_stt.LocalWhisperSTT.check_operation")
    mock_check.return_value = {
        "done": True,
        "response": {
            "chunks": [
                {
                    "alternatives": [
                        {
                            "text": "Тестовая транскрипция",
                            "words": []
                        }
                    ]
                }
            ]
        }
    }
    
    return operation_id


@pytest.fixture
def test_yandex_response():
    """Legacy fixture: типичный ответ STT API."""
    return {
        "result": "Привет мир это тестовая транскрипция"
    }


@pytest.fixture
def test_yandex_chunks_response():
    """Legacy fixture: ответ STT API с chunks (для speaker diarization)."""
    return {
        "chunks": [
            {
                "alternatives": [
                    {
                        "text": "Привет",
                        "words": [
                            {
                                "word": "Привет",
                                "startTime": "0.0s",
                                "endTime": "0.5s",
                                "speakerTag": "1"
                            }
                        ]
                    }
                ]
            },
            {
                "alternatives": [
                    {
                        "text": "Как дела",
                        "words": [
                            {
                                "word": "Как",
                                "startTime": "0.6s",
                                "endTime": "0.8s",
                                "speakerTag": "2"
                            },
                            {
                                "word": "дела",
                                "startTime": "0.8s",
                                "endTime": "1.0s",
                                "speakerTag": "2"
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_ffprobe(mocker):
    """Mock ffprobe для валидации файлов"""
    import subprocess
    
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "streams": [
            {"codec_type": "audio", "codec_name": "pcm_s16le"}
        ]
    })
    
    mocker.patch("subprocess.run", return_value=mock_result)
    
    return mock_result


@pytest.fixture
def app_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from app import app
    
    return TestClient(app)
