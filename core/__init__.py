"""
HearYou Core - общие модули для всех сервисов

Этот модуль содержит переиспользуемый код для работы с Yandex SpeechKit STT:
- yandex_stt.py - клиент API
- filler_words_filter.py - фильтр слов-паразитов
- stt_corrections.py - пост-обработка и исправления
- transcribe.py - CLI для транскрибации

Импорт:
    from core.yandex_stt import YandexSTT
    from core.filler_words_filter import FillerWordsFilter
    from core.stt_corrections import TranscriptionCorrector
"""

from .yandex_stt import YandexSTT
from .filler_words_filter import FillerWordsFilter
from .stt_corrections import TranscriptionCorrector, correct_transcription

__all__ = [
    'YandexSTT',
    'FillerWordsFilter',
    'TranscriptionCorrector',
    'correct_transcription',
]

__version__ = '1.0.0'
