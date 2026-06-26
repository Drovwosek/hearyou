#!/usr/bin/env python3
"""
OpenAI-compatible transcription provider for HearYou.
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


def _env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


def _load_key_from_env_file(path: str, key_name: str) -> Optional[str]:
    env_path = Path(path)
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(key_name + ":"):
            return stripped.split(":", 1)[1].strip() or None
        if stripped.startswith(key_name + "="):
            return stripped.split("=", 1)[1].strip() or None
    return None


def _map_language(language: str) -> Optional[str]:
    if not language:
        return None
    normalized = language.strip()
    mapping = {
        "ru-RU": "ru",
        "en-US": "en",
        "tr-TR": "tr",
        "uk-UK": "uk",
        "uz-UZ": "uz",
        "kk-KK": "kk",
        "de-DE": "de",
        "fr-FR": "fr",
        "es-ES": "es",
    }
    if normalized in mapping:
        return mapping[normalized]
    if len(normalized) == 2:
        return normalized.lower()
    if "-" in normalized:
        return normalized.split("-", 1)[0].lower()
    return None


def _seconds(value: float) -> str:
    return f"{max(value, 0.0):.3f}s"


def _tokenize(text: str) -> List[str]:
    return [token for token in (text or "").split() if token]


def _synthesize_words(text: str, start: float, end: float) -> List[Dict[str, str]]:
    words = _tokenize(text)
    if not words:
        return []

    if end <= start:
        return [
            {
                "word": word,
                "startTime": _seconds(start),
                "endTime": _seconds(end),
            }
            for word in words
        ]

    step = (end - start) / max(len(words), 1)
    synthesized = []
    current = start
    for idx, word in enumerate(words):
        word_start = current
        word_end = end if idx == len(words) - 1 else min(end, current + step)
        synthesized.append(
            {
                "word": word,
                "startTime": _seconds(word_start),
                "endTime": _seconds(word_end),
            }
        )
        current = word_end
    return synthesized


class OpusTranscriptionSTT:
    provider_name = "opus-api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        env_file = _env("OPUS_ENV_FILE", "/Users/kaban/codex/.env")
        self.api_key = (
            api_key
            or _env("API_KEY_OPUS", "")
            or _env("OPENAI_API_KEY", "")
            or _load_key_from_env_file(env_file, "API_KEY_OPUS")
            or _load_key_from_env_file(env_file, "OPENAI_API_KEY")
            or ""
        ).strip()
        if not self.api_key:
            raise ValueError("API_KEY_OPUS or OPENAI_API_KEY is required for remote transcription")

        self.base_url = (base_url or _env("OPUS_BASE_URL", "") or _env("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or _env("OPUS_TRANSCRIPTION_MODEL", "whisper-1")
        self.response_format = _env("OPUS_TRANSCRIPTION_FORMAT", "verbose_json")
        self._operations: Dict[str, Dict[str, Any]] = {}

    def _request(self, audio_file: str, language: str, hints: Optional[List[str]]) -> Dict[str, Any]:
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        payload = {
            "model": self.model,
            "response_format": self.response_format,
            "temperature": "0",
        }

        mapped_language = _map_language(language)
        if mapped_language:
            payload["language"] = mapped_language

        prompt = ", ".join(hints or []).strip()
        if prompt:
            payload["prompt"] = prompt

        payload["timestamp_granularities[]"] = "word"

        with open(audio_file, "rb") as audio_handle:
            files = {"file": (Path(audio_file).name, audio_handle)}
            response = requests.post(
                self.base_url + "/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                data=payload,
                timeout=900,
            )

        if not response.ok:
            detail = response.text.strip()
            try:
                parsed = response.json()
                detail = parsed.get("error", {}).get("message", detail) or detail
            except Exception:
                pass
            raise RuntimeError(f"Remote transcription API error: {detail[:500]}")

        data = response.json()
        text = (data.get("text") or "").strip()
        chunks = []
        text_parts = []

        segments = data.get("segments") or []
        if segments:
            for segment in segments:
                segment_text = (segment.get("text") or "").strip()
                if segment_text:
                    text_parts.append(segment_text)

                words = []
                for word in segment.get("words") or []:
                    token = (word.get("word") or "").strip()
                    if not token:
                        continue
                    words.append(
                        {
                            "word": token,
                            "startTime": _seconds(float(word.get("start", word.get("start_time", 0.0)) or 0.0)),
                            "endTime": _seconds(float(word.get("end", word.get("end_time", 0.0)) or 0.0)),
                        }
                    )

                if not words and segment_text:
                    words = _synthesize_words(
                        segment_text,
                        float(segment.get("start", 0.0) or 0.0),
                        float(segment.get("end", 0.0) or 0.0),
                    )

                chunks.append(
                    {
                        "alternatives": [{
                            "text": segment_text,
                            "words": words,
                        }],
                        "startTime": _seconds(float(segment.get("start", 0.0) or 0.0)),
                        "endTime": _seconds(float(segment.get("end", 0.0) or 0.0)),
                    }
                )

        if not chunks:
            words = []
            for word in data.get("words") or []:
                token = (word.get("word") or "").strip()
                if not token:
                    continue
                words.append(
                    {
                        "word": token,
                        "startTime": _seconds(float(word.get("start", word.get("start_time", 0.0)) or 0.0)),
                        "endTime": _seconds(float(word.get("end", word.get("end_time", 0.0)) or 0.0)),
                    }
                )
            if not words and text:
                words = _synthesize_words(text, 0.0, float(data.get("duration", 0.0) or 0.0))

            if words:
                chunks.append(
                    {
                        "alternatives": [{"text": text, "words": words}],
                        "startTime": _seconds(0.0),
                        "endTime": _seconds(float(data.get("duration", 0.0) or 0.0)),
                    }
                )
            elif text:
                chunks.append(
                    {
                        "alternatives": [{"text": text, "words": []}],
                        "startTime": _seconds(0.0),
                        "endTime": _seconds(float(data.get("duration", 0.0) or 0.0)),
                    }
                )

        if not text:
            text = " ".join(text_parts).strip()

        return {
            "result": text,
            "chunks": chunks,
            "provider": self.provider_name,
            "model": self.model,
            "language": data.get("language") or _map_language(language),
            "duration": data.get("duration"),
            "raw": data,
        }

    def transcribe_sync(
        self,
        audio_file: str,
        language: str = "ru-RU",
        format: str = "auto",
        profanity_filter: bool = False,
        punctuation: bool = True,
        hints: Optional[List[str]] = None,
        literature_text: bool = False,
    ) -> Dict[str, Any]:
        return self._request(audio_file, language, hints)

    def transcribe_async(
        self,
        audio_file: str,
        language: str = "ru-RU",
        profanity_filter: bool = False,
        punctuation: bool = True,
        literature_text: bool = False,
        auto_upload: bool = True,
    ) -> str:
        operation_id = f"opus-{uuid.uuid4().hex}"
        try:
            result = self.transcribe_sync(
                audio_file,
                language=language,
                profanity_filter=profanity_filter,
                punctuation=punctuation,
                literature_text=literature_text,
            )
            self._operations[operation_id] = {"done": True, "response": result}
        except Exception as exc:
            self._operations[operation_id] = {"done": True, "error": str(exc)}
        return operation_id

    def check_operation(self, operation_id: str) -> Dict[str, Any]:
        if operation_id not in self._operations:
            return {"done": False}
        return self._operations[operation_id]

    def wait_for_completion(
        self,
        operation_id: str,
        timeout: int = 600,
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            operation = self.check_operation(operation_id)
            if operation.get("done"):
                if "error" in operation:
                    raise RuntimeError(operation["error"])
                return operation.get("response", {})
            time.sleep(poll_interval)
        raise TimeoutError(f"Transcription operation timed out: {operation_id}")

    def delete_from_storage(self, object_name: str):
        return None
