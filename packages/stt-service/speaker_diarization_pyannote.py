"""
Speaker Diarization с использованием pyannote.audio

State-of-the-art решение для определения "кто когда говорит".
Значительно лучше resemblyzer - точнее определяет границы реплик,
работает с перебиваниями, короткими фразами.
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeakerDiarizationPyannote:
    """
    Определение спикеров в аудио файле с помощью pyannote.audio
    """
    
    def __init__(self, hf_token: Optional[str] = None):
        """
        Инициализация
        
        Args:
            hf_token: HuggingFace токен для доступа к моделям
                     Если None - берётся из env: HUGGINGFACE_TOKEN
        """
        self.hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
        self.pipeline = None
        
    def _init_pipeline(self):
        """Ленивая инициализация pipeline (только когда нужно)"""
        if self.pipeline is not None:
            return
        
        try:
            from pyannote.audio import Pipeline
            
            logger.info("Загружаю pyannote.audio speaker-diarization pipeline...")
            
            if not self.hf_token:
                raise ValueError(
                    "Требуется HuggingFace токен!\n"
                    "1. Зарегистрируйтесь на https://huggingface.co\n"
                    "2. Создайте токен: https://huggingface.co/settings/tokens\n"
                    "3. Примите условия использования: https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                    "4. Установите: export HUGGINGFACE_TOKEN='your_token'"
                )
            
            # Используем последнюю модель 3.1
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
            )
            
            # Оптимизация для GPU если доступно
            import torch
            if torch.cuda.is_available():
                logger.info("✅ Используется GPU для диаризации")
                self.pipeline.to(torch.device("cuda"))
            else:
                logger.info("ℹ️ Используется CPU (GPU не найден)")
            
            logger.info("✅ Pyannote pipeline загружен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации pyannote: {e}")
            raise
    
    def diarize(
        self, 
        audio_file: str, 
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> List[Dict]:
        """
        Определяет спикеров в аудио файле
        
        Args:
            audio_file: Путь к аудио файлу
            num_speakers: Точное количество спикеров (если известно)
            min_speakers: Минимальное количество (для автоопределения)
            max_speakers: Максимальное количество (для автоопределения)
        
        Returns:
            Список сегментов: [{"speaker": "SPEAKER_00", "start": 1.5, "end": 5.3}, ...]
        """
        self._init_pipeline()
        
        logger.info(f"Начинаю диаризацию: {audio_file}")
        logger.info(f"  num_speakers={num_speakers}, "
                   f"min={min_speakers}, max={max_speakers}")
        
        try:
            # Запускаем диаризацию
            diarization = self.pipeline(
                audio_file,
                num_speakers=num_speakers,
                min_speakers=min_speakers,
                max_speakers=max_speakers
            )
            
            # Конвертируем результат в наш формат
            segments = []
            
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,  # pyannote использует "SPEAKER_00", "SPEAKER_01" и т.д.
                    "start": float(turn.start),
                    "end": float(turn.end)
                })
            
            # Статистика
            unique_speakers = len(set(s["speaker"] for s in segments))
            total_duration = segments[-1]["end"] if segments else 0
            
            logger.info(f"✅ Найдено {unique_speakers} спикеров, "
                       f"{len(segments)} сегментов, "
                       f"{total_duration:.1f}s общая длительность")
            
            # Лог по спикерам
            for speaker in sorted(set(s["speaker"] for s in segments)):
                speaker_segments = [s for s in segments if s["speaker"] == speaker]
                speaker_time = sum(s["end"] - s["start"] for s in speaker_segments)
                logger.info(f"  {speaker}: {len(speaker_segments)} сегментов, "
                           f"{speaker_time:.1f}s ({speaker_time/total_duration*100:.1f}%)")
            
            return segments
            
        except Exception as e:
            logger.error(f"Ошибка диаризации: {e}")
            import traceback
            traceback.print_exc()
            raise


def merge_transcription_with_speakers(
    words: List[Dict],
    speaker_segments: List[Dict]
) -> List[Dict]:
    """
    Объединяет транскрипцию от Yandex с диаризацией от pyannote
    
    Args:
        words: Слова от Yandex: [{"word": "текст", "startTime": "1.5s", ...}, ...]
        speaker_segments: Сегменты от pyannote: [{"speaker": "SPEAKER_00", "start": 1.5, "end": 5.3}, ...]
    
    Returns:
        Слова с добавленным полем speaker: [{"word": "текст", "speaker": "SPEAKER_00", ...}, ...]
    """
    
    def parse_time(time_str: str) -> float:
        """Конвертирует '1.540s' -> 1.54"""
        if isinstance(time_str, (int, float)):
            return float(time_str)
        return float(str(time_str).rstrip('s'))
    
    # Добавляем speaker к каждому слову
    result = []
    
    for word in words:
        word_copy = word.copy()
        
        # Берём среднее время слова
        start_time = parse_time(word.get("startTime", "0s"))
        end_time = parse_time(word.get("endTime", "0s"))
        word_mid_time = (start_time + end_time) / 2
        
        # Ищем какой спикер говорил в это время
        speaker = None
        for segment in speaker_segments:
            if segment["start"] <= word_mid_time <= segment["end"]:
                speaker = segment["speaker"]
                break
        
        # Если не нашли - берём ближайший сегмент
        if speaker is None and speaker_segments:
            # Находим ближайший по времени
            closest = min(
                speaker_segments,
                key=lambda s: min(
                    abs(s["start"] - word_mid_time),
                    abs(s["end"] - word_mid_time)
                )
            )
            speaker = closest["speaker"]
        
        word_copy["speaker"] = speaker or "UNKNOWN"
        result.append(word_copy)
    
    return result


def format_with_speakers(words: List[Dict]) -> str:
    """
    Форматирует текст с разделением по спикерам
    
    Args:
        words: Слова с полем speaker
    
    Returns:
        Отформатированный текст с разделением спикеров
    """
    if not words:
        return ""
    
    lines = []
    current_speaker = None
    current_line = []
    
    for word in words:
        speaker = word.get("speaker", "UNKNOWN")
        word_text = word.get("word", "")
        
        if speaker != current_speaker:
            # Новый спикер - сохраняем предыдущую строку
            if current_line:
                lines.append(f"{current_speaker}: {' '.join(current_line)}")
            
            current_speaker = speaker
            current_line = [word_text]
        else:
            current_line.append(word_text)
    
    # Последняя строка
    if current_line:
        lines.append(f"{current_speaker}: {' '.join(current_line)}")
    
    return "\n\n".join(lines)
