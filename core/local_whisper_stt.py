#!/usr/bin/env python3
"""
Local Whisper STT provider for HearYou.

Uses faster-whisper by default and keeps the response shape close to Yandex
SpeechKit: top-level `result`, plus `chunks[*].alternatives[*].words` for
speaker diarization merge code.
"""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


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


@dataclass(frozen=True)
class WhisperSettings:
    model: str
    device: str
    compute_type: str
    cpu_threads: int
    num_workers: int
    beam_size: int
    vad_filter: bool
    model_dir: Optional[str]

    @classmethod
    def from_env(cls) -> "WhisperSettings":
        return cls(
            model=os.getenv("WHISPER_MODEL", "small"),
            device=os.getenv("WHISPER_DEVICE", "cpu"),
            compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
            cpu_threads=_env_int("WHISPER_CPU_THREADS", max(os.cpu_count() or 1, 1)),
            num_workers=_env_int("WHISPER_NUM_WORKERS", 1),
            beam_size=_env_int("WHISPER_BEAM_SIZE", 5),
            vad_filter=os.getenv("WHISPER_VAD_FILTER", "true").lower() not in {"0", "false", "no"},
            model_dir=os.getenv("WHISPER_MODEL_DIR") or None,
        )


class LocalWhisperSTT:
    """faster-whisper provider with lazy model initialization."""

    def __init__(self, settings: Optional[WhisperSettings] = None):
        self.settings = settings or WhisperSettings.from_env()
        self._model = None
        self._operations: Dict[str, Dict] = {}

    @property
    def model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed. Install packages/stt-service/requirements.txt "
                    "or add faster-whisper to the environment."
                ) from exc

            kwargs = {
                "device": self.settings.device,
                "compute_type": self.settings.compute_type,
                "cpu_threads": self.settings.cpu_threads,
                "num_workers": self.settings.num_workers,
            }
            if self.settings.model_dir:
                kwargs["download_root"] = self.settings.model_dir

            self._model = WhisperModel(self.settings.model, **kwargs)
        return self._model

    def transcribe_sync(
        self,
        audio_file: str,
        language: str = "ru-RU",
        format: str = "auto",
        profanity_filter: bool = False,
        punctuation: bool = True,
        hints: Optional[List[str]] = None,
        literature_text: bool = False,
    ) -> Dict:
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        segments, info = self.model.transcribe(
            audio_file,
            language=_map_language(language),
            beam_size=self.settings.beam_size,
            vad_filter=self.settings.vad_filter,
            word_timestamps=True,
            initial_prompt=", ".join(hints or []) or None,
        )

        chunks = []
        text_parts = []

        for segment in segments:
            segment_text = (segment.text or "").strip()
            if segment_text:
                text_parts.append(segment_text)

            words = []
            for word in segment.words or []:
                token = (word.word or "").strip()
                if not token:
                    continue
                words.append({
                    "word": token,
                    "startTime": _seconds(float(word.start or 0.0)),
                    "endTime": _seconds(float(word.end or 0.0)),
                })

            chunks.append({
                "alternatives": [{
                    "text": segment_text,
                    "words": words,
                }],
                "startTime": _seconds(float(segment.start or 0.0)),
                "endTime": _seconds(float(segment.end or 0.0)),
            })

        text = " ".join(text_parts).strip()
        return {
            "result": text,
            "chunks": chunks,
            "provider": "local-whisper",
            "model": self.settings.model,
            "language": getattr(info, "language", _map_language(language)),
            "language_probability": getattr(info, "language_probability", None),
            "duration": getattr(info, "duration", None),
        }

    def transcribe_async(
        self,
        audio_file: str,
        language: str = "ru-RU",
        profanity_filter: bool = False,
        punctuation: bool = True,
        literature_text: bool = False,
        auto_upload: bool = True,
    ) -> str:
        operation_id = f"local-{uuid.uuid4().hex}"
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

    def check_operation(self, operation_id: str) -> Dict:
        if operation_id not in self._operations:
            return {"done": False}
        return self._operations[operation_id]

    def wait_for_completion(
        self,
        operation_id: str,
        timeout: int = 600,
        poll_interval: int = 5,
    ) -> Dict:
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
