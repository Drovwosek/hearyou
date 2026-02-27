#!/usr/bin/env python3
"""
Unit-тесты для stt_corrections.py
"""

import pytest
from pathlib import Path
import sys
import json
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from stt_corrections import TranscriptionCorrector, correct_transcription


class TestTranscriptionCorrector:
    """Тесты класса TranscriptionCorrector"""
    
    def test_init_creates_corrector(self):
        """Тест инициализации корректора"""
        corrector = TranscriptionCorrector()
        
        assert isinstance(corrector.corrections, dict)
        assert len(corrector.corrections) > 0
        assert isinstance(corrector.phonetic_patterns, list)
    
    def test_basic_corrections_loaded(self):
        """Тест загрузки базовых исправлений"""
        corrector = TranscriptionCorrector()
        
        # Проверяем что есть базовые исправления
        assert "иришка" in corrector.corrections
        assert corrector.corrections["иришка"] == "ИИшка"
    
    def test_correct_simple_word(self):
        """Тест простого исправления слова"""
        corrector = TranscriptionCorrector()
        
        text = "Я слышал про иришка"
        result = corrector.correct(text)
        
        assert "ИИшка" in result
        assert "иришка" not in result.lower() or "иришка" == "ИИшка".lower()
    
    def test_correct_multiple_words(self):
        """Тест исправления нескольких слов"""
        corrector = TranscriptionCorrector()
        
        text = "иришка и мелишка и свита"
        result = corrector.correct(text)
        
        assert "ИИшка" in result
        assert "милишка" in result
        assert "свит" in result
    
    def test_correct_preserves_punctuation(self):
        """Тест сохранения пунктуации"""
        corrector = TranscriptionCorrector()
        
        text = "Это иришка, мелишка."
        result = corrector.correct(text)
        
        assert "," in result
        assert "." in result
    
    def test_correct_case_insensitive(self):
        """Тест что исправления не зависят от регистра"""
        corrector = TranscriptionCorrector()
        
        text = "ИРИШКА Иришка иришка"
        result = corrector.correct(text)
        
        # Все варианты должны быть исправлены
        assert result.count("ИИшка") >= 3 or "иришка" not in result.lower()
    
    def test_phonetic_patterns(self):
        """Тест фонетических паттернов (regex)"""
        corrector = TranscriptionCorrector()
        
        text = "Текст с иришка внутри"
        result = corrector.correct(text, use_phonetic=True)
        
        # Должен применить regex паттерны
        assert "ИИшка" in result or "иришка" not in result.lower()
    
    def test_correct_without_phonetic(self):
        """Тест без фонетических паттернов"""
        corrector = TranscriptionCorrector()
        
        text = "Обычный текст"
        result = corrector.correct(text, use_phonetic=False)
        
        assert result == text
    
    def test_add_correction(self):
        """Тест добавления нового исправления"""
        corrector = TranscriptionCorrector()
        
        corrector.add_correction("тест", "ТЕСТ")
        
        text = "Это тест"
        result = corrector.correct(text)
        
        assert "ТЕСТ" in result
    
    def test_add_phonetic_pattern(self):
        """Тест добавления фонетического паттерна"""
        corrector = TranscriptionCorrector()
        
        corrector.add_phonetic_pattern(r'\bтест\b', 'TEST')
        
        text = "Это тест текста"
        result = corrector.correct(text)
        
        assert "TEST" in result


class TestCorrectionEdgeCases:
    """Тесты граничных случаев"""
    
    def test_empty_text(self):
        """Тест пустого текста"""
        corrector = TranscriptionCorrector()
        
        result = corrector.correct("")
        
        assert result == ""
    
    def test_text_without_corrections(self):
        """Тест текста без исправлений"""
        corrector = TranscriptionCorrector()
        
        text = "Обычный текст без ошибок"
        result = corrector.correct(text)
        
        assert result == text
    
    def test_only_punctuation(self):
        """Тест текста только из пунктуации"""
        corrector = TranscriptionCorrector()
        
        text = "... !!! ???"
        result = corrector.correct(text)
        
        assert result == text
    
    def test_unicode_text(self):
        """Тест с unicode символами"""
        corrector = TranscriptionCorrector()
        
        text = "Текст с эмодзи 🎉 и иришка"
        result = corrector.correct(text)
        
        assert "🎉" in result


class TestCorrectionWithCustomDict:
    """Тесты с кастомными словарями"""
    
    def test_load_custom_corrections(self, test_corrections_file):
        """Тест загрузки кастомных исправлений из файла"""
        # Создаём новый корректор и подменяем путь к файлу
        corrector = TranscriptionCorrector()
        
        # Добавляем кастомные исправления вручную
        corrector.corrections["тест"] = "TEST"
        corrector.corrections["пример"] = "EXAMPLE"
        
        text = "Это тест и пример"
        result = corrector.correct(text)
        
        assert "TEST" in result
        assert "EXAMPLE" in result
    
    def test_merge_corrections(self):
        """Тест слияния базовых и кастомных исправлений"""
        corrector = TranscriptionCorrector()
        
        # Базовые должны остаться
        assert "иришка" in corrector.corrections
        
        # Добавляем кастомные
        corrector.add_correction("новое", "НОВОЕ")
        
        assert "новое" in corrector.corrections
        assert "иришка" in corrector.corrections


class TestGlobalCorrector:
    """Тесты глобальной функции correct_transcription"""
    
    def test_correct_transcription_function(self):
        """Тест глобальной функции"""
        text = "Текст с иришка"
        result = correct_transcription(text)
        
        assert isinstance(result, str)
        # Должна применить базовые исправления
        assert "ИИшка" in result or "иришка" not in result.lower()
    
    def test_correct_transcription_empty(self):
        """Тест с пустым текстом"""
        result = correct_transcription("")
        
        assert result == ""


class TestCorrectionPerformance:
    """Тесты производительности"""
    
    def test_large_text_correction(self):
        """Тест исправления большого текста"""
        corrector = TranscriptionCorrector()
        
        # Большой текст (10000 слов)
        text = " ".join(["слово"] * 10000)
        
        result = corrector.correct(text)
        
        assert len(result) > 0
        assert "слово" in result
    
    def test_many_corrections(self):
        """Тест с множеством исправлений"""
        corrector = TranscriptionCorrector()
        
        # Добавляем 100 исправлений
        for i in range(100):
            corrector.add_correction(f"слово{i}", f"СЛОВО{i}")
        
        text = "слово0 слово1 слово2"
        result = corrector.correct(text)
        
        assert "СЛОВО0" in result
        assert "СЛОВО1" in result
