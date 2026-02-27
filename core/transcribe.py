#!/usr/bin/env python3
"""
CLI утилита для транскрибации через Yandex SpeechKit
Использование: python3 transcribe.py audio.mp3
"""

import sys
import argparse
import json
from pathlib import Path
from yandex_stt import YandexSTT
from stt_corrections import TranscriptionCorrector
from filler_words_filter import FillerWordsFilter


def main():
    parser = argparse.ArgumentParser(
        description="Транскрибация аудио через Yandex SpeechKit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Простая транскрибация
  python3 transcribe.py audio.mp3
  
  # С указанием языка
  python3 transcribe.py audio.mp3 --lang en-US
  
  # Сохранить в файл
  python3 transcribe.py audio.mp3 -o output.txt
  
  # Без пунктуации
  python3 transcribe.py audio.mp3 --no-punctuation
        """
    )
    
    parser.add_argument('audio_file', help='Путь к аудио файлу')
    parser.add_argument('-l', '--lang', default='ru-RU', 
                        help='Язык (ru-RU, en-US, etc). По умолчанию: ru-RU')
    parser.add_argument('-o', '--output', help='Сохранить результат в файл')
    parser.add_argument('--no-punctuation', action='store_true',
                        help='Отключить автоматическую пунктуацию')
    parser.add_argument('--profanity-filter', action='store_true',
                        help='Включить фильтр мата')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Подробный вывод (включая метаданные)')
    parser.add_argument('--corrections', metavar='FILE',
                        help='JSON файл с исправлениями ({\"неправильно\": \"правильно\"})')
    parser.add_argument('--no-corrections', action='store_true',
                        help='Отключить автоматические исправления')
    parser.add_argument('--clean', action='store_true',
                        help='Убрать слова-паразиты ("эээ", "ммм", "ну" и т.д.)')
    parser.add_argument('--literature', action='store_true',
                        help='Литературный текст (Yandex убирает паразиты)')
    
    args = parser.parse_args()
    
    # Проверить файл
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ Файл не найден: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # Проверить размер (ограничение 1 МБ)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 1:
        print(f"⚠️  Предупреждение: размер файла {file_size_mb:.2f} МБ", file=sys.stderr)
        print(f"   Синхронный API поддерживает до 1 МБ", file=sys.stderr)
        print(f"   Для больших файлов используй async API", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"📁 Файл: {audio_path.name}")
        print(f"📊 Размер: {file_size_mb:.2f} МБ")
        print(f"🌍 Язык: {args.lang}")
        print()
    
    # Инициализация
    try:
        stt = YandexSTT()
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}", file=sys.stderr)
        print(f"   Проверь файл .env.yandex", file=sys.stderr)
        sys.exit(1)
    
    # Конвертация в OGG Opus если нужно
    audio_to_send = str(audio_path)
    temp_file = None
    
    # Определить формат
    import subprocess
    file_info = subprocess.check_output(['file', str(audio_path)]).decode()
    
    # Если не OGG Opus - конвертируем
    if 'Ogg data' not in file_info or 'Opus' not in file_info:
        if args.verbose:
            print("🔄 Конвертация в OGG Opus для лучшей совместимости...")
        
        temp_file = audio_path.parent / f".tmp_{audio_path.stem}.ogg"
        
        try:
            subprocess.run([
                'ffmpeg', '-i', str(audio_path),
                '-c:a', 'libopus',
                '-b:a', '48k',
                '-ar', '48000',
                '-ac', '1',
                str(temp_file),
                '-y'
            ], check=True, capture_output=True)
            
            audio_to_send = str(temp_file)
            
            if args.verbose:
                print("   ✅ Конвертация завершена")
        except Exception as e:
            if args.verbose:
                print(f"   ⚠️ Конвертация не удалась, отправляю оригинал")
            # Fallback to original
    
    # Транскрибация
    if args.verbose:
        print("🎤 Транскрибация...")
    
    try:
        result = stt.transcribe_sync(
            audio_to_send,
            language=args.lang,
            format='oggopus',
            punctuation=not args.no_punctuation,
            profanity_filter=args.profanity_filter,
            literature_text=args.literature,
        )
        
        if args.verbose:
            print("✅ Готово!")
            print()
            print("📋 Полный результат:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print()
            print("📝 Текст:")
        
        # Извлечь текст
        text = result.get('result', '')
        
        if not text:
            print("⚠️  Ничего не распознано", file=sys.stderr)
            sys.exit(0)
        
        # Очистка слов-паразитов
        if args.clean:
            filler_filter = FillerWordsFilter()
            original_text = text
            text = filler_filter.clean(text, aggressive=False)
            
            if args.verbose and original_text != text:
                print()
                print("🧹 Убраны слова-паразиты:")
                print(f"   Было: {original_text}")
                print(f"   Стало: {text}")
                print()
        
        # Исправления
        if not args.no_corrections:
            corrector = TranscriptionCorrector()
            
            # Загрузить кастомные исправления если указаны
            if args.corrections:
                corrections_file = Path(args.corrections)
                if corrections_file.exists():
                    with open(corrections_file, 'r', encoding='utf-8') as f:
                        custom_corrections = json.load(f)
                        for wrong, correct in custom_corrections.items():
                            corrector.add_correction(wrong, correct)
                    
                    if args.verbose:
                        print(f"   ✅ Загружено {len(custom_corrections)} исправлений")
            
            # Применить исправления
            original_text = text
            text = corrector.correct(text)
            
            if args.verbose and original_text != text:
                print()
                print("🔧 Применены исправления:")
                orig_words = original_text.split()
                corr_words = text.split()
                for i, (o, c) in enumerate(zip(orig_words, corr_words)):
                    if o != c:
                        print(f"   '{o}' → '{c}'")
                print()
        
        # Вывод
        print(text)
        
        # Сохранение в файл
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(text, encoding='utf-8')
            if args.verbose:
                print()
                print(f"💾 Сохранено в: {output_path}")
        
    except Exception as e:
        print(f"❌ Ошибка транскрибации: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Удалить временный файл
        if temp_file and temp_file.exists():
            temp_file.unlink()


if __name__ == "__main__":
    main()
