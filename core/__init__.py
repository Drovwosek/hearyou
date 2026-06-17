"""
HearYou Core - общие модули для всех сервисов

Этот модуль содержит переиспользуемый код для работы с STT:
- local_whisper_stt.py - локальный Whisper backend
- stt_provider.py - интерфейс STT-провайдера
- filler_words_filter.py - фильтр слов-паразитов
- stt_corrections.py - пост-обработка и исправления
- transcribe.py - CLI для транскрибации

Импорт:
    from core.local_whisper_stt import LocalWhisperSTT
    from core.filler_words_filter import FillerWordsFilter
    from core.stt_corrections import TranscriptionCorrector
"""

from .local_whisper_stt import LocalWhisperSTT, WhisperSettings
from .stt_provider import STTProvider
from .filler_words_filter import FillerWordsFilter
from .stt_corrections import TranscriptionCorrector, correct_transcription

__all__ = [
    'LocalWhisperSTT',
    'WhisperSettings',
    'STTProvider',
    'FillerWordsFilter',
    'TranscriptionCorrector',
    'correct_transcription',
]

__version__ = '1.0.0'
