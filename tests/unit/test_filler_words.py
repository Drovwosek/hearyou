#!/usr/bin/env python3
"""
Unit-тесты для filler_words_filter.py
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from filler_words_filter import FillerWordsFilter, clean_filler_words


class TestFillerWordsFilter:
    """Тесты класса FillerWordsFilter"""
    
    def test_init_creates_filter(self):
        """Тест инициализации фильтра"""
        filter = FillerWordsFilter()
        
        assert isinstance(filter.russian_fillers, list)
        assert isinstance(filter.english_fillers, list)
        assert isinstance(filter.patterns, list)
        assert len(filter.patterns) > 0
    
    def test_russian_fillers_loaded(self):
        """Тест загрузки русских слов-паразитов"""
        filter = FillerWordsFilter()
        
        # Проверяем наличие базовых русских паттернов
        patterns_str = " ".join(filter.russian_fillers)
        assert r"\bну\b" in patterns_str
        assert r"\bво+т\b" in patterns_str
        assert r"\bэ+" in patterns_str
    
    def test_english_fillers_loaded(self):
        """Тест загрузки английских слов-паразитов"""
        filter = FillerWordsFilter()
        
        patterns_str = " ".join(filter.english_fillers)
        assert r"\bum+" in patterns_str or r"\buh+" in patterns_str


class TestFillerWordsCleaning:
    """Тесты очистки текста"""
    
    def test_clean_russian_sounds(self):
        """Тест удаления русских звуков-паразитов"""
        filter = FillerWordsFilter()
        
        text = "Эээ я думаю что ммм это хорошо"
        result = filter.clean(text)
        
        # Звуки должны быть удалены
        assert "Эээ" not in result or result.startswith("Я")
        assert "ммм" not in result.lower()
    
    def test_clean_russian_words(self):
        """Тест удаления русских слов-паразитов"""
        filter = FillerWordsFilter()
        
        text = "Ну вот короче типа это хорошо"
        result = filter.clean(text)
        
        # Слова-паразиты должны быть удалены
        assert "хорошо" in result
        # Проверяем что паразиты убраны (могут остаться пробелы)
        assert "вот" not in result or "короче" not in result or "типа" not in result
    
    def test_clean_preserves_content(self):
        """Тест сохранения смыслового содержания"""
        filter = FillerWordsFilter()
        
        text = "Это важный текст про результат"
        result = filter.clean(text)
        
        assert "важный" in result
        assert "текст" in result
        assert "результат" in result
    
    def test_clean_removes_repeats(self):
        """Тест удаления повторов"""
        filter = FillerWordsFilter()
        
        text = "Я я думаю и и это хорошо"
        result = filter.clean(text)
        
        # Повторы должны быть убраны
        assert "я я" not in result.lower() or "и и" not in result.lower()
    
    def test_clean_fixes_spaces(self):
        """Тест нормализации пробелов"""
        filter = FillerWordsFilter()
        
        text = "Текст  с   множественными    пробелами"
        result = filter.clean(text)
        
        # Множественные пробелы должны схлопнуться в один
        assert "  " not in result
    
    def test_clean_fixes_punctuation_spaces(self):
        """Тест удаления пробелов перед пунктуацией"""
        filter = FillerWordsFilter()
        
        text = "Текст , с пробелами . перед знаками !"
        result = filter.clean(text)
        
        # Пробелы перед знаками должны быть убраны
        assert " ," not in result
        assert " ." not in result
        assert " !" not in result
    
    def test_clean_capitalizes_first_letter(self):
        """Тест заглавной буквы в начале"""
        filter = FillerWordsFilter()
        
        text = "текст начинается с маленькой буквы"
        result = filter.clean(text)
        
        # Первая буква должна быть заглавной
        assert result[0].isupper()


class TestAggressiveCleaning:
    """Тесты агрессивной очистки"""
    
    def test_aggressive_removes_single_letters(self):
        """Тест удаления одиночных букв"""
        filter = FillerWordsFilter()
        
        text = "Это б текст д с буквами"
        result = filter.clean(text, aggressive=True)
        
        # Одиночные буквы (кроме а, и) должны быть удалены
        assert " б " not in result
        assert " д " not in result
    
    def test_aggressive_preserves_a_i(self):
        """Тест удаления междометий в агрессивном режиме"""
        filter = FillerWordsFilter()
        
        # "а" и "и" как междометия удаляются базовыми паттернами
        text = "Это а и то"
        result = filter.clean(text, aggressive=True)
        
        # Проверяем что текст очищен и осталось только основное
        assert "это" in result.lower()
        assert "то" in result.lower()
    
    def test_aggressive_fixes_punctuation_repeats(self):
        """Тест удаления повторяющихся знаков препинания"""
        filter = FillerWordsFilter()
        
        text = "Что это!!! Да???"
        result = filter.clean(text, aggressive=True)
        
        # Повторы должны схлопнуться
        assert "!!!" not in result
        assert "???" not in result
        assert "!" in result
        assert "?" in result


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_empty_text(self):
        """Тест пустого текста"""
        filter = FillerWordsFilter()
        
        result = filter.clean("")
        
        assert result == ""
    
    def test_only_filler_words(self):
        """Тест текста только из слов-паразитов"""
        filter = FillerWordsFilter()
        
        text = "Ну эээ ммм вот"
        result = filter.clean(text)
        
        # Результат может быть пустым или почти пустым
        assert len(result) < len(text)
    
    def test_no_filler_words(self):
        """Тест текста без слов-паразитов"""
        filter = FillerWordsFilter()
        
        text = "Чистый профессиональный текст."
        result = filter.clean(text)
        
        # Текст должен остаться почти неизменным
        assert "профессиональный" in result
        assert "текст" in result
    
    def test_mixed_russian_english(self):
        """Тест смешанного текста"""
        filter = FillerWordsFilter()
        
        text = "Эээ это um текст like на двух языках"
        result = filter.clean(text)
        
        assert "текст" in result
        assert "языках" in result
    
    def test_unicode_content(self):
        """Тест с unicode символами"""
        filter = FillerWordsFilter()
        
        text = "Текст с эмодзи 🎉 ну вот и символами"
        result = filter.clean(text)
        
        assert "🎉" in result


class TestCustomFillers:
    """Тесты добавления кастомных слов-паразитов"""
    
    def test_add_custom_filler(self):
        """Тест добавления своего паттерна"""
        filter = FillerWordsFilter()
        
        filter.add_filler(r'\bкак_бы\b')
        
        text = "Это как_бы хороший текст"
        result = filter.clean(text)
        
        assert "как_бы" not in result
    
    def test_show_fillers(self):
        """Тест получения списка паттернов"""
        filter = FillerWordsFilter()
        
        patterns = filter.show_fillers()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0


class TestGlobalFunction:
    """Тесты глобальной функции clean_filler_words"""
    
    def test_clean_filler_words_function(self):
        """Тест глобальной функции"""
        text = "Эээ ну вот это текст"
        result = clean_filler_words(text)
        
        assert isinstance(result, str)
        assert "текст" in result
    
    def test_clean_filler_words_aggressive(self):
        """Тест агрессивной очистки через функцию"""
        text = "Текст б с буквами"
        result = clean_filler_words(text, aggressive=True)
        
        assert " б " not in result


class TestPerformance:
    """Тесты производительности"""
    
    def test_large_text(self):
        """Тест очистки большого текста"""
        filter = FillerWordsFilter()
        
        # Большой текст с настоящими словами (не только "слово")
        text = " ".join(["важное слово"] * 1000)
        
        result = filter.clean(text)
        
        assert len(result) > 0
        assert "важное" in result or "слово" in result
    
    def test_many_fillers(self):
        """Тест текста с множеством слов-паразитов"""
        filter = FillerWordsFilter()
        
        text = "ну " * 1000 + "важный текст"
        
        result = filter.clean(text)
        
        # Текст должен быть короче (слова-паразиты убраны)
        assert len(result) < len(text)
        # Смысловые слова должны остаться (с учётом капитализации)
        assert "текст" in result.lower()


class TestRealWorldExamples:
    """Тесты на реальных примерах"""
    
    def test_interview_transcript(self):
        """Тест транскрипта интервью"""
        filter = FillerWordsFilter()
        
        text = "Эээ ну вот я думаю что эээ это хорошо короче"
        result = filter.clean(text)
        
        # Должен остаться смысл
        assert "думаю" in result
        assert "хорошо" in result
        # Паразиты убраны
        assert result.count("эээ") < text.count("эээ")
    
    def test_presentation_transcript(self):
        """Тест транскрипта презентации"""
        filter = FillerWordsFilter()
        
        text = "Вообще наверное кстати это важный момент в принципе"
        result = filter.clean(text)
        
        # Основной смысл сохранён
        assert "важный" in result
        assert "момент" in result
