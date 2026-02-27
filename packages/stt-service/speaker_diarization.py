"""
Speaker Diarization с использованием pyannote.audio

Определяет "кто когда говорит" без транскрипции текста.
Используется вместе с Yandex STT для получения текста с разметкой спикеров.
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeakerDiarization:
    """
    Определение спикеров в аудио файле с помощью pyannote.audio
    """
    
    def __init__(self, hf_token: Optional[str] = None):
        """
        Args:
            hf_token: HuggingFace токен для скачивания моделей (опционально)
        """
        self.hf_token = hf_token or os.getenv('HUGGINGFACE_TOKEN')
        self.pipeline = None
        
    def _init_pipeline(self):
        """Ленивая инициализация pipeline (только когда нужно)"""
        if self.pipeline is not None:
            return
        
        try:
            from pyannote.audio import Pipeline
            
            logger.info("Загружаю pyannote speaker-diarization pipeline...")
            
            # Используем speaker-diarization модель
            # Для pyannote 3.0.x используется use_auth_token (старая версия huggingface_hub)
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.0",
                use_auth_token=self.hf_token
            )
            
            logger.info("✅ Pipeline загружен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации pyannote pipeline: {e}")
            raise
    
    def diarize(self, audio_file: str, num_speakers: Optional[int] = None) -> List[Dict]:
        """
        Определяет спикеров в аудио файле
        
        Args:
            audio_file: Путь к аудио файлу
            num_speakers: Ожидаемое количество спикеров (опционально)
        
        Returns:
            Список сегментов: [{"speaker": "SPEAKER_00", "start": 1.5, "end": 5.3}, ...]
        """
        self._init_pipeline()
        
        logger.info(f"Начинаю диаризацию: {audio_file}")
        
        try:
            # Запускаем диаризацию
            diarization_kwargs = {}
            if num_speakers:
                diarization_kwargs['num_speakers'] = num_speakers
            
            diarization = self.pipeline(audio_file, **diarization_kwargs)
            
            # Конвертируем в удобный формат
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,
                    "start": turn.start,
                    "end": turn.end
                })
            
            logger.info(f"✅ Найдено {len(set(s['speaker'] for s in segments))} спикеров, "
                       f"{len(segments)} сегментов")
            
            return segments
            
        except Exception as e:
            logger.error(f"Ошибка диаризации: {e}")
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
        return float(time_str.rstrip('s'))
    
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
    
    return "\n".join(lines)


# Для тестирования
if __name__ == "__main__":
    # Пример использования
    diarizer = SpeakerDiarization()
    
    # Тестовый файл
    test_file = "/app/test_audio.mp3"
    
    if os.path.exists(test_file):
        segments = diarizer.diarize(test_file)
        
        print(f"Найдено спикеров: {len(set(s['speaker'] for s in segments))}")
        print("\nПервые 5 сегментов:")
        for seg in segments[:5]:
            print(f"  {seg['speaker']}: {seg['start']:.2f}s - {seg['end']:.2f}s")
    else:
        print(f"Тестовый файл не найден: {test_file}")
