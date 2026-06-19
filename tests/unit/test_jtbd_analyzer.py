#!/usr/bin/env python3
"""
Unit-тесты для JTBDAnalyzer.
"""

import json as json_module

import pytest

from core.jtbd_analyzer import JTBDAnalyzer


class FakeResponse:
    def __init__(self, payload, ok=True):
        self._payload = payload
        self.ok = ok
        self.text = json_module.dumps(payload, ensure_ascii=False)

    def json(self):
        return self._payload


def test_apinet_provider_is_selected(monkeypatch):
    monkeypatch.setenv("APINET_API_KEY", "test-key")
    monkeypatch.setenv("APINET_MODEL", "qwen3-vl-plus")

    analyzer = JTBDAnalyzer()

    assert analyzer.provider == "apinet"
    assert analyzer.model == "qwen3-vl-plus"


def test_apinet_analyze_parses_json(monkeypatch):
    monkeypatch.setenv("APINET_API_KEY", "test-key")
    monkeypatch.setenv("APINET_MODEL", "qwen3-vl-plus")

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse({
            "choices": [{
                "message": {
                    "content": json_module.dumps({
                        "jobs": [],
                        "pains": [],
                        "gains": [],
                        "context": [],
                        "triggers": [],
                        "summary": "ok",
                    }, ensure_ascii=False),
                }
            }],
            "usage": {"prompt_tokens": 12, "completion_tokens": 34},
        })
    monkeypatch.setattr("core.jtbd_analyzer.requests.post", fake_post)

    analyzer = JTBDAnalyzer()
    result = analyzer.analyze("Пример транскрипции")

    assert captured["url"] == "https://apinet.cloud/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "qwen3-vl-plus"
    assert captured["json"]["messages"][0]["role"] == "system"
    assert result["summary"] == "ok"
    assert result["metadata"]["provider"] == "apinet"
    assert result["metadata"]["input_tokens"] == 12
    assert result["metadata"]["output_tokens"] == 34
