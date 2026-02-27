#!/usr/bin/env python3
"""
Загружает corrections из ispring_corrections.json
"""

import json
from pathlib import Path

def load_ispring_corrections():
    """Загрузить все исправления в плоский словарь"""
    corrections_file = Path(__file__).parent / "ispring_corrections.json"
    
    if not corrections_file.exists():
        return {}
    
    with open(corrections_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Объединить все категории в один словарь
    result = {}
    for category, words in data.items():
        if category.startswith('_'):  # Пропустить комментарии
            continue
        if isinstance(words, dict):
            result.update(words)
    
    return result

if __name__ == "__main__":
    corrections = load_ispring_corrections()
    print("Загружено исправлений:", len(corrections))
    for wrong, correct in corrections.items():
        print(f"  '{wrong}' → '{correct}'")
