#!/usr/bin/env python3
"""
OpenAI Whisper STT (Speech-to-Text) локальный wrapper
Использует локальную модель Whisper для транскрибации
"""

import whisper
import os
import json
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class WhisperSTT:
    """OpenAI Whisper Speech-to-Text клиент (локальный)"""
    
    def __init__(
        self, 
        model_name: str = "medium",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Инициализация клиента Whisper
        
        Args:
            model_name: Размер модели (tiny, base, small, medium, large)
                       medium - хороший баланс качества и скорости для CPU
            device: Устройство для inference ("cpu" или "cuda")
            compute_type: Тип вычислений (int8, float16, float32)
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        
        logger.info(f"🔄 Загрузка модели Whisper '{model_name}' на {device}...")
        try:
            self.model = whisper.load_model(model_name, device=device)
            logger.info(f"✅ Модель Whisper '{model_name}' загружена успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели Whisper: {e}")
            raise
    
    def transcribe_sync(
        self,
        audio_file: str,
        language: str = "ru",
        profanity_filter: bool = False,
        literature_text: bool = False,
        word_timestamps: bool = True,
        hints: Optional[List[str]] = None,
        punctuation: bool = True,
        **kwargs
    ) -> Dict:
        """
        Транскрибация аудио через локальный Whisper
        
        Args:
            audio_file: Путь к аудио файлу
            language: Язык аудио (ru, en, etc.)
            profanity_filter: Игнорируется (для совместимости с YandexSTT)
            literature_text: Игнорируется (для совместимости с YandexSTT)
            word_timestamps: Включить временные метки слов
            hints: Список подсказок (initial_prompt для Whisper)
            punctuation: Игнорируется (Whisper не поддерживает, для совместимости с YandexSTT)
            **kwargs: Дополнительные параметры для whisper.transcribe()
            
        Returns:
            Dict с результатом транскрибации (совместимый формат с YandexSTT)
        """
        try:
            # Конвертация language code: "ru-RU" -> "ru"
            if '-' in language:
                language = language.split('-')[0].lower()
            
            # Подготовка параметров
            transcribe_options = {
                "language": language,
                "task": "transcribe",
                "verbose": False,
                "word_timestamps": word_timestamps,
            }
            
            # Добавляем hints как initial_prompt (помогает модели с терминологией)
            if hints:
                initial_prompt = " ".join(hints[:10])  # Ограничиваем длину
                transcribe_options["initial_prompt"] = initial_prompt
                logger.info(f"📝 Использую hints как initial_prompt: {initial_prompt[:100]}...")
            
            # Мержим с дополнительными параметрами
            transcribe_options.update(kwargs)
            
            logger.info(f"🎤 Начинаю транскрибацию: {audio_file}")
            result = self.model.transcribe(audio_file, **transcribe_options)
            
            # Конвертируем результат в формат, совместимый с YandexSTT
            formatted_result = self._format_result(result, word_timestamps)
            
            logger.info(f"✅ Транскрибация завершена: {len(formatted_result['result'])} символов")
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка транскрибации: {e}")
            return {
                "error": str(e),
                "result": "",
                "chunks": []
            }
    
    def _format_result(self, whisper_result: Dict, include_timestamps: bool = True) -> Dict:
        """
        Форматирует результат Whisper в формат, совместимый с YandexSTT
        
        Args:
            whisper_result: Результат от whisper.transcribe()
            include_timestamps: Включить временные метки
            
        Returns:
            Dict в формате YandexSTT {result, chunks}
        """
        text = whisper_result.get("text", "").strip()
        
        # Формируем chunks из segments
        chunks = []
        for segment in whisper_result.get("segments", []):
            chunk = {
                "alternatives": [{
                    "text": segment["text"].strip(),
                    "confidence": 1.0  # Whisper не даёт confidence, ставим 1.0
                }],
                "start_time": f"{segment['start']:.3f}s",
                "end_time": f"{segment['end']:.3f}s"
            }
            
            # Добавляем word-level timestamps если есть
            if include_timestamps and "words" in segment:
                chunk["alternatives"][0]["words"] = [
                    {
                        "word": word["word"].strip(),
                        "start_time": f"{word['start']:.3f}s",
                        "end_time": f"{word['end']:.3f}s",
                        "confidence": 1.0
                    }
                    for word in segment["words"]
                ]
            
            chunks.append(chunk)
        
        return {
            "result": text,
            "chunks": chunks,
            "language": whisper_result.get("language", "ru")
        }
    
    def transcribe_async(self, *args, **kwargs):
        """
        Асинхронная транскрибация не поддерживается локально
        Используется тот же метод что и sync
        """
        logger.warning("⚠️ WhisperSTT не поддерживает async API, используется sync метод")
        return self.transcribe_sync(*args, **kwargs)
    
    def wait_for_completion(self, operation_result: Dict, poll_interval: int = 5, timeout: int = None) -> Dict:
        """
        Заглушка для совместимости с YandexSTT
        Whisper работает синхронно, поэтому просто возвращаем результат
        
        Args:
            operation_result: Результат от transcribe_async
            poll_interval: Игнорируется
            timeout: Игнорируется (для совместимости с YandexSTT)
            
        Returns:
            Тот же результат (уже готов)
        """
        logger.info("✅ Whisper: результат уже готов (синхронный режим)")
        return operation_result
    
    def upload_to_storage(self, audio_file: str, object_name: Optional[str] = None) -> str:
        """
        Заглушка для совместимости с YandexSTT
        Локальный Whisper не требует загрузки в облако
        """
        logger.warning("⚠️ upload_to_storage не нужен для локального Whisper")
        return audio_file
    
    def delete_from_storage(self, object_name: str) -> None:
        """
        Заглушка для совместимости с YandexSTT
        Локальный Whisper не использует облачное хранилище
        """
        logger.debug("⚠️ delete_from_storage не нужен для локального Whisper")
        pass


# Удобная функция для быстрого использования
def transcribe_file(audio_file: str, model: str = "medium", language: str = "ru") -> str:
    """
    Простая функция для транскрибации файла
    
    Args:
        audio_file: Путь к аудио файлу
        model: Размер модели Whisper
        language: Язык
        
    Returns:
        Текст транскрипции
    """
    stt = WhisperSTT(model_name=model)
    result = stt.transcribe_sync(audio_file, language=language)
    return result.get("result", "")
