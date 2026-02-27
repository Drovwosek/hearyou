#!/usr/bin/env python3
"""
Unit-тесты для yandex_stt.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from yandex_stt import YandexSTT


class TestYandexSTTInit:
    """Тесты инициализации YandexSTT"""
    
    def test_init_with_env_vars(self, mock_env_vars):
        """Тест инициализации с переменными окружения"""
        stt = YandexSTT()
        
        assert stt.api_key == "test_api_key_12345"
        assert stt.folder_id == "test_folder_id"
        assert stt.s3_access_key == "test_s3_access"
        assert stt.s3_secret_key == "test_s3_secret"
        assert stt.s3_bucket == "test-bucket"
    
    def test_init_with_explicit_params(self):
        """Тест инициализации с явными параметрами"""
        stt = YandexSTT(
            api_key="custom_key",
            folder_id="custom_folder",
            s3_access_key="custom_access",
            s3_secret_key="custom_secret",
            s3_bucket="custom-bucket"
        )
        
        assert stt.api_key == "custom_key"
        assert stt.folder_id == "custom_folder"
        assert stt.s3_access_key == "custom_access"
        assert stt.s3_secret_key == "custom_secret"
        assert stt.s3_bucket == "custom-bucket"
    
    def test_init_urls_correct(self, mock_env_vars):
        """Тест правильности URL endpoints"""
        stt = YandexSTT()
        
        assert "stt.api.cloud.yandex.net" in stt.sync_url
        assert "transcribe.api.cloud.yandex.net" in stt.async_url


class TestYandexSTTSync:
    """Тесты синхронной транскрипции"""
    
    def test_transcribe_sync_success(self, mock_env_vars, mock_yandex_api, test_audio_file):
        """Тест успешной синхронной транскрипции"""
        stt = YandexSTT()
        
        result = stt.transcribe_sync(test_audio_file, language="ru-RU")
        
        assert "result" in result
        assert isinstance(result["result"], str)
        assert len(result["result"]) > 0
    
    def test_transcribe_sync_with_options(self, mock_env_vars, mock_yandex_api, test_audio_file):
        """Тест транскрипции с опциями"""
        stt = YandexSTT()
        
        result = stt.transcribe_sync(
            test_audio_file,
            language="en-US",
            profanity_filter=True,
            punctuation=True,
            literature_text=True
        )
        
        assert "result" in result
    
    @patch('requests.post')
    def test_transcribe_sync_api_error(self, mock_post, mock_env_vars, test_audio_file):
        """Тест обработки ошибки API"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        stt = YandexSTT()
        
        with pytest.raises(Exception) as exc_info:
            stt.transcribe_sync(test_audio_file)
        
        assert "API Error" in str(exc_info.value)
        assert "400" in str(exc_info.value)


