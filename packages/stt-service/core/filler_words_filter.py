#!/usr/bin/env python3
"""
Фильтр слов-паразитов и лишних звуков
"""

import re
from typing import List


class FillerWordsFilter:
    """Удаляет слова-паразиты из транскрипции"""
    
    def __init__(self):
        # Русские слова-паразиты
        self.russian_fillers = [
            # Лишние звуки (растянутые гласные)
            r'\bэ+\b', r'\bэ+м+\b', r'\bм+\b', r'\bм+м+\b',
            r'\bа+\b', r'\bа+м+\b', r'\bо+\b', r'\bу+\b', r'\bу+м+\b',
            r'\bы+\b', r'\bи+\b',
            
            # Повторяющиеся слоги (а-а-а, э-э-э)
            r'\b([эмаоуы])-\1(-\1)*\b',
            
            # Междометия и звуки
            r'\bбе\b', r'\bме\b', r'\bэм\b', r'\bам\b', 
            r'\bхм+\b', r'\bгм+\b', r'\bкхм+\b', r'\bм-да\b',
            
            # Слова-паразиты
            r'\bну\b', r'\bво+т\b', r'\bтипа\b', r'\bкак бы\b',
            r'\bв общем\b', r'\bв общем-то\b', r'\bв принципе\b', r'\bблин\b',
            r'\bэто самое\b', r'\bкороче\b', r'\bкароч\b', r'\bпросто\b',
            r'\bдопустим\b', r'\bнапример\b(?!\s+\w)',  # "например" без продолжения
            r'\bто есть\b', r'\bвообще\b', r'\bваще\b', r'\bнаверное\b',
            r'\bкстати\b', r'\bзнаешь\b', r'\bпонимаешь\b',
            r'\bвидишь ли\b', r'\bсобственно\b', r'\bзначит\b',
            r'\bтак сказать\b', r'\bну вот\b', r'\bвот так\b', r'\bпрям\b',
            r'\bбуквально\b', r'\bреально\b', r'\bчё\b', r'\bчо\b',
            
            # Повторы
            r'\b(\w+)\s+\1\b',  # "я я", "и и"
        ]
        
        # Английские слова-паразиты
        self.english_fillers = [
            r'\bum+\b', r'\buh+\b', r'\ber+\b', r'\bah+\b',
            r'\blike\b', r'\byou know\b', r'\bI mean\b',
            r'\bactually\b', r'\bbasically\b', r'\bliterally\b',
            r'\bkinda\b', r'\bsorta\b',
        ]
        
        # Все паттерны
        self.patterns = self.russian_fillers + self.english_fillers
        
    def clean(self, text: str, aggressive: bool = False) -> str:
        """
        Очистить текст от слов-паразитов
        
        Args:
            text: Исходный текст
            aggressive: Агрессивная очистка (удаляет больше слов)
            
        Returns:
            Очищенный текст
        """
        result = text
        
        # Базовые паттерны
        for pattern in self.patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        # Агрессивная очистка
        if aggressive:
            # Убрать одиночные буквы (кроме "а" и "и")
            result = re.sub(r'\b(?![аиАИ])[а-яА-Яa-zA-Z]\b', '', result)
            
            # Убрать повторяющиеся знаки препинания
            result = re.sub(r'([,.!?])\1+', r'\1', result)
        
        # Очистить лишние пробелы (НО СОХРАНИТЬ \n\n для разделения спикеров!)
        # Разбиваем по \n\n, чистим каждый блок отдельно, соединяем обратно
        blocks = result.split('\n\n')
        cleaned_blocks = []
        
        for block in blocks:
            # Убираем лишние пробелы внутри блока
            block = re.sub(r'[ \t]+', ' ', block)  # Только горизонтальные пробелы
            block = re.sub(r'\n+', '\n', block)    # Убираем множественные \n (но не \n\n между блоками!)
            block = re.sub(r'\s+([,.!?])', r'\1', block)
            block = block.strip()
            if block:  # Пропускаем пустые блоки
                cleaned_blocks.append(block)
        
        result = '\n\n'.join(cleaned_blocks)
        
        # Заглавная буква в начале
        if result and result[0].islower():
            result = result[0].upper() + result[1:]
        
        return result
    
    def add_filler(self, pattern: str):
        """Добавить свой паттерн слова-паразита"""
        self.patterns.append(pattern)
    
    def show_fillers(self) -> List[str]:
        """Показать все паттерны слов-паразитов"""
        return self.patterns


# Глобальный фильтр
filler_filter = FillerWordsFilter()


def clean_filler_words(text: str, aggressive: bool = False) -> str:
    """Быстрая функция для очистки"""
    return filler_filter.clean(text, aggressive)


if __name__ == "__main__":
    # Тесты
    test_cases = [
        "Эээ ну вот я думаю что эээ это хорошо",
        "Ммм короче типа я не знаю",
        "Это самое ну в общем в принципе",
        "Я я думаю что э это хорошо",
        "Вообще наверное кстати блин",
    ]
    
    filter = FillerWordsFilter()
    
    print("🧹 Тестирование фильтра слов-паразитов\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. Исходный текст:")
        print(f"   {test}")
        
        cleaned = filter.clean(test)
        print(f"   → Очищенный:")
        print(f"   {cleaned}")
        
        cleaned_aggressive = filter.clean(test, aggressive=True)
        if cleaned != cleaned_aggressive:
            print(f"   → Агрессивная очистка:")
            print(f"   {cleaned_aggressive}")
        
        print()
