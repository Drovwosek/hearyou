#!/usr/bin/env python3
"""
Полный пайплайн улучшения качества транскрипции
"""

try:
    from .filler_words_filter import FillerWordsFilter
    from .stt_corrections import TranscriptionCorrector
except ImportError:
    # Fallback для прямого запуска
    from filler_words_filter import FillerWordsFilter
    from stt_corrections import TranscriptionCorrector


class TranscriptionCleaner:
    """
    Полная очистка и улучшение качества транскрипции
    
    Пайплайн:
    1. Удаление лишних звуков (эээ, ммм, бе, ме)
    2. Удаление слов-паразитов (вот, типа, короче)
    3. Исправление артефактов транскрипции (иишка → ИИшка)
    """
    
    def __init__(self):
        self.filler_filter = FillerWordsFilter()
        self.corrector = TranscriptionCorrector()
    
    def clean(
        self, 
        text: str,
        remove_filler_sounds: bool = True,
        remove_filler_words: bool = False,
        fix_artifacts: bool = True,
    ) -> str:
        """
        Полная очистка текста
        
        Args:
            text: Исходный текст транскрипции
            remove_filler_sounds: Удалить лишние звуки (эээ, ммм)
            remove_filler_words: Удалить слова-паразиты (вот, типа)
            fix_artifacts: Исправить артефакты (иишка → ИИшка)
            
        Returns:
            Очищенный текст
        """
        result = text
        
        # Шаг 1: Удаление лишних звуков и слов-паразитов
        if remove_filler_sounds or remove_filler_words:
            result = self.filler_filter.clean(
                result, 
                aggressive=remove_filler_words
            )
        
        # Шаг 2: Исправление артефактов транскрипции
        if fix_artifacts:
            result = self.corrector.correct(result)
        
        return result
    
    def add_custom_correction(self, wrong: str, correct: str):
        """Добавить свою коррекцию"""
        self.corrector.add_correction(wrong, correct)
    
    def add_filler(self, pattern: str):
        """Добавить своё слово-паразит"""
        self.filler_filter.add_filler(pattern)


# Глобальный cleaner
cleaner = TranscriptionCleaner()


def clean_transcription(
    text: str,
    remove_filler_sounds: bool = True,
    remove_filler_words: bool = False,
    fix_artifacts: bool = True,
) -> str:
    """
    Быстрая функция для очистки транскрипции
    
    Рекомендуемые настройки:
    - Для интервью: all True
    - Для лекций: filler_sounds=True, artifacts=True
    - Для casual разговоров: только artifacts=True
    """
    return cleaner.clean(
        text,
        remove_filler_sounds=remove_filler_sounds,
        remove_filler_words=remove_filler_words,
        fix_artifacts=fix_artifacts,
    )


if __name__ == "__main__":
    # Тесты
    print("🧹 Полный пайплайн очистки транскрипции\n")
    
    test_cases = [
        {
            "text": "Эээ, ну вот, я хотел рассказать про иишка и испринг",
            "label": "AI термины + звуки",
        },
        {
            "text": "Ммм, короче, мы используем лмс и апи для спринт",
            "label": "Технические термины",
        },
        {
            "text": "А-а-а, типа это самое, егэ и огэ ваще сложные",
            "label": "ЕГЭ/ОГЭ + паразиты",
        },
        {
            "text": "Бе ме эм, в общем-то иришка это прям круто вот",
            "label": "Лишние звуки + имена",
        },
    ]
    
    for case in test_cases:
        print(f"📝 {case['label']}")
        print(f"   Исходный:       {case['text']}")
        
        # Разные уровни очистки
        light = clean_transcription(
            case['text'],
            remove_filler_sounds=True,
            remove_filler_words=False,
            fix_artifacts=True,
        )
        
        full = clean_transcription(
            case['text'],
            remove_filler_sounds=True,
            remove_filler_words=True,
            fix_artifacts=True,
        )
        
        print(f"   Лёгкая очистка: {light}")
        print(f"   Полная очистка: {full}")
        print()