class TestYandexSTTAsync:
    """Тесты асинхронной транскрипции"""
    
    @patch('requests.post')
    def test_transcribe_async_returns_operation_id(self, mock_post, mock_env_vars, mock_s3_client, test_audio_file):
        """Тест что async API возвращает operation_id"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_operation_123"}
        mock_post.return_value = mock_response
        
        stt = YandexSTT()
        operation_id = stt.transcribe_async(test_audio_file, auto_upload=True)
        
        assert operation_id == "test_operation_123"
    
    @patch('requests.get')
    def test_check_operation_pending(self, mock_get, mock_env_vars):
        """Тест проверки незавершённой операции"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"done": False}
        mock_get.return_value = mock_response
        
        stt = YandexSTT()
        result = stt.check_operation("test_op_123")
        
        assert result["done"] is False
    
    @patch('requests.get')
    def test_check_operation_completed(self, mock_get, mock_env_vars):
        """Тест проверки завершённой операции"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "done": True,
            "response": {
                "chunks": [
                    {
                        "alternatives": [
                            {"text": "Тест"}
                        ]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        stt = YandexSTT()
        result = stt.check_operation("test_op_123")
        
        assert result["done"] is True
        assert "response" in result


class TestYandexSTTS3:
    """Тесты работы с S3 Object Storage"""
    
    def test_upload_to_storage(self, mock_env_vars, mock_s3_client, test_audio_file):
        """Тест загрузки файла в S3"""
        stt = YandexSTT()
        
        uri = stt.upload_to_storage(test_audio_file)
        
        assert uri.startswith("https://storage.yandexcloud.net/")
        assert "test-bucket" in uri
        mock_s3_client.upload_file.assert_called_once()
    
    def test_upload_to_storage_custom_name(self, mock_env_vars, mock_s3_client, test_audio_file):
        """Тест загрузки с кастомным именем"""
        stt = YandexSTT()
        
        uri = stt.upload_to_storage(test_audio_file, object_name="custom_name.wav")
        
        assert "custom_name.wav" in uri
    
    def test_delete_from_storage(self, mock_env_vars, mock_s3_client):
        """Тест удаления файла из S3"""
        stt = YandexSTT()
        
        # Не должно падать
        stt.delete_from_storage("test_file.wav")
        
        mock_s3_client.delete_object.assert_called_once()
    
    def test_delete_from_storage_no_client(self, mock_env_vars):
        """Тест удаления когда S3 client не инициализирован"""
        stt = YandexSTT()
        stt.s3_client = None
        
        # Не должно падать
        stt.delete_from_storage("test_file.wav")


class TestYandexSTTWaitCompletion:
    """Тесты ожидания завершения операции"""
    
    @patch('yandex_stt.YandexSTT.check_operation')
    @patch('time.sleep', return_value=None)
    def test_wait_for_completion_immediate(self, mock_sleep, mock_check, mock_env_vars):
        """Тест когда операция сразу завершена"""
        mock_check.return_value = {
            "done": True,
            "response": {
                "chunks": [
                    {
                        "alternatives": [
                            {"text": "Тест"}
                        ]
                    }
                ]
            }
        }
        
        stt = YandexSTT()
        result = stt.wait_for_completion("test_op_123", poll_interval=1)
        
        assert "result" in result
        assert "Тест" in result["result"]
    
    @patch('yandex_stt.YandexSTT.check_operation')
    @patch('time.sleep', return_value=None)
    def test_wait_for_completion_timeout(self, mock_sleep, mock_check, mock_env_vars):
        """Тест таймаута ожидания"""
        mock_check.return_value = {"done": False}
        
        stt = YandexSTT()
        
        with pytest.raises(TimeoutError):
            stt.wait_for_completion("test_op_123", timeout=1, poll_interval=0.5)
    
    @patch('yandex_stt.YandexSTT.check_operation')
    @patch('time.sleep', return_value=None)
    def test_wait_for_completion_error(self, mock_sleep, mock_check, mock_env_vars):
        """Тест обработки ошибки операции"""
        mock_check.return_value = {
            "done": True,
            "error": {"message": "Test error"}
        }
        
        stt = YandexSTT()
        
        with pytest.raises(Exception) as exc_info:
            stt.wait_for_completion("test_op_123")
        
        assert "failed" in str(exc_info.value).lower()


class TestYandexSTTEdgeCases:
    """Тесты граничных случаев"""
    
    def test_empty_result_handling(self, mock_env_vars):
        """Тест обработки пустого результата"""
        stt = YandexSTT()
        
        # Тест с пустыми chunks
        with patch.object(stt, 'check_operation') as mock_check:
            mock_check.return_value = {
                "done": True,
                "response": {"chunks": []}
            }
            
            result = stt.wait_for_completion("test_op")
            
            assert result["result"] == ""
    
    def test_missing_credentials(self, monkeypatch):
        """Тест ошибки при отсутствии credentials"""
        monkeypatch.delenv("YANDEX_API_KEY", raising=False)
        monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            stt = YandexSTT()
        
        assert "Missing" in str(exc_info.value)
