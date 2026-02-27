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

# Добавляем путь к core модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "stt-yandex"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "stt-service"))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables для Yandex API"""
    monkeypatch.setenv("YANDEX_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "test_folder_id")
    monkeypatch.setenv("YANDEX_S3_ACCESS_KEY", "test_s3_access")
    monkeypatch.setenv("YANDEX_S3_SECRET_KEY", "test_s3_secret")
    monkeypatch.setenv("YANDEX_S3_BUCKET", "test-bucket")


@pytest.fixture
def mock_yandex_api(mocker):
    """Mock Yandex STT API responses"""
    
    # Mock requests.post для sync API
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": "Тестовая транскрипция текста"
    }
    
    mocker.patch("requests.post", return_value=mock_response)
    
    return mock_response


@pytest.fixture
def mock_s3_client(mocker):
    """Mock boto3 S3 client"""
    mock_client = MagicMock()
    
    # Mock upload_file
    mock_client.upload_file.return_value = None
    
    # Mock delete_object
    mock_client.delete_object.return_value = None
    
    mocker.patch("boto3.client", return_value=mock_client)
    
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
    """Mock асинхронной операции Yandex"""
    
    # Mock для transcribe_async
    operation_id = "test_operation_123"
    
    # Mock для check_operation
    mock_check = mocker.patch("yandex_stt.YandexSTT.check_operation")
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
    """Типичный ответ от Yandex STT API"""
    return {
        "result": "Привет мир это тестовая транскрипция"
    }


@pytest.fixture
def test_yandex_chunks_response():
    """Ответ Yandex API с chunks (для speaker diarization)"""
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
