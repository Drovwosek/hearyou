#!/usr/bin/env python3
"""
Shared STT provider contract for HearYou.

Runtime services should depend on this protocol instead of a concrete cloud
client. Implementations return a Yandex-compatible result shape so the rest of
the pipeline can keep using `result` and `chunks` without API changes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Protocol


class STTProvider(Protocol):
    """Speech-to-text provider interface used by the service runtime."""

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
        """Transcribe a local audio file and return a compatible result dict."""

    def transcribe_async(
        self,
        audio_file: str,
        language: str = "ru-RU",
        profanity_filter: bool = False,
        punctuation: bool = True,
        literature_text: bool = False,
        auto_upload: bool = True,
    ) -> str:
        """Start transcription and return an operation id if backend supports it."""

    def check_operation(self, operation_id: str) -> Dict:
        """Return async operation status."""

    def wait_for_completion(
        self,
        operation_id: str,
        timeout: int = 600,
        poll_interval: int = 5,
    ) -> Dict:
        """Wait for async operation completion."""

    def delete_from_storage(self, object_name: str):
        """Cleanup backend storage when applicable."""
