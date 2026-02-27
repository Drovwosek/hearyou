#!/usr/bin/env python3
"""
Post-processing для исправления частых ошибок транскрипции
"""

from typing import Dict, List
import re


class TranscriptionCorrector:
    """Исправляет частые ошибки в транскрипции"""
    
    def __init__(self):
        # Словарь замен: {что_слышит_STT: что_должно_быть}
        self.corrections = {
            # Имена/никнеймы
            "иришка": "ИИшка",
            "мелишка": "милишка",
            "свита": "свит",
            
            # Можно добавить свои:
            # "артём": "Артём",
            # "спринт": "СПРИНТ",
        }
        
        # Фонетические замены (для похожих звуков)
        self.phonetic_patterns = [
            (r'\bиришка\b', 'ИИшка'),
            (r'\bмелишка\b', 'милишка'),
            (r'\bсвита\b', 'свит'),
        ]
    
    def correct(self, text: str, use_phonetic: bool = True) -> str:
        """
        Исправить текст
        
        Args:
            text: Исходный текст транскрипции
            use_phonetic: Использовать фонетические замены
            
        Returns:
            Исправленный текст
        """
        result = text
        
        # Простые замены (по словарю)
        words = result.split()
        corrected_words = []
        
        for word in words:
            # Убрать пунктуацию для сравнения
            clean_word = word.lower().strip('.,!?;:')
            
            if clean_word in self.corrections:
                # Заменить, сохранив пунктуацию
                replacement = self.corrections[clean_word]
                # Добавить обратно пунктуацию если была
                suffix = word[len(clean_word):]
                corrected_words.append(replacement + suffix)
            else:
                corrected_words.append(word)
        
        result = ' '.join(corrected_words)
        
        # Фонетические замены (regex)
        if use_phonetic:
            for pattern, replacement in self.phonetic_patterns:
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def add_correction(self, wrong: str, correct: str):
        """Добавить новую замену"""
        self.corrections[wrong.lower()] = correct
    
    def add_phonetic_pattern(self, pattern: str, replacement: str):
        """Добавить фонетический паттерн"""
        self.phonetic_patterns.append((pattern, replacement))


# Глобальный корректор (можно использовать везде)
corrector = TranscriptionCorrector()


def correct_transcription(text: str) -> str:
    """Быстрая функция для исправления"""
    return corrector.correct(text)


if __name__ == "__main__":
    # Тест
    test_text = "Аудиозапись до 1 минуты иришка мелишка свита"
    
    print("Исходный текст:")
    print(f"  {test_text}")
    print()
    
    corrected = correct_transcription(test_text)
    
    print("Исправленный текст:")
    print(f"  {corrected}")
    print()
    
    # Проверим что изменилось
    if test_text != corrected:
        print("✅ Исправления применены:")
        orig_words = test_text.split()
        corr_words = corrected.split()
        for i, (o, c) in enumerate(zip(orig_words, corr_words)):
            if o != c:
                print(f"   {i+1}. '{o}' → '{c}'")
    else:
        print("⚠️ Изменений нет")
