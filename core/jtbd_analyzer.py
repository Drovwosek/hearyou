#!/usr/bin/env python3
"""
JTBD (Jobs To Be Done) Analyzer для HearYou
Автоматический анализ транскрипций через Claude Sonnet 4.5
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class JTBDAnalyzer:
    """
    Анализатор транскрипций по фреймворку Jobs To Be Done
    
    JTBD Framework:
    - Job: основная работа/цель, которую хочет выполнить пользователь
    - Pains: боли, проблемы, препятствия на пути к цели
    - Gains: выгоды, желаемые результаты, что улучшится
    - Context: контекст, ситуация, условия использования
    - Triggers: триггеры, что запускает потребность в "работе"
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Инициализация анализатора
        
        Args:
            api_key: API ключ Anthropic (если None, берётся из env)
            model: модель Claude для использования
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY не найден. Установите переменную окружения "
                "или передайте api_key в конструктор."
            )
        
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        
        logger.info(f"JTBDAnalyzer initialized with model: {model}")
    
    def _build_prompt(self, text: str) -> str:
        """
        Построение промпта для Claude
        
        Args:
            text: текст транскрипции для анализа
            
        Returns:
            Готовый промпт для Claude
        """
        return f"""Проанализируй следующую транскрипцию по фреймворку Jobs To Be Done (JTBD).

КОНТЕКСТ:
Это транскрипция аудио/видео записи. Твоя задача — извлечь элементы JTBD для понимания потребностей пользователя.

ФРЕЙМВОРК JTBD:
1. **Jobs** (Работы) — основные цели и задачи, которые пользователь хочет выполнить
   - Функциональные работы (что нужно сделать)
   - Эмоциональные работы (как хочется себя чувствовать)
   - Социальные работы (как хочется выглядеть в глазах других)

2. **Pains** (Боли) — проблемы, препятствия, риски
   - Нежелательные результаты
   - Проблемы и сложности
   - Риски и страхи
   - Барьеры к достижению цели

3. **Gains** (Выгоды) — желаемые результаты, улучшения
   - Требуемые выгоды (минимум, без которого не обойтись)
   - Ожидаемые выгоды (стандартные ожидания)
   - Желаемые выгоды (приятные сюрпризы)
   - Неожиданные выгоды (превышение ожиданий)

4. **Context** (Контекст) — ситуации и условия
   - Когда возникает потребность
   - Где происходит
   - С кем взаимодействует
   - Какие ограничения существуют

5. **Triggers** (Триггеры) — что запускает работу
   - События, запускающие потребность
   - Моменты переключения (switching moments)
   - Проблемы, требующие решения прямо сейчас

ИНСТРУКЦИИ:
- Извлеки все значимые элементы из каждой категории
- Цитируй конкретные фразы из транскрипции (в кавычках)
- Укажи уровень уверенности (confidence): high/medium/low
- Если какая-то категория не представлена в тексте — верни пустой массив
- Используй оригинальные формулировки из текста, минимизируй интерпретацию
- Один элемент = одна чёткая мысль (не объединяй разные идеи в один пункт)

ТРАНСКРИПЦИЯ:
{text}

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "jobs": [
    {{
      "text": "описание работы/цели",
      "quote": "прямая цитата из транскрипции",
      "type": "functional|emotional|social",
      "confidence": "high|medium|low"
    }}
  ],
  "pains": [
    {{
      "text": "описание боли/проблемы",
      "quote": "прямая цитата из транскрипции",
      "severity": "critical|high|medium|low",
      "confidence": "high|medium|low"
    }}
  ],
  "gains": [
    {{
      "text": "описание выгоды/результата",
      "quote": "прямая цитата из транскрипции",
      "type": "required|expected|desired|unexpected",
      "confidence": "high|medium|low"
    }}
  ],
  "context": [
    {{
      "text": "описание контекста/ситуации",
      "quote": "прямая цитата из транскрипции",
      "dimension": "when|where|who|constraints",
      "confidence": "high|medium|low"
    }}
  ],
  "triggers": [
    {{
      "text": "описание триггера/события",
      "quote": "прямая цитата из транскрипции",
      "type": "event|problem|switching_moment",
      "confidence": "high|medium|low"
    }}
  ],
  "summary": "краткое резюме: основная работа пользователя и ключевые инсайты (2-3 предложения)"
}}

Верни ТОЛЬКО валидный JSON, без дополнительных комментариев."""

    def analyze(self, text: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """
        Анализ транскрипции по JTBD фреймворку
        
        Args:
            text: текст транскрипции
            max_tokens: максимальное количество токенов для ответа
            
        Returns:
            Словарь с элементами JTBD:
            {
                "jobs": [...],
                "pains": [...],
                "gains": [...],
                "context": [...],
                "triggers": [...],
                "summary": "...",
                "metadata": {...}
            }
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for JTBD analysis")
            return self._empty_result("Пустой текст")
        
        try:
            logger.info(f"Starting JTBD analysis ({len(text)} chars)")
            
            # Вызов Claude API
            prompt = self._build_prompt(text)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Извлечение текста ответа
            response_text = message.content[0].text
            
            logger.debug(f"Claude response length: {len(response_text)} chars")
            
            # Парсинг JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Claude: {e}")
                logger.debug(f"Raw response: {response_text[:500]}")
                
                # Попытка извлечь JSON из markdown блока
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                    result = json.loads(json_text)
                else:
                    raise ValueError("Не удалось извлечь JSON из ответа Claude")
            
            # Добавление метаданных
            result["metadata"] = {
                "model": self.model,
                "input_length": len(text),
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "total_elements": (
                    len(result.get("jobs", [])) +
                    len(result.get("pains", [])) +
                    len(result.get("gains", [])) +
                    len(result.get("context", [])) +
                    len(result.get("triggers", []))
                )
            }
            
            logger.info(
                f"JTBD analysis completed: {result['metadata']['total_elements']} elements, "
                f"{result['metadata']['input_tokens']} in / {result['metadata']['output_tokens']} out tokens"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"JTBD analysis failed: {e}")
            return self._empty_result(f"Ошибка анализа: {str(e)}")
    
    def _empty_result(self, error: str = "") -> Dict[str, Any]:
        """
        Пустой результат (при ошибке или пустом тексте)
        
        Args:
            error: текст ошибки
            
        Returns:
            Пустая структура JTBD
        """
        return {
            "jobs": [],
            "pains": [],
            "gains": [],
            "context": [],
            "triggers": [],
            "summary": error or "Анализ не выполнен",
            "metadata": {
                "model": self.model,
                "error": error,
                "total_elements": 0
            }
        }
    
    def analyze_batch(self, texts: List[str], max_tokens: int = 4000) -> List[Dict[str, Any]]:
        """
        Пакетный анализ нескольких транскрипций
        
        Args:
            texts: список текстов для анализа
            max_tokens: максимальное количество токенов для каждого ответа
            
        Returns:
            Список результатов JTBD анализа
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Analyzing text {i+1}/{len(texts)}")
            result = self.analyze(text, max_tokens=max_tokens)
            results.append(result)
        
        return results
    
    def format_as_markdown(self, result: Dict[str, Any]) -> str:
        """
        Форматирование результата JTBD в Markdown
        
        Args:
            result: результат анализа
            
        Returns:
            Отформатированный Markdown текст
        """
        md = ["# JTBD Analysis Results\n"]
        
        # Summary
        if result.get("summary"):
            md.append(f"## 📋 Summary\n\n{result['summary']}\n")
        
        # Jobs
        if result.get("jobs"):
            md.append("## 🎯 Jobs (Работы)\n")
            for job in result["jobs"]:
                md.append(f"- **{job['text']}**")
                if job.get("quote"):
                    md.append(f"  > \"{job['quote']}\"")
                md.append(f"  - Type: {job.get('type', 'N/A')}, Confidence: {job.get('confidence', 'N/A')}\n")
        
        # Pains
        if result.get("pains"):
            md.append("## 😰 Pains (Боли)\n")
            for pain in result["pains"]:
                md.append(f"- **{pain['text']}**")
                if pain.get("quote"):
                    md.append(f"  > \"{pain['quote']}\"")
                md.append(f"  - Severity: {pain.get('severity', 'N/A')}, Confidence: {pain.get('confidence', 'N/A')}\n")
        
        # Gains
        if result.get("gains"):
            md.append("## 🎁 Gains (Выгоды)\n")
            for gain in result["gains"]:
                md.append(f"- **{gain['text']}**")
                if gain.get("quote"):
                    md.append(f"  > \"{gain['quote']}\"")
                md.append(f"  - Type: {gain.get('type', 'N/A')}, Confidence: {gain.get('confidence', 'N/A')}\n")
        
        # Context
        if result.get("context"):
            md.append("## 🌍 Context (Контекст)\n")
            for ctx in result["context"]:
                md.append(f"- **{ctx['text']}**")
                if ctx.get("quote"):
                    md.append(f"  > \"{ctx['quote']}\"")
                md.append(f"  - Dimension: {ctx.get('dimension', 'N/A')}, Confidence: {ctx.get('confidence', 'N/A')}\n")
        
        # Triggers
        if result.get("triggers"):
            md.append("## 🚀 Triggers (Триггеры)\n")
            for trigger in result["triggers"]:
                md.append(f"- **{trigger['text']}**")
                if trigger.get("quote"):
                    md.append(f"  > \"{trigger['quote']}\"")
                md.append(f"  - Type: {trigger.get('type', 'N/A')}, Confidence: {trigger.get('confidence', 'N/A')}\n")
        
        # Metadata
        if result.get("metadata"):
            meta = result["metadata"]
            md.append("\n---\n")
            md.append("## 📊 Metadata\n")
            md.append(f"- Model: {meta.get('model', 'N/A')}\n")
            md.append(f"- Total Elements: {meta.get('total_elements', 0)}\n")
            if meta.get("input_tokens"):
                md.append(f"- Tokens: {meta['input_tokens']} in / {meta.get('output_tokens', 0)} out\n")
        
        return "\n".join(md)


if __name__ == "__main__":
    # Пример использования
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python jtbd_analyzer.py <text_file>")
        sys.exit(1)
    
    # Чтение файла
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Анализ
    analyzer = JTBDAnalyzer()
    result = analyzer.analyze(text)
    
    # Вывод
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "="*80 + "\n")
    print(analyzer.format_as_markdown(result))
