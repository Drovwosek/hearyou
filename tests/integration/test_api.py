#!/usr/bin/env python3
"""
Integration тесты для FastAPI приложения
"""

import pytest
from pathlib import Path
import sys
import json
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "stt-service"))

# Тесты требуют запущенный сервер или используют TestClient
# Для unit-тестов используем моки


class TestHealthEndpoint:
    """Тесты health endpoint"""
    
    def test_root_endpoint_returns_html(self, app_client):
        """Тест главной страницы"""
        response = app_client.get("/")
        
        assert response.status_code == 200
        assert "html" in response.text.lower()
    
    def test_health_check(self, app_client):
        """Тест health check (если есть endpoint)"""
        # Если нет специального health endpoint, проверяем root
        response = app_client.get("/")
        
        assert response.status_code == 200


class TestStatsEndpoint:
    """Тесты статистики"""
    
    def test_stats_endpoint(self, app_client):
        """Тест получения статистики"""
        response = app_client.get("/stats")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "total_tasks" in data
        assert "completed" in data
        assert "failed" in data
        assert "queued" in data
        assert "processing" in data
    
    def test_stats_returns_numbers(self, app_client):
        """Тест что статистика возвращает числа"""
        response = app_client.get("/stats")
        data = response.json()
        
        assert isinstance(data["total_tasks"], int)
        assert isinstance(data["completed"], int)
        assert isinstance(data["failed"], int)


class TestFormatsEndpoint:
    """Тесты поддерживаемых форматов"""
    
    def test_formats_endpoint(self, app_client):
        """Тест получения списка форматов"""
        response = app_client.get("/formats")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "supported" in data or "max_file_size_mb" in data
    
    def test_formats_includes_max_size(self, app_client):
        """Тест что включен максимальный размер"""
        response = app_client.get("/formats")
        data = response.json()
        
        assert "max_file_size_mb" in data
        assert isinstance(data["max_file_size_mb"], (int, float))


class TestHistoryEndpoint:
    """Тесты истории транскрибаций"""
    
    def test_history_endpoint(self, app_client):
        """Тест получения истории"""
        response = app_client.get("/history")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_history_with_limit(self, app_client):
        """Тест истории с лимитом"""
        response = app_client.get("/history?limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 10


class TestUploadEndpoint:
    """Тесты загрузки файлов"""
    
    @pytest.mark.skip(reason="Требует моков для полноценной работы")
    def test_upload_file_success(self, app_client, test_audio_file, mock_yandex_api, mock_s3_client):
        """Тест успешной загрузки файла"""
        with open(test_audio_file, "rb") as f:
            files = {"file": ("test.wav", f, "audio/wav")}
            data = {
                "language": "ru-RU",
                "punctuation": "true",
                "literature": "false",
                "clean": "false",
                "corrections": "true"
            }
            
            response = app_client.post("/transcribe", files=files, data=data)
        
        assert response.status_code == 200
        
        result = response.json()
        assert "task_id" in result
        assert "status" in result
        assert result["status"] in ["queued", "processing"]
    
    def test_upload_without_file(self, app_client):
        """Тест загрузки без файла"""
        response = app_client.post("/transcribe", data={
            "language": "ru-RU"
        })
        
        # Должна быть ошибка 422 (validation error)
        assert response.status_code == 422
    
    @pytest.mark.skip(reason="Требует моков")
    def test_upload_invalid_language(self, app_client, test_audio_file):
        """Тест с невалидным языковым кодом"""
        with open(test_audio_file, "rb") as f:
            files = {"file": ("test.wav", f, "audio/wav")}
            data = {"language": "invalid-lang"}
            
            response = app_client.post("/transcribe", files=files, data=data)
        
        # Сервис должен заменить на ru-RU по умолчанию
        assert response.status_code == 200


class TestStatusEndpoint:
    """Тесты проверки статуса задачи"""
    
    def test_status_not_found(self, app_client):
        """Тест статуса несуществующей задачи"""
        response = app_client.get("/status/nonexistent_task_id")
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="Требует создания задачи")
    def test_status_existing_task(self, app_client):
        """Тест статуса существующей задачи"""
        # Создать задачу, затем проверить статус
        pass


