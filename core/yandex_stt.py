#!/usr/bin/env python3
"""
Yandex SpeechKit STT (Speech-to-Text) API wrapper
Поддержка синхронного (до 1 МБ) и асинхронного API (до 1 ГБ)
"""

import requests
import os
import json
import time
import boto3
from pathlib import Path
from typing import Optional, Dict, List
from botocore.exceptions import ClientError


class YandexSTT:
    """Yandex SpeechKit Speech-to-Text API client"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        folder_id: Optional[str] = None,
        s3_access_key: Optional[str] = None,
        s3_secret_key: Optional[str] = None,
        s3_bucket: Optional[str] = None
    ):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID каталога Yandex Cloud
            s3_access_key: Access Key для Object Storage (для async API)
            s3_secret_key: Secret Key для Object Storage (для async API)
            s3_bucket: Имя bucket в Object Storage (для async API)
        """
        self.api_key = api_key or self._load_env('YANDEX_API_KEY')
        self.folder_id = folder_id or self._load_env('YANDEX_FOLDER_ID')
        
        # S3 credentials для async API
        self.s3_access_key = s3_access_key or self._load_env('YANDEX_S3_ACCESS_KEY')
        self.s3_secret_key = s3_secret_key or self._load_env('YANDEX_S3_SECRET_KEY')
        self.s3_bucket = s3_bucket or self._load_env('YANDEX_S3_BUCKET')
        
        # Endpoints
        self.sync_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        self.async_url = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"
        
        # S3 client
        self.s3_client = None
        if self.s3_access_key and self.s3_secret_key:
            self.s3_client = boto3.client(
                's3',
                endpoint_url='https://storage.yandexcloud.net',
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key,
                region_name='ru-central1'
            )
        
    def _load_env(self, key: str) -> str:
        """Загрузить переменную из .env.yandex"""
        env_file = Path(__file__).parent / '.env.yandex'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            k, v = line.strip().split('=', 1)
                            if k == key:
                                return v
        
        # Fallback на environment variables
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing {key}. Set it in .env.yandex or environment")
        return value
    
    def upload_to_storage(self, audio_file: str, object_name: Optional[str] = None) -> str:
        """
        Загрузить файл в Yandex Object Storage
        
        Args:
            audio_file: Путь к локальному файлу
            object_name: Имя объекта в S3 (если не указано, используется имя файла)
            
        Returns:
            URI файла в формате s3://bucket/object
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized. Check S3 credentials.")
        
        if not object_name:
            object_name = Path(audio_file).name
        
        try:
            self.s3_client.upload_file(audio_file, self.s3_bucket, object_name)
            uri = f"https://storage.yandexcloud.net/{self.s3_bucket}/{object_name}"
            return uri
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {e}")
    
    def delete_from_storage(self, object_name: str):
        """Удалить файл из Object Storage после обработки"""
        if not self.s3_client:
            return
        
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=object_name)
        except ClientError:
            pass  # Игнорируем ошибки удаления
    
    def transcribe_sync(
        self, 
        audio_file: str,
        language: str = "ru-RU",
        format: str = "auto",
        profanity_filter: bool = False,
        punctuation: bool = True,
        hints: Optional[List[str]] = None,
        literature_text: bool = False,
    ) -> Dict:
        """
        Синхронная транскрибация (для файлов до 1 минуты и 1 МБ)
        
        Args:
            audio_file: Путь к аудио файлу
            language: Язык распознавания (ru-RU, en-US, tr-TR и др.)
            format: Формат аудио (lpcm, oggopus, mp3, auto)
            profanity_filter: Фильтровать мат
            punctuation: Расставлять пунктуацию
            hints: Список подсказок для улучшения точности
            literature_text: Литературный текст (убирает "эээ", "ммм")
            
        Returns:
            Dict с результатом транскрибации
        """
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        params = {
            'lang': language,
            'folderId': self.folder_id,
            'format': format,
            'profanityFilter': str(profanity_filter).lower(),
            'punctuation': str(punctuation).lower(),
        }
        
        # Литературный текст
        if literature_text:
            params['literature_text'] = 'true'
        
        # Hints
        if hints:
            params['hints'] = ','.join(hints)
        
        response = requests.post(
            self.sync_url,
            headers=headers,
            params=params,
            data=audio_data
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        return response.json()
    
    def transcribe_async(
        self,
        audio_file: str,
        language: str = "ru-RU",
        profanity_filter: bool = False,
        punctuation: bool = True,
        literature_text: bool = False,
        auto_upload: bool = True,
    ) -> str:
        """
        Асинхронная транскрибация (для файлов до 1 ГБ)
        
        Args:
            audio_file: Путь к аудио файлу (локальный или URI)
            language: Язык распознавания
            profanity_filter: Фильтровать мат
            punctuation: Расставлять пунктуацию
            literature_text: Литературный текст
            auto_upload: Автоматически загружать локальные файлы в S3
            
        Returns:
            Operation ID для проверки статуса
        """
        # Если локальный файл - загружаем в S3
        if not audio_file.startswith('http') and auto_upload:
            audio_file = self.upload_to_storage(audio_file)
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        config = {
            "config": {
                "specification": {
                    "languageCode": language,
                    "profanityFilter": profanity_filter,
                    "model": "general",
                    "audioEncoding": "OGG_OPUS",
                    "sampleRateHertz": 48000,
                    "audioChannelCount": 1,
                    "punctuation": punctuation,
                }
            },
            "audio": {
                "uri": audio_file
            }
        }
        
        # Литературный текст
        if literature_text:
            config["config"]["specification"]["literatureText"] = True
        
        response = requests.post(
            self.async_url,
            headers=headers,
            json=config
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        result = response.json()
        return result.get('id')
    
    def check_operation(self, operation_id: str) -> Dict:
        """
        Проверить статус асинхронной операции
        
        Args:
            operation_id: ID операции из transcribe_async()
            
        Returns:
            Статус и результат:
            - done: bool (завершена ли операция)
            - response: результат транскрибации (если done=True)
            - error: ошибка (если была)
        """
        url = f"https://operation.api.cloud.yandex.net/operations/{operation_id}"
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        return response.json()
    
    def wait_for_completion(self, operation_id: str, timeout: int = 600, poll_interval: int = 5) -> Dict:
        """
        Ждать завершения асинхронной операции
        
        Args:
            operation_id: ID операции
            timeout: Максимальное время ожидания (секунды)
            poll_interval: Интервал проверки (секунды)
            
        Returns:
            Результат транскрибации
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.check_operation(operation_id)
            
            if result.get('done'):
                if 'error' in result:
                    raise Exception(f"Transcription failed: {result['error']}")
                
                # Извлечь текст из результата
                response = result.get('response', {})
                chunks = response.get('chunks', [])
                
                if not chunks:
                    return {"result": ""}
                
                # Собрать весь текст
                full_text = ' '.join([
                    ' '.join([alt['text'] for alt in chunk.get('alternatives', [])])
                    for chunk in chunks
                ])
                
                return {"result": full_text.strip()}
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Operation {operation_id} did not complete within {timeout} seconds")
    
    def transcribe_async_with_cleanup(
        self,
        audio_file: str,
        language: str = "ru-RU",
        profanity_filter: bool = False,
        punctuation: bool = True,
        literature_text: bool = False,
        timeout: int = 600,
        poll_interval: int = 5,
        hints: Optional[List[str]] = None,
        speaker_labeling: bool = False,
    ) -> Dict:
        """
        Полный workflow: загрузка → транскрибация → очистка
        
        Автоматически удаляет временный файл из Object Storage после получения результата.
        
        Args:
            audio_file: Путь к аудио файлу
            language: Язык распознавания
            profanity_filter: Фильтровать мат
            punctuation: Расставлять пунктуацию
            literature_text: Литературный текст
            timeout: Максимальное время ожидания (секунды)
            poll_interval: Интервал проверки (секунды)
            hints: Список подсказок для улучшения распознавания
            speaker_labeling: Разметка спикеров (требует стерео)
            
        Returns:
            Результат транскрибации
        """
        # Сохраняем имя файла для последующего удаления
        object_name = Path(audio_file).name
        
        try:
            # Транскрибация
            operation_id = self.transcribe_async(
                audio_file,
                language=language,
                profanity_filter=profanity_filter,
                punctuation=punctuation,
                literature_text=literature_text,
                auto_upload=True,
                hints=hints,
                speaker_labeling=speaker_labeling,
            )
            
            # Ожидание результата
            result = self.wait_for_completion(operation_id, timeout=timeout, poll_interval=poll_interval)
            
            return result
            
        finally:
            # Удаление файла из S3 (в любом случае - успех или ошибка)
            try:
                self.delete_from_storage(object_name)
            except Exception:
                pass  # Игнорируем ошибки удаления


def example_usage():
    """Пример использования"""
    
    # Инициализация
    stt = YandexSTT()
    
    # Асинхронная транскрибация (большие файлы)
    try:
        print("Загрузка и транскрибация...")
        operation_id = stt.transcribe_async(
            "interview.mp3",
            language="ru-RU",
            punctuation=True,
            literature_text=True
        )
        
        print(f"Operation ID: {operation_id}")
        print("Ожидание результата...")
        
        result = stt.wait_for_completion(operation_id, timeout=600)
        print(f"\nТранскрипция: {result['result']}")
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    example_usage()
