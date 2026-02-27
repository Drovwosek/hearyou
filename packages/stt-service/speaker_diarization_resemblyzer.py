"""
Speaker Diarization с использованием Resemblyzer

Определяет "кто когда говорит" используя voice embeddings.
Используется вместе с Yandex STT для получения текста с разметкой спикеров.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeakerDiarizationResemblyzer:
    """
    Определение спикеров в аудио файле с помощью Resemblyzer
    """
    
    def __init__(self):
        """Инициализация"""
        self.encoder = None
        
    def _init_encoder(self):
        """Ленивая инициализация encoder (только когда нужно)"""
        if self.encoder is not None:
            return
        
        try:
            from resemblyzer import VoiceEncoder
            
            logger.info("Загружаю Resemblyzer voice encoder...")
            self.encoder = VoiceEncoder()
            logger.info("✅ Encoder загружен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Resemblyzer: {e}")
            raise
    
    def diarize(
        self, 
        audio_file: str, 
        num_speakers: Optional[int] = None,
        min_segment_duration: float = 1.0
    ) -> List[Dict]:
        """
        Определяет спикеров в аудио файле
        
        Args:
            audio_file: Путь к аудио файлу
            num_speakers: Ожидаемое количество спикеров (если None - автоопределение)
            min_segment_duration: Минимальная длительность сегмента в секундах
        
        Returns:
            Список сегментов: [{"speaker": "SPEAKER_00", "start": 1.5, "end": 5.3}, ...]
        """
        self._init_encoder()
        
        logger.info(f"Начинаю диаризацию: {audio_file}")
        
        try:
            from resemblyzer import preprocess_wav
            import librosa
            from sklearn.cluster import AgglomerativeClustering
            
            # Загружаем аудио
            wav, sr = librosa.load(audio_file, sr=16000, mono=True)
            logger.info(f"Аудио загружено: {len(wav)/sr:.2f} сек, {sr} Hz")
            
            # Разбиваем на сегменты по min_segment_duration
            segment_samples = int(min_segment_duration * sr)
            n_segments = len(wav) // segment_samples
            
            if n_segments < 2:
                logger.warning(f"Аудио слишком короткое ({len(wav)/sr:.2f}s), создаю 1 спикера")
                return [{
                    "speaker": "SPEAKER_00",
                    "start": 0.0,
                    "end": len(wav) / sr
                }]
            
            # Создаём embeddings для каждого сегмента
            embeddings = []
            segment_times = []
            
            for i in range(n_segments):
                start_sample = i * segment_samples
                end_sample = min((i + 1) * segment_samples, len(wav))
                segment = wav[start_sample:end_sample]
                
                if len(segment) < sr * 0.5:  # Пропускаем слишком короткие
                    continue
                
                # Получаем embedding
                embedding = self.encoder.embed_utterance(segment)
                embeddings.append(embedding)
                
                start_time = start_sample / sr
                end_time = end_sample / sr
                segment_times.append((start_time, end_time))
            
            embeddings = np.array(embeddings)
            logger.info(f"Создано {len(embeddings)} embeddings")
            
            # Определяем количество спикеров если не задано
            if num_speakers is None:
                # Эвристика: предполагаем 2-4 спикера для большинства случаев
                # Можно улучшить используя silhouette score
                num_speakers = min(2, len(embeddings) // 3)
                num_speakers = max(1, num_speakers)
            
            logger.info(f"Кластеризация на {num_speakers} спикеров...")
            
            # Кластеризуем embeddings
            if num_speakers == 1:
                labels = np.zeros(len(embeddings), dtype=int)
            else:
                clustering = AgglomerativeClustering(
                    n_clusters=num_speakers,
                    metric='cosine',
                    linkage='average'
                )
                labels = clustering.fit_predict(embeddings)
            
            # Формируем результат
            segments = []
            current_speaker = labels[0]
            current_start = segment_times[0][0]
            
            for i in range(len(labels)):
                speaker = labels[i]
                start, end = segment_times[i]
                
                if speaker != current_speaker:
                    # Закрываем предыдущий сегмент
                    segments.append({
                        "speaker": f"SPEAKER_{current_speaker:02d}",
                        "start": current_start,
                        "end": segment_times[i-1][1]
                    })
                    
                    # Начинаем новый сегмент
                    current_speaker = speaker
                    current_start = start
            
            # Последний сегмент
            segments.append({
                "speaker": f"SPEAKER_{current_speaker:02d}",
                "start": current_start,
                "end": segment_times[-1][1]
            })
            
            logger.info(f"✅ Найдено {len(set(labels))} спикеров, "
                       f"{len(segments)} сегментов")
            
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
    Объединяет транскрипцию от Yandex с диаризацией от Resemblyzer
    
    Args:
        words: Слова от Yandex: [{"word": "текст", "startTime": "1.5s", ...}, ...]
        speaker_segments: Сегменты от Resemblyzer: [{"speaker": "SPEAKER_00", "start": 1.5, "end": 5.3}, ...]
    
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
    
    return "\n".join(lines)


# Для тестирования
if __name__ == "__main__":
    diarizer = SpeakerDiarizationResemblyzer()
    
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
