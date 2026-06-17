#!/usr/bin/env python3
"""
Unit-тесты для локального Whisper STT-провайдера.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.local_whisper_stt import LocalWhisperSTT, WhisperSettings


class FakeWhisperSTT(LocalWhisperSTT):
    def __init__(self):
        settings = WhisperSettings(
            model="tiny",
            device="cpu",
            compute_type="int8",
            cpu_threads=1,
            num_workers=1,
            beam_size=1,
            vad_filter=True,
            model_dir=None,
        )
        super().__init__(settings)
        self.fake_model = Mock()

    @property
    def model(self):
        return self.fake_model


def make_segment(text, start=0.0, end=1.0):
    return SimpleNamespace(
        text=text,
        start=start,
        end=end,
        words=[
            SimpleNamespace(word="Привет", start=start, end=start + 0.4),
            SimpleNamespace(word="мир", start=start + 0.5, end=end),
        ],
    )


class TestWhisperSettings:
    def test_settings_from_env(self, monkeypatch):
        monkeypatch.setenv("WHISPER_MODEL", "medium")
        monkeypatch.setenv("WHISPER_DEVICE", "cpu")
        monkeypatch.setenv("WHISPER_COMPUTE_TYPE", "int8")
        monkeypatch.setenv("WHISPER_CPU_THREADS", "4")
        monkeypatch.setenv("WHISPER_NUM_WORKERS", "2")
        monkeypatch.setenv("WHISPER_BEAM_SIZE", "3")
        monkeypatch.setenv("WHISPER_VAD_FILTER", "false")
        monkeypatch.setenv("WHISPER_MODEL_DIR", "/tmp/models")

        settings = WhisperSettings.from_env()

        assert settings.model == "medium"
        assert settings.device == "cpu"
        assert settings.compute_type == "int8"
        assert settings.cpu_threads == 4
        assert settings.num_workers == 2
        assert settings.beam_size == 3
        assert settings.vad_filter is False
        assert settings.model_dir == "/tmp/models"

    def test_settings_do_not_require_yandex_credentials(self, monkeypatch):
        monkeypatch.delenv("YANDEX_API_KEY", raising=False)
        monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)

        settings = WhisperSettings.from_env()

        assert settings.model
        assert settings.device


class TestLocalWhisperSTT:
    def test_transcribe_sync_returns_compatible_shape(self, test_audio_file):
        stt = FakeWhisperSTT()
        stt.fake_model.transcribe.return_value = (
            [make_segment("Привет мир")],
            SimpleNamespace(language="ru", language_probability=0.99, duration=1.0),
        )

        result = stt.transcribe_sync(test_audio_file, language="ru-RU", hints=["iSpring"])

        assert result["result"] == "Привет мир"
        assert result["provider"] == "local-whisper"
        assert result["model"] == "tiny"
        assert result["language"] == "ru"
        assert result["chunks"][0]["alternatives"][0]["text"] == "Привет мир"
        assert result["chunks"][0]["alternatives"][0]["words"][0] == {
            "word": "Привет",
            "startTime": "0.000s",
            "endTime": "0.400s",
        }
        stt.fake_model.transcribe.assert_called_once()
        _, kwargs = stt.fake_model.transcribe.call_args
        assert kwargs["language"] == "ru"
        assert kwargs["word_timestamps"] is True
        assert kwargs["initial_prompt"] == "iSpring"

    def test_transcribe_sync_rejects_missing_file(self):
        stt = FakeWhisperSTT()

        with pytest.raises(FileNotFoundError):
            stt.transcribe_sync("/tmp/does-not-exist.wav")

    def test_transcribe_async_stores_completed_operation(self, test_audio_file):
        stt = FakeWhisperSTT()
        stt.fake_model.transcribe.return_value = (
            [make_segment("Привет мир")],
            SimpleNamespace(language="ru", language_probability=0.99, duration=1.0),
        )

        operation_id = stt.transcribe_async(test_audio_file, language="ru-RU")
        operation = stt.check_operation(operation_id)
        result = stt.wait_for_completion(operation_id, timeout=1, poll_interval=0)

        assert operation["done"] is True
        assert result["result"] == "Привет мир"

    def test_check_unknown_operation_is_pending(self):
        stt = FakeWhisperSTT()

        assert stt.check_operation("missing") == {"done": False}

    def test_delete_from_storage_is_noop(self):
        stt = FakeWhisperSTT()

        assert stt.delete_from_storage("anything") is None
