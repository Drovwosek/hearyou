#!/usr/bin/env python3
"""
Post-processing для исправления частых ошибок транскрипции
"""

from typing import Dict, List
import re
import json
from pathlib import Path


class TranscriptionCorrector:
    """Исправляет частые ошибки в транскрипции"""
    
    def __init__(self):
        # Словарь замен: {что_слышит_STT: что_должно_быть}
        self.corrections = {
            # AI-термины
            "иришка": "ИИшка",
            "иишка": "ИИшка",
            "мелишка": "милишка",
            "свита": "свит",
            
            # Продукты iSpring/СПРИНТ (общие)
            "испринг": "iSpring",
            "ай спринг": "iSpring",
            "спринт": "СПРИНТ",
            "егэ": "ЕГЭ",
            "огэ": "ОГЭ",
            
            # Технические термины
            "лмс": "LMS",
            "апи": "API",
            "айпи": "IP",
            "эс кю эль": "SQL",
            "ви пи эн": "VPN",
            
            # Имена людей (примеры)
            "артём": "Артём",
            "артем": "Артём",
        }
        
        # Загрузить дополнительные исправления из JSON
        self._load_ispring_corrections()
        
        # Фонетические замены (для похожих звуков)
        self.phonetic_patterns = [
            # AI термины
            (r'\bи+ришка\b', 'ИИшка'),
            (r'\bи+шка\b', 'ИИшка'),
            (r'\bмелишка\b', 'милишка'),
            (r'\bсвита\b', 'свит'),
            
            # iSpring варианты
            (r'\bи+\s*спринг\b', 'iSpring'),
            (r'\bай\s*спринг\b', 'iSpring'),
            
            # Аббревиатуры (разделённые пробелами)
            (r'\bл\s*м\s*с\b', 'LMS'),
            (r'\bа\s*п\s*и\b', 'API'),
        ]
    
    def _load_ispring_corrections(self):
        """Загрузить дополнительные исправления из ispring_corrections.json"""
        corrections_file = Path(__file__).parent / "ispring_corrections.json"
        
        if not corrections_file.exists():
            return
        
        try:
            with open(corrections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Объединить все категории
            count = 0
            for category, words in data.items():
                if category.startswith('_'):  # Пропустить комментарии
                    continue
                if isinstance(words, dict):
                    self.corrections.update(words)
                    count += len(words)
            
            print(f"✅ Загружено {count} дополнительных исправлений из ispring_corrections.json")
        except Exception as e:
            print(f"⚠️  Не удалось загрузить ispring_corrections.json: {e}")
    
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