class TestResultEndpoint:
    """Тесты получения результатов"""
    
    def test_result_not_found(self, app_client):
        """Тест результата несуществующей задачи"""
        response = app_client.get("/result/nonexistent_task_id")
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="Требует завершённой задачи")
    def test_result_completed_task(self, app_client):
        """Тест получения результата завершённой задачи"""
        # Требует создать и завершить задачу
        pass


class TestDownloadEndpoint:
    """Тесты скачивания результатов"""
    
    def test_download_not_found(self, app_client):
        """Тест скачивания несуществующего результата"""
        response = app_client.get("/download/nonexistent_task_id")
        
        assert response.status_code == 404


class TestSanitization:
    """Тесты санитизации входных данных"""
    
    @pytest.mark.skip(reason="Требует моков")
    def test_filename_sanitization(self, app_client):
        """Тест санитизации имени файла"""
        from app import sanitize_filename
        
        # Тест опасных символов
        assert "../etc/passwd" not in sanitize_filename("../etc/passwd.mp3")
        assert ".." not in sanitize_filename("../../file.mp3")
        
        # Тест пустого имени
        result = sanitize_filename("")
        assert result != ""
        assert ".mp3" in result
        
        # Тест длинного имени
        long_name = "a" * 300 + ".mp3"
        result = sanitize_filename(long_name)
        assert len(result) <= 210  # 200 + расширение
    
    def test_language_sanitization(self):
        """Тест санитизации языкового кода"""
        from app import sanitize_language_code
        
        # Валидные коды
        assert sanitize_language_code("ru-RU") == "ru-RU"
        assert sanitize_language_code("en-US") == "en-US"
        
        # Невалидные коды -> ru-RU
        assert sanitize_language_code("invalid") == "ru-RU"
        assert sanitize_language_code("xx-XX") == "ru-RU"


class TestRateLimiting:
    """Тесты rate limiting"""
    
    @pytest.mark.skip(reason="Сложный интеграционный тест")
    def test_rate_limit_exceeded(self, app_client):
        """Тест превышения rate limit"""
        # Отправить >10 запросов за минуту
        # Должен получить 429 Too Many Requests
        pass


class TestChunkedUpload:
    """Тесты загрузки больших файлов по частям"""
    
    @pytest.mark.skip(reason="Требует сложной настройки")
    def test_upload_chunk_success(self, app_client):
        """Тест загрузки чанка"""
        chunk_data = b"test_audio_data"
        
        response = app_client.post("/upload-chunk", data={
            "upload_id": "test_upload_123",
            "chunk_index": 0,
            "total_chunks": 1,
            "filename": "test.mp3"
        }, files={"chunk": ("chunk_0", BytesIO(chunk_data))})
        
        assert response.status_code == 200
        
        result = response.json()
        assert "upload_id" in result
        assert "complete" in result
    
    @pytest.mark.skip(reason="Требует сложной настройки")
    def test_complete_upload(self, app_client):
        """Тест завершения chunked upload"""
        # Загрузить все чанки, затем вызвать complete-upload
        pass


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    @pytest.mark.skip(reason="Требует моков")
    def test_api_error_handling(self, app_client):
        """Тест обработки ошибок API"""
        # Смоделировать ошибку Yandex API
        pass
    
    @pytest.mark.skip(reason="Требует моков")  
    def test_s3_error_handling(self, app_client):
        """Тест обработки ошибок S3"""
        # Смоделировать ошибку S3
        pass


class TestConcurrency:
    """Тесты параллельной обработки"""
    
    @pytest.mark.skip(reason="Требует реального окружения")
    def test_multiple_tasks_parallel(self, app_client):
        """Тест параллельной обработки нескольких задач"""
        # Отправить несколько задач одновременно
        # Проверить что обрабатываются параллельно (3 воркера)
        pass


class TestCleanup:
    """Тесты очистки старых файлов"""
    
    def test_cleanup_endpoint_exists(self, app_client):
        """Тест наличия endpoint для очистки"""
        response = app_client.delete("/cleanup?days=7")
        
        # Может вернуть 200 или требовать авторизацию
        assert response.status_code in [200, 401, 403]
